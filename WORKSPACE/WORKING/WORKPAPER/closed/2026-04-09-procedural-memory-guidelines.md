# Workpaper: Procedural Memory — GUIDELINES/ als lernbare Arbeitsweise

- **Datum:** 2026-04-09
- **Agent:** GitHub Copilot (Claude Opus 4.6)
- **Status:** CLOSED
**Geschlossen:** 2026-04-10
- **Bezug:** SCIENCE Review `2026-04-09-mantisclaw-vs-state-of-the-art-review.md` — Hypothese H1
- **Priorität:** Hoch

---

## Session Goal

GUIDELINES/ als **Procedural Memory** in MantisClaw's Agent-Loop integrieren. Der Agent soll seine eigenen Arbeitsrichtlinien nicht nur lesen, sondern aktiv schreiben und aktualisieren können — basierend auf Erfahrungen aus dem Loop.

---

## 1. Das Problem

### Was Procedural Memory ist

Procedural Memory = **"Wie arbeite ich?"** — der Agent lernt aus Erfahrung, welche Strategien funktionieren und welche nicht. In der Cognitive-Science-Taxonomie (CoALA/Princeton) ist das der vierte Memory-Typ neben Working, Episodic und Semantic.

### Was MantisClaw heute hat

MantisClaw hat drei Memory-Typen implizit abgedeckt:

| CoALA-Typ | MantisClaw-Äquivalent | Status |
|-----------|----------------------|--------|
| Working Memory | Workpaper (aktuelle Session) | ✅ Vorhanden |
| Episodic Memory | Diary (Entscheidungs-Kontext) | ✅ Vorhanden |
| Semantic Memory | LTM / Memory (ltm-index.md) | ✅ Vorhanden |
| **Procedural Memory** | **???** | ❌ Fehlt explizit |

### Was fehlt

Der Agent kann heute **nicht** sagen:
- "Letzte Woche hat Strategie X bei ähnlichen Tasks versagt — ich versuche Y"
- "Bei Python-Projekten funktioniert es besser, Tests vor Code zu schreiben"
- "Dieser User bevorzugt kurze Antworten"

---

## 2. Die Hypothese: GUIDELINES/ ist bereits Procedural Memory

`WORKSPACE/WORKING/GUIDELINES/` existiert bereits in der AAMS-Struktur. Aktuell: leer (nur `.gitkeep`).

**Hypothese H1:** Wenn der Agent GUIDELINES/ aktiv **lesen UND schreiben** kann, hat MantisClaw implizit Procedural Memory.

### Warum das funktioniert

GUIDELINES als Procedural Memory passt weil:
- **Dateibasiert** — konsistent mit "Files are all you need"
- **Bereits im Workspace** — keine neue Struktur nötig
- **Human-editable** — Owner kann Richtlinien korrigieren
- **Versionierbar** — Git trackt Änderungen an Arbeitsweisen
- **Kontextabhängig** — verschiedene Guidelines für verschiedene Agenden

### Was sich ändert

