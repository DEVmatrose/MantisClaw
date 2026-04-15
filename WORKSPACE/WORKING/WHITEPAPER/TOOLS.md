# WH-TOOLS — Werkzeuge, Skills & Körper-Interface

> **MantisClaw Whitepaper** | Version 0.3.0 | 2026-04-15
> Status: **PARTIALLY IMPLEMENTED**

---

## §1 Zweck

Dieses Whitepaper definiert, wie MantisClaw **handelt** — wie der Loop (Gehirn) auf den Körper (WORKING/) und die Außenwelt zugreift. Es trennt sauber:

- **Was existiert** → Tool-Registry (Fähigkeiten)
- **Wie kombiniert wird** → Skill-Kasten (Rezepte)
- **Wo zugegriffen wird** → Körper-Interface (WORKING/ Zugriff über Tools)

### Bezug zu anderen Whitepapers

| Whitepaper | Beziehung |
|---|---|
| WH-CORE | Der Loop ruft Tools/Skills über den Executor auf |
| WH-WORKING | Der Körper — wird passiv über workspace-Tools angesprochen |
| WH-IDENTITY | Identität beeinflusst, welche Skills/Tools bevorzugt werden |

---

## §2 Architektur-Schärfung: Gehirn vs. Körper

### Das bisherige Problem

WH-CORE definiert den Loop **und** die Körper-Zugriffsmodule in einem Dokument:

```
core/ (bisher)
├── runtime.py      ← Loop
├── planner.py      ← Loop
├── executor.py     ← Loop
├── observer.py     ← Loop
├── reflect.py      ← Loop
├── context.py      ← Körper-Interface (liest WORKING/)
├── llm.py          ← Infrastruktur (L0)
├── session.py      ← Körper-Interface (liest/schreibt WORKING/)
├── workpaper.py    ← Körper-Interface (WORKING/WORKPAPER/)
└── ltm.py          ← Körper-Interface (WORKING/MEMORY/)
```

**Problem:** Der Core vermischt Loop-Logik mit Körper-Zugriff. Das verletzt die Schichtentrennung aus WH-CORE §3.

### Die Lösung: Körper-Zugriff als Tools

Die Module `context.py`, `session.py`, `workpaper.py`, `ltm.py` werden zu **workspace-Tools** in der Tool-Registry. Der Core bleibt reiner Loop.

> **Implementierungsstand (2026-04-15):** Registry + 13 Tools implementiert (filesystem 5, memory 2, analysis 2, llm_management 2, loop_monitor 2). Body-Access-Module (`session.py`, `workpaper.py`, `ltm.py`, `context.py`) existieren noch als Core-Module — Migration zu Registry-Tools ausstehend.

**Aktuelle Struktur (implementiert):**
```
core/ (aktuell)
├── runtime.py        ← Loop-Orchestrierung + Tool-Registration
├── planner.py        ← Planung (mit tool_descriptions Injection)
├── executor.py       ← Ausführung (Fuzzy Action Matching)
├── observer.py       ← Beobachtung + Health-Tracking
├── reflect.py        ← Reflexion (Stub)
├── llm.py            ← LLM-Backend (L0-Anbindung)
├── session.py        ← AAMS Session (noch Core, Migration geplant)
├── workpaper.py      ← Workpaper-Mgmt (noch Core, Migration geplant)
├── ltm.py            ← LTM-Manager (noch Core, Migration geplant)
├── context.py        ← Context-Loader (noch Core, Migration geplant)
└── registry/         ← Tool-Registry + implementierte Tools
    ├── __init__.py
    ├── registry.py       ← ToolRegistry + Tool Klassen
    └── tools/
        ├── filesystem.py  ← read_file, write_file, append_file, list_dir, workspace_status
        ├── memory.py      ← query_memory, log_diary
        ├── analysis.py    ← analyze, summarize (LLM-powered)
        ├── llm_management.py ← list_models, switch_model
        └── loop_monitor.py   ← loop_monitor, token_budget
```

