# Workpaper — Project-Scoped AAMS

**Created:** 2026-04-13
**Status:** OPEN
**Agent:** copilot
**Project:** mantisclaw-core

---

## Session Goal

Redesign AAMS so that each project has its own knowledge body.
The agent keeps global memories (identity, agent-memory).
Everything else is project-scoped.

---

## Core Insight

```
Agent (global, permanent):
  identity/          ← base.md, agenda.md — who am I
  AGENT-MEMORY/      ← cross-project memory: "I worked on X, closed 3 WPs, wrote CORE.md"
  WORKING/TOOLS/     ← global toolbox: read_file, write_file, analyze, summarize,
                       list_models, switch_model — always available, ANY project

Project (scoped, per project):
  WORKPAPER/         ← active session documents
  WHITEPAPER/        ← stable architecture truth
  DIARY/             ← chronological decision log
  MEMORY/            ← project-specific LTM index
  GUIDELINES/        ← procedural patterns for THIS project
  SCIENCE/           ← knowledge validation
  TOOLS/skills/      ← project-specific skills (e.g. loop_monitor for mantisclaw-core)
  LOGS/              ← audit trail
```

## Key Distinction: Agent Memory vs. Project Knowledge

The agent REMEMBERS everything — across all projects. AGENT-MEMORY stores:
- Which projects exist and what happened in them
- When workpapers were opened/closed
- Which whitepapers were created or changed
- Cross-project patterns and lessons learned

But the actual KNOWLEDGE (workpapers, whitepapers, guidelines) belongs to the project.
When you delete a project, its knowledge goes with it.
When you share a project, its AAMS body travels with it.

## Tool Ownership

**Global Agent Tools (WORKING/TOOLS/):**
- Filesystem: read_file, write_file, append_file, list_dir, workspace_status
- Analysis: analyze, summarize
- Memory: query_memory, log_diary
- LLM: list_models, switch_model
- → Available in EVERY project. Like a craftsman's basic toolkit.

**Project Tools (PROJECT/<slug>/TOOLS/):**
- loop_monitor, token_budget → specific to mantisclaw-core
- deploy-to-vercel → specific to a web project
- run-tests → specific to a test project
- → Only loaded when this project is active.

## Current vs. Target

### Current Structure
```
WORKSPACE/
└── WORKING/
    ├── AGENT-MEMORY/     ← agent-level (correct)
    ├── WORKPAPER/        ← flat, all projects mixed
    ├── WHITEPAPER/       ← flat, all projects mixed
    ├── DIARY/            ← flat
    ├── MEMORY/           ← flat
    ├── GUIDELINES/       ← flat
    ├── SCIENCE/          ← flat
    ├── TOOLS/            ← flat
    ├── LOGS/             ← flat
    └── PROJECT/
        ├── _active.yaml
        ├── mantisclaw-core/
        │   └── project.yaml
        └── testprojekt1/
            └── project.yaml
```

### Target Structure
```
WORKSPACE/
├── AGENT-MEMORY/              ← agent-level (promoted out of WORKING)
└── WORKING/
    └── PROJECT/
        ├── _active.yaml
        ├── mantisclaw-core/
        │   ├── project.yaml
        │   ├── WORKPAPER/     ← project-scoped
        │   ├── WHITEPAPER/
        │   ├── DIARY/
        │   ├── MEMORY/
        │   ├── GUIDELINES/
        │   ├── SCIENCE/
        │   ├── TOOLS/
        │   └── LOGS/
        └── testprojekt1/
            ├── project.yaml
            ├── WORKPAPER/     ← project-scoped
            ├── WHITEPAPER/
            └── ...
```

## Migration Strategy

**Phase 1 (now):** Document the architecture. Keep current flat structure as mantisclaw-core's body.
**Phase 2 (next):** Move existing WORKING/ folders INTO PROJECT/mantisclaw-core/.
**Phase 3 (later):** New projects auto-create AAMS structure on init.

Phase 1 is safe — no file moves, just clarity.
Phase 2 requires updating all path references in:
  - core/runtime.py (workspace_root)
  - core/registry/tools/filesystem.py (allowed_paths)
  - dashboard/app.py (workpaper listing, workspace tree)
  - core/workpaper.py (workpaper creation)
  - core/ltm.py (memory index)

## Dashboard R4 Impact

R4 should show the ACTIVE PROJECT's AAMS tree, not the global flat view.
When project changes → R4 changes.

---

## Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Project-scoped AAMS body | Each project owns its knowledge, portable |
| D2 | AGENT-MEMORY stays global | Agent identity transcends projects |
| D3 | identity/ stays global | Soul base doesn't change per project |
| D4 | Phase 1 first (document, don't move) | Safe, reversible |
| D5 | R4 shows active project's tree | Immediate UX improvement |

---

## Next Steps

- [x] Document architecture (this workpaper)
- [ ] Update R4 to show active project's folder tree
- [ ] Phase 2: File migration to project-scoped structure
- [ ] Update filesystem tools for project-scoped paths
- [ ] Auto-create AAMS structure for new projects
