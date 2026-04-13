# WHITEPAPER: Working System — Die integrierte Arbeitsstruktur

**Dokument:** WH-WORKING
**Version:** 0.3.0
**Erstellt:** 2026-04-09
**Status:** DRAFT
**Herkunft:** WH-CORE §6/§7, WP-Procedural-Memory, WP-JIT-Context, WP-SCIENCE, SCIENCE-Review, WP-AAMS-Upgrade

---

## 1. Zusammenfassung

Das Working System ist MantisClaw's **integrierte Arbeitsstruktur** — basierend auf AAMS (Autonomous Agent Manifest Specification). AAMS ist kein externes Paket, sondern fest in MantisClaw eingebaut. Das Framework arbeitet frameworkbedingt an Workpapers und nutzt die WORKING-Struktur für strukturiertes Arbeiten an komplexen Aufgaben — ob Coding, Planung oder Organisation.

Das Working System ist der `working_context` in der Soul-Formel. Alles was der Agent über seine Arbeit, seine Architektur und seine Erkenntnisse weiß, lebt hier.

---

## 2. Ordnerstruktur

```
WORKSPACE/
└── WORKING/
    ├── PROJECT/            ← Projekt-Definitionen (Scope, Ziele, Meilensteine)
    │   ├── _active.yaml    ← Pointer auf aktives Projekt
    │   └── <slug>/
    │       └── project.yaml ← Manifest
    ├── WORKPAPER/          ← Session-Arbeit (eine Datei pro Session)
    │   └── closed/         ← Archivierte Sessions
    ├── WHITEPAPER/         ← Stabile Architektur-Wahrheit
    ├── MEMORY/             ← Langzeitgedächtnis (ltm-index.md)
    ├── DIARY/              ← Temporal Index (pointer-only, chronologisch)
    ├── GUIDELINES/         ← Procedural Memory (gelernte Arbeitsweisen)
    ├── SCIENCE/            ← Knowledge Validation (Erkenntnisse, Reviews)
    ├── LOGS/               ← Audit-Trail
    └── TOOLS/              ← Werkzeuge & Orchestrierung
        └── skills/         ← Markdown+YAML Workflows (Procedural Memory, L5)
```

---

## 3. Die fünf Memory-Schichten

MantisClaw deckt alle vier Memory-Typen der Cognitive-Science-Taxonomie (CoALA/Princeton) ab — plus eine fünfte, eigene Schicht:

| Schicht | Ordner | CoALA-Typ | Frage die sie beantwortet |
|---------|--------|-----------|--------------------------|
| **Project** | `PROJECT/` | Strategic Memory | Woran arbeite ich? |
| **Workpaper** | `WORKPAPER/` | Working Memory | Was tue ich jetzt? |
| **Whitepaper** | `WHITEPAPER/` | Semantic Memory (stabil) | Wie ist das System aufgebaut? |
| **Diary** | `DIARY/` | Temporal Index | Wann wurde was angefasst? |
| **Memory/LTM** | `MEMORY/` | Semantic Memory (gelernt) | Was haben wir gelernt? |
| **Guidelines** | `GUIDELINES/` | Procedural Memory | Wie arbeite ich am besten? |

Plus eine Erweiterung die kein anderes Framework hat:

| Schicht | Ordner | Typ | Frage |
|---------|--------|-----|-------|
| **Science** | `SCIENCE/` | Epistemisch | Stimmt das? Wo stehen wir? |

### 3.1 Workpaper — Working Memory

**Eine Datei pro Session.** Enthält:
- Session Goal
- Entscheidungen
- File Protocol (welche Dateien erstellt/geändert)
- Next Steps

Lifecycle: `erstellt → bearbeitet → geschlossen → archiviert (closed/)`

Das Workpaper ist der **Fokus** des Agenten. MantisClaw arbeitet frameworkbedingt an einem Workpaper — das erzwingt strukturiertes, nachvollziehbares Arbeiten.

### 3.2 Whitepaper — Architektur-Wahrheit

**Stabile Dokumente.** Werden nur bei Architektur-Entscheidungen aktualisiert.

Aktuelle Whitepapers:
- `CORE.md` — Runtime, Loop, Gehirn, Dashboard
- `IDENTITY.md` — Emergente Identität, soul(t)
- `WORKING.md` — Dieses Dokument
- `TOOLS.md` — Tool-Registry, Skills, Körper-Interface

Whitepapers sind die **Quelle der Wahrheit** für die System-Architektur. Wenn ein Workpaper und ein Whitepaper sich widersprechen, gilt das Whitepaper — bis ein neues Workpaper das Whitepaper explizit aktualisiert.

### 3.3 Diary — Temporal Index (AAMS v1.3.0)

