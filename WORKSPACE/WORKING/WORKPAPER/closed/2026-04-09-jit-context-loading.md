# Workpaper: JIT Context Loading — Selektives Laden statt Alles-in-den-Prompt

- **Datum:** 2026-04-09
- **Agent:** GitHub Copilot (Claude Opus 4.6)
- **Status:** CLOSED
**Geschlossen:** 2026-04-10
- **Bezug:** SCIENCE Review `2026-04-09-mantisclaw-vs-state-of-the-art-review.md` — Hypothese H5
- **Priorität:** Hoch

---

## Session Goal

**JIT Context Loading** (Just-In-Time) für MantisClaw's `working_context` designen. Der Planner soll selektiv laden was er braucht, nicht alles was existiert.

---

## 1. Das Problem

### Aktueller Ansatz (CORE.md §4.1)

```python
working_context = load_whitepapers_and_workpapers()
soul_t = compute_soul(base, agenda, accounts, social, decentral, working_context)
```

`load_whitepapers_and_workpapers()` lädt **alles**:
- Alle Whitepapers
- Aktuelles Workpaper
- LTM-Index
- (Zukünftig: GUIDELINES/, SCIENCE/)

### Warum das nicht skaliert

| Szenario | Dateien | ~Tokens |
|----------|---------|---------|
| Frischer Workspace | 2-3 Dateien | ~2k |
| Nach 1 Monat | 10-15 Dateien | ~15k |
| Nach 6 Monaten | 50+ Dateien | ~80k+ |
| Mit SCIENCE + GUIDELINES | 70+ Dateien | ~120k+ |

Bei einem 128k-Token-Kontextfenster (lokales Modell) ist nach 6 Monaten **kein Platz mehr für den eigentlichen Plan**.

### Der State of the Art sagt

> "Der eigentliche Engpass ist nicht das Modell, sondern: was gespeichert wird, wie es strukturiert ist, wie es wiedergefunden wird."

> JIT Context: "Agent macht `search_memory()`, `load_file()`, `query_vector_db()` — statt mega prompt mit allem."

LangChain's Context Engineering formalisiert das als vier Operationen:
1. **Write** — Speichern außerhalb des Kontexts
2. **Select** — Relevantes per Query ins Fenster holen
3. **Compress** — Nur relevante Tokens behalten
4. **Forget** — Gezielt vergessen um Rauschen zu reduzieren

MantisClaw hat "Write" (AAMS-Struktur). Was fehlt: **Select**, **Compress**, **Forget**.

---

## 2. Design: Dreistufiges Context Loading

### 2.1 Architektur-Übersicht

```
                    ┌─────────────────┐
                    │   WORKING/      │  ← Alles was existiert (Disk)
                    │   ├── WP/       │
                    │   ├── WH/       │
                    │   ├── LTM/      │
                    │   ├── GL/       │
                    │   ├── SCIENCE/  │
                    │   └── DIARY/    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Context Loader  │  ← NEU: Selektiert was relevant ist
                    │                  │
                    │  1. Always-Load  │  ← Immer laden (klein, kritisch)
                    │  2. Agenda-Load  │  ← Was die Agenda braucht
                    │  3. Query-Load   │  ← Was der Planner nachfragt
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ working_context  │  ← Was tatsächlich in den Prompt geht
                    │  (~10-20k Token) │
                    └─────────────────┘
```

### 2.2 Die drei Lade-Stufen

#### Stufe 1: Always-Load (Core Context)

Wird bei **jedem Tick** geladen. Immer. Ohne Ausnahme.

```python
always_load = [
    "WORKPAPER/{current_session}.md",    # Aktuelles Workpaper
    "MEMORY/ltm-index.md",               # LTM-Index (nicht Details)
]
```

**~2-4k Tokens.** Das ist die minimale Orientierung.

#### Stufe 2: Agenda-Load (Filtered by Agenda)

Die Agenda bestimmt welche Whitepapers und Guidelines relevant sind.

```python
def agenda_load(agenda):
    """Lädt was die aktuelle Agenda braucht."""
    relevant = []
    
    # Agenda sagt: "Ich arbeite an Core-Architektur"
    if agenda.topic in ["architecture", "core"]:
        relevant.append("WHITEPAPER/CORE.md")
    
    # Agenda sagt: "Coding-Task"
    if agenda.task_type == "coding":
        relevant.append("GUIDELINES/coding.md")
    
    # Agenda referenziert SCIENCE
    if agenda.needs_validation:
        relevant.append("SCIENCE/{latest_relevant}.md")
    
    return relevant
```

**~5-10k Tokens.** Agenda-gefiltert.

#### Stufe 3: Query-Load (On-Demand by Planner)

