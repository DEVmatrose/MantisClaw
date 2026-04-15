# Workpaper — Runtime Tests & Tooling

**Erstellt:** 2026-04-15
**Status:** OPEN
**Agent:** copilot
**Project:** mantisclaw-core

---

## Session Goal

1. AAMS Housekeeping: Git commit + push aller offenen Änderungen
2. README auf aktuellen Stand prüfen und aktualisieren
3. Runtime-Lauffähigkeit testen und absichern
4. Erstes Test-Framework aufsetzen (pytest)
5. Informationen sammeln → mächtiges, hilfreiches Tool konzipieren

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| CREATE | `pyproject.toml` | pytest config |
| CREATE | `tests/conftest.py` | Shared fixtures |
| CREATE | `tests/test_registry.py` | 6 Unit-Tests Registry |
| CREATE | `tests/test_runtime.py` | 5 Unit-Tests Runtime Init |
| CREATE | `tests/test_tools_filesystem.py` | 4 Tests (inkl. Path Traversal Security) |
| CREATE | `tests/test_tools_llm.py` | 2 Tests (list_models, token_budget) |
| CREATE | `tests/test_integration.py` | 2 Integration-Tests (LLM tick, completion) |
| MODIFY | `README.md` | Tool-Tree aktualisiert (13 Tools) |
| FIX | `WORKSPACE/WORKING/LOGS/` | loop_monitor Log-Pfad korrigiert |

---

## Decisions

| # | Entscheidung | Begründung |
|---|-------------|------------|
| D1 | pytest + pytest-asyncio als Test-Framework | Standard, async-support, Marker für integration/slow |
| D2 | Unit-Tests ohne LLM, Integration-Tests mit LLM getrennt | Schnelle Unit-Tests (2s), langsame Integration (45s) separat |
| D3 | Path Traversal als Security-Test | Filesystem-Tools blockieren korrekt mit PermissionError |
| D4 | Single Tick braucht ~48s mit qwen3-coder-30b | Groß aber funktional, kleineres Modell für Speed möglich |

---

## Erkenntnisse

### Runtime-Status
- **Voll funktional**: Ein Tick durchläuft Identity → Context → Plan → Execute → Observe → Reflect
- **13 Tools** alle registriert und getestet
- **reflect.py** ist KEIN Stub — hat echte LLM-basierte Reflection mit Retry-Logik
- **Security**: Path Traversal Protection funktioniert
- **Encoding-Bug**: Plan-Ausgabe zeigt `▄berpr³fe` statt `Überprüfe` (Console-Encoding)

### Offene Lücken
1. **Body-Access-Migration** (session.py, workpaper.py, ltm.py, context.py → Registry-Tools)
2. **Dashboard :8080** nicht aktiv (Dashboard-Code existiert, muss gestartet werden)
3. **8 offene Workpapers** in WORKPAPER/ — einige davon evtl. veraltet

### Nächstes mächtiges Tool — Konzept
Was fehlt am meisten: ein **Workspace Health / Self-Diagnostic Tool** das:
- AAMS-Zustand prüft (offene WP, veraltete WP, MEMORY-Sync, Diary-Aktualität)
- Runtime-Health merged mit AAMS-Health
- Whitepapers auf Konsistenz prüft (Tool-Counts, Versionen, Cross-References)
- Actionable Empfehlungen generiert ("WP X schließen", "WH-CORE updaten")

---

## Next Steps

- [x] Git commit + push
- [x] README prüfen + aktualisieren
- [x] Runtime end-to-end getestet (Single Tick: 48s, 5/5 Steps OK)
- [x] pytest Grundgerüst (17 Unit + 2 Integration = 19 Tests, alle grün)
- [ ] Workspace Health Tool implementieren
- [ ] Offene Workpapers reviewen + ggf. schließen
