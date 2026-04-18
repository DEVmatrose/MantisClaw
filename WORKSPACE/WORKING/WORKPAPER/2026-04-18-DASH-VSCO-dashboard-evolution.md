---
title: "Dashboard Evolution — Was bleibt, was geht, Umbau-Plan"
workpaper_id: WP-DASH-VSCO-002
date: 2026-04-18
status: OPEN
topic: DASH
subtopic: VSCO
related_whitepapers: [DASHBOARD.md]
related_workpapers: [2026-04-18-DASH-VSCO-ui-design-decision.md, 2026-04-16-dashboard-ui-refactor.md (CLOSED, v1-Basis)]
file_protocol:
  read: [WORKSPACE/WORKING/WHITEPAPER/DASHBOARD.md, dashboard/app.py, dashboard/templates/index.html, dashboard/static/style.css]
  changed: [dieses Workpaper]
  to_update_after: [WORKSPACE/WORKING/WHITEPAPER/DASHBOARD.md → v2.0]
---

# WP: Dashboard Evolution — Was bleibt, was geht, Umbau-Plan

## §1 Ausgangslage

Entscheidung aus WP-DASH-VSCO-001: **Option C — Hybrid**. Dashboard wird Companion für Voice, Runtime, Identity. VS Code übernimmt File-Tree, Editor, Terminal, Git, Chat.

Dieses Workpaper plant den konkreten Dashboard-Umbau.

> **Baut auf:** WP `2026-04-16-dashboard-ui-refactor.md` (CLOSED, M1–M5 ✅) — definiert das aktuelle Layout (3-spaltig, R1–R4, Footer-Modals, Voice links). Die hier geplanten Änderungen sind die v2-Evolution: R2+R3 werden entfernt zugunsten von VSCodium, Runtime-Monitor wird prominenter.

---

## §2 Bestandsaufnahme: Was existiert heute

### Grid-Struktur (aktuell)

```
Navbar (44px)
├── Links (240px)   — Voice-Assistent
├── Center (1fr)    — Chat / SSE
└── Rechts (260px)  — R1 Projekt | R2 Workpaper | R3 WORKING-Baum | R4 Chat-History
Footer (36px)       — Backend | Model | Identity | Runtime | Tools | Events | Prompts
```

### Routen in dashboard/app.py (aktuell)

| Route | Methode | Funktion |
|-------|---------|---------|
| `/` | GET | index.html |
| `/voice` | GET | voice.html (Voice-only Ansicht) |
| `/chat/stream` | GET | SSE Chat-Streaming |
| `/api/conversations` | GET/POST | Chat-History |
| `/api/conversations/{id}` | DELETE | Konversation löschen |
| `/api/models/lmstudio` | GET | LM Studio Modelle |
| `/api/models/ollama` | GET | Ollama Modelle |
| `/api/models/lmstudio/loaded` | GET | Geladene Modelle |
| `/api/models/lmstudio/load` | POST | Modell laden |
| `/api/models/lmstudio/unload` | POST | Modell entladen |
| `/api/voice/tts` | POST | Text → Speech |
| `/api/voice/stt` | POST | Audio → Text |
| `/api/voice/config` | GET/POST | Voice-Konfiguration |
| `/api/voice/greeting` | GET | Begrüßungs-Context |
| `/api/voice/talk` | POST | Voice-Chat Endpoint |
| `/api/voice/classify` | POST | Intent Classifier |
| `/api/identity/update` | POST | Identity updaten |

**Neu hinzuzufügen:**
| Route | Methode | Funktion |
|-------|---------|---------|
| `/v1/chat/completions` | POST | OpenAI-kompatibler Endpoint für Continue.dev |
| `/api/runtime/status` | GET | Loop-Status (Health, letzter Tick, Plan) |

---

## §3 Was GEHT (wird entfernt)

### R3 — WORKING-Baum (File-Tree)