Der Planner kann während der Planung **nachfragen**:

```python
def plan(soul_t, hooks, memory, guidelines, context_loader):
    # Planner erkennt: "Ich brauche mehr Kontext zu Topic X"
    additional = context_loader.query("Was wissen wir über LLM-Backend-Auswahl?")
    # → Lädt relevante Sections aus WHITEPAPER/CORE.md §4.5
    # → Lädt relevante LTM-Einträge
    # → Lädt relevante SCIENCE-Reviews
    
    plan = llm.plan(soul_t, hooks, memory, guidelines, additional)
    return plan
```

**~3-8k Tokens.** Nur was der Planner explizit braucht.

### 2.3 Gesamt-Token-Budget

```
Always-Load:  ~3k  Tokens  (fest)
Agenda-Load:  ~8k  Tokens  (variabel, agenda-abhängig)
Query-Load:   ~5k  Tokens  (variabel, planner-abhängig)
─────────────────────────────
Gesamt:      ~16k  Tokens  (statt 80k+ bei vollem Load)

Verbleibend für Plan + Execution: ~112k Tokens (bei 128k Fenster)
```

---

## 3. Context Loader — Das neue Modul

### 3.1 Platzierung im Schichtenmodell

> **Update (WH-TOOLS):** Context Loading ist jetzt eine **Tool-Chain** in der Tool-Registry (L4), nicht mehr ein eigenständiges Core-Modul. Der Core (L3) greift auf den Körper (L2) ausschließlich über registrierte Tools zu.

```
L3 Runtime (Planner, Executor, Observer)
    ↓ delegiert an
L4 Tool-Registry
    ├── load_context_always    → JIT Stage 1
    ├── load_context_agenda    → JIT Stage 2
    └── load_context_query     → JIT Stage 3
    ↓ greift zu auf
L2 AAMS Body (WORKING/)
```

Die drei Lade-Stufen bleiben konzeptionell identisch — aber die Implementierung wird zu workspace-Tools (`context`-Kategorie in der Registry). Siehe WH-TOOLS §3.3 und §5.

### 3.2 API

```python
class ContextLoader:
    def __init__(self, workspace_path, token_budget):
        self.workspace = workspace_path
        self.budget = token_budget  # aus config/default.yaml
    
    def load_always(self) -> Context:
        """Stufe 1: Core Context. Immer laden."""
        
    def load_for_agenda(self, agenda) -> Context:
        """Stufe 2: Agenda-gefilterter Context."""
        
    def query(self, question: str) -> Context:
        """Stufe 3: On-Demand Query. Planner fragt nach."""
        
    def build_working_context(self, agenda) -> Context:
        """Kombiniert Stufe 1 + 2. Stufe 3 wird vom Planner getriggert."""
```

### 3.3 Query-Mechanismus (Stufe 3)

Für Stufe 3 braucht der Context Loader eine **Suchfähigkeit**:

**Option A: Keyword-basiert (einfach, local-first)**
```python
def query(self, question):
    keywords = extract_keywords(question)
    matches = []
    for file in self.workspace.all_files():
        if file.contains_any(keywords):
            matches.append(file.relevant_sections(keywords))
    return top_k(matches, k=3, by=relevance)
```

**Option B: LTM-Index-basiert (strukturiert)**
```python
def query(self, question):
    # LTM-Index hat Topics + Datei-Referenzen
    entries = ltm_index.search(question)
    return load_referenced_files(entries)
```

**Option C: Embedding-basiert (optional, wenn ChromaDB aktiv)**
```python
def query(self, question):
    embedding = embed(question)
    results = chromadb.similarity_search(embedding, k=5)
    return results
```

**Empfehlung:** Option A als Default (local-first, kein externer Service), Option C als Upgrade-Pfad.

---

## 4. Integration in den Tick-Cycle

### Angepasster Tick

```python
async def tick():
    # L1 — Identity
    soul_t = compute_soul(base, agenda, accounts, social, decentral, 
                          working_context=None)  # Noch kein Context
    
    # NEU: Context Loading
    context_loader = ContextLoader(workspace, config.token_budget)
    core_context = context_loader.load_always()
    agenda_context = context_loader.load_for_agenda(agenda)
    working_context = core_context + agenda_context
    
    # Soul mit Context neu berechnen
    soul_t = compute_soul(base, agenda, accounts, social, decentral, 
                          working_context)
    
    # L3 — Planner (kann Stufe 3 nutzen)
    plan = planner(soul_t, hooks, memory, guidelines, 
                   context_loader=context_loader)  # Für Query-Load
    
    # Rest wie bisher
    results = executor(plan)
    assessment = observer(results, diary, guidelines)
    # ... RFL, LTM, Sleep
```

