"""
Dashboard Voice Backend — TTS (edge-tts) + STT (faster-whisper).
Provides audio generation and transcription for the dashboard chat.
"""

import asyncio
import io
import json
import logging
import os
import tempfile
from pathlib import Path

import edge_tts
from faster_whisper import WhisperModel

logger = logging.getLogger("mantisclaw.dashboard.voice")

# Lazy-load whisper model (heavy on first call)
_whisper_model: WhisperModel | None = None
VOICE_CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "voice_config.json"

# In-memory voice conversation (separate from project chats)
_voice_history: list[dict] = []
MAX_VOICE_HISTORY = 20


def _get_whisper() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        logger.info("Loading Whisper model (base, CPU)...")
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Whisper model loaded.")
    return _whisper_model


def load_voice_config() -> dict:
    """Load persistent voice config from data/voice_config.json."""
    defaults = {"name": "", "voice": "de-DE-KatjaNeural", "enabled": True, "auto_read": False}
    if VOICE_CONFIG_PATH.exists():
        try:
            with open(VOICE_CONFIG_PATH, "r", encoding="utf-8") as f:
                stored = json.load(f)
                defaults.update(stored)
        except Exception:
            pass
    return defaults


def save_voice_config(config: dict):
    """Save voice config to data/voice_config.json."""
    VOICE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(VOICE_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


async def generate_tts(text: str, voice: str | None = None) -> bytes:
    """Generate TTS audio bytes (MP3) from text using edge-tts."""
    if not voice:
        voice = load_voice_config().get("voice", "de-DE-KatjaNeural")
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data


def transcribe_audio(audio_bytes: bytes, language: str = "de") -> str:
    """Transcribe audio bytes (WAV/WebM) to text using faster-whisper."""
    model = _get_whisper()
    # Write to temp file — whisper needs a file path
    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    try:
        os.write(fd, audio_bytes)
        os.close(fd)
        segments, _info = model.transcribe(tmp_path, beam_size=5, language=language)
        text = "".join([seg.text for seg in segments]).strip()
        return text
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def get_greeting_level() -> str:
    """Determine greeting level: first_start, new_session, or resume."""
    config = load_voice_config()
    if not config.get("name"):
        return "first_start"

    # Check for open workpapers
    wp_dir = Path(__file__).resolve().parent.parent / "WORKSPACE" / "WORKING" / "WORKPAPER"
    if wp_dir.exists():
        open_wps = [f for f in wp_dir.iterdir() if f.is_file() and f.suffix == ".md"]
        if open_wps:
            return "resume"

    return "new_session"


def get_greeting_context() -> dict:
    """Build context for the greeting prompt."""
    config = load_voice_config()
    level = get_greeting_level()
    agent_name = config.get("name") or "Mantis"

    context = {
        "level": level,
        "agent_name": agent_name,
        "voice": config.get("voice", "de-DE-KatjaNeural"),
    }

    if level == "resume":
        wp_dir = Path(__file__).resolve().parent.parent / "WORKSPACE" / "WORKING" / "WORKPAPER"
        open_wps = sorted(
            [f for f in wp_dir.iterdir() if f.is_file() and f.suffix == ".md"],
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        if open_wps:
            latest = open_wps[0]
            context["latest_workpaper"] = latest.name
            # Read first 20 lines for summary
            try:
                with open(latest, "r", encoding="utf-8") as f:
                    lines = f.readlines()[:20]
                context["workpaper_excerpt"] = "".join(lines)
            except Exception:
                pass

    elif level == "new_session":
        # Check closed workpapers for the last one worked on
        closed_dir = Path(__file__).resolve().parent.parent / "WORKSPACE" / "WORKING" / "WORKPAPER" / "closed"
        if closed_dir.exists():
            closed_wps = sorted(
                [f for f in closed_dir.iterdir() if f.is_file() and f.suffix == ".md"],
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            if closed_wps:
                context["last_closed_workpaper"] = closed_wps[0].name

    return context


def build_greeting_prompt(context: dict) -> str:
    """Build the system prompt for the greeting based on level."""
    name = context["agent_name"]
    level = context["level"]

    if level == "first_start":
        return (
            f"Du bist {name}, ein autonomer KI-Agent. "
            "Dies ist dein allererster Start. "
            "Stelle dich kurz vor mit deinem Namen. "
            "Frage den Nutzer, ob er eine männliche oder weibliche Stimme für dich bevorzugt "
            "und ob er dir einen anderen Namen geben möchte. "
            "Weise darauf hin, dass das Mikrofon jederzeit ausgeschaltet werden kann. "
            "Antworte kurz und freundlich, maximal 4 Sätze."
        )

    elif level == "new_session":
        last_wp = context.get("last_closed_workpaper", "")
        return (
            f"Du bist {name}, ein autonomer KI-Agent. Neuer Session-Start. "
            f"Kein offenes Projekt. Letztes abgeschlossenes Workpaper: {last_wp}. "
            "Begrüße den Nutzer kurz mit deinem Namen, "
            "frage was heute ansteht und schlage vor, am letzten Thema weiterzuarbeiten. "
            "Weise kurz darauf hin, dass das Mikro ausgeschaltet werden kann. "
            "Maximal 4 Sätze."
        )

    else:  # resume
        wp_name = context.get("latest_workpaper", "")
        excerpt = context.get("workpaper_excerpt", "")
        return (
            f"Du bist {name}, ein autonomer KI-Agent. Session-Wiederaufnahme. "
            f"Aktuelles offenes Workpaper: {wp_name}. "
            f"Inhalt (Auszug):\n{excerpt}\n"
            "Begrüße den Nutzer kurz, fasse den aktuellen Stand in 2-3 Sätzen zusammen "
            "und warte auf Instruktionen. Maximal 4 Sätze."
        )


def get_voice_system_prompt() -> str:
    """System prompt for the L5 voice assistant conversation."""
    config = load_voice_config()
    name = config.get("name") or "Mantis"
    personality = config.get("personality") or "freundlich, direkt, hilfsbereit"
    voice_type = "weibliche" if "Katja" in config.get("voice", "Katja") else "männliche"
    return (
        f"Du bist {name}, ein autonomer KI-Agent und Voice-Assistent mit {voice_type}r Stimme. "
        f"Deine Persönlichkeit: {personality}. "
        "Du kommunizierst per Sprache — antworte kurz, klar und auf Deutsch. "
        "Maximal 3 Sätze pro Antwort. Sei direkt und hilfreich. "
        "Wenn der Nutzer dir einen Auftrag gibt, bestätige kurz und fasse zusammen was du tun wirst."
    )


# ========== ACTION CLASSIFICATION ==========

CLASSIFY_SYSTEM_PROMPT = """Du bist ein Intent-Classifier für einen Voice-Assistenten in einem Agenten-Tool.
Klassifiziere den User-Text in GENAU EINE Kategorie. Antworte NUR mit dem Kategorie-Kürzel.

Kategorien:
- IDENTITY: User gibt Informationen über Assistenten-Identität (Name, Stimme, Geschlecht, Sprachstil, Persönlichkeit)
  Beispiele: "Nenn dich Mantis", "Sprich weiblich", "Sei lockerer", "männliche Stimme"
- SYSTEM: User fragt nach System-Zustand oder gibt System-Befehle (Projekte, Workpapers, Konversationen)
  Beispiele: "In welchem Projekt sind wir?", "Öffne die letzte Konversation", "Lege ein neues Workpaper an", "Was ist offen?"
- CHAT: Normale Konversation, Fragen, Smalltalk, allgemeine Anweisungen
  Beispiele: "Wie geht es dir?", "Was kannst du?", "Erkläre mir X"

Antworte NUR: IDENTITY oder SYSTEM oder CHAT"""


def build_classify_prompt(user_text: str) -> list[dict]:
    """Build messages for action classification."""
    return [
        {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]


def parse_action_intent(llm_response: str) -> str:
    """Extract action intent from classifier response."""
    text = llm_response.strip().upper()
    # Handle think tags from reasoning models
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    for intent in ("IDENTITY", "SYSTEM", "CHAT"):
        if intent in text:
            return intent
    return "CHAT"  # Safe fallback


def extract_identity_updates(user_text: str, assistant_response: str) -> dict:
    """Extract identity-relevant changes from conversation context."""
    updates = {}
    text_lower = user_text.lower()

    # Name extraction — patterns: "nenn dich X", "heiß X", "name X", "X heißen"
    import re

    # Pattern 1: "nenn dich NAME" / "name sei NAME" / "name ist NAME"
    name_match = re.search(r'(?:nenn\s+dich|name\s+(?:ist|sei))\s+([A-Za-zÄÖÜäöüß]+)', user_text, re.IGNORECASE)
    if not name_match:
        # Pattern 2: "NAME heißen" / "NAME heissen"
        name_match = re.search(r'([A-Za-zÄÖÜäöüß]{2,})\s+hei[ßs]en', user_text, re.IGNORECASE)
    if not name_match:
        # Pattern 3: "heiß NAME" / "heißt NAME"
        name_match = re.search(r'hei[ßs](?:t|e)?\s+([A-Za-zÄÖÜäöüß]+)', user_text, re.IGNORECASE)

    if name_match:
        candidate = name_match.group(1).strip(".,!?")
        # Filter out common non-name words
        non_names = {"und", "oder", "ist", "sei", "bitte", "dich", "du", "ich", "ein", "eine"}
        if candidate.lower() not in non_names and len(candidate) >= 2:
            updates["name"] = candidate

    # Voice / gender
    if any(w in text_lower for w in ["weiblich", "frau", "weibliche stimme", "katja"]):
        updates["voice"] = "de-DE-KatjaNeural"
    elif any(w in text_lower for w in ["männlich", "mann", "männliche stimme", "conrad"]):
        updates["voice"] = "de-DE-ConradNeural"

    # Speed hints
    if any(w in text_lower for w in ["schneller", "tempo", "zügiger", "kürzer"]):
        updates["style_hint"] = "schnell und direkt"
    elif any(w in text_lower for w in ["langsam", "ruhig", "gemächlich"]):
        updates["style_hint"] = "ruhig und bedächtig"

    return updates


def apply_identity_updates(updates: dict) -> str:
    """Apply identity updates to voice config. Returns summary of what changed."""
    if not updates:
        return ""
    config = load_voice_config()
    changes = []

    if "name" in updates:
        config["name"] = updates["name"]
        changes.append(f"Name → {updates['name']}")

    if "voice" in updates:
        config["voice"] = updates["voice"]
        voice_label = "weiblich" if "Katja" in updates["voice"] else "männlich"
        changes.append(f"Stimme → {voice_label}")

    if "style_hint" in updates:
        config["personality"] = updates["style_hint"]
        changes.append(f"Stil → {updates['style_hint']}")

    save_voice_config(config)
    return ", ".join(changes)


def get_system_context() -> dict:
    """Gather current system context for SYSTEM intent responses."""
    from pathlib import Path
    import yaml

    workspace = Path(__file__).resolve().parent.parent / "WORKSPACE" / "WORKING"
    result = {"project": None, "workpapers": [], "latest_workpaper": None, "whitepapers": []}

    # Active project
    active_file = workspace / "PROJECT" / "_active.yaml"
    if active_file.exists():
        try:
            data = yaml.safe_load(active_file.read_text(encoding="utf-8"))
            slug = data.get("active_project")
            if slug:
                proj_file = workspace / "PROJECT" / slug / "project.yaml"
                if proj_file.exists():
                    proj = yaml.safe_load(proj_file.read_text(encoding="utf-8"))
                    result["project"] = {
                        "name": proj.get("name", slug),
                        "slug": slug,
                        "status": proj.get("status", "unknown"),
                    }
        except Exception:
            pass

    # Open workpapers
    wp_dir = workspace / "WORKPAPER"
    if wp_dir.exists():
        for f in sorted(wp_dir.glob("*.md"), reverse=True):
            content = f.read_text(encoding="utf-8", errors="ignore")[:200]
            is_closed = "**Status:** CLOSED" in content
            if not is_closed:
                result["workpapers"].append(f.stem)
        if result["workpapers"]:
            result["latest_workpaper"] = result["workpapers"][0]

    # Whitepapers
    wh_dir = workspace / "WHITEPAPER"
    if wh_dir.exists():
        for f in sorted(wh_dir.glob("*.md")):
            result["whitepapers"].append(f.stem)

    return result


def build_system_response_prompt(user_text: str, context: dict) -> str:
    """Build a system prompt that includes system context for answering system queries."""
    config = load_voice_config()
    name = config.get("name") or "Mantis"

    project_info = "Kein aktives Projekt." if not context["project"] else (
        f"Aktives Projekt: {context['project']['name']} (Status: {context['project']['status']})"
    )
    wp_info = "Keine offenen Workpapers." if not context["workpapers"] else (
        f"Offene Workpapers ({len(context['workpapers'])}): {', '.join(context['workpapers'][:5])}"
    )
    wh_info = "Keine Whitepapers." if not context.get("whitepapers") else (
        f"Whitepapers (stabile Architektur-Wahrheit): {', '.join(context['whitepapers'])}"
    )

    return (
        f"Du bist {name}, ein autonomer KI-Agent. Beantworte die System-Frage kurz und präzise auf Deutsch.\n"
        f"Aktueller System-Zustand:\n- {project_info}\n- {wp_info}\n- {wh_info}\n"
        f"- Letztes Workpaper: {context.get('latest_workpaper', 'keins')}\n"
        f"- Arbeitsweise: AAMS (Autonomous Agent Manifest Specification)\n"
        "Antworte in maximal 3 Sätzen. Wenn der User einen Befehl gibt (z.B. 'lege Workpaper an'), "
        "antworte mit Bestätigung und gib das Aktions-Tag zurück: [ACTION:BEFEHL]\n"
        "Mögliche Aktionen: [ACTION:CREATE_WORKPAPER], [ACTION:OPEN_CONVERSATION], [ACTION:LIST_WORKPAPERS]"
    )


def add_voice_message(role: str, content: str):
    """Add a message to the in-memory voice conversation."""
    _voice_history.append({"role": role, "content": content})
    # Trim to max size (keep system context)
    while len(_voice_history) > MAX_VOICE_HISTORY:
        _voice_history.pop(0)


def get_voice_history() -> list[dict]:
    """Return the current voice conversation history."""
    return list(_voice_history)


def clear_voice_history():
    """Clear voice history (e.g. on mic off)."""
    _voice_history.clear()