**Begründung:** VS Code Explorer macht das besser. Nativ, interaktiv, Multi-Root.

**Was zu entfernen ist:**
- HTML: `<div class="box" id="box-r3">` mit File-Tree Rendering
- JS: `loadWorkspaceStatus()` Polling-Funktion (alle 5s `workspace_status` Tool)
- CSS: `.workspace-tree`, `.tree-*` Selektoren

**Backend bleibt:** `workspace_status` Tool in der Registry bleibt (wird vom Loop genutzt). Nur der UI-Teil fällt weg.

### R2 — Aktives Workpaper Preview

**Begründung:** VS Code Markdown Preview ist besser (Syntax Highlighting, Links, interaktiv). Dashboard-Preview war read-only.

**Was zu entfernen ist:**
- HTML: `<div class="box" id="box-r2">` mit Workpaper-Content
- JS: `loadActiveWorkpaper()` Polling-Funktion (`read_file` auf aktives WP)
- CSS: `.workpaper-content` Stile

### Dashboard Chat-Center (teilweise)

**Status: OFFEN** — Continue.dev übernimmt den primären Text-Chat. Dashboard-Chat bleibt vorerst als Fallback (Voice-Interaktion läuft darüber).

**Entscheidung für später:** Chat-Center wird zu "Voice-Transcript" — zeigt was der Voice-Assistent gesagt/gehört hat. Kein freier Text-Chat mehr im Dashboard (der gehört in Continue.dev).

---

## §4 Was BLEIBT (und verbessert wird)

### Voice-Assistent (Links, 240px) — BLEIBT, wird Kernstück

Voice ist der wichtigste Differenziator zum VS Code Setup. Bleibt vollständig.

**Verbesserungen:**
- VAD-Indikator prominenter (aktuell: kleines Mic-Icon)
- Transcript-Anzeige: letzte 3 Turns sichtbar
- Status-Bar: STT-Verarbeitung / TTS-Wiedergabe visuell anzeigen

### Runtime-Monitor — WIRD PROMINENTER

Aktuell: nur als Footer-Modal (`⚙️ Runtime` Button). Das ist zu versteckt.

**Plan:** Runtime-Monitor zieht in die rechte Sidebar als permanente Box.

```
Rechte Sidebar (neu):
├── R1: Runtime-Monitor (Live: Health, aktueller Tick, letzter Plan)
├── R2: Projekt-Übersicht (aktives Workpaper, offene Punkte)
└── R3: Token-Budget (Input/Output Counter, Warnschwelle)
```

### Identity Inspector (Footer-Modal) — BLEIBT

soul(t) live anzeigen ist wertvoll. Bleibt als Modal, wird vielleicht auch als kleine Sidebar-Box.

### Model-Switcher (Navbar/Footer) — BLEIBT

LM Studio / Ollama Modelle wechseln ist wichtig. Bleibt in Navbar.

### Event-Feed (Footer-Modal) — BLEIBT

Was tut der Agent gerade? Wertvoll für Debugging und Transparenz.

---

## §5 Neues Grid-Layout

### Vorher

```
grid-template-columns: 240px 1fr 260px
```

### Nachher (Option C)

```
grid-template-columns: 240px 1fr 260px

Links:    Voice-Assistent (bleibt 240px)
Center:   Voice-Transcript / Chat-Fallback (bleibt 1fr)
Rechts:   R1 Runtime-Monitor | R2 Projekt-Übersicht | R3 Token-Budget
```

Das Grid bleibt **3-spaltig** — aber die rechte Sidebar bekommt neue Inhalte: Runtime statt File-Tree.

---

## §6 Neuer Endpoint: `/v1/chat/completions`

Dies ist der Kern-Blocker für Continue.dev. 

### Implementierungsplan