### Unterschied zum alten Tick

| Vorher | Nachher |
|--------|---------|
| `working_context = load_everything()` | `working_context = context_loader.build(agenda)` |
| Alles im Prompt | Nur Relevantes im Prompt |
| Planner arbeitet mit vollem Kontext | Planner kann nachfragen (Stufe 3) |
| Skaliert nicht | Skaliert mit Workspace-Größe |

---

## 5. Config

```yaml
# In config/default.yaml
context:
  token_budget: 20000       # Max Tokens für working_context
  always_load:
    - "WORKPAPER/{current}"   # Aktuelles Workpaper
    - "MEMORY/ltm-index.md"   # LTM-Index
  query_backend: "keyword"   # keyword | ltm-index | embedding
  query_max_results: 3       # Max Dateien pro Query
  compress_threshold: 5000   # Dateien > 5000 Tokens werden zusammengefasst
```

---

## 6. Compress-Strategie

Große Dateien (z.B. CORE.md mit ~3k Tokens) können komprimiert werden:

```python
def compress(content, max_tokens):
    """Komprimiert ein Dokument auf max_tokens."""
    if count_tokens(content) <= max_tokens:
        return content
    
    # Strategie: Headers + erste Zeile jeder Section
    sections = parse_markdown_sections(content)
    compressed = []
    for section in sections:
        compressed.append(f"## {section.header}")
        compressed.append(section.first_line)
    
    return "\n".join(compressed)
```

Das gibt dem Planner eine **Übersicht** ohne das volle Dokument. Bei Bedarf kann er per Query-Load die Details nachladen.

---

## 7. Forget-Strategie

Nicht alles was geladen wurde muss im Kontext bleiben:

```python
# Nach Stufe 3 Query-Load: alte Query-Ergebnisse vergessen
# wenn neuer Query kommt
context_loader.forget_queries_except(latest=2)
```

Für MantisClaw's Tick-basiertes Modell ist Forget einfach: **Ende des Ticks = Reset.** Jeder Tick baut seinen Kontext neu auf. Es gibt kein akkumulierendes Kontextfenster das überläuft.

---

## 8. Zusammenspiel mit anderen Workpapers

### Mit Procedural Memory (GUIDELINES/)
GUIDELINES/ werden in Stufe 2 (Agenda-Load) geladen — nur die zum Task-Typ passenden.

### Mit Reflection-Loop (RFL)
Wenn der Reflection-Loop startet, kann der Planner per Query-Load (Stufe 3) zusätzlichen Kontext nachladen der für die Korrektur relevant ist.

### Mit SCIENCE
SCIENCE-Dokumente werden nur geladen wenn die Agenda `needs_validation` hat oder der Planner explizit fragt.

---

## 9. Entscheidungen

| # | Entscheidung | Begründung |
|---|-------------|-----------|
| D1 | Dreistufiges Loading: Always + Agenda + Query | Balance zwischen Vollständigkeit und Token-Effizienz |
| D2 | Token-Budget konfigurierbar (default: 20k) | Verschiedene LLM-Backends haben verschiedene Limits |
| D3 | Keyword-Search als Default Query-Backend | Local-first, kein externer Service. Embedding als Upgrade. |
| D4 | Context wird pro Tick neu aufgebaut | Kein akkumulierender Kontext. Jeder Tick ist frisch. Forget = Reset. |
| D5 | Planner kann nachfragen (Stufe 3) | Planner weiß am besten was er braucht. Nicht alles vorher laden. |
| D6 | Compress für große Dateien (>5k Tokens) | Übersicht statt Volltext. Details per Query nachladen. |

---

## 10. Next Steps

- [x] ~~Context Loader als neues Modul spezifizieren (core/context.py)~~ → Jetzt Tool-Chain in Registry (`context`-Kategorie), siehe WH-TOOLS §3.3
- [ ] CORE.md §4.1 Tick-Cycle anpassen: Context Loading als Tool-Chain
- [ ] config/default.yaml: context-Config anlegen
- [ ] Token-Counting-Utility (einfach: ~4 chars = 1 Token)
- [ ] Keyword-Search-Implementierung für Query-Load
- [ ] Compress-Funktion für Markdown-Dateien
- [ ] Agenda-basiertes Tool-Filtering integriert JIT Stage 2 (siehe WH-TOOLS §3.7)

---

## File Protocol

| # | Aktion | Datei | Beschreibung |
|---|--------|-------|-------------|
| F1 | CREATED | `WORKPAPER/2026-04-09-jit-context-loading.md` | Dieses Workpaper |

---

> **Ein Agent der alles liest versteht nichts. Ein Agent der gezielt liest versteht alles.**