**Ziel-Struktur (Design):**
├── runtime.py        ← Loop-Orchestrierung
├── planner.py        ← Planung
├── executor.py       ← Ausführung (delegiert an Registry/Skills)
├── observer.py       ← Beobachtung
├── reflect.py        ← Reflexion (RFL)
├── llm.py            ← LLM-Backend (L0-Anbindung)
└── registry/         ← Tool-Registry + Skill-Executor
    ├── __init__.py
    ├── registry.json
    ├── skill_executor.py
    └── tools/
        ├── workspace.py   ← read_workpaper, write_workpaper, query_ltm, ...
        ├── context.py     ← load_context (JIT 3-Stage)
        ├── session.py     ← start_session, end_session, ...
        ├── file_io.py     ← read_file, write_file, list_dir
        ├── llm_tools.py   ← llm_complete, llm_embed
        ├── network.py     ← http_get, http_post
        └── nostr.py       ← nostr_publish, nostr_subscribe
```

### Schichtentrennung (geschärft)

```
L0  LLM-Backend         → core/llm.py (Infrastruktur, kein Tool)
L1  Identity             → WH-IDENTITY (soul(t) Berechnung)
L2  AAMS Body            → WORKING/ (passiv, wird über Tools angesprochen)
L3  Runtime / Loop       → core/ (runtime, planner, executor, observer, reflect)
L4  Tool-Registry        → core/registry/ (alle Fähigkeiten, inkl. Körper-Zugriff)
L5  Skills               → WORKING/TOOLS/skills/ (Orchestrierung)
L6  Security             → Querschnitt (Security-Levels in Registry)
L7  Network / MantisNostr → core/registry/tools/nostr.py (als Tool)
```

> **Kernaussage:** L2 (Körper) wird **ausschließlich** über L4 (Tools) angesprochen. L3 (Loop) berührt den Körper nie direkt.

---

## §3 Tool-Registry

### 3.1 Definition

Ein **Tool** ist eine atomare, zustandslose Funktion mit definierter Schnittstelle. Nur registrierte Tools existieren für das System.

### 3.2 Tool-Deklaration

**Implementiert:**
```python
@dataclass
class Tool:
    name: str               # Eindeutiger Identifier (snake_case)
    handler: Callable        # Async Handler-Funktion
    description: str = ""    # Für LLM-Kontext (max 100 Zeichen)
    security_level: int = 2  # 1=read, 2=read+write, 3=full
    tags: list[str] = []     # Kategorisierung (statt category)
```

**Design (Ziel-Erweiterung):**
```
Tool = {
    name: str,              # ✅ Implementiert
    handler: Callable,      # ✅ Implementiert
    description: str,       # ✅ Implementiert
    security_level: int,    # ✅ Implementiert (1/2/3 statt read/write/execute/admin)
    tags: list[str],        # ✅ Implementiert (ersetzt category)
    version: str,           # 🔮 Geplant — SemVer
    parameters: Schema,     # 🔮 Geplant — JSON-Schema der Eingabe
    returns: Schema,        # 🔮 Geplant — JSON-Schema der Ausgabe
    requires: list[str],    # 🔮 Geplant — Systemvoraussetzungen
}
```

### 3.3 Tool-Kategorien

**Implementiert (9 Tools):**

| Tag | Tools | Zugriff auf | Status |
|---|---|---|---|
| `filesystem` | `read_file`, `write_file`, `append_file`, `list_dir`, `workspace_status` | Dateisystem (Pfad-validiert) | ✅ |
| `memory` | `query_memory`, `log_diary` | WORKING/MEMORY/, WORKING/DIARY/ | ✅ |
| `analysis` | `analyze`, `summarize` | LLM-Backend (L0) | ✅ |
| `voice` | `tts`, `stt`, `voice_config`, `voice_talk`, `voice_greeting` | Dashboard Voice (L5) | ✅ |
| `voice_action` | `classify_intent`, `identity_update` | Voice Action Pipeline (L5) | ✅ |

**Geplant (Design):**

| Kategorie | Tools | Zugriff auf | Status |
|---|---|---|---|
| `workspace` | `read_workpaper`, `write_workpaper`, `read_whitepaper`, `write_diary`, `read_guidelines` | WORKING/ (Körper) | 🔮 |
| `context` | `load_context_always`, `load_context_agenda`, `load_context_query` | WORKING/ → JIT 3-Stage | 🔮 |
| `session` | `start_session`, `end_session`, `create_workpaper`, `close_workpaper` | WORKING/WORKPAPER/ | 🔮 |
| `science` | `science_research`, `science_validate`, `science_hypothesize` | SCIENCE-Pipeline | 🔮 |
| `network` | `http_get`, `http_post` | Internet | 🔮 |
| `nostr` | `nostr_publish`, `nostr_subscribe`, `nostr_query` | MantisNostr Netzwerk | 🔮 |

### 3.4 ToolRegistry API

**Implementiert:**

```python
class ToolRegistry:
    """Zentrale Whitelist aller verfügbaren Tools."""

    def __init__(self, permission_level: int = 2):
        """Erstellt Registry mit Security-Level-Schwelle."""

    def register(self, tool: Tool) -> None:
        """Tool registrieren. Überschreibt bei Namens-Duplikat."""

    def get(self, name: str) -> Tool | None:
        """Exact lookup nach Name."""

    def resolve(self, action: str) -> Tool | None:
        """Fuzzy-Resolution: exact match → contains-match (case-insensitive)."""

    def is_allowed(self, tool: Tool) -> bool:
        """Prüft ob Tool.security_level <= permission_level."""

    def list_tools(self) -> list[Tool]:
        """Alle registrierten Tools."""

    def list_available(self) -> list[Tool]:
        """Nur Tools die am aktuellen Permission-Level erlaubt sind."""

    def get_tool_descriptions(self) -> str:
        """Formatiert Tool-Liste für Planner System-Prompt."""
