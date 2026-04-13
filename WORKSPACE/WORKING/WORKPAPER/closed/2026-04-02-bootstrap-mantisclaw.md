# WP-005 — MantisClaw: Eigenständiges Agent-Loop-Framework

**Workpaper:** WP-005  
**Erstellt:** 2026-04-02  
**Geschlossen:** 2026-04-08  
**Status:** CLOSED  
**Autor:** ogerly (Mensch) + LOS (Agent)  
**Kontext:** Entsteht aus der Mantis-Familie-Architektur (WP-004, MANTIS-OS.md v0.2)

---

## Auftrag

MantisClaw als eigenständiges Repo definieren und anlegen. MantisClaw ist das **Agent-Loop-Framework** der Mantis-Familie: Identity + Heartbeat + soul(t). Es läuft allein — und wird in Mantis-OS zum Gehirn.

**Repo:** `d:\Entwicklung\Projekte\CLAW-NETZWERK\MantisClaw`  
**GitHub:** github.com/DEVmatrose/MantisClaw (neues Repo)  
**Projekt:** github.com/orgs/DEVmatrose/projects/1 (Mantis)

---

## Was ist MantisClaw?

MantisClaw ist ein eigenständiges Framework für autonome Agenten mit **emergenter Identität**.

**Der Kern-Satz:** Ein Agent-Loop, der nach einer Formel seine Persönlichkeit berechnet.

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

### Was MantisClaw ist

- Ein autonomer **Heartbeat-Loop** (Tick → Denken → Handeln → Beobachten)
- Ein **Identity-System** mit emergenter Soul
- Ein Framework das **AAMS als Körper** nutzt (Workspace, Workpaper, LTM)
- Ein Ansatz Richtung **Multi-Agenten** (verschiedene Agendas = verschiedene Persönlichkeiten)

### Was MantisClaw NICHT ist

- Kein Nostr-Client (das ist MantisNostr)
- Kein Workspace-Standard (das ist AAMS)
- Kein Monolith — es ist ein LEGO-Stein

---

## Architektur

### Ordnerstruktur

```
MantisClaw/
│
├── .agent.json                      ← AAMS Bootstrap (One File)
├── AGENTS.md                        ← Tool-Bridge
├── READ-AGENT.md                    ← Agent-Vertrag
├── LEGENDE.md                       ← Abkürzungen & Begriffe
│
├── core/                            ← Der Loop (L0 + L3)
│   ├── __init__.py
│   ├── runtime.py                   ← Heartbeat: Tick, Tick, Tick...
│   ├── planner.py                   ← Denken: Context → Plan
│   ├── executor.py                  ← Handeln: Plan → Aktionen
│   ├── observer.py                  ← Beobachten: Metriken, Diary, Guidelines
│   ├── llm.py                       ← LLM-Backend (L0): OpenAI / Anthropic / Ollama
│   ├── session.py                   ← AAMS Session-Lifecycle
│   ├── workpaper.py                 ← Workpaper-Management
│   └── ltm.py                       ← LTM-Ingest (Wissenskette)
│
├── identity/                        ← Die Seele (L1)
│   ├── base.md                      ← Konstanten: Name, Ethik, Keys
│   ├── agenda.md                    ← Wurzelknoten: aktive Agenda → Persönlichkeit
│   ├── account.md                   ← Register: Plattform-Zugänge + Normen
│   ├── social.md                    ← CRM-State: Kontakte pro Account
│   ├── decentral.md                 ← Trust-Map: Nodes + Trust-Level
│   └── hook.md                      ← Trigger-Definitionen
│
├── WORKSPACE/                       ← AAMS-Körper
│   ├── WORKING/                     ← Bau-Memory (Markdown)
│   │   ├── WHITEPAPER/
│   │   ├── WORKPAPER/
│   │   │   └── closed/
│   │   ├── MEMORY/
│   │   ├── AGENT-MEMORY/
│   │   ├── DIARY/
│   │   ├── LOGS/
│   │   ├── GUIDELINES/
│   │   ├── TOOLS/
│   │   └── TESTS/
│   └── AGENDA/                      ← Operations-Memory (SQLite)
│       ├── agenda.db
│       └── ltm/
│
├── config/
│   ├── default.yaml
│   └── .env.example
│
├── requirements.txt
├── README.md
└── .gitignore
```

### Der Loop

```python
async def tick():
    # L1 — Identity
    base = load("identity/base.md")
    agenda = resolve_agenda()
    soul_t = compute_soul(base, agenda)

    # L2 — AAMS Session
    context = session.load_context()

    # L3 — Denken
    plan = planner.think(soul_t, context)

    # L4 — Handeln
    results = executor.run(plan.actions)

    # L2 — Dokumentieren
    session.log(plan, results)

    # Wissenskette bei Close
    if plan.close_session:
        session.close()  # WP → WH → LTM
```

