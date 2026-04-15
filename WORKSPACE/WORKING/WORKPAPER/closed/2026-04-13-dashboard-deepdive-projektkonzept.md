# Workpaper — Dashboard Deep-Dive & Projekt-Konzept

**Erstellt:** 2026-04-13
**Status:** CLOSED
**Geschlossen:** 2026-04-13
**Agent:** copilot
**Project:** mantisclaw-core

---

## Session Goal

Dashboard für Entwickler-Kontrolle ausbauen (Identity Inspector, Prompt Inspector)
und Projekt-Konzept klären: Wie verhält sich MantisClaw Core vs. externe Projekte?

---

## Erkenntnisse aus der Session

### 1. Dashboard zeigt zu wenig inneres Leben

**Problem:** Das Dashboard zeigt nur Oberfläche — Name, Owner, soul(t)-Formel.
Aber was tatsächlich im `base.md`, `agenda.md`, `account.md` steht, ist nicht einsehbar.
Ebenso: Was der Planner als System-Prompt + User-Prompt rausschickt, ist unsichtbar.

**Entscheidung:** Zwei neue Inspektoren einbauen:
- 🧬 **Identity Inspector** — alle Identity-Dateien (base.md, agenda.md, account.md, social.md, decentral.md) als Read-Only-Tabs
- 🔍 **Prompt Inspector** — letzte N Planner-Prompts (System + User + Response) chronologisch

**Umsetzung:**
- `core/planner.py`: Prompt-Logging nach `LOGS/prompt_log.jsonl` (JSONL, ein Entry pro Plan-Call)
- `dashboard/app.py`: `/api/identity` (alle Identity-Files + soul(t) Felder) + `/api/logs/prompts` (letzte N Entries)
- `dashboard/templates/index.html`: Zwei Modal-Panels mit Click-to-open
- `dashboard/static/style.css`: Modal-Overlay + Tab-System + Prompt-Entry-Styles

### 2. Planner-Prompt muss nachvollziehbar sein

**Erkenntnis:** Ohne den exakten Prompt zu sehen, können wir nicht beurteilen ob der Agent sinnvoll plant.
Besonders wichtig:
- Sieht der Planner die richtigen Tools?
- Wird das aktive Projekt korrekt injiziert?
- Wie sieht der Memory-Context aus den der Agent bekommt?
- Wie viele Tokens gehen rein / kommen raus?

**Entscheidung:** Jeder `planner.plan()` Call loggt System+User+Response als JSONL-Zeile.
Runtime setzt den Pfad via `set_prompt_log_path()` beim Init.

### 3. TestProjekt1 — erstes externes Testprojekt

**Entscheidung:** Neues Projekt `testprojekt1` im PROJECT-Ordner angelegt.
Ziel: Validieren dass MantisClaw mit mehreren Projekten umgehen kann.

**Datei:** `WORKSPACE/WORKING/PROJECT/testprojekt1/project.yaml`
- Status: active
- Goals: Projekt-Isolation validieren, Agent arbeitet im Scope, Dashboard zeigt korrekt an
- 3 Milestones (1 done, 2 open)

**Achtung:** `_active.yaml` zeigt weiterhin auf `mantisclaw-core`.
TestProjekt1 ist angelegt, aber noch nicht "aktiviert" — wir wollen erstmal beides sehen.

### 4. Konzept: MantisClaw Core ≠ Projekt

**Erkenntnis (Userdiskussion):**

> MantisClaw Core ist KEIN normales Projekt. Wir sind die Ausnahme — wir bauen das Framework selbst.
> Ein normaler User installiert MantisClaw und öffnet dann ein externes Projekt (Ordner/GitHub-Repo).
> Die Projektoberfläche wäre für den normalen User leer beim Start.

**Implikationen:**
- MantisClaw Core als "Meta-Projekt" behandeln — Sonderfall für Entwickler
- Ein reguläres Projekt = externer Ordner/Repo, das der Agent analysiert + bearbeitet
- Jedes Projekt hat eigene Workpapers, Whitepapers, Chat-History, eigener Projektordner in AAMS
- MantisClaw-Runtime (Planner, Executor, RFL, Tools) bleibt gleich — nur der Scope wechselt
- Es wäre zu überlegen: AAMS direkt ins Projekt-Repo integrieren (späterer Schritt)

**Offene Fragen:**
- [ ] Soll _active.yaml mehrere Projekte erlauben oder strikt 1-aktiv?
- [ ] Projekt anlegen: per Dashboard-Button (Ordner wählen / GitHub-URL) oder nur CLI/Agent?
- [ ] Eigene WP/WH pro Projekt — im AAMS-Ordner oder im Projekt-Repo selbst?
- [ ] Projekt-Wechsel: Was passiert mit laufenden Workpapers?

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| MODIFIED | core/planner.py | Prompt-Logging (JSONL) + set_prompt_log_path() |
| MODIFIED | core/runtime.py | Import set_prompt_log_path, Pfad setzen bei Init |
| MODIFIED | dashboard/app.py | /api/identity + /api/logs/prompts Endpoints |
| MODIFIED | dashboard/templates/index.html | Identity Inspector Modal + Prompt Inspector Modal + JS |
| MODIFIED | dashboard/static/style.css | Modal + Inspector CSS |
| CREATED | WORKSPACE/WORKING/PROJECT/testprojekt1/project.yaml | Testprojekt |
| CREATED | WORKSPACE/WORKING/WORKPAPER/2026-04-13-MCP-integration-research.md | MCP-Forschung (separates WP) |

---

## Decisions Log

| # | Entscheidung | Begründung |
|---|-------------|------------|
| D1 | Identity-Files read-only im Dashboard | Editieren nicht nötig für jetzt, Einsicht reicht |
| D2 | Prompt-Logging als JSONL | Append-only, leicht parsbar, keine DB nötig |
| D3 | TestProjekt1 ohne Aktivierung | Erstmal Struktur validieren, kein Scope-Switch nötig |
| D4 | MantisClaw Core ≠ normales Projekt | Core ist Sonderfall, reguläre Projekte sind extern |
| D5 | MCP als separates Workpaper | Überschneidet nicht direkt mit Dashboard-Arbeit |

---

## Ergebnisse

- [x] Dashboard UI: Identity Inspector + Prompt Inspector funktional
- [x] Runtime 10+ Ticks: Alle 5/5 Steps OK, Prompts sichtbar im Inspector
- [x] Dashboard Layout vollständig umgebaut (L1-L4 left, R1-R4 right)
- [x] Live Tick Feed + `/api/runtime/ticks` Endpoint
- [x] Runtime-Effizienz: Token-Limits (Planner 500, Analyze 300, Summarize 200)
- [x] Path-Fix: `_validate_path()` strippt halluzinierte WORKSPACE/-Prefixe
- [x] Planner VERBOTEN-Block + `<Warum>`-Fallback-Parsing
- [x] Idle Detection implementiert (skip nach 3 identischen Plänen)
- [x] TestProjekt1 angelegt
- [ ] Projekt-Wechsel im Dashboard designen (Dropdown? Sidebar?) → Folge-WP
- [ ] Konzept: Projekt = externer Ordner mit optionaler AAMS-Integration → Folge-WP

## Token-Reduktion (verifiziert via LM Studio Logs)

| Metrik | Vorher | Nachher |
|--------|--------|---------|
| Planner Tokens/Tick | ~2100 | ~284 |
| Analyze Tokens/Tick | unbegrenzt | max 300 |
| Summarize Tokens | unbegrenzt | max 200 |
| Gesamt/Tick | ~6000 | ~2500 |
| Pfad-Fehler | häufig | 0 |
