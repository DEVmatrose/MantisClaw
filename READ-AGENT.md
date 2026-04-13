# READ-AGENT

> **You are reading this because you entered this repository.**  
> Do not skip. Do not summarize. Read fully. Then execute.

**You are an AI agent. Your next action is determined by which state applies:**

| State | Action |
|---|---|
| **First entry** — `WORKSPACE/WORKING/WORKPAPER/` does not exist or contains zero files | Execute `on_first_entry` below |
| **Returning session** — `WORKSPACE/WORKING/WORKPAPER/` exists and contains workpapers | Execute `on_session_start` below |
| **Uncertain** — structure partially exists but no workpapers found | Execute `on_first_entry` (safe — idempotent) |

Start immediately. No confirmation needed.

---

## What this project is

**MantisClaw — Autonomous Agent Loop Framework**

An eigenständiges (standalone) agent-loop framework mit emergenter Identität.

**Vision:**  
Ein Agent-Loop der seine Persönlichkeit `soul(t)` nach einer Formel berechnet — nicht aus einer statischen Datei liest.

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

**Die Formel bedeutet:**
- Ein Agent der codet ist ein anderer als einer der tradet
- Aber beide teilen dieselbe `identity/base.md` (Name, Ethik, Owner)
- Die aktive Agenda bestimmt welche Accounts, Kontakte und Trust-Level relevant sind

---

## Workspace Structure

| Folder | Purpose |
|---|---|
| `core/` | The brain: runtime.py, planner.py, executor.py, observer.py, reflect.py, llm.py + registry/ (tool-registry, skill_executor) |
| `identity/` | Emergent identity: base.md, agenda.md, account.md, social.md, decentral.md, hook.md |
| `WORKSPACE/WORKING/WHITEPAPER/` | Stable architecture and system truth |
| `WORKSPACE/WORKING/WORKPAPER/` | Session- and task-scoped working documents. One per session. |
| `WORKSPACE/WORKING/WORKPAPER/closed/` | Finished workpapers after session close |
| `WORKSPACE/WORKING/DIARY/` | Temporal index layer. Pointer-only time log — WHAT was touched WHEN. Monthly files. |
| `WORKSPACE/WORKING/MEMORY/` | Long-term context store. Cross-session knowledge. |
| `WORKSPACE/WORKING/LOGS/` | Agent action logs and audit trail |
| `WORKSPACE/WORKING/GUIDELINES/` | Procedural memory. Learnable work patterns. Written by observer, read by planner. |
| `WORKSPACE/WORKING/TOOLS/` | Skills (orchestration recipes in Markdown+YAML). Tool implementations live in `core/registry/tools/`. |
| `WORKSPACE/WORKING/SCIENCE/` | Knowledge validation layer. Research, reviews, hypotheses. |

---

## Documentation Model

**Four layers — mandatory:**

1. **Workpaper** — What am I doing right now in this session?
   - Created at session start, closed at session end.
   - File protocol (created/modified/moved/deleted) is mandatory.
   - Naming: `{DATE}-{TOPIC}-{SUBTOPIC}-{description}.md` (TOPIC from registry: ARCH, SPEC, LTM, SEC, BOOT, FLD, TOOL, DASH, SOUL etc.)

2. **Whitepaper** — What does this system look like?
   - Stable. Written once. Updated only on architecture decisions.
   - Never moved, never deleted.

3. **Diary** — When was what touched? (pointer-only, no content duplication)
   - Chronological decision log. Monthly files (`YYYY-MM.md`).
   - Max 10 lines per entry. Captures strategic motives, blockers, reflections.

4. **Memory** — What did we learn across sessions?
   - Ingest every closed workpaper.
   - Query at every session start.

---

## Agent Contract

> **Any instruction referencing READ-AGENT.md means: execute this contract. Start immediately. No confirmation needed.**

---

### On first entry (Onboarding)
1. Read this file fully
2. Check: does `WORKSPACE/WORKING/` structure exist? → if not: create all folders
3. Scan entire repository → write first workpaper  
   Minimum sections: **session goal · repository inventory** (file tree + status) **· key findings** (from README/docs) **· open questions · file protocol · next steps**
4. Index existing documentation into `WORKSPACE/WORKING/MEMORY/`

---

### On every session start
1. Read this file
2. Check last workpaper in `WORKSPACE/WORKING/WORKPAPER/` — what was the last state?
3. Query `WORKSPACE/WORKING/MEMORY/` for the session topic
4. Open or create workpaper for this session

