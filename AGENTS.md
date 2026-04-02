# AGENTS.md

> **This file is read automatically by GitHub Copilot, Cursor, Claude Code, OpenAI Codex, Windsurf, Aider, Continue.dev, and most other AI coding agents.**

This repository uses **AAMS — Autonomous Agent Manifest Specification**.

---

## Execute now. No confirmation needed.

1. Read [`.agent.json`](./.agent.json) — your workspace contract
2. Read [`READ-AGENT.md`](./READ-AGENT.md) — full project context and session rules  
3. **Check state before executing:**
   - IF `WORKSPACE/WORKING/WORKPAPER/` does not exist or is empty → Execute `agent_contract.on_first_entry`
   - IF `WORKSPACE/WORKING/WORKPAPER/` exists and contains workpapers → Execute `agent_contract.on_session_start`

---

## You MUST

- Follow the agent contract in `READ-AGENT.md`
- Create a workpaper in `WORKSPACE/WORKING/WORKPAPER/` at session start
- Query `WORKSPACE/WORKING/MEMORY/` for prior context before starting work
- Complete the workpaper (file protocol + decisions + next steps) at session end
- Ingest the workpaper into `WORKSPACE/WORKING/MEMORY/` before closing

## You MUST NOT

- Write secrets, tokens, or credentials into any workpaper, whitepaper, or manifest
- Delete files in `WORKSPACE/WORKING/` — only create and move
- Skip the file protocol in workpapers

---

## Workspace structure

```
WORKSPACE/
└── WORKING/
    ├── WHITEPAPER/     ← stable architecture truth
    ├── WORKPAPER/      ← active session (one file per session)
    │   └── closed/     ← archived sessions
    ├── DIARY/          ← chronological decision log (monthly)
    ├── MEMORY/         ← long-term context index
    ├── GUIDELINES/     ← coding standards
    ├── LOGS/           ← audit trail
    └── TOOLS/          ← project-specific scripts
```

---

## What is MantisClaw?

**MantisClaw** is an autonomous agent-loop framework with **emergent identity**.

**Core Formula:**
```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

The Soul is not static — it emerges from the current context. A coding agent has a different soul than a trading agent, but both share the same `base.md`.

**Structure:**
- `core/` — The brain (runtime, planner, executor, observer)
- `identity/` — Emergent identity (base, agenda, accounts, social, decentral)
- `WORKSPACE/` — AAMS body (whitepapers, workpapers, LTM)

**Eigenständig:** MantisClaw läuft standalone, benötigt aber AAMS für agentisches Arbeiten.