```

**Geplant (Design-Erweiterung):**

```python
class ToolRegistry:
    def execute(self, name: str, params: dict) -> ToolResult:
        """Schema validieren → ausführen → Result zurückgeben."""

    def validate_dependencies(self, tool_names: list[str]) -> ValidationResult:
        """Prüft ob alle geforderten Tools registriert sind."""

    def list_tools_for_agenda(self, agenda: Agenda) -> ToolContext:
        """Agenda-basiertes Filtering (Rucksack-Metapher, §3.7)."""
```

### 3.5 Security-Levels

**Implementiert:** Integer-basiert (1/2/3) statt String-basiert.

| Level (int) | Level (Design) | Erlaubt | Beispiele |
|---|---|---|---|
| 1 | `read` | Nur lesen, keine Seiteneffekte | `read_file`, `query_memory`, `list_dir`, `workspace_status`, `analyze`, `summarize` |
| 2 | `write` | Lesen + Schreiben | `write_file`, `append_file`, `log_diary` |
| 3 | `full` | Alles inkl. externe Prozesse | (reserviert für network, nostr) |

> Design hatte 4 Levels (read/write/execute/admin). Implementierung vereinfacht auf 3 Integer-Levels. Reicht für aktuelle 9 Tools. Bei Bedarf erweiterbar.

### 3.6 Prinzip: Whitelist statt dynamisches Laden

| Eigenschaft | Dynamisches Laden | Whitelist-Registry (gewählt) |
|---|---|---|
| Vorhersagbarkeit | LLM sieht nur, was geladen wird | LLM sieht alle verfügbaren Tools |
| Sicherheit | Code-Injection möglich | Nur registrierte Tools existieren |
| Debugging | Fehler erst zur Laufzeit | Fail-fast bei fehlendem Tool |
| Token-Budget | Variabel, unkontrolliert | Planbar, begrenzt |

### 3.7 Agenda-basiertes Tool-Filtering

#### Die Überlegung

Eine zentrale Registry mit Whitelist löst das Sicherheitsproblem. Aber: 50+ Tools im LLM-Kontext erzeugen ein neues Problem — **Entscheidungskomplexität**. Ein LLM, das zwischen 50 Tools wählen muss, plant schlechter als eines, das 12 relevante sieht.

Die Lösung kommt aus zwei bestehenden Konzepten, die hier zusammenfließen:

1. **JIT Context Loading** (WH-WORKING §5): Nicht alles laden — nur was die Agenda braucht
2. **Agenda als Filter** (WH-IDENTITY §4): Die Agenda bestimmt, was relevant ist

Angewendet auf die Tool-Registry ergibt sich: **Die Agenda bestimmt, welche Tool-Kategorien der Planner sieht.**

#### Das Konzept: Rucksäcke

Die Registry ist ein Schrank voller Rucksäcke. Jede Tool-Kategorie ist ein Rucksack. Der Agent nimmt nicht alle Rucksäcke auf jede Tour mit — er wählt basierend auf seiner Agenda.

```
Registry (Schrank)
├── workspace-Rucksack    → read_workpaper, write_diary, read_guidelines, ...
├── memory-Rucksack       → query_ltm, ingest_ltm, search_memory, ...
├── context-Rucksack      → load_context_always, _agenda, _query
├── session-Rucksack      → start_session, create_workpaper, close_workpaper, ...
├── llm-Rucksack          → llm_complete, llm_embed, llm_summarize
├── science-Rucksack      → science_research, science_validate, science_hypothesize
├── file_io-Rucksack      → read_file, write_file, list_dir, move_file
├── network-Rucksack      → http_get, http_post
└── nostr-Rucksack        → nostr_publish, nostr_subscribe, nostr_query
```

#### Agenda → Rucksack-Mapping

Die Agenda-Definition in `identity/agenda/` erhält ein neues Feld `tool_categories`:

```yaml
# identity/agenda/coding.yaml
name: coding
description: "Softwareentwicklung und Code-Arbeit"
tool_categories:
  always: [workspace, memory, session]      # Immer dabei (Basis-Rucksäcke)
  primary: [llm, file_io]                   # Kern der Aufgabe
  optional: [science, network]              # Bei Bedarf nachladen (JIT Stage 3)
  excluded: [nostr]                         # Bewusst ausgeschlossen
