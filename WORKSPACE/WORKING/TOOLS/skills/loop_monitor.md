---
name: loop_monitor
version: 0.1.0
description: "Überwacht den Runtime-Loop auf Token-Effizienz, Format-Fehler und Anomalien"
requires_tools:
  - loop_monitor
  - token_budget
category: monitoring
trigger: manual
project: mantisclaw-core
max_retries: 0
---

# Skill: Loop Monitor

## Zweck

Validiert den Runtime-Loop auf:
- Token-Budget-Einhaltung (Planner ≤500, Analyze ≤300, Summarize ≤200)
- Planner-Format (GOAL/REASONING/STEP)
- Pfad-Korrektheit (WORKING/ statt WORKSPACE/)
- Plan-Wiederholungen (Hamster-Wheel Detection)
- LM Studio Erreichbarkeit

## Workflow

### Step 1: Health Check ausführen

```
tool: loop_monitor
target: full_check
params: {}
```

Ergebnis: Strukturierter Report mit Anomalien und RFL-Empfehlungen.

### Step 2: Token-Budget prüfen

```
tool: token_budget
target: show
params: {}
```

Ergebnis: Aktuelle Token-Limits und Empfehlungen.

### Step 3: Report auswerten

Report liegt in `WORKING/LOGS/loop_monitor_*.txt`.
Bei Anomalien → RFL-Feedback an Planner weitergeben.

## Wann einsetzen?

- Nach Code-Änderungen an Planner, Executor, oder Tool-Registrierung
- Regelmäßig nach 10+ Ticks zur Qualitätssicherung
- Bei Verdacht auf Token-Explosion oder Format-Regression
- Vor einem Commit: "Läuft der Loop sauber?"
