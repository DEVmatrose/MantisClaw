---
title: "VSCodium + Continue.dev — Integration & Setup"
workpaper_id: WP-DASH-VSCO-003
date: 2026-04-18
status: OPEN
topic: DASH
subtopic: VSCO
related_whitepapers: [ASSISTANT.md, TOOLS.md]
related_workpapers: [2026-04-18-DASH-VSCO-ui-design-decision.md, 2026-04-18-DASH-VSCO-dashboard-evolution.md]
file_protocol:
  read: [WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md, WORKSPACE/WORKING/WHITEPAPER/TOOLS.md]
  changed: [dieses Workpaper]
  to_update_after: [WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md → v2.0]
---

# WP: VSCodium + Continue.dev — Integration & Setup

## §1 Ziel

VSCodium als primäre Entwicklungsumgebung etablieren. Continue.dev als Chat-Interface mit MantisClaw koppeln. Der Developer arbeitet in VSCodium — MantisClaw ist sein Pair-Programmer.

---

## §2 VSCodium vs. VS Code — Die Wahl

### Warum VSCodium?

| Kriterium | VS Code | VSCodium |
|-----------|---------|---------|
| Telemetrie | ❌ ja (Microsoft) | ✅ nein (deaktiviert) |
| Lizenz | Microsoft (proprietär) | MIT |
| Marketplace | Visual Studio Marketplace | Open VSX Registry |
| Extensions | Alle VS Code Extensions | Fast alle (Open VSX) |
| Continue.dev | ✅ verfügbar | ✅ verfügbar (Open VSX) |
| Kompatibilität | VS Code | VS Code-kompatibel |

**Entscheidung: VSCodium** — passt zu MantisClaw-Ethik (base.md: Souveränität, eigene Daten, kein Tracking).

### Einschränkungen VSCodium

- **Copilot** nicht verfügbar (Microsoft-exklusiv) — aber das wollen wir nicht, wir haben MantisClaw
- **Remote Development** Extensions (SSH, Container) aus Microsoft-Marketplace nicht verfügbar → Workaround: Open VSX Alternativen oder direkt VS Code für Remote
- **Settings Sync** anders (kein Microsoft-Account nötig) → lokale Profiles reichen

---

## §3 VSCodium Setup (Schritt für Schritt)

### 3.1 Installation

```powershell
# Windows: winget
winget install VSCodium.VSCodium

# Oder: https://vscodium.com/#install
# Portable-Version verfügbar (kein Admin nötig)
```

### 3.2 Empfohlene Extensions (Open VSX)

```powershell
# Alle via codium --install-extension

# Python
codium --install-extension ms-python.python
codium --install-extension ms-python.vscode-pylance

# Linting
codium --install-extension charliermarsh.ruff

# Git
codium --install-extension eamodio.gitlens

# Continue.dev (Hauptsache)
codium --install-extension continue.continue

# Convenience
codium --install-extension usernamehw.errorlens
codium --install-extension Gruntfuggly.todo-tree
codium --install-extension bierner.markdown-preview-github-styles

# Optional
codium --install-extension ms-azuretools.vscode-docker
```

### 3.3 Settings (Empfohlen)

```json
// .vscode/settings.json (projekt-lokal)
{
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true
    }
}
```

---

## §4 Continue.dev Setup

### 4.1 Was ist Continue.dev?

Open-Source AI Code Assistant Extension für VS Code / VSCodium. Unterstützt:
- Chat im Editor (Sidebar)
- Inline Suggestions
- `/edit` Slash-Commands
- Custom Providers (OpenAI-kompatibel)
- MCP Tool-Integration (optional)

**GitHub:** https://github.com/continuedev/continue  
**Lizenz:** Apache 2.0

### 4.2 Continue.dev mit MantisClaw koppeln

MantisClaw-Endpoint muss `/v1/chat/completions` unterstützen (aus WP-DASH-VSCO-002 §6).

**Config-Datei:** `~/.continue/config.json` (Windows: `C:\Users\<user>\.continue\config.json`)

```json
{
  "models": [
    {
      "title": "Mantis (MantisClaw)",
      "provider": "openai",
      "model": "mantis",
      "apiBase": "http://localhost:8080",
      "apiKey": "local",
      "systemMessage": ""
    }
  ],
  "tabAutocompleteModel": {
    "title": "Mantis Autocomplete",
    "provider": "openai",
    "model": "mantis",
    "apiBase": "http://localhost:8080",
    "apiKey": "local"
  },
  "contextProviders": [
    {
      "name": "code",
      "params": {}
    },
    {
      "name": "docs",
      "params": {}
    },
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "terminal",
      "params": {}
    }
  ],
  "slashCommands": [
    {
      "name": "edit",
      "description": "Edit selected code"
    },
    {
      "name": "comment",
      "description": "Write comments for code"
    },
    {
      "name": "share",
      "description": "Export conversation"
    }
  ]
}
```

### 4.3 Context Provider — was das bedeutet

