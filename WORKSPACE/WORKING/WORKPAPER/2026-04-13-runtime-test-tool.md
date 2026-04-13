# Workpaper — Runtime Test Tool (loop_monitor)

**Erstellt:** 2026-04-13
**Status:** OPEN
**Agent:** copilot
**Project:** mantisclaw-core

---

## Session Goal

Erstes Projekt-Tool bauen: `loop_monitor` — ein Test-/Monitoring-Tool das:
1. Den Runtime-Loop startet (oder prüft ob er läuft)
2. Per LM Studio API die Token-Nutzung pro Tick überwacht
3. Anomalien erkennt (Token-Explosion, Pfad-Fehler, Format-Fehler)
4. RFL-Feedback generiert um den Loop zu verbessern

**Warum:** Token-Effizienz ist kritisch. Im Loop (heartbeat) sind 500 Tokens/Plan gut.
Aber wenn wir später echte Coding-Tasks machen, brauchen wir mehr — das muss bewusst gesteuert werden.
Dieses Tool wird das erste Tool das im Projekt registriert und sichtbar ist.

---

## Design

### Tool-Typ: Skill (AAMS L4)

**Format:** Markdown + YAML Frontmatter (wie `workspace_status.md`)

**Trigger:** Manuell per Dashboard oder CLI (nicht automatisch pro Tick)

### Kernfunktionen

1. **Token-Monitor** — Fragt LM Studio `/v1/completions` Stats ab
2. **Tick-Validator** — Prüft `/api/runtime/ticks` ob Pläne sinnvoll, nicht repetitiv
3. **Format-Check** — Validiert dass Planner GOAL/REASONING/STEP Format nutzt
4. **RFL-Feedback** — Generiert Verbesserungsvorschläge basierend auf Anomalien

### API-Endpunkte die genutzt werden

- `http://localhost:1234/v1/completions` — LM Studio API (Token-Stats)
- `http://localhost:8080/api/runtime/ticks` — Dashboard Tick-History
- `http://localhost:8080/api/runtime` — Runtime Status
- `http://localhost:8080/api/logs/prompts` — Prompt-Log

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| CREATE | `core/registry/tools/loop_monitor.py` | Python-Tool: loop_monitor + token_budget |
| CREATE | `WORKING/TOOLS/skills/loop_monitor.md` | Skill-YAML Wrapper |
| MODIFY | `core/runtime.py` | Import + Registrierung loop_monitor_tools |
| MODIFY | `PROJECT/mantisclaw-core/project.yaml` | Tool-Sektion + Milestone |
| CREATE | `WORKING/GUIDELINES/token-budget.md` | Token-Budget Guideline |

---

## Decisions

| # | Entscheidung | Begründung |
|---|-------------|------------|
| D1 | Python-Script, kein reines Skill-YAML | Braucht HTTP-Calls + Logik, zu komplex für reinen Skill-Workflow |
| D2 | Eigenständiges Tool + Skill-Wrapper | Python-Tool in core/registry/tools/, Skill-YAML als Orchestrierung |
| D3 | Registrierung im Projekt | Unter PROJECT/mantisclaw-core/ sichtbar, im Dashboard angezeigt |

---

## Token-Budget Guideline (aus Session-Erkenntnissen)

| Kontext | Max Tokens | Begründung |
|---------|-----------|------------|
| Planner (Heartbeat/Idle) | 500 | Kurze Pläne, 5 Steps max |
| Planner (Active Task) | 1500 | Komplexere Aufgaben brauchen mehr Schritte |
| Analyze | 300 | Zusammenfassungen, kein Roman |
| Summarize | 200 | Ultra-kurz |
| Coding Tasks | 2000-4000 | Hier MUSS mehr investiert werden |

**Regel:** Token-Limits sind kontextabhängig. Der Loop spart, echte Arbeit investiert.

---

## Next Steps

- [ ] Python-Tool `loop_monitor.py` in `core/registry/tools/` implementieren
- [ ] Skill-YAML `loop_monitor.md` in `WORKSPACE/WORKING/TOOLS/skills/` anlegen
- [ ] Tool in Registry registrieren
- [ ] Dashboard: Tool unter Projekt-Tools anzeigen
- [ ] Erster Testlauf: Runtime 5 Ticks → Monitor auswerten
