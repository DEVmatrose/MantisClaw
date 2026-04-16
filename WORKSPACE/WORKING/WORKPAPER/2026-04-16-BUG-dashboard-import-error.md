# BUG — Dashboard Import Error: faster_whisper

**Date:** 2026-04-16  
**Type:** Bug Analysis  
**Status:** RESOLVED  
**Severity:** BLOCKING — Dashboard konnte nicht starten  
**Related WP:** `2026-04-15-voice-integration-dashboard.md` (Voice Phase 1–3)

---

## File Protocol

| # | File | Action | Notiz |
|---|------|--------|-------|
| 1 | `dashboard/voice.py` | READ | Root Cause identifiziert (Zeile 14–15: edge_tts + faster_whisper) |
| 2 | `dashboard/app.py` | READ | Import-Chain bestätigt (Zeile 15–21) |
| 3 | `core/voice.py` | READ | Nur edge_tts — daher Runtime unberührt |
| 4 | `requirements.txt` | READ → MODIFY | Fehlende Voice-Deps ergänzt |
| 5 | `.venv/` | INSTALL | `faster-whisper` + Deps ins venv installiert |

---

## Kontext

Am **2026-04-15** wurde die Voice-Integration (TTS + STT) ins Dashboard eingebaut:
- `dashboard/voice.py` — TTS via `edge-tts`, STT via `faster-whisper`
- `dashboard/app.py` — 7 Voice-Endpoints  
- Phase 1–3 abgeschlossen, getestet, Workpaper auf DONE gesetzt

**Alles funktionierte gestern**, weil:
- Die Session am 15.04. lief mit dem **globalen Python** (pyenv 3.10.11)
- `faster-whisper` (1.2.1) und `edge-tts` (7.2.8) waren dort bereits installiert  
  (Location: `c:\users\devma\.pyenv\pyenv-win\versions\3.10.11\lib\site-packages`)
- Die Packages wurden aber **nie in `requirements.txt` aufgenommen**

**Heute crasht das Dashboard**, weil:
- Das Terminal mit aktiviertem `.venv` gestartet wurde
- `pip install -r requirements.txt` installierte nur die gelisteten Packages
- `faster-whisper` war nicht gelistet → nicht im venv → Import-Fehler

---

## Problem

```
uvicorn dashboard.app:app --reload --port 8080
→ ModuleNotFoundError: No module named 'faster_whisper'
```

**Import-Chain:**
1. `uvicorn` → `dashboard.app` (Modul-Import)
2. `dashboard/app.py:15` → `from dashboard.voice import (...)`
3. `dashboard/voice.py:15` → `from faster_whisper import WhisperModel` → **CRASH**

**Warum Runtime davon nicht betroffen:**
- `core/voice.py` nutzt **nur** `edge_tts` (TTS-only, kein STT)
- `core/runtime.py:35` → `from core.voice import VoiceOutput` — OK
- `core/` importiert niemals `dashboard/` — komplett getrennt

---

## Root Cause

| Package | Verwendet in | In requirements.txt? | Im globalen Python? | Im .venv? |
|---------|-------------|---------------------|---------------------|-----------|
| `edge-tts` | `core/voice.py` + `dashboard/voice.py` | **NEIN** (war Zufall im venv) | ✅ 7.2.8 | ✅ 7.2.8 |
| `faster-whisper` | `dashboard/voice.py` | **NEIN** | ✅ 1.2.1 | ❌ FEHLTE |

**Ursache:** In der Voice-Integration-Session (WP-VOICE, 15.04.) wurden die Dependencies implementiert und getestet, aber der File-Protocol-Eintrag für `requirements.txt` fehlt — die Datei wurde nicht aktualisiert.

---

## Fix (umgesetzt)

### 1. requirements.txt aktualisiert

```diff
+ # Voice (TTS + STT)
+ edge-tts>=6.1
+ faster-whisper>=1.0
+
  # LLM Backends — Local-first, zero dependencies:
```

### 2. faster-whisper ins .venv installiert

```bash
.venv\Scripts\pip.exe install faster-whisper edge-tts
→ Successfully installed faster-whisper-1.2.1 + 15 Abhängigkeiten
   (ctranslate2, onnxruntime, numpy, huggingface-hub, av, tokenizers, ...)
```

---

## Lektion / Guideline-Kandidat

> **Dependency-Check bei Feature-Abschluss:** Wenn ein neues Feature externe Packages einführt, 
> MUSS `requirements.txt` im File-Protocol stehen und vor WP-Close aktualisiert werden.
> Testen im globalen Python ≠ Testen im venv — beides prüfen.

---

## Decisions

- [x] Fix-Option: **A + B** — Dependencies in requirements.txt + direkt installiert
- [x] `requirements.txt` aktualisiert (edge-tts, faster-whisper)  
- [x] `faster-whisper` im `.venv` installiert
- [ ] Dashboard-Start verifizieren (nächster Schritt)
- [ ] Optional: Lazy-Import in voice.py als Hardening (Dashboard soll auch ohne Voice starten können)

---

## Next Steps

1. Dashboard testen: `uvicorn dashboard.app:app --reload --port 8080`
2. Optional: Lazy-Import für graceful degradation einbauen
3. Workpaper schließen nach erfolgreicher Verifizierung