```python
# dashboard/app.py

@app.post("/v1/chat/completions")
async def openai_chat_completions(request: Request):
    """
    OpenAI-kompatibler Endpoint für Continue.dev und andere Clients.
    Führt einen Mini-Loop (Plan → Execute → Observe) durch.
    """
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    model = body.get("model", "mantis")
    
    # 1. soul(t) bauen
    soul = identity.compute_soul(working_context="chat-mode")
    system_prompt = build_system_prompt(soul)
    
    # 2. Vollständige Message-History mit System-Prompt
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    # 3. LLM Call (direkt, kein Planner-Overhead für einfache Chats)
    if stream:
        return StreamingResponse(
            stream_openai_format(full_messages),
            media_type="text/event-stream"
        )
    else:
        response = await asyncio.to_thread(llm.complete, full_messages)
        return {
            "id": f"mantis-{datetime.now().timestamp()}",
            "object": "chat.completion",
            "model": model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response},
                "finish_reason": "stop"
            }]
        }
```

### Phase 2 (mit Tool-Calls)

Wenn Tier-1 Tools implementiert sind:
- Planner analysiert User-Message auf Tool-Bedarf
- Executor ruft Tools auf (shell_exec, git_status, etc.)
- Observer fasst zusammen
- Response enthält Tool-Ergebnisse

---

## §7 Dashboard-Umbau Phasen

### Phase 1 — Endpoint (Blocker)
- [ ] `/v1/chat/completions` implementieren (einfache Version, kein Tool-Calling)
- [ ] Continue.dev testen: Antworten kommen mit soul(t)-Kontext?

### Phase 2 — Layout-Cleanup
- [ ] R2 (Workpaper-Preview) entfernen
- [ ] R3 (File-Tree) entfernen
- [ ] Rechte Sidebar: Runtime-Monitor Box einbauen
- [ ] Rechte Sidebar: Token-Budget Box einbauen

### Phase 3 — Voice-Verbesserung
- [ ] Transcript-Anzeige (letzte 3 Turns)
- [ ] STT/TTS Status-Bar verbessern
- [ ] VAD-Indikator prominenter

### Phase 4 — WH-DASHBOARD v2.0
- [ ] Whitepaper aktualisieren auf neues Layout
- [ ] `/v1/chat/completions` Endpoint dokumentieren
- [ ] Option-C Entscheidung in Whitepaper festhalten

---

## §8 Theoretischer Test-Durchlauf: Dashboard nach Umbau

```
Szenario: Developer öffnet Dashboard nach Phase 2

LINKS:   Voice-Assistent
         Mic-Button, VAD aktiv
         Transcript: [leer — wartet auf Sprache]

CENTER:  Voice-Transcript / Fallback-Chat
         "Mantis bereit. LM Studio verbunden."

RECHTS:  Runtime-Monitor
         Health: IDLE
         Letzter Tick: vor 12s
         Letzter Plan: "workspace_status + log_diary"
         
         Projekt-Übersicht
         Aktives WP: 2026-04-18-DASH-VSCO-...
         Offene WPs: 3
         
         Token-Budget
         Session: 2.4k / 16k
         Letzte Anfrage: 847 tokens

NAVBAR:  🦗 MantisClaw | [MantisClaw ▼] | ● qwen3-coder-30b

FOOTER:  🟢 lmstudio | qwen3-coder | 🧬 Identity | ⚙️ Events | 📋 Prompts
         (Runtime und Tools sind jetzt Sidebar-Boxen, nicht mehr Footer-Modals)
```

**Ergebnis:** Dashboard ist kompakter, fokussierter. Alles relevante sofort sichtbar.

---

## §9 File Protocol

| Aktion | Datei |
|--------|-------|
| READ | WORKSPACE/WORKING/WHITEPAPER/DASHBOARD.md |
| READ | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-ui-design-decision.md |
| CREATED | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-dashboard-evolution.md |
| TO UPDATE | WORKSPACE/WORKING/WHITEPAPER/DASHBOARD.md → v2.0 (nach Phase 4) |
