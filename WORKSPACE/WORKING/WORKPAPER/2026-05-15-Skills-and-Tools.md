---
title: "Skills & Tools — Inventar, Priorisierung und Roadmap"
workpaper_id: WP-SKILLS-TOOLS
date: 2026-05-15
status: OPEN
related_whitepapers: [WH-TOOLS, WH-CORE]
file_protocol:
  read: [WH-TOOLS, WH-CORE, core/registry/tools/*, WORKSPACE/WORKING/TOOLS/skills/*]
  changed: [dieses Workpaper]
---

# WP: Skills & Tools — Inventar, Priorisierung und Roadmap

## §1 Kontext

MantisClaw braucht Werkzeuge um autonom zu arbeiten. Das Whitepaper WH-TOOLS definiert die Architektur (Registry, Security-Levels, Rucksack-Konzept, Skill-Executor). Dieses Workpaper inventarisiert den **Ist-Zustand**, definiert was **als nächstes** gebaut wird, und was **später** kommt.

**Grundprinzip:** Wir arbeiten 100% lokal. Coding-Projekte sind der primäre Use-Case.

---

## §2 Ist-Zustand (Inventar)

### 2.1 Implementierte Tools (core/registry/tools/)

| Tool | Datei | Sec-Level | Tags | Beschreibung |
|------|-------|-----------|------|-------------|
| `read_file` | filesystem.py | 1 | filesystem | Datei lesen |
| `write_file` | filesystem.py | 2 | filesystem | Datei schreiben |
| `append_file` | filesystem.py | 2 | filesystem | An Datei anhängen |
| `list_dir` | filesystem.py | 1 | filesystem | Verzeichnis auflisten |
| `workspace_status` | filesystem.py | 1 | filesystem | WORKING/ Übersicht |
| `query_memory` | memory.py | 1 | memory | LTM durchsuchen |
| `log_diary` | memory.py | 2 | memory | Diary-Eintrag schreiben |
| `analyze` | analysis.py | 1 | analysis | LLM-gestützte Analyse |
| `summarize` | analysis.py | 1 | analysis | LLM-gestützte Zusammenfassung |
| `list_models` | llm_management.py | 1 | llm | Verfügbare LLM-Modelle |
| `switch_model` | llm_management.py | 2 | llm | LLM-Modell wechseln |
| `loop_monitor` | loop_monitor.py | 1 | monitoring | Runtime-Loop Health-Check |
| `token_budget` | loop_monitor.py | 1 | monitoring | Token-Budget prüfen |

Plus Voice-Tools (tts, stt, voice_config, voice_talk, voice_greeting, classify_intent, identity_update) via Dashboard.

**Gesamt: ~20 Tools implementiert.**

### 2.2 Implementierte Skills (WORKSPACE/WORKING/TOOLS/skills/)

| Skill | Datei | Trigger | Beschreibung |
|-------|-------|---------|-------------|
| `loop_monitor` | loop_monitor.md | manual | Runtime-Loop Health-Check Workflow |
| `workspace_status` | workspace_status.md | planner | Workspace-Zustand zusammenfassen |

**Gesamt: 2 Skills.**

### 2.3 Was fehlt für autonomes Coding

Der Agent kann aktuell: Dateien lesen/schreiben, Memory abfragen, LLM nutzen, sich selbst monitoren.

Der Agent kann **NICHT**: Code ausführen, Terminal-Befehle senden, Git nutzen, Browser öffnen, Dependencies installieren, Tests laufen lassen, Fehler debuggen.

---

## §3 Priorisierung: Was brauchen wir jetzt?

### Tier 1 — Sofort (Autonomous Coding Baseline)

Diese Tools sind **essentiell** damit der Agent eigenständig an Code-Projekten arbeiten kann.

| Tool | Kategorie | Sec-Level | Beschreibung | Umsetzung |
|------|-----------|-----------|-------------|-----------|
| `shell_exec` | coding | 3 | Shell-Befehl ausführen (PowerShell/Bash), Output zurückgeben | Python `subprocess` |
| `vscode_open` | editor | 2 | Datei in VS Code öffnen (`code <file>:<line>`) | `subprocess` + `code` CLI |
| `vscode_diff` | editor | 1 | Zwei Dateien im VS Code Diff-View vergleichen | `code --diff` |
| `vscode_extensions` | editor | 1 | Installierte Extensions auflisten / Extension installieren | `code --list-extensions` / `--install-extension` |
| `git_status` | git | 1 | `git status` — Überblick über Änderungen | Wrapper um `git` CLI |
| `git_diff` | git | 1 | `git diff` — Änderungen anzeigen | Wrapper um `git` CLI |
| `git_commit` | git | 2 | `git add` + `git commit` mit Message | Wrapper um `git` CLI |
| `git_log` | git | 1 | `git log --oneline -n` — letzte Commits | Wrapper um `git` CLI |
| `run_tests` | coding | 3 | Test-Suite ausführen (pytest, npm test, etc.) | `shell_exec` Wrapper |
| `lint_check` | coding | 1 | Linter/Formatter laufen lassen (ruff, eslint, etc.) | `shell_exec` Wrapper |
| `search_codebase` | coding | 1 | Grep/Ripgrep im Projektverzeichnis | `subprocess` + `rg` |
| `pip_install` | coding | 3 | Python Dependencies installieren | `pip install` Wrapper |
| `project_init` | coding | 2 | Neues Projekt scaffolden (Verzeichnis, venv, git init) | Orchestrierung |

### Tier 2 — Bald (Productivity Boost)

Macht den Agent deutlich produktiver, aber nicht strikt notwendig zum Starten.

| Tool | Kategorie | Sec-Level | Beschreibung |
|------|-----------|-----------|-------------|
| `http_get` | network | 3 | HTTP GET Request (API, Doku, etc.) |
| `http_post` | network | 3 | HTTP POST Request |
| `open_browser` | browser | 3 | URL in Browser öffnen (Playwright/Selenium) |
| `scrape_page` | browser | 3 | Webseite scrapen → Markdown |
| `docker_exec` | devops | 3 | Docker Container starten/stoppen/exec |
| `read_pdf` | document | 1 | PDF lesen und als Text extrahieren |
| `db_query` | database | 2 | SQL-Query gegen SQLite/Postgres ausführen |
| `env_manager` | coding | 2 | Virtualenv erstellen/aktivieren/verwalten |

### Tier 3 — Später (Erweiterungen)

Nützlich, aber kein Coding-Blocker. Kommt wenn die Basis steht.

| Kategorie | Tools |
|-----------|-------|
| Media | Bildbearbeitung, OCR, Video-Schnitt, Audio-Bearbeitung |
| Security | Port-Scanner, Netzwerk-Diagnose, Encryption |
| System | System-Monitor, Screenshot, Clipboard, Backup |
| Automation | Workflow-Engine, Scheduler |
| Nostr | nostr_publish, nostr_subscribe, nostr_query |
| Science | science_research, science_validate, science_hypothesize |

---

## §4 Skills-Roadmap

Skills = Orchestrierungsrezepte die mehrere Tools kombinieren. Definiert als Markdown+YAML in `WORKSPACE/WORKING/TOOLS/skills/`.

### Tier 1 Skills (parallel zu Tier 1 Tools)

| Skill | Tools benötigt | Beschreibung |
|-------|---------------|-------------|
| `code_review` | read_file, analyze, git_diff | Änderungen reviewen, Feedback geben |
| `bug_fix` | search_codebase, read_file, analyze, write_file, run_tests | Bug finden, fixen, testen |
| `feature_implement` | read_file, write_file, run_tests, git_commit | Feature nach Spec implementieren |
| `project_setup` | project_init, pip_install, write_file, git_commit | Neues Projekt aufsetzen |
| `test_and_commit` | run_tests, lint_check, git_commit | Tests + Lint + Commit in einem Flow |

### Tier 2 Skills

| Skill | Beschreibung |
|-------|-------------|
| `research_and_validate` | Web-Recherche → SCIENCE-Validierung → Dokumentation |
| `dependency_update` | Dependencies prüfen, updaten, Tests laufen lassen |
| `deploy_check` | Lint + Tests + Docker Build → Deploy-Readiness |

---

## §5 Architektur-Entscheidungen

### 5.1 Tools: Selber schreiben vs. Wrappen

**Entscheidung:** Die meisten Coding-Tools sind **dünne Wrapper** um bestehende CLI-Tools.

```
shell_exec       → subprocess.run()
git_*            → subprocess.run(["git", ...])
run_tests        → shell_exec("pytest" / "npm test")
lint_check       → shell_exec("ruff check" / "eslint")
search_codebase  → subprocess.run(["rg", ...])
pip_install      → shell_exec("pip install ...")
```

Warum? Diese Tools existieren bereits perfekt. Wir schreiben keine eigene Git-Implementierung — wir wrappen `git`. Der Mehrwert des Tools ist: **strukturierter Output** für den LLM + **Security-Level-Kontrolle** über die Registry.

### 5.2 Globale vs. Projekt-spezifische Tools

| Ebene | Ort | Beschreibung |
|-------|-----|-------------|
| **Global** | `core/registry/tools/` | Immer verfügbar. Definiert im Whitepaper WH-TOOLS. |
| **Projekt** | `<project>/WORKSPACE/WORKING/TOOLS/` | Projektspezifisch. Überschreibt/erweitert globale Tools. |

**Auflösung:** Registry lädt zuerst globale Tools, dann Projekt-Tools. Bei Namenskollision gewinnt Projekt.

**Whitepaper-Pflicht:** Jedes globale Tool wird im Whitepaper WH-TOOLS erfasst (Name, Beschreibung, Security-Level, Tags). Das ist die zentrale Wahrheitsquelle.

### 5.3 Skill-Definition: Wo und Wie

- Skills leben in `WORKSPACE/WORKING/TOOLS/skills/` (AAMS Body)
- Format: Markdown + YAML Frontmatter (wie in WH-TOOLS §4.2 definiert)
- Jeder Skill deklariert `requires_tools` — wird gegen Registry validiert
- SkillExecutor (core/skill_executor.py) orchestriert die Ausführung

### 5.4 VS Code Integration: Continue.dev + MantisClaw Loop

**Entscheidung:** Continue.dev als Chat-UI in VS Code. Aber NICHT direkt gegen LM Studio — sondern gegen den MantisClaw Loop.

#### Architektur

```
┌─────────────────────────────────────────────────┐
│  VSCodium / VS Code                              │
│  ┌─────────────────────────────────────────────┐ │
│  │  Continue.dev Extension (Chat-Panel)        │ │
│  │  → Custom Provider: http://localhost:8080   │ │
│  └───────────────┬─────────────────────────────┘ │
│                  │                                │
│  Extensions vom Open VSX Marketplace:            │
│  Python, Git, Ruff, Docker, etc.                 │
└──────────────────┼────────────────────────────────┘
                   │ HTTP / OpenAI-kompatible API
                   ▼
┌─────────────────────────────────────────────────┐
│  MantisClaw Loop (:8080)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ Planner  │→│ Executor │→│ Observer │        │
│  └──────────┘ └────┬─────┘ └──────────┘        │
│                    │                             │
│  ┌────────────────┐│┌──────────┐┌────────────┐  │
│  │ Identity/Soul  │││ Memory   ││ Tools (L4) │  │
│  └────────────────┘│└──────────┘└────────────┘  │
│                    │                             │
│                    ▼                             │
│  ┌─────────────────────────────────────────────┐ │
│  │  LM Studio / Ollama (L0)                    │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

#### Warum so?

1. **Continue.dev spricht mit MantisClaw** — nicht direkt mit LM Studio
2. **MantisClaw IS the brain** — Loop, Memory, Observer, Identity fließen in jede Antwort ein
3. **MantisClaw-Tools als MCP-Tools** exponieren → Continue.dev kann sie direkt aufrufen
4. **Anthravity hat seine Persönlichkeit** — soul(t) beeinflusst Antworten auch im VS Code Chat

#### Was zu tun ist

1. MantisClaw braucht einen **OpenAI-kompatiblen Chat-Endpoint** auf `:8080` (`/v1/chat/completions`)
   - Nimmt User-Message → Loop (Plan → Execute → Observe) → Antwort zurück
2. Continue.dev konfigurieren: Custom Provider → `http://localhost:8080`
3. MantisClaw-Tools als **MCP Server** exponieren (optional, für Tool-Calls direkt aus Continue.dev)

#### Extensions über Marketplace

Standardmäßige Coding-Extensions aus **Open VSX Registry** (VSCodium-kompatibel):
- Python, Pylance, Ruff → Python-Entwicklung
- GitLens → Git-Visualisierung
- Docker → Container-Management
- Continue.dev → Chat-Interface für MantisClaw
- Error Lens → Fehler inline anzeigen
- Todo Tree, Markdown Preview, etc.

Diese müssen **nicht** als MantisClaw-Tools gebaut werden — sie sind VS Code Extensions die der Mensch (und der Agent via `vscode_extensions` Tool) installiert.

---

## §6 Offene Design-Frage: Dashboard vs. VS Code als Hauptoberfläche

> **Status: OFFEN — eigenes Workpaper nötig für Design-Entscheidung**

### Das Problem

Das Dashboard (`:8080`) und VSCodium/VS Code überlappen sich erheblich:

| Feature | Dashboard | VS Code / VSCodium |
|---------|-----------|-------------------|
| File Tree (WORKING/) | R3 Sidebar (selbst gebaut) | **Nativ** (Explorer, besser) |
| Datei-Editor | R2 Preview (read-only Markdown) | **Nativ** (Syntax Highlighting, Multi-Tab, Markdown Preview) |
| Terminal | ❌ nicht vorhanden | **Nativ** (integriert, mehrere Sessions) |
| Git | ❌ nicht vorhanden | **Nativ** (Source Control Panel, GitLens) |
| Chat mit Agent | Center (SSE-Streaming) | Continue.dev Extension |
| Voice-Assistent | Linke Sidebar (Custom) | ❌ nicht nativ (müsste Extension sein) |
| Runtime-Monitor | Footer-Modal (Custom) | ❌ nicht nativ (müsste Extension sein) |
| Identity Inspector | Footer-Modal (Custom) | ❌ nicht nativ (müsste Extension sein) |
| Projekt-Übersicht | R1 Sidebar (Custom) | ❌ nicht nativ (müsste Extension sein) |

### Drei mögliche Wege

**Option A: Dashboard bleibt eigenständig (Status Quo)**
- Dashboard = Mantis-Zentrale (Voice, Runtime, Identity, Projekt)
- VS Code = reiner Code-Editor mit Continue.dev für Chat
- Pro: Getrennte Concerns, Dashboard ist unabhängig von VS Code
- Con: Zwei Fenster, Dopplung beim File-Tree, keine tiefe Integration

**Option B: VS Code wird Hauptoberfläche (Full Extension)**
- Eigene MantisClaw Extension mit:
  - Sidebar: Projekt-Übersicht, Workpaper-Status, Runtime-Monitor
  - WebView-Panel: Voice-Assistent, Identity Inspector
  - Continue.dev: Chat mit MantisClaw Loop
- Dashboard wird reines Headless-Backend (API only)
- Pro: Alles an einem Ort, nutzt VS Code Stärken (Tree, Editor, Terminal, Git)
- Con: VS Code Extension Development ist aufwändig, Extension muss gepflegt werden

**Option C: Hybrid (Dashboard als Companion)**
- VS Code = Arbeitsumgebung (Code, Files, Terminal, Chat via Continue.dev)
- Dashboard = Mantis-spezifische Sachen die VS Code nicht kann:
  - Voice-Assistent (Browser hat Web Audio API)
  - Runtime-Monitor (Live-Ansicht des Loops)
  - Identity Inspector
- Dashboard wird schlanker, kein eigener File-Tree mehr
- Pro: Best of both worlds, weniger Dopplung
- Con: Immer noch zwei Fenster

### Empfehlung (vorläufig)

**Option C (Hybrid)** als pragmatischer Mittelweg:
1. VS Code mit Continue.dev für alles was VS Code besser kann (Files, Code, Git, Terminal, Chat)
2. Dashboard behält was VS Code nicht kann (Voice, Runtime, Identity)
3. Dashboard verliert R3 (File Tree) und R2 (File Preview) — die gehören in VS Code

**→ Eigenes Workpaper nötig** um die Design-Entscheidung sauber zu treffen. Betrifft: WH-DASHBOARD, WH-ASSISTANT, Extension-Architektur.

---

## §7 Nächste Schritte

1. **Tier 1 Tools implementieren** — `shell_exec` zuerst (Basis für alle anderen), dann `git_*`, dann `run_tests` / `lint_check` / `search_codebase`
2. **WH-TOOLS Whitepaper updaten** — Neue Tools in §3.3 Tool-Kategorien eintragen
3. **Erste Tier 1 Skills schreiben** — `test_and_commit` als erster vollständiger Workflow
4. **SkillExecutor fertigstellen** — Markdown+YAML Parser, Step-Execution, Error-Handling
5. **OpenAI-kompatibler Endpoint** — `/v1/chat/completions` auf Dashboard (:8080) für Continue.dev-Anbindung
6. **Continue.dev Setup** — Extension installieren, Custom Provider auf MantisClaw konfigurieren
7. **🔴 Neues Workpaper: Design-Entscheidung UI** — Dashboard vs. VS Code vs. Hybrid. Betrifft:
   - WH-DASHBOARD (Dashboard Layout, was bleibt, was geht)
   - WH-ASSISTANT (Voice-Assistent, wo lebt der?)
   - Dieses Workpaper (§5.4 VS Code Integration, §6 Design-Frage)

---

## §8 Referenzen & Notizen

### Interessante externe Quellen (noch zu evaluieren)
- Continue.dev — Open-Source AI Code Assistant: https://continue.dev / https://github.com/continuedev/continue
- VSCodium — VS Code ohne Telemetrie: https://github.com/VSCodium/vscodium
- Open VSX Registry — Marketplace für VSCodium: https://open-vsx.org
- OpenDataLoader PDF — PDF Parser for AI-ready data: https://github.com/opendataloader-project/opendataloader-pdf
- skills.sh — Reusable capabilities for AI agents: https://skills.sh/
- OpenHands — Autonome Coding Agents mit Sandbox, Browser, Terminal, Editor