| Aspekt | Heute | Mit Procedural Memory |
|--------|-------|----------------------|
| GUIDELINES/ | Leer, statisch | Wächst mit Erfahrung |
| Observer | Meldet Anomalien | Meldet Anomalien **+ extrahiert Lektionen** |
| Planner | Liest Hooks + Memory | Liest Hooks + Memory **+ GUIDELINES/** |
| soul(t) | working_context enthält WP/WH/LTM | working_context enthält WP/WH/LTM **+ GUIDELINES/** |

---

## 3. Integration in den Loop

### 3.1 Observer → GUIDELINES (Schreiben)

Der Observer bekommt eine neue Fähigkeit: **Lektionen extrahieren**.

> **Update (WH-TOOLS):** Der Observer schreibt nicht direkt in GUIDELINES/ — er erzeugt eine Tool-Action, die der Executor über die Registry ausführt. Körper-Zugriff (L2) nur über Tools (L4).

```python
# In observer.py
def observe(results, diary, guidelines):
    anomalies = check_anomalies(results)
    metrics = update_metrics(results)
    
    # NEU: Procedural Memory Update (über Tool-Registry)
    if results.has_lessons():
        lesson = extract_lesson(results)
        # Observer erzeugt Action, Executor führt über Registry aus:
        return Action(type="tool", name="write_guidelines",
                      params={"lesson": lesson, "category": results.task_type})
```

### 3.2 Planner → GUIDELINES (Lesen)

Der Planner liest GUIDELINES/ als Teil der Planungsphase:

```python
# In planner.py  
def plan(soul_t, hooks, memory, guidelines):
    # Guidelines filtern nach aktuellem Task-Typ
    relevant_guidelines = guidelines.query(soul_t.agenda.current_task_type)
    
    # Plan erstellen MIT Erfahrungswissen
    plan = llm.plan(soul_t, hooks, memory, relevant_guidelines)
    return plan
```

### 3.3 GUIDELINES-Dateiformat

Einfach. Markdown. Eine Datei pro Kategorie:

```markdown
# GUIDELINE: {category}

- **Erstellt:** {date}
- **Letzte Aktualisierung:** {date}
- **Quelle:** Observer-Extraktion aus Workpapers

## Regeln

- [{date}] Bei Python-Refactors: Tests zuerst prüfen, dann Code ändern
  → Quelle: WP-2026-04-09 (3 fehlgeschlagene Versuche ohne Tests)
  
- [{date}] Bei Markdown-Edits: Immer Kontext lesen vor Replace
  → Quelle: WP-2026-04-08 (falsches oldString ohne Kontext)
```

### 3.4 Lifecycle

```
1. Agent arbeitet (Executor)
2. Observer bewertet Ergebnis
3. Observer extrahiert Lektion (wenn relevant)
4. Lektion wird in GUIDELINES/{category}.md geschrieben
5. Nächster Tick: Planner liest relevante Guidelines
6. Plan wird informierter
```

---

## 4. Abgrenzung

| Das ist Procedural Memory | Das ist es NICHT |
|--------------------------|-----------------|
| "Bei Task-Typ X funktioniert Strategie Y besser" | Logging von Aktionen (→ DIARY) |
| "Dieser Codebase-Typ braucht immer Tests zuerst" | Fakten über das Projekt (→ LTM) |
| "User bevorzugt deutsche Antworten" | Aufgaben-Status (→ WORKPAPER) |
| "Retry mit anderem Prompt bei LLM-Fehler" | Architektur-Entscheidungen (→ WHITEPAPER) |

---

## 5. Auswirkung auf soul(t)

```
# Vorher:
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)

# Nachher (working_context erweitert):
working_context = whitepapers + workpapers + ltm + guidelines
                                                    ^^^^^^^^
                                                    NEU: Procedural Memory
```

Die Soul emergiert jetzt mit Erfahrungswissen. Ein Agent der 50 Coding-Sessions hatte, arbeitet **anders** als ein frischer Agent — weil seine GUIDELINES/ gewachsen sind.

---

## 6. Risiken

| Risiko | Mitigation |
|--------|-----------|
| Guidelines-Inflation — zu viele Regeln | Max-Regeln pro Kategorie. Observer konsolidiert periodisch. |
| Falsche Lektionen — Agent lernt Falsches | Human-editable. Owner kann korrigieren. Guidelines sind Markdown, kein Black-Box-Modell. |
| Konflikte — Guideline widerspricht Whitepaper | Whitepaper hat Vorrang (Architektur-Wahrheit > Erfahrungswert). |

---

## 7. Entscheidungen

| # | Entscheidung | Begründung |
|---|-------------|-----------|
| D1 | GUIDELINES/ wird als Procedural Memory definiert | Existiert bereits, passt konzeptionell, keine neue Struktur nötig |
| D2 | Observer extrahiert Lektionen, Planner liest sie | Natürlicher Datenfluss im bestehenden Loop |
| D3 | Eine Datei pro Kategorie, nicht pro Lektion | Verhindert File-Explosion. Konsolidierung statt Akkumulation. |
| D4 | Whitepaper > Guideline bei Konflikten | Architektur-Wahrheit ist stabiler als Erfahrungswerte |

---

## 8. Next Steps

- [ ] CORE.md aktualisieren: GUIDELINES/ als Procedural Memory definieren
- [ ] Observer-Spec erweitern: Lektions-Extraktion (über Tool-Action `write_guidelines`)
- [ ] Planner-Spec erweitern: Guidelines-Query (über Tool `read_guidelines`)
- [ ] Erste Guideline-Datei anlegen: `GUIDELINES/coding.md` oder `GUIDELINES/session.md`
- [ ] Schichtenmodell in CORE.md ergänzen: 4 Memory-Typen explizit benennen
- [ ] `write_guidelines` und `read_guidelines` als workspace-Tools in Registry registrieren (WH-TOOLS §3.3)

---

## File Protocol

| # | Aktion | Datei | Beschreibung |
|---|--------|-------|-------------|
| F1 | CREATED | `WORKPAPER/2026-04-09-procedural-memory-guidelines.md` | Dieses Workpaper |

---

> **GUIDELINES/ ist keine leere Konvention — es ist der Ort wo der Agent lernt, wie er arbeitet.**

