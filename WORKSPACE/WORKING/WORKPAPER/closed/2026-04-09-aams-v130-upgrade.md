# WP — AAMS v1.3.0 Upgrade: Diary Reform + Version Centralization

**Erstellt:** 2026-04-09  
**Status:** CLOSED
**Geschlossen:** 2026-04-10  
**Autor:** ogerly (Mensch) + GitHub Copilot (Agent)  
**Kontext:** AAMS v1.3.0 Release übernehmen — Diary Reform + Version Centralization

---

## Session Goal

MantisClaw auf AAMS v1.3.0 aktualisieren:
- **Diary Reform:** Pointer-only temporal index statt Content-Duplikation
- **Version Centralization:** `AAMS_VERSION` als Single Source of Truth
- Workpaper-Naming, RFL in session_start, Wissenskette in session_end

**Quelle:** https://github.com/DEVmatrose/AAMS/releases/tag/v1.3.0

---

## Änderungen (AAMS v1.3.0 → MantisClaw)

### 1. Diary Reform

**Vorher (MantisClaw):** Diary mit vollständigen Einträgen, "max 10 Zeilen pro Eintrag"
**Nachher (v1.3.0):** Pointer-only Format — eine Zeile pro Session:
```
YYYY-MM-DD | WP: {workpaper} | WH: {whitepaper} | {other files}
```

Hierarchische Kompression: Daily → Weekly Rollup → Monthly Summary (429 Einträge/Jahr max)

### 2. Version Centralization

`AAMS_VERSION=1.3.0` in `.env` als Single Source of Truth.

### 3. .agent.json Updates

- Diary-Beschreibung: "Temporal index layer. Pointer-only..."
- Diary-Format: explizit definiert
- Workpaper-Naming: `{DATE}-{TOPIC}-{SUBTOPIC}-{description}.md`
- `on_session_start`: RFL-Step hinzugefügt
- `on_session_end`: Wissenskette WP → WH → LTM explizit

---

## Entscheidungen

- **D1:** Diary `2026-04.md` wird auf Pointer-Format umgebaut — bestehende Einträge komprimiert
- **D2:** AAMS_VERSION kommt in `config/.env.example` (MantisClaw hat kein .env aktuell)
- **D3:** Workpaper-Naming-Konvention übernehmen, aber bestehende WPs nicht umbenennen (`_deviations`)

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| CREATE | `WORKPAPER/2026-04-09-aams-v130-upgrade.md` | Dieses Workpaper |
| EDIT   | `.agent.json` | Diary-Section, Naming, session_start/end |
| EDIT   | `WORKSPACE/WORKING/DIARY/2026-04.md` | Pointer-only Format |
| EDIT   | `config/.env.example` | AAMS_VERSION=1.3.0 |
| EDIT   | `READ-AGENT.md` | Diary-Beschreibung aktualisieren |
| EDIT   | `WORKSPACE/WORKING/WHITEPAPER/WORKING.md` | Diary-Referenz aktualisieren |

---

## Next Steps

- [x] Workpaper anlegen
- [x] .agent.json auf v1.3.0 aktualisieren
- [x] Diary reformatieren
- [x] AAMS_VERSION in config
- [x] READ-AGENT.md + WH-WORKING aktualisieren

---

*Workpaper. Wird bei Session-Close archiviert.*

