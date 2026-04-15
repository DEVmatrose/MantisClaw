# Workpaper — Workspace Health Diagnostic Tool

**Erstellt:** 2026-04-15
**Status:** OPEN
**Agent:** copilot
**Project:** mantisclaw-core

---

## Session Goal

Ein mächtiges Self-Diagnostic-Tool bauen das MantisClaw's gesamten Zustand
auf einen Blick erfassbar macht — und **actionable Empfehlungen** gibt.

**Warum:** Der AAMS-Workspace wächst. Manuell nachschauen ob Whitepapers aktuell sind,
ob Workpapers vergessen wurden, ob Memory-Einträge doppelt sind — das skaliert nicht.
Das Tool soll das automatisieren, was wir heute manuell in jeder Session machen.

---

## Was es können soll

### 1. AAMS Body Health
- **Workpaper-Status:** Wie viele offen / closed? Gibt es verwaiste (>7 Tage offen ohne Aktivität)?
- **Workpaper-Qualität:** Haben alle ein File Protocol, Decisions, Next Steps?
- **Duplikate in closed/:** Gleicher Name mehrfach?
- **Whitepaper-Versionen:** Welche Whitepapers existieren? Wann zuletzt aktualisiert?
- **Memory-Konsistenz:** Duplikate im LTM-Index? Lücken (geschlossene WPs ohne Ingest)?
- **Diary-Aktualität:** Wann war der letzte Diary-Eintrag? Lücken?
- **Guidelines:** Existieren sie? Werden sie referenziert?

### 2. Runtime Health
- **Tool-Registry:** Wie viele Tools registriert? Alle Module importierbar?
- **LLM-Backend:** Erreichbar? Welches Modell geladen?
- **Config-Konsistenz:** Stimmt config/default.yaml mit dem was läuft überein?
- **Dashboard:** Erreichbar auf :8080?

### 3. Code Health
- **Tests:** pytest discoverable? Wie viele? Letzte Ergebnisse?
- **Import-Check:** Alle core/ Module importierbar ohne Fehler?
- **Stale Code:** Dateien die nirgends importiert werden?

### 4. Cross-Reference Check
- **WH-CORE Tool-Count** vs. tatsächliche Registry-Tools
- **WH-TOOLS Struktur** vs. tatsächliche Dateistruktur in core/registry/tools/
- **README Tool-Tree** vs. tatsächliche Dateien
- **project.yaml Meilensteine** vs. offene Workpapers

---

## Design

### Tool-Typ: Python in `core/registry/tools/workspace_health.py`

**Registrierung:** Als Tool `workspace_health` (L1, read-only)

**Aufruf:** `workspace_health` — keine Parameter nötig. Scannt alles automatisch.

**Output-Format:**
```
=== MantisClaw Workspace Health Report ===
Zeitpunkt: 2026-04-15 14:00

📋 AAMS Body
  Workpapers: 4 offen, 25 geschlossen
  ⚠ 1 verwaist: umfeld-analyse.md (kein Datum, kein Status)
  Whitepapers: 5 (CORE v0.4.0, TOOLS v0.3.0, ...)
  Memory: 12 Einträge, 0 Duplikate
  Diary: Letzter Eintrag 2026-04-13

🔧 Runtime
  Tools: 14/14 registriert ✓
  LLM: lmstudio, qwen3-coder-30b erreichbar ✓
  Dashboard: :8080 nicht erreichbar ✗

🧪 Tests
  17 Unit + 2 Integration = 19 total
  Letzter Run: alle grün ✓

🔗 Cross-References
  ⚠ WH-CORE sagt 13 Tools, Registry hat 14
  ✓ README Tool-Tree aktuell

📌 Empfehlungen
  1. umfeld-analyse.md: AAMS-Header ergänzen oder archivieren
  2. Diary-Eintrag für heute fehlt
  3. Dashboard starten für volle Health-Prüfung
```

### Kein LLM-Call nötig
Rein filesystem-basierte Analyse. Kein Token-Verbrauch. Schnell (~1-2s).

### Report-Speicherung
Optional: Report nach `WORKSPACE/WORKING/LOGS/health_YYYYMMDD_HHMMSS.txt`

---

## Implementierungsplan

| Schritt | Was | Aufwand |
|---------|-----|---------|
| 1 | `workspace_health.py` Grundgerüst: AAMS Body Checks | Klein |
| 2 | Runtime Health (Registry, LLM, Config) | Klein |
| 3 | Cross-Reference Checks (WH vs. Reality) | Mittel |
| 4 | Code Health (pytest discovery, imports) | Klein |
| 5 | Report-Formatierung + Log-Speicherung | Klein |
| 6 | Registrierung in Runtime + Test | Klein |

---

## Abgrenzung

- **Nicht:** loop_monitor (der prüft Tick-Qualität zur Laufzeit)
- **Nicht:** Dashboard (das zeigt Live-Status)
- **Ist:** Statischer Snapshot des gesamten Workspace-Zustands

---

## Decisions

| # | Entscheidung | Begründung |
|---|-------------|------------|
| D1 | Kein LLM-Call | Reine Filesystem-Analyse, schnell, deterministisch |
| D2 | Ein einziger Tool-Aufruf | `workspace_health` — keine Parameter, scannt alles |
| D3 | Actionable Output | Nicht nur Status melden, sondern konkrete Empfehlungen |
| D4 | L1 Security Level | Read-only, keine Änderungen am Workspace |

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| CREATE | `core/registry/tools/workspace_health.py` | Haupt-Implementierung |
| MODIFY | `core/runtime.py` | Import + Registrierung |
| CREATE | `tests/test_tools_health.py` | Tests |
| MODIFY | `WORKSPACE/WORKING/WHITEPAPER/TOOLS.md` | Neues Tool dokumentieren |

---

## Next Steps

- [ ] `workspace_health.py` implementieren (Schritt 1-5)
- [ ] In Runtime registrieren
- [ ] Tests schreiben
- [ ] Whitepapers aktualisieren
- [ ] Erster Testlauf + Report prüfen