Continue.dev schickt mit jeder Anfrage **Kontext** mit. Aktivierte Provider:

| Provider | Was wird gesendet |
|----------|------------------|
| `code` | Selektierter Code im Editor |
| `diff` | `git diff` der aktuellen Änderungen |
| `terminal` | Letzte Terminal-Ausgabe |
| `docs` | Inhalte aus verlinkten Docs |

MantisClaw bekommt damit: User-Message + Code-Selektion + Git-Diff + Terminal-Output. Das ist echter Pair-Programming-Kontext.

### 4.4 Tab-Autocomplete (Optional)

Continue.dev kann Code-Vorschläge inline anbieten (wie GitHub Copilot). Braucht ein schnelles Modell — `qwen3-coder-30b` ist zu groß dafür. 

**Empfehlung:** Für Tab-Autocomplete kleineres Modell in LM Studio laden, z.B. `qwen2.5-coder-1.5b-instruct`. Separates Modell-Slot in config.

---

## §5 MantisClaw als "Pair Programmer" — wie das funktioniert

### 5.1 Normaler Coding-Flow

```
1. Developer öffnet MantisClaw-Repo in VSCodium
2. Continue.dev Sidebar öffnen (Ctrl+Shift+L)
3. Dashboard im zweiten Fenster / zweitem Monitor (Companion)

Interaktion:
─────────────────────────────────────────────────────────
[Developer, Continue.dev] → "Was ist der Unterschied zwischen 
                             Planner und Executor in core/?"

[MantisClaw Response] ←── soul(t) Kontext + Code-Files
  "Planner erstellt einen Plan als JSON mit action + args.
   Executor führt ihn aus indem er das passende Tool aus der
   Registry aufruft..."

[Developer, Continue.dev] → /edit [wählt Funktion aus] 
                             "Füge Logging hinzu"

[MantisClaw] → Generiert Edit direkt in der Datei
─────────────────────────────────────────────────────────
```

### 5.2 Workpaper-Awareness

Der MantisClaw `/v1/chat/completions` Endpoint lädt beim Aufbau des System-Prompts:
1. `identity/base.md` → Wer ist Mantis?
2. `identity/agenda.md` → Was ist das aktuelle Ziel?
3. Aktives Workpaper (via `workspace_status`) → Was ist die aktuelle Aufgabe?

Damit weiß Mantis immer: **"Wir arbeiten gerade an der UI-Design-Entscheidung. Kontext: Option C ist gewählt."**

### 5.3 Workflow: Feature implementieren

```
Continue.dev Chat:

Developer: "Implementiere den /v1/chat/completions Endpoint 
            wie in WP-DASH-VSCO-002 §6 beschrieben"

MantisClaw:
  1. soul(t) laden → Kontext: Dashboard-Evolution WP aktiv
  2. read_file(WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md)
  3. read_file(dashboard/app.py)
  4. Analyse: was fehlt, wie integrieren
  5. write_file(dashboard/app.py) → Endpoint hinzufügen
  6. Response: "Endpoint implementiert. Bitte testen mit:
                curl -X POST http://localhost:8080/v1/chat/completions ..."

Developer: sieht Änderung in VS Code, testet in Terminal
```

---

## §6 Loop-Modus vs. Chat-Modus

Dies ist das wichtigste Architektur-Problem (aus WP-DASH-VSCO-001 §5).

### Zwei Betriebsmodi

```
┌─────────────────────────────────────────────────────┐
│  MantisClaw Betriebsmodi                             │
│                                                      │
│  LOOP-MODUS (autonom)                                │
│  ─────────────────────────────────────────────────── │
│  Trigger: Heartbeat (alle 60s)                       │
│  Verhalten: Plan → Execute → Observe → Idle          │
│  Ziel: Autonomes Arbeiten an Workpaper-Aufgaben      │
│  LLM-Nutzung: Planner (LLM), Executor (Tools), ...  │
│                                                      │
│  CHAT-MODUS (reaktiv)                                │
│  ─────────────────────────────────────────────────── │
│  Trigger: HTTP Request (Continue.dev, Dashboard)     │
│  Verhalten: Request → soul(t) → LLM → Response       │
│  Ziel: Pair-Programming, Fragen beantworten          │
│  LLM-Nutzung: Direct Call, kein Planner-Overhead     │
└─────────────────────────────────────────────────────┘
```

### LLM-Lock Problem

Beide Modi nutzen dieselbe LM Studio Instanz. Wenn Loop-Modus gerade plant (LLM-Call) und Continue.dev gleichzeitig einen Request sendet → **Wettbewerb**.

**Lösung: Async Queue**

```python
# core/llm.py — Erweiterung
import asyncio

class LLMBackend:
    def __init__(self, ...):
        ...
        self._lock = asyncio.Lock()  # NEU
    
    async def complete_async(self, messages, ...):
        async with self._lock:  # Serialisiert alle LLM-Calls
            return await asyncio.to_thread(self.complete, messages, ...)
```

