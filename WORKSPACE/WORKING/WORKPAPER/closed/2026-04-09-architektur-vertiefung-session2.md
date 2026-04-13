# Workpaper: Architektur-Vertiefung Session 2

- **Datum:** 2026-04-09
- **Agent:** GitHub Copilot (Claude Opus 4.6)
- **Status:** CLOSED
- **Geschlossen:** 2026-04-09
- **Release:** v0.2.0-draft
- **Bezug:** WP-2026-04-09-core-readme-refactor (Session 1), SCIENCE Review, alle offenen Workpapers

---

## Session Goal

Architektur von MantisClaw in mehreren Phasen vertiefen: AAMS-Korrektur → SCIENCE-Integration → Gap-Analyse → Whitepaper-Restrukturierung → Tools & Skills Architektur → Dokumentations-Sync.

---

## Phasen (chronologisch)

### Phase 1: AAMS-Korrektur
- "MantisClaw braucht AAMS" → "AAMS ist fest in MantisClaw integriert"
- CORE.md und README.md korrigiert

### Phase 2: SCIENCE Knowledge Validation Layer
- Workpaper aus AAMS (VERWORFEN) für MantisClaw wiedereröffnet
- SCIENCE als Agent-Loop-Feature, nicht AAMS-Spec
- Drei Executor-Aktionen: science.research, science.validate, science.hypothesize

### Phase 3: SINCE→SCIENCE Rename
- Tippfehler korrigiert (66 Vorkommen)

### Phase 4: SCIENCE Review — MantisClaw vs. State of the Art
- Vollständiger Review erstellt: ~80% Alignment mit State of Art
- Drei Gaps identifiziert: Procedural Memory, Reflection-Loop, JIT Context Loading

### Phase 5: Gap-Filling Workpapers
- WP Procedural Memory → GUIDELINES/ als lernbare Arbeitsweise
- WP Reflection-Loop (RFL) → Observer→reflect()→Planner Rückkanal
- WP JIT Context Loading → 3-Stage: Always + Agenda + Query

### Phase 6: Whitepaper-Restrukturierung
- CORE.md → Nur noch Runtime/Loop
- IDENTITY.md → Emergente Identität, soul(t)
- WORKING.md → AAMS Body, 5 Memory-Schichten, SCIENCE, JIT

### Phase 7: Tools & Skills Architektur
- Tool-Registry (Whitelist, atomar, stateless) vs. Skill-Kasten (Rezepte, Markdown+YAML)
- Körper-Interface-Prinzip: L3 berührt L2 nie direkt → nur über Tools
- Schichtenmodell geschärft auf L0-L7
- Agenda-basiertes Tool-Filtering (Rucksack-Metapher)
- WH-TOOLS.md als viertes Whitepaper (v0.1.0-WIP) erstellt

### Phase 8: Dokumentations-Sync
- Alle Workpapers auf WH-TOOLS-Änderungen aktualisiert
- LEGENDE.md um neue Begriffe ergänzt (RFL, JIT, SCIENCE, L4-L7)
- README.md: Architektur, Loop, Schichtenmodell, Whitepaper-Tabelle
- AGENTS.md + READ-AGENT.md: Workspace-Struktur, Kernregel, Core-Module

---

## Entscheidungen

| # | Entscheidung | Begründung |
|---|---|---|
| D1 | AAMS ist integriert, nicht extern | Korrektur: AAMS ist Struktur fest in MantisClaw |
| D2 | SCIENCE als MantisClaw-Feature, nicht AAMS | Kognitiver Prozess braucht LLM + Loop |
| D3 | Drei Gaps gefüllt: Procedural Memory, RFL, JIT | SCIENCE Review identifizierte sie |
| D4 | Whitepapers gesplittet: CORE, IDENTITY, WORKING | Separation of Concerns |
| D5 | WH-TOOLS als viertes Whitepaper (WIP) | Tool/Skill-Architektur verdient eigenes Dokument |
| D6 | Whitelist-Registry statt dynamisches Laden | Vorhersagbarkeit, Sicherheit, Fail-fast |
| D7 | Körper-Zugriff nur über Tools | L3→L4→L2, saubere Schichtentrennung |
| D8 | Agenda-basiertes Tool-Filtering | JIT-Integration, Token-Effizienz (60-70% weniger) |
| D9 | Schichtenmodell erweitert auf L0-L7 | L5 für Skills (Procedural Memory/Rezepte) |
| D10 | Skills in WORKING/TOOLS/skills/ | AAMS-Body, nicht Runtime-Code |

---

## File Protocol

| # | Aktion | Datei | Beschreibung |
|---|--------|-------|-------------|
| F1 | UPDATED | `WHITEPAPER/CORE.md` | v0.2.0: Refactored auf reinen Loop, RFL + JIT |
| F2 | CREATED | `WHITEPAPER/IDENTITY.md` | v0.2.0: Emergente Identität, soul(t) |
| F3 | CREATED | `WHITEPAPER/WORKING.md` | v0.2.0: AAMS Body, 5 Memory-Schichten |
| F4 | CREATED | `WHITEPAPER/TOOLS.md` | v0.1.0-WIP: Tool-Registry, Skills, Körper-Interface |
| F5 | CREATED | `WORKPAPER/2026-04-09-core-readme-refactor.md` | AAMS-Korrektur |
| F6 | CREATED | `WORKPAPER/2026-04-09-science-knowledge-validation-layer.md` | SCIENCE als Feature |
| F7 | CREATED | `WORKPAPER/2026-04-09-procedural-memory-guidelines.md` | Procedural Memory |
| F8 | CREATED | `WORKPAPER/2026-04-09-reflection-loop-rfl.md` | RFL Design |
| F9 | CREATED | `WORKPAPER/2026-04-09-jit-context-loading.md` | JIT 3-Stage |
| F10 | CREATED | `WORKPAPER/2026-04-09-whitepaper-restrukturierung.md` | Split-Dokumentation |
| F11 | CREATED | `WORKPAPER/2026-04-09-tools-skills-architecture.md` | Tools & Skills WP (→PROMOTED) |
| F12 | CREATED | `SCIENCE/2026-04-09-mantisclaw-vs-state-of-the-art-review.md` | Full Review |
| F13 | UPDATED | `README.md` | Architektur, Loop, Schichtenmodell, Whitepapers |
| F14 | UPDATED | `AGENTS.md` | Workspace-Struktur, Kernregel |
| F15 | UPDATED | `READ-AGENT.md` | Core-Module, GUIDELINES, TOOLS, SCIENCE, Kernregel |
| F16 | UPDATED | `LEGENDE.md` | L4-L7, RFL, JIT, SCIENCE, WH-TOOLS |
| F17 | CREATED | Dieses Workpaper | Session-Zusammenfassung |

---

## Nächste Schritte

1. WH-CORE aktualisieren: Core = reiner Loop (context.py, session.py, workpaper.py, ltm.py → Tools)
2. WH-WORKING aktualisieren: TOOLS/ Ordnerstruktur mit skills/
3. WH-TOOLS offene Fragen klären (§9: Skill-Generierung, Versionierung, Token-Budget, Verschachtelung, Context-Bootstrap)
4. Erste Skills als .md erstellen (diary_entry, ltm_ingest)
5. registry.json Skeleton erstellen
6. Core-Refactoring planen: workpaper.py + ltm.py → workspace-Tools
