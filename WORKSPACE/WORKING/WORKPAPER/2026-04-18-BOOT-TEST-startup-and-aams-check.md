---
title: "BOOT TEST — AAMS-Check & Startup / Test-Run"
workpaper_id: WP-BOOT-TEST-2026-04-18
date: 2026-04-18
status: OPEN
topic: BOOT
subtopic: TEST
related_whitepapers: [CORE.md, TOOLS.md, WORKING.md]
file_protocol:
  read: [.agent.json, READ-AGENT.md, WORKSPACE/WORKING/MEMORY/ltm-index.md, core/runtime.py, dashboard/app.py, requirements.txt, config/default.yaml]
  changed: [dieses Workpaper]
---

# WP: BOOT TEST — AAMS-Check & Startup / Test-Run

## §1 Session-Ziel

- AAMS-Compliance verifizieren (returning session → on_session_start)
- MantisClaw vollständig starten: Runtime + Dashboard
- Test-Suite ausführen
- Befunde dokumentieren

---

## §2 AAMS on_session_start — Status

| Schritt | Status | Notiz |
|---------|--------|-------|
| 1. READ-AGENT.md gelesen | ✅ | Vollständig |
| 2. Memory abgefragt (LTM) | ✅ | ltm-index.md gelesen |
| 3. RFL TOPIC-Tag bestimmt | ✅ | BOOT+TEST — kein Konflikt |
| 4. Workpaper erstellt | ✅ | Dieses Dokument |

### AAMS Workspace-Compliance

| Element | Status | Notiz |
|---------|--------|-------|
| `.agent.json` AAMS/1.3.0 | ✅ | Vorhanden |
| `READ-AGENT.md` | ✅ | Vorhanden |
| `WORKSPACE/WORKING/WHITEPAPER/` | ✅ | 7 Dokumente |
| `WORKSPACE/WORKING/WORKPAPER/` | ✅ | 9 aktive + closed/ |
| `WORKSPACE/WORKING/MEMORY/ltm-index.md` | ✅ | Befüllt |
| `WORKSPACE/WORKING/DIARY/2026-04.md` | ✅ | 18+ Einträge |
| `WORKSPACE/WORKING/LOGS/` | ✅ | Vorhanden |
| `WORKSPACE/WORKING/GUIDELINES/` | ✅ | 2 Guidelines |
| `WORKSPACE/WORKING/TOOLS/` | ✅ | Vorhanden |
| `WORKSPACE/WORKING/AGENT-MEMORY/` | ✅ | Vorhanden |
| Secrets Policy | ✅ | Keine Secrets in WPs |
| ⚠️ WP `2026-05-15-Skills-and-Tools.md` | ⚠️ | Future-dated (2026-05 statt 04) |

### RFL Consistency Check
Kein Konflikt erkannt. TOOLS/Skills-Workpaper ist future-dated, aber inhaltlich konsistent mit TOOLS.md Whitepaper.

---

## §3 Test-Ergebnisse

| Test | Status |
|------|--------|
| test_registry_* (6) | ✅ PASSED |
| test_runtime_* (5) | ✅ PASSED |
| test_tools_filesystem_* (4) | ✅ PASSED |
| test_tools_llm_* (2) | ✅ PASSED |
| test_integration::test_single_tick | ⚠️ SKIP — LM Studio nicht gestartet |
| test_integration::test_llm_simple_completion | ⚠️ SKIP — LM Studio nicht gestartet |

**Gesamt: 17/19 PASSED, 2 erwartet fehlgeschlagen (LM Studio not running)**

Die 2 Failures sind keine Code-Fehler — die Integration-Tests prüfen `check_connection()` und erfordern einen laufenden LM Studio Server auf localhost:1234.

---

## §4 Startup-Befunde

| Komponente | Status | Detail |
|------------|--------|--------|
| Python 3.10.11 | ✅ | venv aktiv |
| Dependencies | ✅ | Alle Requirements installiert |
| Dashboard (uvicorn) | ✅ | http://0.0.0.0:7860, 45KB HTML |
| Runtime (python -m core) | ℹ️ | Startet, benötigt LM Studio |

**Dashboard** läuft auf Port 7860. Startup-Zeit < 2s.
**Runtime-Loop** kann ohne LM Studio gestartet werden (läuft, aber LLM-Calls schlagen fehl).

---

## §5 Next Steps

- Wenn LM Studio gestartet → Integration-Tests erneut laufen: `pytest tests/test_integration.py -v`
- Skills & Tools Workpaper (2026-05-15) hat falsches Datum → bei Gelegenheit korrigieren/schließen
- Dashboard: http://localhost:7860 im Browser öffnen für UI-Test

---

## §6 File Protocol

| Aktion | Datei |
|--------|-------|
| READ | .agent.json |
| READ | READ-AGENT.md |
| READ | WORKSPACE/WORKING/MEMORY/ltm-index.md |
| READ | core/runtime.py, dashboard/app.py, requirements.txt, config/default.yaml |
| CREATED | WORKSPACE/WORKING/WORKPAPER/2026-04-18-BOOT-TEST-startup-and-aams-check.md |