**Konsequenz:** Chat-Requests warten wenn Loop-Modus gerade läuft. Maximale Wartezeit = Dauer eines LLM-Calls (typisch 2-10s bei qwen3-30B). Akzeptabel.

**Alternative:** Chat-Modus pausiert Heartbeat-Timer. Während ein Chat aktiv ist, kein autonomer Tick.

---

## §7 WH-ASSISTANT v2.0 — Was sich ändert

Aktuelles ASSISTANT.md v1.0 dokumentiert:
- Voice als einzigen Interaktionskanal
- Dashboard als einzige Oberfläche

Nach Integration von Continue.dev:

| Aspekt | v1.0 | v2.0 |
|--------|------|------|
| Primärer Text-Chat | Dashboard Center | Continue.dev in VSCodium |
| Voice-Chat | Dashboard Links | Dashboard Links (bleibt) |
| Betriebsmodi | Loop-Modus (nur) | Loop-Modus + Chat-Modus |
| System-Prompt | soul(t) | soul(t) + aktives Workpaper |
| Tool-Calling | Planner-orchestriert | Phase 1: kein Tool-Calling, Phase 2: MCP |

**WH-ASSISTANT v2.0 muss:**
1. Zwei Betriebsmodi definieren (Loop vs. Chat)
2. Continue.dev als primären Text-Chat-Kanal dokumentieren
3. `/v1/chat/completions` als Standard-Interface festhalten
4. LLM-Lock Lösung dokumentieren

---

## §8 Zeitplan / Umsetzungsreihenfolge

### Schritt 1 (Sofort umsetzbar)
- [ ] VSCodium installieren
- [ ] Empfohlene Extensions installieren
- [ ] `.vscode/settings.json` anlegen

### Schritt 2 (Endpoint — Blocker)
- [ ] `/v1/chat/completions` in `dashboard/app.py` implementieren (einfache Version)
- [ ] Testen: `curl` oder Postman → Response kommt?
- [ ] `asyncio.Lock()` in `llm.py` einbauen

### Schritt 3 (Continue.dev koppeln)
- [ ] `~/.continue/config.json` anlegen
- [ ] Continue.dev in VSCodium öffnen
- [ ] Test: "Erkläre mir die runtime.py" → Antwort mit soul(t)-Kontext?

### Schritt 4 (Validierung)
- [ ] Continue.dev SSE-Streaming testen
- [ ] Loop-Modus läuft parallel — kein Deadlock?
- [ ] Dashboard Voice parallel zu Continue.dev Chat — funktioniert?

### Schritt 5 (WH-ASSISTANT v2.0)
- [ ] Whitepaper updaten nach erfolgreicher Integration

---

## §9 Theoretischer End-to-End Test

```
Setup:
  - VSCodium offen, MantisClaw-Repo
  - Dashboard offen (Companion, zweiter Monitor)
  - uvicorn dashboard.app:app --port 8080 --reload
  - LM Studio: qwen3-coder-30b geladen
  - Continue.dev: Mantis als aktiver Provider

Test-Sequenz:

[1] Dashboard: Voice-Greeting
    Developer sagt nichts, Mantis begrüßt automatisch beim Start:
    "Guten Morgen! Wir haben 3 offene Workpapers. Soll ich beginnen?"
    → ✅ erwartet: TTS spielt ab, Dashboard zeigt Transcript

[2] Continue.dev: Code-Frage
    Developer: "@code was macht executor.py?"
    Continue.dev sendet: messages + code-context (executor.py Inhalt)
    MantisClaw: soul(t) + executor.py → Antwort
    → ✅ erwartet: Antwort im Continue.dev Chat-Panel

[3] Dashboard: Runtime-Monitor
    Developer schaut auf Runtime-Box (rechte Sidebar nach Umbau):
    Health: IDLE | Letzter Tick: vor 23s | Plan: workspace_status
    → ✅ erwartet: Live-Status sichtbar ohne Modal öffnen

[4] Gleichzeitig: Loop-Tick + Continue.dev Request
    Loop-Modus: Tick 5 beginnt (Planner macht LLM-Call)
    Continue.dev: Developer schickt Frage gleichzeitig
    asyncio.Lock → Continue.dev wartet ~3s
    → ✅ erwartet: beide Anfragen werden serialisiert, kein Fehler

[5] Voice: System-Query
    Developer: "Mantis, was ist der aktuelle Tick-Status?"
    Intent: SYSTEM → loop_monitor Tool → Antwort
    → ✅ erwartet: Voice-Antwort, Dashboard aktualisiert

Alle 5 Tests: GRÜN (wenn Endpoint implementiert und LM Studio aktiv)
```

---

## §10 File Protocol

| Aktion | Datei |
|--------|-------|
| READ | WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md |
| READ | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-ui-design-decision.md |
| READ | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-dashboard-evolution.md |
| CREATED | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-vscodium-integration.md |
| TO UPDATE | WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md → v2.0 (nach Schritt 5) |
