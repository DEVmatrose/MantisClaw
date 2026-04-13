# Workpaper: SCIENCE — Knowledge Validation Layer für MantisClaw

- **Datum:** 2026-04-09
- **Agent:** GitHub Copilot (Claude Opus 4.6)
- **Status:** OPEN
- **Herkunft:** Ursprünglich als AAMS-Layer konzipiert und dort **verworfen** — AAMS wird keine SCIENCE-Layer-Ebene als Spec-Element mitgeben. SCIENCE ist rein MantisClaw.
- **Bezug:** `WORKSPACE/WORKING/SCIENCE/2026-04-09-Erkenntnisse und neuen Forschungsbereiche.md` (Research-Grundlage)

---

## Session Goal

SCIENCE als **Knowledge Validation Layer** in MantisClaw's Agent-Loop integrieren. Nicht als AAMS-Spec-Erweiterung, sondern als Framework-Feature — ein kognitiver Schritt im Loop, der besseres agentisches Arbeiten ermöglicht.

---

## 1. Warum SCIENCE in MantisClaw gehört (nicht in AAMS)

### Das Problem bei AAMS

AAMS ist ein **Workspace-Standard** — Ordnerstruktur, Naming, Audit-Trail. AAMS definiert *wo* Dateien liegen und *wie* sie heißen. AAMS definiert **nicht**, was ein Agent damit *tut*.

Ein Knowledge Validation Layer ist aber ein **kognitiver Prozess** — er braucht:
- LLM-Zugriff (für Analyse, Einordnung, Hypothesenbildung)
- Planner-Integration (wann wird validiert?)
- Observer-Feedback (was wurde gelernt?)

Das ist kein Ordner-Problem. Das ist ein **Agent-Loop-Problem**.

### Die Lösung: SCIENCE als MantisClaw-Feature

MantisClaw hat AAMS als Struktur fest integriert. Der `WORKING/SCIENCE/`-Ordner ist **kein AAMS-Spec-Element** — die Entscheidung wurde auf AAMS-Seite bewusst verworfen. SCIENCE ist rein MantisClaw: der Ordner und der Prozess gehören zum Framework, nicht zur Workspace-Spezifikation.

```
AAMS liefert: WORKING/ Struktur (Workpaper, Whitepaper, Diary, Memory, Guidelines, Tools)
MantisClaw ergänzt: WORKING/SCIENCE/ als eigenes Feature (kein AAMS-Element)
MantisClaw stellt: Den Prozess — wann, wie, warum dort geschrieben wird.
```

---

## 2. Was SCIENCE ist

> **SCIENCE = Science, Insights, Novelty, Context, Evidence**

Ein Framework-Feature das dem Agent ermöglicht:

1. **Erkenntnisse sammeln** — State of the Art zu einem Thema erfassen
2. **Annahmen validieren** — Stimmen unsere Architekturentscheidungen?
3. **Einordnen** — Wo stehen wir im Vergleich zur Forschung/Industrie?
4. **Hypothesen bilden** — Was könnten wir besser machen?

### SCIENCE ist nicht:

- ❌ Kein Logging (das ist DIARY)
- ❌ Keine Self-Reflection des Loops (das ist Observer + RFL)
- ❌ Kein Testing (das ist CI/CD)
- ❌ Kein Memory (das ist LTM)

### Analogie im MantisClaw-Kontext

> Workpaper = Was der Agent gerade tut. Whitepaper = Was das System ist. Memory = Was der Agent gelernt hat. **SCIENCE = Was die Welt weiß und wie wir dazu stehen.**

---

## 3. Integration in den Agent-Loop

### 3.1 SCIENCE im Tick-Cycle

SCIENCE ist kein eigener Tick-Schritt der bei jedem Heartbeat läuft. Es ist ein **kognitiver Modus** den der Planner aktivieren kann:

```python
async def tick():
    soul_t = compute_soul(base, agenda, accounts, social, decentral, working_context)
    
    hooks = load("identity/hook.md")
    plan = planner(soul_t, hooks, memory_query(topic))
    
    # Planner kann SCIENCE-Aktionen in den Plan aufnehmen:
    # - "research" → Erkenntnisse sammeln, in SCIENCE/ ablegen
    # - "validate" → Eigene Claims gegen SCIENCE/sources prüfen
    # - "hypothesize" → Neue Hypothesen aus SCIENCE-Daten ableiten
    
    results = executor(plan)
    observer(results, diary, guidelines)
```

### 3.2 SCIENCE-Aktionen im Executor

Der Executor kennt drei SCIENCE-spezifische Aktionen:

| Aktion | Input | Output | Ablage |
|--------|-------|--------|--------|
| `SCIENCE.research` | Thema/Fragestellung | Strukturierte Erkenntnisse | `SCIENCE/{date}-{topic}.md` |
| `SCIENCE.validate` | Claims aus Whitepaper/Workpaper | Validierungsbericht | `SCIENCE/{date}-{topic}-review.md` |
| `SCIENCE.hypothesize` | SCIENCE-Daten + Projektkontext | Neue Hypothesen | Wird in laufendes Workpaper geschrieben |