```

```yaml
# identity/agenda/research.yaml
name: research
description: "Recherche und Wissensvalidierung"
tool_categories:
  always: [workspace, memory, session]
  primary: [llm, network, science]
  optional: [file_io]
  excluded: [nostr]
```

```yaml
# identity/agenda/publish.yaml
name: publish
description: "Inhalte veröffentlichen"
tool_categories:
  always: [workspace, memory, session]
  primary: [nostr, llm]
  optional: [network]
  excluded: [science, file_io]
```

#### Umsetzung im Tick-Cycle

```
Bootstrap:
  1. Registry laden (alle Tools)
  2. Agenda auflösen → soul(t)
  3. tool_categories aus Agenda extrahieren
  4. Planner-Kontext bauen:
     visible_tools = registry.list_tools(categories=always + primary)
     → ~12-18 Tools statt 50+

Pro Tick (on-demand):
  5. Planner braucht Tool aus "optional" Kategorie?
     → JIT Stage 3: registry.list_tools(category=optional_cat)
     → Ergänzt den Kontext für diesen Tick
  
  6. Planner braucht Tool aus "excluded"?
     → WARNUNG: "Tool nostr_publish ist für Agenda 'coding' ausgeschlossen"
     → Observer notiert, RFL kann Agenda-Wechsel vorschlagen
```

#### Erweiterung der ToolRegistry API

```python
class ToolRegistry:
    # ... bestehende Methoden ...

    def list_tools_for_agenda(self, agenda: Agenda) -> ToolContext:
        """Gibt gefilterte Tool-Liste basierend auf Agenda zurück.

        Returns ToolContext mit:
          - visible: list[ToolSummary]     (always + primary)
          - available: list[str]           (optional — Namen für JIT)
          - excluded: list[str]            (excluded — für Warnungen)
          - token_estimate: int            (geschätzter Token-Verbrauch)
        """

    def request_optional(self, category: str, agenda: Agenda) -> list[ToolSummary]:
        """JIT-Nachladen einer optionalen Kategorie für den aktuellen Tick."""
```

#### Erwarteter Mehrwert

| Dimension | Ohne Filtering | Mit Agenda-Filtering | Verbesserung |
|---|---|---|---|
| **Token-Budget** | ~5k Token (alle Tools) | ~1.5-2k Token (gefiltert) | **60-70% weniger** |
| **Planungsqualität** | LLM wählt aus 50+ Tools | LLM wählt aus 12-18 Tools | **Weniger Fehlentscheidungen** |
| **Relevanz** | Nostr-Tools bei Code-Arbeit sichtbar | Nur aufgabenrelevante Tools | **Kein Rauschen** |
| **Sicherheit** | Alle Tools immer verfügbar | Excluded = aktive Sperre | **Agenda-basierte Zugriffskontrolle** |
| **JIT-Integration** | Token-Budget für Tools fix | Tools fließen in JIT Stage 2 ein | **Konsistentes Budget-Management** |
| **Debugging** | "Warum hat der Agent http_post benutzt?" | Agenda sagt: excluded → Warnung | **Nachvollziehbare Entscheidungen** |

#### Zusammenspiel mit bestehendem JIT

Das Tool-Filtering ordnet sich nahtlos in die drei JIT-Stages (WH-WORKING §5) ein:

```
JIT Stage 1 (Always, ~3k):
  base.md + active workpaper + always-Tools

