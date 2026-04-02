# MantisClaw — Autonomous Agent Loop Framework

**Version:** 0.1.0  
**Status:** IN ENTWICKLUNG  
**GitHub:** https://github.com/DEVmatrose/MantisClaw

---

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
├── core/                         ← Das Gehirn (L3)
│   ├── runtime.py                ← Heartbeat-Loop
│   ├── planner.py                ← Denken
│   ├── executor.py               ← Handeln
│   ├── observer.py               ← Beobachten
│   ├── llm.py                    ← LLM-Backend (L0)
│   ├── session.py                ← AAMS Session-Lifecycle
│   ├── workpaper.py              ← Workpaper-Management
│   └── ltm.py                    ← LTM-Ingest
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
│       └── TOOLS/                ← Werkzeuge
│
└── config/                       ← Konfiguration
```

---

## AAMS — Der Körper

**MantisClaw braucht AAMS** für agentisches Arbeiten.

AAMS = Autonomous Agent Manifest Specification — ein framework-unabhängiger Standard für Workspace-Struktur, Gedächtnis und Audit-Trail.

**Was AAMS gibt:**
- **Workpapers** — Session-Arbeit, eine Datei pro Session
- **Whitepapers** — stabile Architektur-Wahrheit
- **LTM** — Langzeitgedächtnis (ltm-index.md + optional ChromaDB)
- **Diary** — Entscheidungs-Kontext (monatliche Dateien)

Link: https://github.com/DEVmatrose/AAMS

---

## Der Loop

```python
async def tick():
    # L1 — Identität emergent berechnen
    base = load("identity/base.md")
    agenda = load("identity/agenda.md")
    
    # Agenda filtert relevante Dimensionen:
    accounts = agenda.resolve(load("identity/account.md"))
    social = agenda.resolve(load("identity/social.md"))
    decentral = agenda.resolve(load("identity/decentral.md"))
    
    working_context = load_whitepapers_and_workpapers()
    
    soul_t = compute_soul(base, agenda, accounts, social, decentral, working_context)
    
    # L3 — Denken
    hooks = load("identity/hook.md")
    plan = planner(soul_t, hooks, memory_query(topic))
    
    # L3 — Handeln
    results = executor(plan)
    
    # L3 — Beobachten
    observer(results, diary, guidelines)
```

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
#   - LLM_BACKEND=openai|anthropic|ollama
#   - API Keys

# 5. Identität einrichten
cp identity/base.md.example identity/base.md
cp identity/agenda.md.example identity/agenda.md
cp identity/account.md.example identity/account.md
cp identity/social.md.example identity/social.md
cp identity/decentral.md.example identity/decentral.md
cp identity/hook.md.example identity/hook.md

# 6. Starten
python -m core.runtime
```

---

## Eigenständig, aber braucht AAMS

| Aspekt | MantisClaw Standalone |
|--------|----------------------|
| AAMS | ✅ Eigene `.agent.json`, eigener `WORKSPACE/` |
| Runtime | ✅ Eigener Heartbeat-Loop |
| Identity | ✅ Alle Dateien lokal in `identity/` |
| LLM Backend | ✅ OpenAI / Anthropic / Ollama |
| Deployment | ✅ Einzelnes Repo, eigenständig lauffähig |

**Der Code ist identisch mit MantisClaw in Mantis-OS** — nur die Integration unterscheidet sich.

---

## Integration in Mantis-OS

MantisClaw kann allein laufen — oder als Teil von **Mantis-OS** (Autonomes Agenten-Betriebssystem):

```
Mantis-OS (vollständiger Agenten-Knoten)
  ├── MantisClaw (Gehirn + Identität)  ← das ist dieses Repo
  ├── AAMS (Körper)
  └── MantisNostr (Mesh-Netzwerk)
```

Link: https://github.com/DEVmatrose/Mantis-OS

---

## Dokumentation

Siehe `WORKSPACE/WORKING/WORKPAPER/2026-04-02-bootstrap-mantisclaw.md` — das erste Workpaper beschreibt die Extraktion aus Mantis-OS.

Weitere Whitepapers folgen bei Architektur-Entscheidungen.

---

## Lizenz

MIT
