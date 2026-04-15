# Workpaper — PROJECT Layer Implementation

**Erstellt:** 2026-04-10
**Status:** OPEN
**Agent:** copilot
**Project:** mantisclaw-core

---

## Session Goal

Implementierung des PROJECT-Layers gemäß WH-PROJECT v0.1.0:
1. Ordnerstruktur + Manifest für erstes Projekt anlegen
2. Runtime-Integration (soul(t) + Planner)
3. Dashboard-Integration (Sidebar + System-Prompt)
4. Validierung per Runtime-Test

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| CREATE | WHITEPAPER/PROJECT.md | WH-PROJECT v0.1.0 — Design |
| CREATE | PROJECT/mantisclaw-core/project.yaml | Erstes Projekt-Manifest |
| CREATE | PROJECT/_active.yaml | Aktives Projekt Pointer |
| MODIFY | core/runtime.py | Projekt in soul(t) + Planner-Injection |
| MODIFY | core/planner.py | Projekt-Kontext im System-Prompt |
| MODIFY | dashboard/app.py | Projekt in Sidebar + System-Prompt |
| MODIFY | WHITEPAPER/WORKING.md | PROJECT/ Ordner dokumentieren |
| | | |

---

## Decisions

- PROJECT/ lebt in WORKING/ (L2 Body, nicht L1 Identity)
- Genau ein aktives Projekt via _active.yaml
- Workpaper/Whitepaper-Zuordnung per optionalem `**Project:**` Header
- Rückwärtskompatibel: WPs ohne Projekt-Referenz bleiben gültig

---

## Ergebnisse

- [x] Runtime-Test: 9 Tools, 5/5 Steps OK, Projekt in soul(t) geladen
- [x] Dashboard: HTTP 200, "MantisClaw Core" + Meilensteine in Sidebar sichtbar
- [x] Planner: Bekommt Projekt-Scope + offene Meilensteine im System-Prompt
- [x] WH-WORKING.md aktualisiert: PROJECT/ Ordner + 6. Memory-Schicht

**Status:** CLOSED  
**Geschlossen:** 2026-04-13
