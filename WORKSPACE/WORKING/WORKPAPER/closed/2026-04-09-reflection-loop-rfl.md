# Workpaper: Reflection-Loop — Observer→Planner Rückkanal

- **Datum:** 2026-04-09
- **Agent:** GitHub Copilot (Claude Opus 4.6)
- **Status:** CLOSED
**Geschlossen:** 2026-04-10
- **Bezug:** SCIENCE Review `2026-04-09-mantisclaw-vs-state-of-the-art-review.md` — Hypothese H3
- **Priorität:** Hoch

---

## Session Goal

Den fehlenden **Reflection-Loop** in MantisClaw formalisieren: Observer findet Problem → Planner revidiert → neuer Versuch. Der Loop wird dadurch selbstkorrigierend.

---

## 1. Das Problem

### Aktueller Loop (CORE.md §4.1)

```
TICK: Session → Identity → Hooks → Planner → Executor → Observer → LTM → Sleep
                                      ↓                      ↓
                                    Plan                   Bewertung
```

Der Datenfluss ist **linear**. Observer bewertet das Ergebnis, meldet Anomalien, aktualisiert Metriken — aber **es gibt keinen Rückkanal zum Planner**.

### Was das bedeutet

Wenn der Executor einen Plan ausführt und der Observer feststellt dass das Ergebnis schlecht ist, passiert:
- ❌ Der Agent wartet auf den nächsten Tick
- ❌ Der nächste Tick startet mit frischem Plan — ohne explizites Wissen über den Fehler
- ❌ Zwischen Observer-Erkenntnis und Planner-Korrektur liegt ein ganzer Tick

### Was passieren sollte

```
Observer: "Ergebnis ist unvollständig — 3 von 5 Tests fehlgeschlagen"
    ↓
Reflection: "Ursache: Planner hat Edge-Cases ignoriert. Korrektur: Tests zuerst lesen."
    ↓
Planner: Revidierter Plan mit Edge-Case-Behandlung
    ↓
Executor: Zweiter Versuch
```

---

## 2. State of the Art: Reflexion in Agent-Loops

### Das Forschungsfeld

Alle drei Quellen aus der SCIENCE-Recherche bestätigen:

> **"Ideal Agent = Global Planning (Plan) + Flexible Execution (ReAct) + Continuous Optimization (Reflexion)"** — Kimi

Reflexion ist der dritte Pfeiler neben Planning und Execution. MantisClaw hat die ersten zwei, aber nicht den dritten.

### Wie andere Frameworks es lösen

| Framework | Reflexion-Ansatz |
|-----------|-----------------|
| **Reflexion (Shinn et al.)** | Expliziter Self-Reflection-Step nach Fehler. Agent schreibt Reflexion in Memory. |
| **Claude Code** | Auto-Retry bei Tool-Fehlern. Kein expliziter Reflexion-Step. |
| **LangChain ReAct** | Observe-Schritt nach jeder Aktion. Kann Strategie ändern. |
| **LATS (Language Agent Tree Search)** | Baumsuche mit Backtracking bei schlechten Ergebnissen. |

### Was MantisClaw anders machen kann

Wir brauchen keine neue Architektur. Wir brauchen einen **Rückkanal** im bestehenden Loop.

---

## 3. Design: RFL (Reflection) als Loop-Schritt

### 3.1 Angepasster Tick-Cycle

```
TICK START
│
├── 1. Session prüfen
├── 2. Identity laden → soul(t)
├── 3. Hooks prüfen
├── 4. Planner → Plan
├── 5. Executor → Results
├── 6. Observer → Bewertung
│
├── 7. RFL (Reflection) ← NEU
│   ├── Bewertung OK? → weiter zu 8.
│   └── Bewertung NICHT OK?
│       ├── Reflection: Ursache analysieren
│       ├── Planner: Plan revidieren (mit Reflection-Context)
│       └── Executor: Zweiter Versuch
│       └── Observer: Erneute Bewertung
│           └── Max-Retries erreicht? → weiter zu 8. mit Warnung
│
├── 8. LTM updaten
└── 9. Sleep
```

### 3.2 Reflection im Code

```python
# In runtime.py — angepasster Tick
async def tick():
    soul_t = compute_soul(...)
    plan = planner(soul_t, hooks, memory, guidelines)
    results = executor(plan)
    assessment = observer(results, diary, guidelines)
    
    # NEU: Reflection-Loop
    retries = 0
    while assessment.needs_revision and retries < max_reflection_retries:
        reflection = reflect(assessment, results, plan)
        # reflection enthält: was ging schief, warum, was anders machen
        
        revised_plan = planner(soul_t, hooks, memory, guidelines, 
                               reflection_context=reflection)
        results = executor(revised_plan)
        assessment = observer(results, diary, guidelines)
        retries += 1
    
    if retries > 0:
        diary.log(f"Reflection: {retries} Revisionen nötig. Letzte: {reflection}")
    
    ltm_update(results, assessment)
```

### 3.3 Die reflect()-Funktion

```python
def reflect(assessment, results, original_plan):
    """
    Analysiert warum ein Plan gescheitert ist.
    
    Input:  Observer-Bewertung + Ergebnisse + ursprünglicher Plan
    Output: Reflection-Context für den Planner
    
    Enthält:
    - was_wrong: Was hat nicht funktioniert?
    - why_wrong: Warum? (Ursachenanalyse)
    - correction: Was sollte der Planner anders machen?
    - confidence: Wie sicher ist die Analyse? (0.0–1.0)
    """
    return llm.reflect(
        system="Du analysierst warum ein Plan gescheitert ist.",
        context={
            "plan": original_plan,
            "results": results,
            "assessment": assessment,
            "guidelines": load_relevant_guidelines(original_plan.task_type)
        }
    )
```