**Pointer-only Format.** Monatliche Dateien (`YYYY-MM.md`). Eine Zeile pro Session:

```
YYYY-MM-DD | WP: {workpaper} | WH: {whitepaper} | {other files}
```

Hierarchische Kompression: Daily → Weekly Rollup → Monthly Summary (429 Einträge/Jahr max).

> **AAMS v1.3.0 (2026-04-09):** Diary Reform — Pointer-only statt inhaltlicher Duplikation. Version Centralization — `_spec: "AAMS/1.3.0"` in `.agent.json`. Topic Registry für Workpaper-Naming.

Das Diary ist der **temporale Index** — es zeigt WANN WAS angefasst wurde, ohne Inhalte zu duplizieren. Details stehen im Workpaper, Architektur im Whitepaper, Wissen im LTM.

**Technische Schutzmechanismen (seit 2026-04-10):**
- **Rate-Limit:** Max 3 Einträge pro Tag — verhindert Tick-Spam durch automatische Loops
- **Dedup:** Identische Einträge am selben Tag werden übersprungen
- **Pointer-only:** Max 120 Zeichen pro Eintrag, danach Truncation
- Implementiert in `core/registry/tools/memory.py` → `log_to_diary()`

### 3.4 Memory/LTM — Langzeitgedächtnis

**ltm-index.md** als zentraler Index. Ingestiert aus geschlossenen Workpapers.

Dual-Track möglich:
- **Markdown** (default) — ltm-index.md mit Topics + Datei-Referenzen
- **Vector** (optional) — ChromaDB für Embedding-basierte Suche

LTM ist das **semantische Gedächtnis** — extrahierte Fakten, Entscheidungen, Erkenntnisse die über Sessions hinweg gelten.

### 3.5 Guidelines — Procedural Memory

**NEU.** Gelernte Arbeitsweisen. Der Agent lernt wie er am besten arbeitet.

```
GUIDELINES/
├── coding.md        ← "Bei Refactors: Tests zuerst prüfen"
├── session.md       ← "Immer Kontext lesen vor Edits"
└── planning.md      ← "Große Tasks in Steps zerlegen"
```

Datenfluss:
```
Executor → Results → Observer → Lektion extrahiert → GUIDELINES/{category}.md
                                                            ↓
Nächster Tick: Planner liest relevante Guidelines → informierterer Plan
```

Guidelines wachsen mit der Erfahrung des Agenten. Ein Agent mit 50 Sessions arbeitet **anders** als ein frischer Agent — weil er gelernt hat.

Konfliktregel: **Whitepaper > Guideline**. Architektur-Wahrheit ist stabiler als Erfahrungswerte.

### 3.6 Science — Knowledge Validation

**NEU.** Erkenntnisse, Validierungen, externe Einordnung.

```
SCIENCE/
├── 2026-04-09-erkenntnisse-forschungsbereiche.md   ← Research-Sammlung
└── 2026-04-09-mantisclaw-vs-state-of-the-art.md    ← Validierungs-Review
```

SCIENCE beantwortet Delta_3: **Eigene Lösung vs. Stand der Forschung.**

Drei Executor-Aktionen für SCIENCE:
- `science.research` — Erkenntnisse sammeln
- `science.validate` — Claims gegen Quellen prüfen
- `science.hypothesize` — Neue Hypothesen ableiten

SCIENCE-Material fließt als Teil des `working_context` in `soul(t)` ein. Ein Agent mit Research-Grundlage trifft informiertere Entscheidungen.

---

## 4. Die Wissenskette

Strikte Reihenfolge: **Arbeit → Wahrheit → Gedächtnis**

```
Session-Arbeit (Workpaper)
    ↓  Erkenntnisse stabilisiert?
Architektur-Wahrheit (Whitepaper)
    ↓  Ingest
Langzeitgedächtnis (LTM)
```

Die Wissenskette erzwingt **epistemische Hygiene**:
- Flüchtige Ideen leben im Workpaper
- Nur bewährte Ideen werden Whitepaper
- Nur stabile Wahrheiten werden LTM

Kein anderes bekanntes Framework hat eine so explizite Wissens-Hierarchie. Die meisten Systeme haben flache Memory (alles auf einer Ebene) oder implizite Hierarchien (Mensch entscheidet was wichtig ist).

---

## 5. JIT Context Loading

Das Working System skaliert durch **selektives Laden** statt alles in den Prompt zu packen.

### Dreistufiges Loading

