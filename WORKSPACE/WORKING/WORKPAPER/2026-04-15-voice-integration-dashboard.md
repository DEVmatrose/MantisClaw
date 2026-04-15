# Workpaper — Voice Integration: Dashboard TTS + STT

**Workpaper:** WP-VOICE  
**Erstellt:** 2026-04-15  
**Status:** DONE  
**Autor:** ogerly (Mensch) + GitHub Copilot (Agent)  
**Kontext:** Mantis Voice Agent Konzept in MantisClaw Dashboard integrieren

---

## Session Goal

Voice-I/O (TTS + STT) direkt ins MantisClaw Dashboard einbauen.  
Mantis spricht und hört — alles über eine eigene L5-Box in der linken Sidebar.

---

## Phase 1 — Erledigt ✅

### Backend (dashboard/voice.py)
- TTS via edge-tts (MP3 base64)
- STT via faster-whisper (audio → text)
- Voice-Config persistent (data/voice_config.json)
- Greeting-Logic: 3 Ebenen (first_start, new_session, resume)
- Greeting-Prompt-Builder (LLM-gesteuert)

### API-Endpoints (dashboard/app.py)
- `POST /api/tts` — Text → Audio (base64 MP3)
- `POST /api/stt` — Audio-Upload → Text
- `GET /api/voice/config` — Voice-Settings lesen
- `POST /api/voice/config` — Voice-Settings setzen (name, voice, enabled)
- `GET /api/voice/greeting` — Greeting via LLM + TTS generieren

### Frontend (Phase 1 — wird in Phase 2 refactored)
- Message-Icons: 📋 Copy + 🔊 Read-aloud pro Nachricht
- Audio-Toggle + Mic-Button im Chat-Input
- Greeting bei Page-Load (Welcome-Screen)

### Getestet
- Voice Config API: ✅
- TTS "Hallo, ich bin Mantis": ✅ 21KB Audio
- Greeting (first_start + LLM + TTS): ✅ — Mantis begrüßt, fragt nach Stimme
- Dashboard startet mit allen Endpoints: ✅

---

## Phase 2 — L5 Voice Assistant (Frontend fertig)

### Architektur-Entscheidung: Trennung von Chat und Voice

**Problem:** Voice-Assistent war in die Chat-Conversations eingebettet.  
**Lösung:** Eigene L5-Box in der linken Sidebar.

**Grund:**
- Conversations gehören zu Projekten/Workpapers (Arbeitskontexte)
- Voice-Assistent ist ein separater Kommunikationskanal (direkte Interaktion)
- Trennung ermöglicht Observer: relevante Voice-Infos → Projekt-Kontext

### L5 — Voice Assistant Box

```
┌─────────────────────────┐
│ L5 · Voice Assistant 🎤 │
│ [🔴 ON / ⚫ OFF]        │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ Chat-Log (scrollbar)│ │
│ │ User: Hallo Mantis  │ │
│ │ Agent: Hallo! Ich...│ │
│ └─────────────────────┘ │
│ Status: Hört zu...      │
└─────────────────────────┘
```

### Verhalten
- **AUS (Standard):** Assistant stumm & taub. Kein Mic, kein TTS.
- **AN (manuell aktiviert):** 
  - Mic öffnet sich (getUserMedia)
  - Mantis meldet sich akustisch ("Ich höre.")
  - VAD: 2.5s Stille → Audio-Chunk an /api/stt → Text  
  - Text → /api/voice/talk → LLM-Antwort + TTS
  - Continuous Loop bis manuell AUS

### API (Phase 2)
```
POST /api/voice/talk     ← User-Text → LLM-Antwort + TTS (eigene Konversation)
GET  /api/voice/history  ← Voice-Chat-History der aktuellen Session
POST /api/voice/clear    ← Voice-History leeren
```

### Implementiert ✅
- L5 HTML-Box in linker Sidebar (nach L4)
- Voice-Toggle ON/OFF mit Status-Indicator
- VAD-Loop (Voice Agent Pattern: setInterval 100ms, VOLUME_THRESHOLD=5, SILENCE_THRESHOLD_MS=2500)
- Voice Chat-Log in L5 (scrollbar, mit Copy/Read-aloud Icons)
- Greeting nur in L5 (nicht mehr im Center-Chat)
- CSS: voice-power-btn, voice-chat-log, voice-msg, voice-indicator
- Backend: /api/voice/talk, /api/voice/history, /api/voice/clear

### Referenz: Lokaler-Voice-Agent-
Pattern aus https://github.com/DEVmatrose/Lokaler-Voice-Agent-:
- VAD mit setInterval (100ms), analyser.getByteFrequencyData
- MediaRecorder.onstop → sendAudioToServer → playAudioResponse → restart loop
- disableContinuousMode: cleanup tracks, context, interval

