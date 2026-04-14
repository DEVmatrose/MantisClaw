# MantisClaw — Autonomous Agent Loop Framework

<p align="center">
  <img src="docs/mantisclaw-overview.png" alt="MantisClaw Overview" width="700">
</p>

**Version:** 0.1.0  
**Status:** IN ENTWICKLUNG  
**GitHub:** [DEVmatrose/MantisClaw](https://github.com/DEVmatrose/MantisClaw)  
**Autor:** [@ogerly](https://github.com/ogerly) · [DEVmatrose](https://github.com/DEVmatrose)  
**Teil der:** [Mantis-Familie](https://github.com/DEVmatrose)  
**Lizenz:** MIT

## Was ist MantisClaw?

MantisClaw ist ein **eigenständiges** Agent-Loop-Framework mit **emergenter Identität**.

### Die Kernidee: Emergente Soul

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

Die Soul wird **nie geschrieben** — sie wird bei jedem Tick **berechnet**. Ein Agent der codet ist ein anderer als einer der tradet, aber beide teilen dieselbe `identity/base.md`.

---

## Architektur

```
MantisClaw/
│
├── .agent.json                   ← AAMS Bootstrap
├── AGENTS.md                     ← Tool-Bridge
├── READ-AGENT.md                 ← Agent-Vertrag
│
├── core/                         ← Das Gehirn (L3) — reiner Loop
│   ├── runtime.py                ← Heartbeat-Loop (60s, Idle Detection)
│   ├── planner.py                ← Denken (Tool-Injection + JSONL Prompt Logging)
│   ├── executor.py               ← Handeln (Fuzzy Action Matching)
│   ├── observer.py               ← Beobachten + Health-Tracking
│   ├── reflect.py                ← Reflexion (RFL) — Selbstkorrektur
│   ├── context.py                ← JIT Context Loading (3-Stage)
│   ├── skill_executor.py         ← Skill-Orchestrierung (L5)
│   ├── llm.py                    ← LLM-Backend (L0)
│   ├── session.py                ← AAMS Session-Management
│   ├── workpaper.py              ← Workpaper-Verwaltung
│   ├── ltm.py                    ← Langzeitgedächtnis
│   └── registry/                 ← Tool-Registry (L4)
│       ├── __init__.py           ← ToolRegistry + Tool Klassen
│       ├── registry.py           ← Whitelist, Security-Levels, Fuzzy-Resolve
│       └── tools/                ← Tool-Implementierungen
│           ├── filesystem.py     ← read_file, write_file, list_dir, workspace_status
│           ├── memory.py         ← query_memory, log_diary
│           └── analysis.py       ← analyze, summarize (LLM-powered)
│
├── identity/                     ← Emergente Identität (L1)
│   ├── base.md.example           ← Konstanten: Name, Ethik, Keys
│   ├── agenda.md.example         ← Wurzelknoten: aktive Agenda
│   ├── account.md.example        ← Plattform-Zugänge
│   ├── social.md.example         ← CRM-State: Kontakte
│   ├── decentral.md.example      ← Trust-Map: Nodes
│   └── hook.md.example           ← Trigger-Definitionen
│
├── WORKSPACE/                    ← AAMS Körper (L2)
│   └── WORKING/                  ← Bau-Memory
│       ├── WHITEPAPER/           ← Architektur-Wahrheit
│       ├── WORKPAPER/            ← Session-Arbeit
│       ├── MEMORY/               ← LTM (ltm-index.md)
│       ├── DIARY/                ← Entscheidungs-Kontext
│       ├── GUIDELINES/           ← Procedural Memory
│       ├── SCIENCE/              ← Knowledge Validation
│       ├── LOGS/                 ← Audit Trail (prompt_log.jsonl)
│       ├── PROJECT/              ← Projekt-Definitionen (project.yaml)
│       └── TOOLS/                ← Skills (Orchestrierungs-Rezepte)
│           └── skills/           ← Markdown+YAML Workflows
│
└── config/                       ← Konfiguration
```

---

## AAMS — Der Körper

[AAMS](https://github.com/DEVmatrose/AAMS) (Autonomous Agent Manifest Specification) ist ein **framework-unabhängiger Standard** für agentisches Arbeiten. AAMS ist kein Teil von MantisClaw — es ist ein externer, universeller Standard.

MantisClaw nutzt AAMS als **strukturierten Körper** (`WORKSPACE/WORKING/`). Die gesamte WORKING-Struktur ermöglicht strukturiertes Arbeiten an komplexen Aufgaben — ob Coding, Planung oder Organisation.

**Was die AAMS-Struktur gibt:**
- **Workpapers** — Session-Arbeit, eine Datei pro Session
- **Whitepapers** — stabile Architektur-Wahrheit
- **LTM** — Langzeitgedächtnis (ltm-index.md + optional ChromaDB)
- **Diary** — Entscheidungs-Kontext (monatliche Dateien)
- **Guidelines** — Procedural Memory (lernbare Arbeitsweisen)
- **SCIENCE** — Knowledge Validation (externe Forschung, Hypothesen)
- **Skills** — Orchestrierungs-Rezepte in TOOLS/skills/
- **Logs** — Audit Trail (prompt_log.jsonl, Runtime-Metriken)
- **Project** — Projekt-Definitionen mit Milestones und Status

AAMS-Standard: [github.com/DEVmatrose/AAMS](https://github.com/DEVmatrose/AAMS)

---

## Der Loop

```python
async def tick():
    # L1 — Identität emergent berechnen
    soul_t = compute_soul(base, agenda, accounts, social, decentral)
    
    # L4 — Context laden (JIT 3-Stage)
    registry.execute("load_context_always", {})          # ~3k Tokens
    registry.execute("load_context_agenda", {agenda})    # ~8k Tokens
    
    # L3 — Denken
    hooks = load("identity/hook.md")
    guidelines = registry.execute("read_guidelines", {task_type})
    plan = planner(soul_t, hooks, memory, guidelines)
    
    # L3 — Handeln (Tool oder Skill)
    if plan.type == "skill":
        results = skill_executor.execute(plan.skill, context)
    else:
        results = registry.execute(plan.tool, plan.params)
    
    # L3 — Beobachten
    assessment = observer(results, diary, guidelines)
    
    # L3 — Reflexion (RFL)
    if assessment.needs_revision:
        reflection = reflect(assessment, results, plan)
        plan = planner.revise(soul_t, reflection)
        results = executor(plan)  # Zweiter Versuch
    
    # L2 — Procedural Memory + LTM
    observer.extract_lessons(results)  # → GUIDELINES/
    ltm_update(results, assessment)
```

### Schichtenmodell

```
L0  LLM-Backend            → core/llm.py
L1  Identity               → identity/ (soul(t) Berechnung)
L2  AAMS Body (Körper)     → WORKING/ (passiv, nur über Tools)
L3  Runtime / Loop         → core/ (planner, executor, observer, reflect)
L4  Tool-Registry           → core/registry/ (Whitelist, inkl. Körper-Zugriff)
L5  Security               → Querschnitt (Security-Levels pro Tool)
```

> In **Mantis-OS** kommen zusätzlich L6 (Network/MantisNostr) und Skills (WORKING/TOOLS/skills/) hinzu.

> **Kernregel:** L3 (Loop) berührt L2 (Körper) nie direkt. Jeder Zugriff auf WORKING/ läuft über ein registriertes Tool in L4.

---

## Quick Start

```bash
# 1. Repository klonen
git clone https://github.com/DEVmatrose/MantisClaw
cd MantisClaw

# 2. Python Virtual Environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# 3. Dependencies
pip install -r requirements.txt

# 4. Konfiguration
cp config/.env.example .env
# .env editieren:
#   - LLM_BACKEND=lmstudio (default) oder ollama
#   - Optional: Cloud-Keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)

# 5. Identität einrichten
cp identity/base.md.example identity/base.md
cp identity/agenda.md.example identity/agenda.md
# Optional: account.md, social.md, decentral.md, hook.md
```

### LLM-Backend starten

MantisClaw ist **local-first** — ein lokales LLM muss laufen bevor der Agent startet:

```bash
# Option A: LM Studio (default, empfohlen)
# → LM Studio öffnen, Modell laden, Server auf localhost:1234 starten

# Option B: Ollama
ollama serve                    # localhost:11434
ollama run qwen3-coder          # oder ein anderes Modell
```

### Agent-Loop starten (Headless)

```bash
python -m core.runtime
```

Der Runtime-Loop läuft im Terminal und loggt jeden Tick:
```
12:00:00 [mantisclaw.runtime] INFO: MantisClaw starting...
12:00:00 [mantisclaw.runtime] INFO: Health: HEALTHY
12:00:00 [mantisclaw.runtime] INFO: Heartbeat: 60s
12:01:00 [mantisclaw.runtime] INFO: === TICK 1 ===
12:01:00 [mantisclaw.runtime] DEBUG: Soul computed. Agent: MantisClaw
12:01:00 [mantisclaw.runtime] INFO: Plan: ... (2 steps)
```

Stoppt mit `Ctrl+C`. Erstellt automatisch ein Workpaper in `WORKSPACE/WORKING/WORKPAPER/`.

### Dashboard starten (Web-UI)

```bash
uvicorn dashboard.app:app --reload --port 8080
```

Öffne **http://localhost:8080** — das Dashboard zeigt:

```
┌─────────────┬──────────────────────────────────┬───────────────┐
│ L1 Core     │                                  │ R1 Chat-Hist. │
│ L2 Identity │        Chat mit dem Agent         │ R2 Project    │
│ L3 Runtime  │        (SSE-Streaming)            │ R3 Workpapers │
│ L4 Tools    │                                  │ R4 Workspace  │
└─────────────┴──────────────────────────────────┴───────────────┘
```

- **Links (Agent):** L1 Core (Backend/Model-Switcher), L2 Identity (soul(t) + Inspector), L3 Runtime (Health + Live Tick Feed + Prompt Inspector), L4 Tools (Registry)
- **Mitte:** Chat-Interface mit SSE-Streaming (Token-by-Token)
- **Rechts (AAMS):** R1 Chat-History, R2 Projekt + Milestones, R3 Workpapers (mit Closed-Toggle), R4 Workspace-Baum + WP-Preview
- **Model-Switcher:** Wechselt live zwischen LM Studio / Ollama Modellen
- **Identity Inspector:** Zeigt alle 6 Identity-Dateien (base, agenda, account, social, decentral, hook) in Tabs
- **Prompt Inspector:** Letzte LLM-Prompts (System/User/Response) zur Analyse

---

## Eigenständig

| Aspekt | MantisClaw |
|--------|------------|
| AAMS | ✅ Nutzt AAMS als Körper (externer Standard) |
| Runtime | ✅ Eigener Heartbeat-Loop |
| Identity | ✅ Alle Dateien lokal in `identity/` |
| LLM Backend | ✅ LM Studio (default) / Ollama / Cloud optional |
| Dashboard | ✅ Web-UI auf localhost:8080 (FastAPI + SSE + Live Tick Feed) |
| Idle Detection | ✅ Identische Pläne werden nach 3 Wiederholungen übersprungen |
| Prompt Logging | ✅ JSONL-basiert, über Dashboard inspizierbar |
| Deployment | ✅ Einzelnes Repo, eigenständig lauffähig |

**Der Code ist identisch mit MantisClaw in Mantis-OS** — nur die Integration unterscheidet sich.

---

## Runtime-Effizienz

Der autonome Loop verbraucht LLM-Tokens bei jedem Tick. Ohne Gegenmaßnahmen kann ein „Hamsterrad" entstehen — identische Pläne werden endlos wiederholt, jeder Schritt produziert Fehler, und das `analyze`-Tool generiert lange Erklärungen zu nicht-existierenden Pfaden.

### Gegenmaßnahmen (implementiert)

| Problem | Lösung |
|---------|--------|
| **10s Heartbeat zu aggressiv** | Heartbeat auf 60s erhöht (`config/default.yaml`) |
| **Identische Pläne im Loop** | Idle Detection: Plan-Signatur wird gehasht, nach 3 identischen Plänen wird Execution übersprungen |
| **Kein Gedächtnis zwischen Ticks** | Letzte 3 Tick-Summaries werden in den Planner-Context injiziert mit „NICHT wiederholen!" |
| **LLM erfindet Dateipfade** | `_validate_path()` strippt halluzinierte Prefixe (`WORKSPACE/`, `./WORKSPACE/WORKING/`), Tool-Descriptions geben korrekte Beispielpfade |
| **LLM nutzt WORKSPACE/ statt WORKING/** | `workspace_status` gibt Pfade mit `WORKING/` Prefix aus, Planner-Regel: „NIEMALS WORKSPACE/ als Prefix" |
| **LLM ignoriert Antwortformat** | Explizite Format-Instruktion + `VERBOTEN:` Block (keine XML-Tags) + `_parse_plan()` fängt `<Warum>` graceful ab |
| **LLM-Antworten zu lang (2000+ Tokens)** | Planner max 500 Tokens, Analyze max 300 Tokens, Summarize max 200 Tokens |
| **Analyze erklärt Fehler endlos** | Token-Limit + korrigierte Pfade → weniger Fehler → weniger Erklärungen |

### Monitoring

- **Prompt Logging:** Jeder Planner-Call wird als JSONL in `WORKSPACE/WORKING/LOGS/prompt_log.jsonl` gespeichert
- **Prompt Inspector:** Dashboard-Modal zeigt die letzten LLM-Prompts (System/User/Response)
- **Live Tick Feed:** Dashboard zeigt die letzten 8 Ticks mit Erfolgsrate, Goal und Anomalien
- **Idle-Indikator:** Dashboard zeigt „💤 IDLE: X identische Pläne" wenn der Agent im Leerlauf ist

---

## Integration in Mantis-OS

MantisClaw kann allein laufen — oder als Teil von **Mantis-OS** (Autonomes Agenten-Betriebssystem):

```
Mantis-OS (vollständiger Agenten-Knoten)
  ├── MantisClaw (Gehirn + Identität + AAMS-Körper)  ← das ist dieses Repo
  └── MantisNostr (Mesh-Netzwerk)
```

Link: https://github.com/DEVmatrose/Mantis-OS

---

## Dokumentation

### Whitepapers

| Whitepaper | Inhalt |
|---|---|
| [WH-CORE](WORKSPACE/WORKING/WHITEPAPER/CORE.md) | Runtime & Loop — das Gehirn |
| [WH-IDENTITY](WORKSPACE/WORKING/WHITEPAPER/IDENTITY.md) | Emergente Identität — soul(t) |
| [WH-WORKING](WORKSPACE/WORKING/WHITEPAPER/WORKING.md) | AAMS Body — der Körper |
| [WH-TOOLS](WORKSPACE/WORKING/WHITEPAPER/TOOLS.md) | Tool-Registry, Skills & Körper-Interface |

Siehe `WORKSPACE/WORKING/WORKPAPER/` für aktive Session-Arbeit.

---

## Lizenz

MIT