```
Stufe 1: Always-Load (Core Context)
    → Aktuelles Workpaper + LTM-Index
    → ~3k Tokens, immer geladen

Stufe 2: Agenda-Load (Gefiltert)
    → Relevante Whitepapers + Guidelines (passend zur Agenda)
    → ~8k Tokens, agenda-abhängig

Stufe 3: Query-Load (On-Demand)
    → Planner fragt nach spezifischem Kontext
    → ~5k Tokens, planner-getriggert
```

### Warum JIT nötig ist

| Workspace-Alter | Dateien | Tokens ohne JIT | Tokens mit JIT |
|-----------------|---------|-----------------|----------------|
| Frisch | 3 | ~2k | ~2k |
| 1 Monat | 15 | ~15k | ~10k |
| 6 Monate | 50+ | ~80k+ | ~16k |

Bei 128k-Token-Kontextfenster (lokales Modell) ist ohne JIT nach 6 Monaten kein Platz mehr für den Plan. Mit JIT bleibt das Budget stabil bei ~16k.

### Context Loader

Neues Infrastruktur-Modul zwischen L2 (AAMS Body) und L3 (Runtime):

```python
class ContextLoader:
    def load_always(self) -> Context          # Stufe 1
    def load_for_agenda(self, agenda) -> Context  # Stufe 2
    def query(self, question) -> Context       # Stufe 3
```

Query-Backend: Keyword-Search (default, local-first) oder Embedding-Search (optional, bei ChromaDB).

---

## 6. Memory-Klassen

| Klasse | Speicher | Format | Zweck |
|--------|----------|--------|-------|
| **BAU** (Bau-Memory) | `WORKSPACE/WORKING/` | Markdown | WP, WH, DI, GL, SC — Architektur, Arbeit, Erkenntnis |
| **OPS** (Ops-Memory) | `WORKSPACE/AGENDA/` | SQLite | Posts, Interaktionen, CRM (Zukunft) |

BAU-Memory ist das was heute existiert und funktioniert. OPS-Memory ist für operative Daten geplant die nicht in Markdown passen (z.B. tausende Social-Media-Interaktionen).

---

## 7. AAMS-Integration

### AAMS v1.3.0 (aktuell)

MantisClaw nutzt AAMS v1.3.0 (Spec: `"AAMS/1.3.0"` in `.agent.json`).

**v1.3.0 Änderungen (2026-04-09):**
- **Diary Reform:** Pointer-only Format, keine Inhaltsduplikation
- **Version Centralization:** `_spec` Feld in `.agent.json`
- **Topic Registry:** ARCH, SPEC, LTM, SEC, BOOT, FLD, RES, MKT, ISS, GOV, EDU, TOOL, DASH, SOUL
- **Deviations:** Whitepaper-Naming und Extra-Ordner dokumentiert in `_deviations`

### Was AAMS gibt (Struktur)

AAMS definiert:
- Ordnernamen und -hierarchie (`WORKING/WORKPAPER/`, `WORKING/WHITEPAPER/`, etc.)
- Naming-Konventionen (`{date}-{agent}-{topic}.md`)
- Session-Lifecycle (open → work → close → archive)
- File Protocol in Workpapers

### Was MantisClaw dazugibt (Prozess)

MantisClaw definiert:
- **Wann** was geladen wird (JIT Context Loading)
- **Wie** Guidelines geschrieben werden (Observer → Procedural Memory)
- **Warum** SCIENCE-Reviews erstellt werden (Planner → science.validate)
- **Wie** die Wissenskette durchgesetzt wird (Session-Lifecycle)

```
AAMS = Der Körper (Struktur, Ordner, Naming)
MantisClaw = Der Verstand (Prozesse, Entscheidungen, Lernen)
```

---

## 8. Bootstrap

**"One File to Bootstrap"** — `.agent.json` genügt.

```
.agent.json gelesen
    → READ-AGENT.md lesen
    → WORKSPACE/ Struktur anlegen (idempotent)
    → Erste Session starten
    → Workpaper erstellen
```

Die gesamte WORKING-Struktur wird beim ersten Start automatisch angelegt. Idempotent — mehrfaches Ausführen ändert nichts an existierenden Dateien.

---

## 9. Bezug zu den anderen Whitepapers

```
WH-WORKING (dieses Dokument)
    ↑ liefert working_context an
WH-IDENTITY (Emergente Identität)
    ↑ berechnet soul(t) für
WH-CORE (Runtime/Loop)
```

- **WH-CORE** beschreibt den Loop der auf dem Working System operiert
- **WH-IDENTITY** beschreibt die Soul die den Working Context als Input hat
- **WH-WORKING** (dieses Dokument) beschreibt die Struktur in der Arbeit, Wissen und Erfahrung leben

---

*Whitepaper. Stabile Architektur-Wahrheit. Wird bei Architektur-Entscheidungen aktualisiert.*