---

## Phase 3 — Voice-Routing + Observer Integration (Nächster Schritt)

### Gesamtarchitektur: Zwei Kommunikationskanäle

```
┌─────────────────────────────────────────────────────────────┐
│  L5 Voice Assistant (linke Sidebar)                         │
│  ─────────────────────────────────                          │
│  • Mic ON/OFF Toggle                                        │
│  • Eigener Chat-Log (Voice-Chat)                            │
│  • Identity: Greeting, Name, Stimme                         │
│  • Kurze Rückmeldungen ("Ist angelegt", "Erledigt")         │
│  • Konversation mit Mantis (allgemein)                      │
│  • KEIN Projektarbeit-Output — nur Kommunikationskanal      │
└────────────┬────────────────────────────────────────────────┘
             │
             │ ① Intent-Router (LLM-Kurzklassifikation)
             │    "Ist das ein Projekt-Befehl oder Konversation?"
             │
             ├─── KONVERSATION → Voice-Chat (L5 intern)
             │    Mantis antwortet akustisch + Text in L5
             │
             ├─── BEFEHL → Center-Chat (Projekt-Konversation)
             │    Befehl wird als User-Message in aktive
             │    Konversation injiziert → Projekt-Ausführung
             │
             │ ② Observer (Heartbeat-getriggert, ~30s)
             │    Analysiert Voice-Chat periodisch:
             │    "Wurde etwas projektrelevantes besprochen?"
             │
             └─── JA → Workpaper/Projekt-Update via L4-Tools
                  Kurzer Bericht in L5: "Habe X im Workpaper ergänzt"
```

### Intent-Router Design

**Eingabe:** STT-Text vom User  
**Ausgabe:** `{ intent: "command" | "conversation", confidence: 0.0-1.0 }`

**Ansatz:** LLM-Kurzklassifikation (1 Satz Prompt, schnell)
```
System: "Klassifiziere den folgenden Text. Ist es ein direkter Befehl/Anweisung 
an einen Agenten (command) oder allgemeine Konversation (conversation)?
Antwort nur: command oder conversation"
User: "{stt_text}"
```

**Routing-Logik:**
- `command` + aktive Konversation → Text als User-Message in Center-Chat senden
- `command` + keine Konversation → Neue Konversation starten, Text senden
- `conversation` → Voice-Chat intern (L5), Mantis antwortet akustisch

**Fallback:** Wenn confidence < 0.5 → als Konversation behandeln (sicherer Default)

### Observer auf Voice-Chat

**Trigger:** Heartbeat (alle ~30s oder konfigurierbares Intervall)

**Eingabe:** Letzte N Voice-Nachrichten seit letztem Check  
**Prompt:**
```
"Analysiere diesen Voice-Chat-Ausschnitt im Kontext des aktiven Projekts '{project_name}'
und Workpapers '{workpaper_name}'. 
Gibt es projektrelevante Informationen, Entscheidungen oder Erkenntnisse?
Antwort als JSON: { relevant: bool, summary: str, action: 'note'|'update'|'none' }"
```

**Aktionen:**
- `note` → Erkenntnis im Workpaper als Notiz ergänzen (über L4 filesystem-Tool)
- `update` → Bestehenden Workpaper-Abschnitt aktualisieren
- `none` → Nichts tun

**Rückmeldung in L5:**
- "Ich habe '{summary}' im Workpaper vermerkt."
- Als Text + TTS in Voice-Chat

### Sprachfähigkeit im Center-Chat

**Wenn Voice ON:** Auch im Center-Chat kann gesprochen werden.
- Message-Icons 📋 Copy und 🔊 Read-aloud bleiben auf allen Chat-Nachrichten
- Agent-Antworten im Center-Chat können vorgelesen werden (Read-aloud)
- Rückmeldungen bei Tool-Ausführungen kommen als TTS in L5:
  "Workpaper angelegt", "Analyse gestartet", "Fertig, schau dir das Ergebnis an"

### API (neu für Phase 3)
```
POST /api/voice/talk     ← Jetzt mit Action Classification:
                           1. Intent-Klassifikation (IDENTITY/SYSTEM/CHAT)
                           2. Bei IDENTITY: extract + apply identity updates
                           3. Bei SYSTEM: enriched system context prompt
                           4. Response + TTS + intent + action_result
POST /api/voice/route     ← (geplant) Expliziter Routing-Endpoint
POST /api/voice/observe   ← (geplant) Observer-Trigger
GET  /api/voice/observer/status ← (geplant) Letztes Observer-Ergebnis
```