### 3.3 Observer-Feedback

Der Observer kann SCIENCE-Trigger erkennen:
- Architekturentscheidung getroffen → "Sollte validiert werden"
- Neues Themengebiet betreten → "Research empfohlen"
- Widerspruch zu bekanntem SCIENCE-Material entdeckt → "Conflict alert"

---

## 4. Die Lücke die SCIENCE schließt

### Aktuelles Modell ohne SCIENCE

```
soul(t) = f(base, agenda.resolve(...), working_context)
```

Der Agent weiß nur was **im Workspace steht**. Er hat kein Konzept von "Was weiß die Welt zu diesem Thema?" oder "Sind unsere Annahmen noch aktuell?"

### Mit SCIENCE

```
soul(t) = f(base, agenda.resolve(...), working_context + science_context)
```

SCIENCE-Material fließt als Teil des `working_context` in die Soul-Berechnung ein. Ein Agent der Research in `SCIENCE/` hat, trifft **informiertere Entscheidungen** — seine Soul emergiert mit externem Wissen.

Das ist der entscheidende Punkt: **SCIENCE macht den Agent schlauer, nicht durch ein besseres Modell, sondern durch besseren Kontext.** Das ist exakt der State-of-the-Art-Trend: *"Agent-Fehler sind Context-Fehler, nicht Model-Fehler."*

---

## 5. Differenzanalyse-Modell (Delta)

Drei Deltas die im agentischen Arbeiten auftreten:

```
Delta_1 = Whitepaper vs. Workpaper    → Architekturziel vs. operative Umsetzung
Delta_2 = Workpaper vs. Code/Output   → Plan vs. tatsächliches Ergebnis
Delta_3 = System vs. externe Realität → Eigene Lösung vs. Stand der Forschung
```

- **Delta_1 und Delta_2** werden durch Observer + Workpaper-Review abgedeckt
- **Delta_3** ist das was heute komplett fehlt — SCIENCE adressiert genau das

Ein Agent kann heute nie sagen: *"Unsere Architektur ist State-of-the-Art"* oder *"Es gibt dafür bereits eine bessere Lösung"*. Mit SCIENCE kann er das.

---

## 6. SCIENCE-Dokument-Struktur

Dateien in `WORKING/SCIENCE/` folgen einem einfachen Schema:

```markdown
# SCIENCE: {Topic}

- **Datum:** {YYYY-MM-DD}
- **Typ:** research | review | hypothesis
- **Trigger:** {Warum — manuell, Architekturentscheidung, neues Thema}

## Kontext
Warum diese Recherche/Validierung jetzt?

## Erkenntnisse
Was wurde gefunden? (strukturiert, mit Quellen)

## Einordnung
Wo steht unser Projekt im Vergleich?

## Quellen
| Quelle | Level | Kernaussage |
|--------|-------|-------------|

Level: A (peer-reviewed) | B (offizielle Doku) | C (Blog/Artikel) | D (Meinung/Erfahrung)

## Hypothesen / Next Steps
Was folgt daraus für MantisClaw?
```

### Quellengewichtung

| Level | Typ | Beispiel |
|-------|-----|---------|
| **A** | Peer-reviewed Paper | arXiv, ACM, IEEE |
| **B** | Offizielle Dokumentation | Framework-Docs, RFCs, Standards |
| **C** | Blog / Artikel / Konferenzvortrag | Heise, Medium, YouTube-Talk |
| **D** | Meinung / Erfahrungsbericht | Reddit, Feldberichte, Agent-Output |

---

## 7. Trigger-Modell

### Wann wird SCIENCE aktiviert?

| Trigger | Auslöser | Im Loop |
|---------|----------|---------|
| **Manuell** | User oder Agent startet Research | Planner nimmt `SCIENCE.research` in Plan auf |
| **Architekturentscheidung** | Whitepaper-Update | Observer empfiehlt Delta_3-Prüfung |
| **Neues Thema** | Agent betritt unbekanntes Gebiet | Planner erkennt fehlenden Kontext |
| **Periodisch** | Zeitbasiert (z.B. monatlich) | Hook in `identity/hook.md` |

SCIENCE ist **kein Automatismus bei jedem Tick**. Es ist ein bewusster kognitiver Schritt:

> `Plan → Build → Observe → (SCIENCE wenn nötig) → Refine`

---

## 8. Warum das besseres agentisches Arbeiten ermöglicht

### 8.1 Context Engineering statt Prompt Engineering

Der State of the Art 2026 ist klar: **Agent-Fehler sind Context-Fehler**. SCIENCE erweitert den verfügbaren Kontext systematisch um externes Wissen — persistent, strukturiert, querybar.

### 8.2 Persistent statt ephemer