JIT Stage 2 (Agenda, ~8k):
  Agenda-relevante Whitepapers + Memory + primary-Tools
  → Tool-Filtering passiert HIER

JIT Stage 3 (Query, ~5k pro Tick):
  On-demand Memory-Abfragen + optional-Tools bei Bedarf
  → Tool-Nachladen passiert HIER
```

Die Registry bleibt **eine** — vollständig, validiert, fail-fast. Aber der **Planner-Kontext** sieht nur den relevanten Ausschnitt. Die Agenda ist der Kurator.

---

## §4 Skill-Kasten

### 4.1 Definition

Ein **Skill** ist ein Orchestrierungsrezept — eine Kombination aus Instruktionen (Prompt), Workflow-Logik und Tool-Dependencies. Skills sind **Procedural Memory** in Aktion.

### 4.2 Format: Markdown + YAML Hybrid

```markdown
---
name: research_and_validate
version: 0.1.0
description: "Recherchiert ein Thema und validiert über SCIENCE"
requires_tools:
  - llm_complete
  - http_get
  - write_workpaper
  - science_validate
category: knowledge
trigger: manual | planner
max_retries: 2
---

# Skill: Research & Validate

## System-Prompt
Du bist ein Recherche-Agent. Dein Ziel ist es, {topic} zu untersuchen
und die Ergebnisse über die SCIENCE-Pipeline zu validieren.

## Workflow

### Step 1: Recherche
- tool: llm_complete
- input: "Recherchiere {topic} mit Fokus auf {focus}"
- output: $research_result

### Step 2: Quellenprüfung
- tool: http_get
- input: $research_result.sources[0..3]
- output: $source_checks
- on_failure: skip_and_note

### Step 3: SCIENCE-Validierung
- tool: science_validate
- input:
    claim: $research_result.summary
    sources: $source_checks
    confidence_threshold: 0.7
- output: $validation

### Step 4: Dokumentation
- tool: write_workpaper
- input:
    title: "Research: {topic}"
    content: $validation.report
- condition: $validation.passed == true
```

### 4.3 Skill-Verzeichnis

```
WORKSPACE/WORKING/TOOLS/
└── skills/
    ├── research_and_validate.md
    ├── code_review.md
    ├── diary_entry.md
    ├── ltm_ingest.md
    └── nostr_publish.md
```

> **Warum in WORKING/TOOLS/?** Skills sind AAMS-Body — Rezepte, die der Agent gelernt hat. Tools (Implementierungen) sind Runtime-Code in `core/`. Diese Trennung ist analog zu: Hände (Tools in core/) vs. Wissen wie man sie benutzt (Skills in WORKING/).

### 4.4 SkillExecutor API

```python
class SkillExecutor:
    """Führt Skills aus: parst Workflow, orchestriert Tool-Calls."""

    def __init__(self, registry: ToolRegistry, skill_dir: str):
        """Alle Skills laden, Tool-Dependencies gegen Registry validieren."""

    def load_skill(self, name: str) -> Skill:
        """Markdown+YAML parsen → Skill-Objekt."""

    def validate(self, skill: Skill) -> ValidationResult:
        """Alle requires_tools in Registry? Schema-kompatibel?"""

    def execute(self, skill: Skill, context: dict) -> SkillResult:
        """Workflow Step für Step:
        - Tool aus Registry holen → execute → Output in State
        - on_failure: retry | skip_and_note | abort
        - Conditions: Ausdrücke über State-Variablen
        """

    def list_skills(self, category: str = None) -> list[SkillSummary]:
        """Für Planner-Kontext: Name + Description aller Skills."""
