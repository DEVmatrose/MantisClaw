# Workpaper: Whitepaper-Restrukturierung

- **Datum:** 2026-04-09
- **Agent:** GitHub Copilot (Claude Opus 4.6)
- **Status:** CLOSED
- **Bezug:** WH-CORE v0.1.0, WP-Procedural-Memory, WP-RFL, WP-JIT-Context, SCIENCE-Review

---

## Session Goal

CORE.md in drei separate Whitepapers aufteilen: Core (Runtime), Identity (Emergenz), Working (Arbeitsstruktur). Neue Erkenntnisse aus Workpapers und SCIENCE-Review einarbeiten.

---

## Entscheidungen

| # | Entscheidung | Begründung |
|---|-------------|-----------|
| D1 | Split in drei Whitepapers: CORE, IDENTITY, WORKING | Separation of Concerns. Jedes Dokument hat einen klaren Fokus. |
| D2 | CORE.md behält das Schichtenmodell als Übersicht | Core ist das "Gehirn" — es braucht die Gesamtübersicht |
| D3 | CORE.md referenziert IDENTITY + WORKING statt zu duplizieren | Single Source of Truth. Kein Copy-Paste zwischen Docs. |
| D4 | Tick-Cycle in CORE.md um RFL + Context Loading erweitert | Neue Erkenntnisse aus Workpapers → stabilisiert als Whitepaper |
| D5 | IDENTITY.md erklärt soul(t) Berechnung + Abgrenzung zu SOUL.md | Das ist MantisClaw's Differenzierungsmerkmal — verdient eigenes Dokument |
| D6 | WORKING.md integriert alle 5 Memory-Typen + SCIENCE + JIT | Das Working System ist MantisClaw's Körper — der komplexeste Teil |
| D7 | TOOLS.md als viertes Whitepaper (WIP) | Tool-Registry + Skills + Körper-Interface verdient eigenes Dokument — trennt "wie der Loop auf den Körper zugreift" |

---

## File Protocol

| # | Aktion | Datei | Beschreibung |
|---|--------|-------|-------------|
| F1 | CREATED | `WHITEPAPER/IDENTITY.md` | Emergente Identität — soul(t), 6 Dimensionen, Abgrenzung |
| F2 | CREATED | `WHITEPAPER/WORKING.md` | Arbeitsstruktur — 5 Memory-Schichten, SCIENCE, JIT, Wissenskette |
| F3 | UPDATED | `WHITEPAPER/CORE.md` | Refactored: Nur noch Runtime/Loop, Querverweise, RFL + Context Loader |
| F4 | CREATED | `WORKPAPER/2026-04-09-whitepaper-restrukturierung.md` | Dieses Workpaper |
| F5 | CREATED | `WHITEPAPER/TOOLS.md` | WH-TOOLS v0.1.0-WIP: Tool-Registry, Skills, Körper-Interface, Agenda-Filtering |

---

## Next Steps

- [x] README.md aktualisieren (Whitepaper-Referenzen)
- [x] LTM-Ingest