### Emergente Identität

```
Agenda (Wurzelknoten)
  │
  ├── account.md → Welche Skills brauche ich?
  ├── social.md  → Mit wem spreche ich?
  └── decentral.md → Wem vertraue ich?
  
  ↓ base.md = Ethik + Konstanten (immer)
  ↓ working_context = aktuelle Session
  
  = soul(t) → Prompt-Kontext für LLM
```

---

## Bootstrap: "One File" Prinzip

Wie AAMS mit `.agent.json` — MantisClaw hat **eine Datei** die alles auslöst.

Die `.agent.json` im MantisClaw-Repo erweitert AAMS um die MantisClaw-spezifischen Felder:

```json
{
  "agent_id": "mantisclaw-agent",
  "version": "0.1.0",
  "spec": "AAMS/1.0",
  
  "identity": {
    "base": "identity/base.md",
    "agenda": "identity/agenda.md",
    "account": "identity/account.md",
    "social": "identity/social.md",
    "decentral": "identity/decentral.md",
    "hook": "identity/hook.md"
  },
  
  "workspace": "WORKSPACE/WORKING/",
  
  "mantisclaw": {
    "version": "0.1.0",
    "heartbeat_interval": 10,
    "soul_formula": "soul(t) = f(base, agenda.resolve(account, social, decentral), context)",
    "core": {
      "runtime": "core/runtime.py",
      "planner": "core/planner.py",
      "executor": "core/executor.py",
      "observer": "core/observer.py",
      "llm": "core/llm.py"
    }
  },
  
  "config": "config/default.yaml"
}
```

---

## Mantis-OS als Webstuhl

Das Gesamtbild: Mantis-OS ist kein Monolith — es ist ein **Webstuhl** der drei Fäden verwebt.

```
┌─────────────────────────────────────────────────────────────┐
│                    mantisagent.json                          │
│                    "One File to weave them all"              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. AAMS ausführen                                         │
│      → .agent.json → WORKSPACE/ anlegen                     │
│      → Workpaper, Whitepaper, LTM, Diary, Guidelines        │
│                                                             │
│   2. MantisClaw ausführen                                   │
│      → identity/ + core/ anlegen                            │
│      → Heartbeat-Loop starten                               │
│      → soul(t) berechnen                                    │
│                                                             │
│   3. MantisNostr ausführen (optional)                       │
│      → mesh/mantisnostr/ anlegen                            │
│      → Nostr-Client starten                                 │
│      → Events an MantisClaw-Heartbeat liefern               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│   Ergebnis: Ein souveräner, autonomer Agent                 │
└─────────────────────────────────────────────────────────────┘
```

**Strategischer Einstiegspunkt:** AAMS wirbt mit "One File". Mantis-OS macht es genauso — **eine `mantisagent.json`** die einem Agent sagt: Bau mir AAMS auf, starte MantisClaw, verbinde MantisNostr. Fertig.

---

## Abgrenzung: MantisClaw Standalone vs. in Mantis-OS

| Aspekt | MantisClaw Standalone | MantisClaw in Mantis-OS |
|--------|----------------------|------------------------|
| AAMS | Eigene .agent.json, eigener Workspace | Mantis-OS .agent.json, geteilter Workspace |
| MantisNostr | Nicht vorhanden | mesh/mantisnostr/ als Sidecar |
| Identity | Alle Dateien lokal in identity/ | Alle Dateien lokal in identity/ (identisch) |
| Heartbeat | Eigener Loop | Eigener Loop (identisch) |
| Deployment | Einzelnes Repo | Teil des Mantis-OS Monorepos |

**Der Code ist derselbe.** Der Unterschied ist nur: Was steckt man drumherum?

---

## Nächste Schritte

1. **Repo anlegen:** `d:\Entwicklung\Projekte\CLAW-NETZWERK\MantisClaw`
2. **GitHub Repo erstellen:** DEVmatrose/MantisClaw
3. **Zu Mantis-Projekt hinzufügen:** github.com/orgs/DEVmatrose/projects/1
4. **GitHub MantisClaw → MantisNostr umbenennen:** DEVmatrose/MantisClaw → DEVmatrose/MantisNostr
5. **mantisagent.json erstellen:** Bootstrap-Datei für Mantis-OS
6. **README.md für MantisClaw:** Eigenständige Dokumentation

---

## Offene Fragen

- Soll MantisClaw ein eigenes Whitepaper-Set bekommen oder referenziert es Mantis-OS Whitepapers?
- Wie verhält sich die Wissenskette wenn MantisClaw standalone läuft vs. in Mantis-OS?
- Git Submodules vs. Copy für die Integration in Mantis-OS?

---

*Workpaper. Wird bei Session-Close archiviert.*