```

---

## §5 Integration in den Tick-Cycle

### Executor-Erweiterung

Der Planner erzeugt eine Action. Der Executor unterscheidet:

```
Planner
  ↓ action = { type: "skill" | "tool", name: str, params: dict }
Executor
  ├── type == "skill" → SkillExecutor.execute(skill, context)
  │                        ↓ (pro Step im Workflow)
  │                      ToolRegistry.execute(tool, params)
  │
  └── type == "tool"  → ToolRegistry.execute(tool, params)
Observer
  ↓ beobachtet SkillResult oder ToolResult
```

### Kontext-Loading als Tool-Chain

Bisher war `context.py` ein Core-Modul. Jetzt ist Context-Loading eine Tool-Chain:

```
Bootstrap:
  1. ToolRegistry.execute("load_context_always", {})     → ~3k tokens
  2. ToolRegistry.execute("load_context_agenda", {agenda}) → ~8k tokens

Pro Tick (on-demand):
  3. ToolRegistry.execute("load_context_query", {query})  → ~5k tokens
```

### Session-Management als Tool-Chain

```
Start:
  ToolRegistry.execute("start_session", {})
  ToolRegistry.execute("create_workpaper", {title, date})

Ende:
  ToolRegistry.execute("close_workpaper", {decisions, next_steps})
  ToolRegistry.execute("ingest_ltm", {workpaper_path})
  ToolRegistry.execute("end_session", {})
```

---

## §6 Körper-Interface Prinzip

### Die Regel

> **L3 (Loop) berührt L2 (Körper) nie direkt.**  
> Jeder Zugriff auf WORKING/ läuft über ein registriertes Tool in L4.

### Warum?

1. **Nachvollziehbarkeit:** Jeder Körper-Zugriff ist ein Tool-Call im Log
2. **Security:** Zugriffe haben Security-Levels, nicht alle Module dürfen alles
3. **Testbarkeit:** Tools können gemockt werden — Loop-Tests ohne Dateisystem
4. **Austauschbarkeit:** WORKING/ könnte auch eine DB sein — nur die Tool-Implementierung ändert sich

### Analogie

```
Mensch:
  Gehirn (denken)  →  Nervenbahnen (signalisieren)  →  Hände (greifen)  →  Objekte (Welt)

MantisClaw:
  Core/Loop (denken)  →  Executor (delegieren)  →  Tools (ausführen)  →  WORKING/ (Körper)