Andere Frameworks (Reflexion, Critic-Agents) machen Validierung **im Prompt** — nach der Session ist alles weg. MantisClaw mit SCIENCE macht es **dateibasiert** — Erkenntnisse überleben Sessions, werden Teil des working_context, fließen in die Soul-Berechnung ein.

### 8.3 "Files are all you need"

Das ist exakt das Manus-Prinzip: File-basierte Memory-Systeme funktionieren weil sie persistent, transparent, editierbar, portabel und vendor-lock-in-frei sind. SCIENCE erweitert dieses Prinzip um eine epistemische Dimension.

### 8.4 Multi-Agent-Kompatibilität

In einer Mantis-OS-Umgebung mit mehreren Agenten kann SCIENCE-Material **geteilt** werden. Ein Research-Agent füllt `SCIENCE/`, ein Coding-Agent nutzt es als Kontext. Die Soul jedes Agents emergiert informierter.

---

## 9. Bezug zum MantisClaw-Schichtenmodell

SCIENCE operiert auf **L2 (AAMS Body)** als Speicher und auf **L3 (Runtime)** als Prozess:

```
┌─────────────────────────────────────────┐
│  L3  Runtime — Das Gehirn (core/)       │  ← SCIENCE.research, SCIENCE.validate, SCIENCE.hypothesize
├─────────────────────────────────────────┤
│  L2  AAMS Body (WORKSPACE/WORKING/)     │  ← SCIENCE/ Ordner als persistenter Speicher
├─────────────────────────────────────────┤
│  L1  Identität (identity/)              │  ← hook.md kann SCIENCE-Trigger definieren
└─────────────────────────────────────────┘
```

Das ist der Unterschied zu AAMS-only: AAMS stellt L2 (den Ordner). MantisClaw stellt L3 (die Logik die den Ordner nutzt).

---

## 10. Kritische Punkte & Grenzen

| Risiko | Mitigation |
|--------|-----------|
| **Overhead** — Research kann Sessions aufblähen | Bewusster Trigger, kein Automatismus. Planner entscheidet. |
| **Quellenqualität** — LLM halluziniert Quellen | Quellengewichtung (A/B/C/D) + explizite URLs/DOIs pflicht |
| **Scope Explosion** — Recherche kann unendlich werden | Begrenzung im Planner: `max_sources`, `max_depth` |
| **Halluzinierte Validierung** — Agent "bestätigt" sich selbst | Unsicherheitsmodell (Confidence/Evidence) + Observer-Check |

---

## 11. Entscheidungen

| # | Entscheidung | Begründung |
|---|-------------|-----------|
| D1 | SCIENCE ist ein MantisClaw-Feature, kein AAMS-Spec-Element | AAMS = Struktur, MantisClaw = Prozess. Validierung braucht LLM + Loop. |
| D2 | SCIENCE-Ordner liegt in `WORKING/SCIENCE/` | Konsistenz mit AAMS-Struktur die MantisClaw integriert hat |
| D3 | Drei Executor-Aktionen: research, validate, hypothesize | Minimal aber vollständig. Deckt die drei Kernfunktionen ab. |
| D4 | SCIENCE-Material fließt in working_context → soul(t) | Erkenntnisse machen den Agent informierter, nicht nur die Doku besser |
| D5 | Quellengewichtung A/B/C/D ist verpflichtend | LLMs halluzinieren sonst "Wahrheit" — epistemische Hygiene |
| D6 | Trigger: hybrid (manuell + Observer-Empfehlung + Hooks) | Balance zwischen Kontrolle und Automatisierung |
| D7 | SCIENCE-Dokumente folgen flachem Schema (kein Unterordner-Baum) | Einfachheit. Ein Ordner, klare Dateinamen, fertig. |

---

## 12. Next Steps

- [ ] SCIENCE-Aktionen in Executor-Spec aufnehmen (CORE.md Update)
- [ ] Hook-Trigger für SCIENCE in hook.md.example ergänzen
- [ ] Erstes SCIENCE-Dokument: Delta_3 MantisClaw vs. State of the Art
- [ ] Observer-Logic: SCIENCE-Empfehlungen bei Architekturentscheidungen
- [ ] AGENTS.md + README.md: SCIENCE in Workspace-Struktur dokumentieren
- [ ] LTM-Ingest dieses Workpapers

---

## File Protocol

| # | Aktion | Datei | Beschreibung |
|---|--------|-------|-------------|
| F1 | REOPENED | `WORKING/WORKPAPER/2026-04-09-science-knowledge-validation-layer.md` | Von CLOSED/VERWORFEN → OPEN. Adaptiert für MantisClaw. |
| F2 | REFERENCED | `WORKING/SCIENCE/2026-04-09-Erkenntnisse und neuen Forschungsbereiche.md` | Research-Grundlage für dieses Konzept |

---

> **SCIENCE gehört in den Agent-Loop, nicht in die Workspace-Spec.** AAMS gibt den Ordner. MantisClaw gibt den Verstand.