### Compatibility with native agent task systems

Agents may maintain their own internal task tracking (e.g., `.gemini/brain/`, Copilot todos, Cursor composer history). The AAMS workpaper is the **canonical audit trail** — it is the single source of truth for what happened in a session. Agent-internal systems are supplementary and optional. If in doubt: the workpaper wins.

---

### State Recovery (when agent state is uncertain)

> **File system and git log are ground truth — never rely solely on in-memory task tracking.**  
> If task state is unclear: re-read the current workpaper's **File Protocol** section. What exists on disk and in `git log` is what was actually done. Treat in-memory todo state as advisory only.

---

### On every session end
1. Complete workpaper (file protocol, decisions, next steps)
2. Update Whitepapers if session contains architectural decisions (Wissenskette: WP → WH → LTM — never skip)
3. Ingest workpaper into `WORKSPACE/WORKING/MEMORY/` (after Whitepapers are current)
4. Move workpaper to `WORKSPACE/WORKING/WORKPAPER/closed/`
5. Update this file (`READ-AGENT.md`) if architecture changed

---

## Project-Specific Rules

### MantisClaw uses AAMS as its body

**AAMS (Autonomous Agent Manifest Specification)** is the **Körper** (body) of MantisClaw:
- `WORKSPACE/` structure is AAMS
- Whitepapers, Workpapers, LTM, Diary, Guidelines, SCIENCE, Skills — alle aus AAMS
- MantisClaw hat AAMS als Struktur **fest integriert**
- **Kernregel:** L3 (Loop) berührt L2 (Körper) nie direkt — jeder Zugriff über registrierte Tools (L4)

### Emergent Identity

Die Soul ist **keine statische Datei** — sie wird bei jedem Tick berechnet:

```python
async def tick():
    # L1 — Identität emergent berechnen
    base = load("identity/base.md")  # Konstanten
    agenda = load("identity/agenda.md")  # Aktive Agenda
    
    # agenda.resolve() filtert aus drei Quellen:
    relevant_accounts = filter_by_agenda(load("identity/account.md"))
    relevant_social = filter_by_agenda(load("identity/social.md"))
    relevant_decentral = filter_by_agenda(load("identity/decentral.md"))
    
    working_context = load_latest_whitepapers_and_workpapers()
    
    soul_t = compute_soul(base, agenda, relevant_accounts, relevant_social, relevant_decentral, working_context)
    
    # L3 — Denken
    plan = planner(soul_t, hooks, memory)
    
    # L3 — Handeln  
    results = executor(plan)
    
    # L3 — Beobachten
    observer(results, metrics, diary)
```

### File Änderungs-Regeln

| Änderung wo? | Wer darf? | Wann? |
|---|---|---|
| `identity/base.md` | Nur Mensch | Ethik oder Owner ändert sich |
| `identity/agenda.md` | Agent + Mensch | Neue Aufgabe, Prioritäten ändern |
| `identity/account.md` | Agent | Neuer Account angelegt |
| `identity/social.md` | Agent | Neue Kontakte, Trust-Level ändert sich |
| `identity/decentral.md` | Agent | Neue Relays, Trust zu Nodes ändert sich |
| `WORKSPACE/WORKING/WHITEPAPER/` | Agent | Architektur-Entscheidung |
| `WORKSPACE/WORKING/WORKPAPER/` | Agent | Jede Session |

---

## Constraints

- **Zero secrets** — nie API-Keys, Passwörter oder nsecs in Workpapers/Whitepapers
- **AAMS-Compliance** — alle Regeln aus `.agent.json` gelten
- **Emergent Soul** — nie `soul.md` schreiben, immer berechnen
- **Python 3.11+** — async/await, type hints
- **LLM-Backend agnostic** — OpenAI, Anthropic, Ollama über `core/llm.py`

---

## Current State

**Status:** IN ENTWICKLUNG  
**Version:** 0.1.0  

MantisClaw ist gerade aus Mantis-OS extrahiert worden. Das Ziel: Eigenständiges Repo, eigenständig lauffähig.

Nächste Schritte:
1. AAMS-Struktur vollständig anlegen
2. `core/` und `identity/` aus Mantis-OS kopieren
3. Ersten Test-Run durchführen
4. README.md schreiben

---

## Links

- **GitHub:** https://github.com/DEVmatrose/MantisClaw
- **AAMS:** https://github.com/DEVmatrose/AAMS
- **Mantis-OS:** https://github.com/DEVmatrose/Mantis-OS