```

---

## §7 Bootstrap-Sequenz (geschärft)

```
1. llm.py initialisieren                          → L0 Backend verfügbar
2. ToolRegistry.__init__(whitelist_path)           → Alle Tools laden + validieren
3. SkillExecutor.__init__(registry, skill_dir)     → Alle Skills laden + Dependencies prüfen
4. Falls Tool/Skill-Dependency fehlt → FATAL       → Fail-fast, kein Start
5. registry.execute("start_session", {})           → Session öffnen
6. identity.compute(base, agenda, context)         → soul(t) berechnen
7. registry.execute("load_context_always", {})     → JIT Stage 1
8. registry.execute("load_context_agenda", {soul}) → JIT Stage 2
9. Planner erhält: list_tools() + list_skills()    → Verfügbare Aktionen
10. Loop startet                                    → Erster Tick
```

---

## §8 Abgrenzungstabelle

| Aspekt | Tool | Skill |
|---|---|---|
| **Granularität** | Atomar (eine Funktion) | Zusammengesetzt (Workflow) |
| **Format** | `.py` (Code) | `.md` mit YAML-Header (Rezept) |
| **Zustand** | Stateless | Stateful (Workflow-State pro Ausführung) |
| **Ort** | `core/registry/tools/` | `WORKING/TOOLS/skills/` |
| **Schicht** | L4 (Runtime-Fähigkeit) | L5 (AAMS Body / Procedural Memory) |
| **Erstellt von** | Entwickler | Entwickler oder Agent |
| **Sicherheit** | Security-Level pro Tool | Erbt Security-Level der verwendeten Tools |
| **LLM-Sichtbarkeit** | Name + Description + Schema | Name + Description + System-Prompt |
| **Analogie** | Hand / Werkzeug | Rezept / Anleitung |

---

## §9 Offene Fragen (WIP)

> Diese Fragen sind bewusst offen gelassen — sie treiben die Weiterentwicklung.

### F1: Skill-Generierung durch Agent
Kann MantisClaw selbst neue Skills erstellen und in `WORKING/TOOLS/skills/` ablegen?  
→ Wäre **Procedural Memory** in Aktion: Agent lernt neues Rezept, speichert es.  
→ Security-Implikation: Generierte Skills dürfen nur `read`/`write`-Tools nutzen?

### F2: Skill-Versionierung & Lifecycle
Unterliegen Skills dem Workpaper-Lifecycle (OFFEN → GESCHLOSSEN)?  
Oder sind sie stabil wie Whitepapers?  
→ Vermutlich: Skills werden über Workpaper entwickelt, dann als stabile `.md` abgelegt.

### F3: Tool-Kontext-Budget
Wie viele Token verbraucht `list_tools()` + `list_skills()` im LLM-Kontext?  
→ Muss in JIT-Budget (WH-WORKING §5) eingeplant werden.  
→ Hypothese: ~2k Token für Registry-Übersicht, ~1k für Skill-Übersicht.

### F4: Verschachtelte Skills
Kann ein Skill einen anderen Skill aufrufen?  
→ Erhöht Wiederverwendbarkeit, aber auch Komplexität.  
→ Alternative: Flache Skills, Komposition nur durch Planner.

### F5: Context-Loading — Tool oder Sonderfall?
`load_context_*` als Tools macht die Architektur sauber. Aber: Context muss **vor** dem ersten Planner-Aufruf geladen sein. Bootstrap-Sonderfall?  
→ Bootstrap-Sequenz (§7) löst das — aber: was wenn ein Tick neuen Context braucht?

### F6: Core-Refactoring Tiefe
Wie weit wird WH-CORE angepasst?  
→ Minimal: Executor delegiert an Registry  
→ Maximal: workpaper.py, ltm.py, context.py, session.py werden komplett zu Tools  
→ **Empfehlung:** Schrittweise. Erst Registry + SkillExecutor als neue Module, dann Migration.

---

## §10 Entscheidungen

| # | Entscheidung | Begründung |
|---|---|---|
| E1 | Whitelist-Registry statt dynamisches Laden | Vorhersagbarkeit, Sicherheit, Fail-fast |
| E2 | Skills als Markdown+YAML in WORKING/TOOLS/ | AAMS-konform, lesbar, Procedural Memory |
| E3 | Tools als Python in core/registry/tools/ | Runtime-Code, nicht AAMS-Body |
| E4 | Planner kann Tool oder Skill wählen | Flexibilität: atomar oder orchestriert |
| E5 | Fail-fast bei fehlenden Dependencies | Kein Start mit unvollständiger Registry |
| E6 | Security-Levels (read/write/execute/admin) | Granulare Zugriffskontrolle |
| E7 | Körper-Zugriff nur über Tools | Saubere Schichtentrennung L3→L4→L2 |
| E8 | Schichtenmodell erweitert (L5 für Skills) | Skills sind Procedural Memory, nicht Runtime |

---

## Changelog

| Version | Datum | Änderung |
|---|---|---|
| 0.1.0-WIP | 2026-04-09 | Initiale Version: Registry, Skills, Körper-Interface |
| 0.2.0 | 2026-04-10 | Implementation-Status: 8 Tools, Registry API, Security-Levels (int), Fuzzy-Matching. Design vs. Realität synchronisiert. |
| 0.2.1 | 2026-04-10 | 9 Tools (workspace_status hinzu). log_diary gehärtet: Dedup + Rate-Limit (3/Tag) + 120-Zeichen-Limit. analyze/summarize Level 2→1 korrigiert. |
| 0.3.0 | 2026-04-15 | 13 Tools: +llm_management (list_models, switch_model), +loop_monitor (loop_monitor, token_budget). Struktur-Dokumentation aktualisiert. |
| 0.4.0 | 2026-04-15 | +Voice-Tools (L5): TTS, STT, Voice-Config, Voice-Talk, Greeting, Action-Classifier, Identity-Handler. Voice Assistant als L5-Erweiterung dokumentiert. Whitepapers in System-Context integriert. |
