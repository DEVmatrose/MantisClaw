# MantisClaw — Autonomous Agent Loop Framework

> **Language:** English | [Deutsch](README-DE.md) | [中文](README-CH.md)

<p align="center">
  <img src="docs/mantisclaw-overview.png" alt="MantisClaw Overview" width="700">
</p>

**Version:** 0.1.0  
**Status:** IN DEVELOPMENT  
**GitHub:** [DEVmatrose/MantisClaw](https://github.com/DEVmatrose/MantisClaw)  
**Author:** [@ogerly](https://github.com/ogerly) · [DEVmatrose](https://github.com/DEVmatrose)  
**Part of:** [Mantis Family](https://github.com/DEVmatrose)  
**License:** MIT

## What is MantisClaw?

MantisClaw is a **standalone** agent-loop framework with **emergent identity**.

### The Core Idea: Emergent Soul

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

The soul is **never written** — it is **computed** at every tick. An agent who codes is different from one who trades, yet both share the same `identity/base.md`.

-----

## Architecture

```
MantisClaw/
│
├── .agent.json                 ← AAMS Bootstrap
├── AGENTS.md                   ← Tool-Bridge
├── READ-AGENT.md               ← Agent Contract
│
├── core/                       ← The Brain (L3) — pure loop
│   ├── runtime.py              ← Heartbeat-Loop (60s, Idle Detection)
│   ├── planner.py              ← Thinking (Tool-Injection + JSONL Prompt Logging)
│   ├── executor.py             ← Action (Fuzzy Action Matching)
│   ├── observer.py             ← Observing + Health-Tracking
│   ├── reflect.py              ← Reflection (RFL) — Self-Correction
│   ├── context.py              ← JIT Context Loading (3-Stage)
│   ├── skill_executor.py       ← Skill Orchestration (L5)
│   ├── llm.py                  ← LLM-Backend (L0)
│   ├── session.py              ← AAMS Session Management
│   ├── workpaper.py            ← Workpaper Management
│   ├── ltm.py                  ← Long-Term Memory
│   └── registry/               ← Tool-Registry (L4)
│       ├── __init__.py         ← ToolRegistry + Tool Classes
│       ├── registry.py         ← Whitelist, Security-Levels, Fuzzy-Resolve
│       └── tools/              ← Tool Implementations
│           ├── filesystem.py   ← read_file, write_file, list_dir, workspace_status
│           ├── memory.py       ← query_memory, log_diary
│           └── analysis.py     ← analyze, summarize (LLM-powered)
│
├── identity/                   ← Emergent Identity (L1)
│   ├── base.md.example         ← Constants: Name, Ethics, Keys
│   ├── agenda.md.example       ← Root Node: Active Agenda
│   ├── account.md.example      ← Platform Access
│   ├── social.md.example       ← CRM-State: Contacts
│   ├── decentral.md.example    ← Trust-Map: Nodes
│   └── hook.md.example         ← Trigger Definitions
│
├── WORKSPACE/                  ← AAMS Body (L2)
│   └── WORKING/                ← Construction Memory
│       ├── WHITEPAPER/         ← Architectural Truth
│       ├── WORKPAPER/          ← Session Work
│       ├── MEMORY/             ← LTM (ltm-index.md)
│       ├── DIARY/              ← Decision Context
│       ├── GUIDELINES/         ← Procedural Memory
│       ├── SCIENCE/            ← Knowledge Validation
│       ├── LOGS/               ← Audit Trail (prompt_log.jsonl)
│       ├── PROJECT/            ← Project Definitions (project.yaml)
│       └── TOOLS/              ← Skills (Orchestration Recipes)
│           └── skills/         ← Markdown+YAML Workflows
│
└── config/                     ← Configuration
```

-----

## AAMS — The Body

[AAMS](https://github.com/DEVmatrose/AAMS) (Autonomous Agent Manifest Specification) is a **framework-independent standard** for agentic work. AAMS is not a part of MantisClaw — it is an external, universal standard.

MantisClaw uses AAMS as a **structured body** (`WORKSPACE/WORKING/`). The entire WORKING structure enables structured labor on complex tasks — whether coding, planning, or organization.

**What the AAMS structure provides:**

  - **Workpapers** — Session work, one file per session
  - **Whitepapers** — Stable architectural truth
  - **LTM** — Long-term memory (ltm-index.md + optional ChromaDB)
  - **Diary** — Decision context (monthly files)
  - **Guidelines** — Procedural memory (learnable workflows)
  - **SCIENCE** — Knowledge validation (external research, hypotheses)
  - **Skills** — Orchestration recipes in TOOLS/skills/
  - **Logs** — Audit trail (prompt\_log.jsonl, runtime metrics)
  - **Project** — Project definitions with milestones and status

AAMS-Standard: [github.com/DEVmatrose/AAMS](https://github.com/DEVmatrose/AAMS)

-----

## The Loop

```python
async def tick():
    # L1 — Compute emergent identity
    soul_t = compute_soul(base, agenda, accounts, social, decentral)
    
    # L4 — Load context (JIT 3-Stage)
    registry.execute("load_context_always", {})          # ~3k Tokens
    registry.execute("load_context_agenda", {agenda})    # ~8k Tokens
    
    # L3 — Thinking
    hooks = load("identity/hook.md")
    guidelines = registry.execute("read_guidelines", {task_type})
    plan = planner(soul_t, hooks, memory, guidelines)
    
    # L3 — Action (Tool or Skill)
    if plan.type == "skill":
        results = skill_executor.execute(plan.skill, context)
    else:
        results = registry.execute(plan.tool, plan.params)
    
    # L3 — Observation
    assessment = observer(results, diary, guidelines)
    
    # L3 — Reflection (RFL)
    if assessment.needs_revision:
        reflection = reflect(assessment, results, plan)
        plan = planner.revise(soul_t, reflection)
        results = executor(plan)  # Second attempt
    
    # L2 — Procedural Memory + LTM
    observer.extract_lessons(results)  # → GUIDELINES/
    ltm_update(results, assessment)
```

### Layer Model

```
L0  LLM-Backend             → core/llm.py
L1  Identity                → identity/ (soul(t) calculation)
L2  AAMS Body               → WORKING/ (passive, access via tools only)
L3  Runtime / Loop          → core/ (planner, executor, observer, reflect)
L4  Tool-Registry           → core/registry/ (Whitelist, incl. body access)
L5  Security                → Cross-cutting (Security levels per tool)
```

> In **Mantis-OS**, L6 (Network/MantisNostr) and Skills (WORKING/TOOLS/skills/) are added.

> **Core Rule:** L3 (Loop) never touches L2 (Body) directly. Every access to WORKING/ runs through a registered tool in L4.

-----

## Quick Start

```bash
# 1. Clone Repository
git clone https://github.com/DEVmatrose/MantisClaw
cd MantisClaw

# 2. Python Virtual Environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows

# 3. Dependencies
pip install -r requirements.txt

# 4. Configuration
cp config/.env.example .env
# Edit .env:
#   - LLM_BACKEND=lmstudio (default) or ollama
#   - Optional: Cloud-Keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)

# 5. Set up Identity
cp identity/base.md.example identity/base.md
cp identity/agenda.md.example identity/agenda.md
# Optional: account.md, social.md, decentral.md, hook.md
```

### Start LLM-Backend

MantisClaw is **local-first** — a local LLM must be running before the agent starts:

```bash
# Option A: LM Studio (default, recommended)
# → Open LM Studio, load model, start server on localhost:1234

# Option B: Ollama
ollama serve                    # localhost:11434
ollama run qwen3-coder          # or another model
```

### Start Agent-Loop (Headless)

```bash
python -m core.runtime
```

The runtime loop runs in the terminal and logs every tick:

```
12:00:00 [mantisclaw.runtime] INFO: MantisClaw starting...
12:00:00 [mantisclaw.runtime] INFO: Health: HEALTHY
12:00:00 [mantisclaw.runtime] INFO: Heartbeat: 60s
12:01:00 [mantisclaw.runtime] INFO: === TICK 1 ===
12:01:00 [mantisclaw.runtime] DEBUG: Soul computed. Agent: MantisClaw
12:01:00 [mantisclaw.runtime] INFO: Plan: ... (2 steps)
```

Stop with `Ctrl+C`. Automatically creates a workpaper in `WORKSPACE/WORKING/WORKPAPER/`.

### Start Dashboard (Web-UI)

```bash
uvicorn dashboard.app:app --reload --port 8080
```

Open **http://localhost:8080** — the dashboard displays:

```
┌─────────────┬──────────────────────────────────┬───────────────┐
│ L1 Core     │                                  │ R1 Chat-Hist. │
│ L2 Identity │        Chat with the Agent       │ R2 Project    │
│ L3 Runtime  │        (SSE-Streaming)           │ R3 Workpapers │
│ L4 Tools    │                                  │ R4 Workspace  │
└─────────────┴──────────────────────────────────┴───────────────┘
```

  - **Left (Agent):** L1 Core (Backend/Model-Switcher), L2 Identity (soul(t) + Inspector), L3 Runtime (Health + Live Tick Feed + Prompt Inspector), L4 Tools (Registry)
  - **Center:** Chat interface with SSE streaming (token-by-token)
  - **Right (AAMS):** R1 Chat history, R2 Project + Milestones, R3 Workpapers (with closed-toggle), R4 Workspace tree + WP preview
  - **Model-Switcher:** Live switching between LM Studio / Ollama models
  - **Identity Inspector:** Shows all 6 identity files (base, agenda, account, social, decentral, hook) in tabs
  - **Prompt Inspector:** Latest LLM prompts (System/User/Response) for analysis

-----

## Standalone

| Aspect | MantisClaw |
|--------|------------|
| AAMS | ✅ Uses AAMS as body (external standard) |
| Runtime | ✅ Native heartbeat loop |
| Identity | ✅ All files local in `identity/` |
| LLM Backend | ✅ LM Studio (default) / Ollama / Cloud optional |
| Dashboard | ✅ Web-UI on localhost:8080 (FastAPI + SSE + Live Tick Feed) |
| Idle Detection | ✅ Identical plans skipped after 3 repetitions |
| Prompt Logging | ✅ JSONL-based, inspectable via Dashboard |
| Deployment | ✅ Single repo, runs standalone |

**The code is identical to MantisClaw in Mantis-OS** — only the integration differs.

-----

## Runtime Efficiency

The autonomous loop consumes LLM tokens at every tick. Without countermeasures, a "hamster wheel" effect can occur — identical plans are repeated endlessly, every step produces errors, and the `analyze` tool generates long explanations for non-existent paths.

### Countermeasures (Implemented)

| Problem | Solution |
|---------|--------|
| **10s Heartbeat too aggressive** | Heartbeat increased to 60s (`config/default.yaml`) |
| **Identical plans in loop** | Idle Detection: Plan signature is hashed; after 3 identical plans, execution is skipped |
| **No memory between ticks** | Last 3 tick summaries injected into Planner context with "DO NOT repeat\!" |
| **LLM invents file paths** | `_validate_path()` strips hallucinated prefixes (`WORKSPACE/`, `./WORKSPACE/WORKING/`); tool descriptions provide correct example paths |
| **LLM uses WORKSPACE/ instead of WORKING/** | `workspace_status` returns paths with `WORKING/` prefix; Planner rule: "NEVER use WORKSPACE/ as prefix" |
| **LLM ignores response format** | Explicit format instruction + `FORBIDDEN:` block (no XML tags) + `_parse_plan()` handles `<Reasoning>` gracefully |
| **LLM responses too long (2000+ tokens)** | Planner max 500 tokens, Analyze max 300 tokens, Summarize max 200 tokens |
| **Analyze explains errors endlessly** | Token limit + corrected paths → fewer errors → fewer explanations |

### Monitoring

  - **Prompt Logging:** Every planner call is saved as JSONL in `WORKSPACE/WORKING/LOGS/prompt_log.jsonl`
  - **Prompt Inspector:** Dashboard modal shows the latest LLM prompts (System/User/Response)
  - **Live Tick Feed:** Dashboard shows the last 8 ticks with success rate, goal, and anomalies
  - **Idle Indicator:** Dashboard displays "💤 IDLE: X identical plans" when the agent is idling

-----

## Integration in Mantis-OS

MantisClaw can run alone — or as part of **Mantis-OS** (Autonomous Agent Operating System):

```
Mantis-OS (Full Agent Node)
  ├── MantisClaw (Brain + Identity + AAMS Body)   ← This repository
  └── MantisNostr (Mesh Network)
```

Link: [https://github.com/DEVmatrose/Mantis-OS](https://github.com/DEVmatrose/Mantis-OS)

-----

## Documentation

### Whitepapers

| Whitepaper | Content |
|---|---|
| [WH-CORE](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/CORE.md) | Runtime & Loop — the Brain |
| [WH-IDENTITY](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/IDENTITY.md) | Emergent Identity — soul(t) |
| [WH-WORKING](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/WORKING.md) | AAMS Body — the Body |
| [WH-TOOLS](https://www.google.com/search?q=WORKSPACE/WORKING/WHITEPAPER/TOOLS.md) | Tool Registry, Skills & Body Interface |

See `WORKSPACE/WORKING/WORKPAPER/` for active session work.

-----

## License

MIT