### Implementiert ✅ (Phase 3 Teilschritt)
- **Action Classifier**: LLM-basiert, 3 Kategorien (IDENTITY/SYSTEM/CHAT)
- **Identity Handler**: Regex-basierte Extraktion (Name, Voice, Style) + Config-Update
- **System Handler**: Kontext-Anreicherung (Projekt, Workpapers) für System-Fragen
- **Think-Tag Bereinigung**: Reasoning-Model Output sauber
- **Intent-Badge im Frontend**: 🪪 für Identity, ⚙️ für System-Aktionen
- **[ACTION:TAG] Parsing**: System-Aktionen aus LLM-Response extrahierbar

### Schichtenmodell-Zuordnung

| Komponente      | Schicht | Begründung |
|-----------------|---------|------------|
| Voice ON/OFF    | L5      | Skill-Orchestrierung |
| TTS/STT         | L4      | Registrierte Tools |
| Intent-Router   | L5      | Skill (Orchestrierung) |
| Observer        | L3      | Bestandteil des Loops (observer.py) |
| Workpaper-Write | L4→L2   | Über registriertes filesystem-Tool |
| Greeting/Name   | L1      | Identity (base.md, voice_config) |
| Voice-Config    | L4      | Tool (Persistenz) |

---

## File Protocol

| Aktion   | Datei | Notiz |
|----------|-------|-------|
| CREATE   | `WORKPAPER/2026-04-15-voice-integration-dashboard.md` | Dieses Workpaper |
| CREATE   | `dashboard/voice.py` | TTS + STT + Greeting + Voice-History Backend ✅ |
| MODIFY   | `dashboard/app.py` | Voice-Endpoints Phase 1 ✅ + Phase 2 ✅ (/voice/talk, /voice/history, /voice/clear) |
| MODIFY   | `dashboard/templates/index.html` | Phase 1 ✅ → Phase 2 ✅ (L5 Box, VAD, Greeting-Bug-Fix) |
| MODIFY   | `dashboard/static/style.css` | Phase 1 ✅ → Phase 2 ✅ (L5 styles) |
| CREATE   | `data/voice_config.json` | Persistente Voice-Settings ✅ |
| GEPLANT  | `dashboard/voice.py` | Phase 3: Intent-Router + Observer-Funktionen |
| GEPLANT  | `dashboard/app.py` | Phase 3: /voice/route, /voice/observe Endpoints |
| GEPLANT  | `core/observer.py` | Phase 3: Voice-Chat als Input-Kanal für Observer |
| MODIFY   | `dashboard/voice.py` | Phase 3: Intent-Classifier, Identity-Handler, System-Context ✅ |
| MODIFY   | `dashboard/app.py` | Phase 3: /api/voice/talk 2-stage pipeline ✅ |
| MODIFY   | `dashboard/templates/index.html` | VAD-Bugfix (warmup, loudCount) ✅ |
| MODIFY   | `WORKSPACE/WORKING/WHITEPAPER/CORE.md` | L5 Voice-Sektion, Layer-Model-Update ✅ |
| MODIFY   | `WORKSPACE/WORKING/WHITEPAPER/TOOLS.md` | voice + voice_action Tool-Kategorien ✅ |
| MODIFY   | `WORKSPACE/WORKING/WHITEPAPER/IDENTITY.md` | §9 Assistenten-Identität ✅ |
| MODIFY   | `README.md` | dashboard/ Baum, L5 Voice, Layer-Model, Voice-Sektion, v0.4.0 ✅ |

---

## Session Summary (2026-04-15)

### Accomplished

1. **Voice Backend** — TTS (edge-tts), STT (faster-whisper), greeting logic, voice config persistence
2. **L5 Frontend** — Separate sidebar box with VAD loop, voice chat log, power button
3. **Action Classification** — 2-stage LLM pipeline: IDENTITY / SYSTEM / CHAT intent routing
4. **Identity Handler** — Regex-based name/voice/speed extraction, persists to voice_config.json
5. **System Context** — Enriched prompts with project state, workpapers, whitepapers
6. **VAD Bugfix** — 800ms warmup, 3 consecutive loud frames, proper loudCount scoping
7. **Greeting Bugfix** — Removed center-chat greeting, L5-only on toggle-on
8. **Whitepaper Updates** — CORE v0.4.0 (L5 Voice), TOOLS v0.4.0, IDENTITY §9
9. **README Update** — dashboard/ tree, Layer Model fix (L5=Skills+Voice), Voice section, v0.4.0

### Open / Next Steps

- Observer integration: Voice-chat as input channel for observer.py
- System-action execution: CREATE_WORKPAPER, SWITCH_MODEL from voice
- Voice routing to center chat for project-related conversations
- Browser end-to-end testing