---

## 4. Observer-Bewertung: Wann wird reflektiert?

Nicht jedes Ergebnis braucht Reflexion. Der Observer entscheidet:

| Bewertung | Aktion |
|-----------|--------|
| `OK` — Ergebnis wie erwartet | Kein RFL. Weiter. |
| `PARTIAL` — Teilweise erfolgreich | RFL optional. Planner entscheidet. |
| `FAILED` — Plan gescheitert | RFL verpflichtend. Reflection-Loop startet. |
| `ANOMALY` — Unerwartetes Ergebnis | RFL verpflichtend. Könnte Architektur-Problem sein. |

### assessment.needs_revision

```python
class Assessment:
    status: str          # OK | PARTIAL | FAILED | ANOMALY
    needs_revision: bool # True wenn FAILED oder ANOMALY
    details: str         # Was genau passiert ist
    metrics: dict        # Quantitative Bewertung
```

---

## 5. Grenzen: Max-Retries und Eskalation

Reflexion darf nicht endlos laufen.

```yaml
# In config/default.yaml
reflection:
  max_retries: 2          # Maximal 2 Revisionen pro Tick
  escalate_after: 2       # Nach 2 gescheiterten Reflexionen → Diary-Eintrag + nächster Tick
  cooldown_ticks: 3       # Nach Eskalation: 3 Ticks ohne Reflexion (Anti-Loop-Schutz)
```

### Eskalationspfad

```
Versuch 1: Plan → Fail → Reflect → Revidierter Plan
Versuch 2: Revidierter Plan → Fail → Reflect → Zweite Revision
Versuch 3: Zweite Revision → Fail → ESKALATION
    → Diary: "Task X nach 2 Reflexionen gescheitert. Mögliche Ursache: [...]"
    → Nächster Tick mit frischem Kontext
    → Optional: Menschliche Intervention empfehlen
```

---

## 6. Zusammenspiel mit Procedural Memory

Reflexion und Procedural Memory (GUIDELINES/) ergänzen sich:

```
Reflexion = Kurzfristig: "Dieser Plan hat nicht funktioniert, versuch es anders"
Procedural = Langfristig: "Bei diesem Task-Typ funktioniert Strategie X generell besser"
```

Der Datenfluss:

```
Observer → Reflection (innerhalb des Ticks, kurzfristig)
Observer → GUIDELINES/ (nach dem Tick, langfristig)
```

Reflexion ist das **Arbeitsgedächtnis** für Korrekturen. GUIDELINES/ ist das **Langzeitgedächtnis** für Lektionen.

---

## 7. Auswirkung auf den Tick-Cycle

### Zeitliche Auswirkung

Ein Tick ohne Reflexion: ~10s (heartbeat_interval)
Ein Tick mit Reflexion (1 Retry): ~20-30s (Plan + Execute + Observe × 2 + Reflect)
Ein Tick mit Eskalation (2 Retries): ~40-50s

### Config-Anpassung

```yaml
# session_timeout muss Reflexion berücksichtigen
session_timeout: 3600s    # unverändert — Reflexion ist innerhalb des Ticks
heartbeat_interval: 10s   # unverändert — gilt für Ticks OHNE Reflexion
```

---

## 8. Entscheidungen

| # | Entscheidung | Begründung |
|---|-------------|-----------|
| D1 | RFL ist ein Schritt innerhalb des Ticks, kein eigener Tick | Reflexion muss sofort korrigieren, nicht erst beim nächsten Heartbeat |
| D2 | Max 2 Retries, dann Eskalation | Verhindert Endlos-Loops. 2 Versuche reichen für die meisten Korrekturen. |
| D3 | Observer entscheidet ob Reflexion nötig (needs_revision) | Observer hat die Bewertungs-Kompetenz. Planner soll planen, nicht bewerten. |
| D4 | Reflexion nutzt LLM (reflect-Prompt) | Ursachenanalyse braucht Reasoning — das ist ein LLM-Job. |
| D5 | Reflexion wird in Diary geloggt | Audit-Trail. Nachvollziehbar warum der Agent seinen Plan geändert hat. |
| D6 | Cooldown nach Eskalation (3 Ticks) | Anti-Pattern: Agent der ständig reflektiert statt zu arbeiten. |

---

## 9. Next Steps

- [ ] CORE.md §4.1 (Tick-Cycle) um RFL-Schritt erweitern
- [ ] Observer-Spec: `needs_revision` und Assessment-Klasse definieren
- [ ] reflect()-Funktion spezifizieren
- [ ] config/default.yaml: reflection-Config anlegen
- [ ] Diary-Format für Reflexions-Einträge definieren

---

## File Protocol

| # | Aktion | Datei | Beschreibung |
|---|--------|-------|-------------|
| F1 | CREATED | `WORKPAPER/2026-04-09-reflection-loop-rfl.md` | Dieses Workpaper |

---

> **Reflexion macht den Unterschied zwischen einem Agenten der scheitert und einem der aus Scheitern lernt — innerhalb desselben Ticks.**

