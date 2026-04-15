# WHITEPAPER: MantisClaw Core — Runtime & Loop

**Dokument:** WH-CORE
**Version:** 0.4.0
**Erstellt:** 2026-04-08
**Aktualisiert:** 2026-04-15
**Status:** DRAFT
**Herkunft:** WP-005 (Bootstrap), WP-RFL, WP-JIT-Context, SCIENCE-Review, WP-TOOL-DASH

---

## 1. Zusammenfassung

MantisClaw ist ein eigenständiges Agent-Loop-Framework mit **emergenter Identität**. Dieses Whitepaper beschreibt den **Core** — das Gehirn: den Heartbeat-Loop, die Module die denken, handeln und beobachten, und die Mechanismen die das System selbstkorrigierend machen.

Für die Identity-Berechnung siehe **WH-IDENTITY**. Für die Arbeitsstruktur siehe **WH-WORKING**.

---

## 2. Kernformel

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

Die Soul wird bei jedem Tick berechnet. Wie sie berechnet wird → WH-IDENTITY. Was in `working_context` steckt → WH-WORKING.

---

## 3. Schichtenmodell

```
┌─────────────────────────────────────────┐
│  L7  Netzwerk / MantisNostr             │  ← Mesh, Relays (extern)
├─────────────────────────────────────────┤
│  L6  Security                           │  ← Audit, Permissions (Querschnitt)
├─────────────────────────────────────────┤
│  L5  Skills (WORKING/TOOLS/skills/)     │  ← Orchestrierung, Procedural Memory
├─────────────────────────────────────────┤
│  L4  Tool-Registry (core/registry/)     │  ← Alle Fähigkeiten, inkl. Körper-Zugriff
├─────────────────────────────────────────┤
│  L3  Runtime — Das Gehirn (core/)       │  ← Heartbeat, Planner, Executor, Observer
├─────────────────────────────────────────┤
│  L2  AAMS Body (WORKSPACE/WORKING/)     │  ← Workpapers, Whitepapers, LTM, Diary (integriert)
├─────────────────────────────────────────┤
│  L1  Identität (identity/)              │  ← base, agenda, account, social, decentral
├─────────────────────────────────────────┤
│  L0  LLM Backend (core/llm.py + config) │  ← LM Studio / Ollama / Cloud
└─────────────────────────────────────────┘
```

> **Kernregel:** L3 (Loop) berührt L2 (Körper) nie direkt — jeder Zugriff auf WORKING/ läuft über ein registriertes Tool in L4. Details → **WH-TOOLS**.

---

## 4. Core-Module (L3)

> L3-Module sind das **Gehirn** — sie denken, planen, handeln und bewerten. Zugriff auf den Körper (L2) läuft ausschließlich über registrierte Tools (L4). Siehe WH-TOOLS.

### 4.1 runtime.py — Heartbeat-Loop

Der zentrale Loop. Koordiniert alle anderen Module.

```
┌──────────────────────────────────────┐
│              TICK START              │
│                                      │
│  1. Session prüfen (open/resume)     │
│  2. Identity laden → soul(t)         │
│  3. Context Loading (JIT, 3 Stufen)  │
│  4. Hooks prüfen → Trigger?          │
│  5. Planner → Plan erstellen         │
│  6. Executor → Plan ausführen        │
│  7. Observer → Ergebnis bewerten     │
│  8. RFL (Reflection-Loop)            │
│     ├─ OK? → weiter                  │
│     └─ FAIL? → Reflect → Replan     │
│        → Re-Execute → Re-Observe    │
│        → Max 2 Retries, dann Eskal. │
│  9. Procedural Memory updaten        │
│ 10. LTM updaten falls nötig          │
│ 11. Sleep(heartbeat_interval)        │
│                                      │
│              TICK END                │
└──────────────────────────────────────┘
```

**Konfiguration:** `config/default.yaml`
- `heartbeat_interval`: 10s
- `max_retries`: 3
- `session_timeout`: 3600s
- `reflection.max_retries`: 2
- `reflection.cooldown_ticks`: 3

### 4.2 planner.py — Denken

Nimmt `soul(t)` + Hooks + Memory-Query + **Guidelines** → erzeugt einen Plan.
Plan = Liste von Steps mit Tool-Calls.

**Implementiert (v0.1.0):**
- `tool_descriptions: str` — wird vom Runtime injiziert (`registry.get_tool_descriptions()`)
- System-Prompt enthält verfügbare Tools: _"Nutze NUR diese als ACTION"_
- Plan-Format: `STEP: <tool_name> | <target> | <beschreibung>`
- Output: `Plan(goal, steps, reasoning)` — geparst aus LLM-Response

**Geplant:**
- Context Loader für JIT Stage 3 (on-demand Nachfragen)
- `reflection_context` bei Reflection-Reruns — was beim letzten Versuch schief ging
- Guidelines als zusätzlicher Planner-Input

Nimmt Plan → führt Steps aus → gibt Results zurück.
**Tool-Dispatch:** Alle Aktionen laufen über die Registry (§4.6). Der Executor ruft nie direkt L2-Module auf.
Retry-Logik bei Tool-Fehlern (`max_retries`).

**Implementiert (v0.1.0):**
- `register_handler(action, handler)` — Registry-Tools werden als Handler verdrahtet
- **Fuzzy Action Matching:** Exakter Match zuerst, dann Prüfung ob ein Tool-Name im Action-String enthalten ist (case-insensitive). Fängt LLM-generierte Varianten ab.
- `ExecutionResult` mit `all_succeeded`, `summary` Properties

**Geplant (als registrierte Tools):**
- `science.research` — Erkenntnisse sammeln
- `science.validate` — Claims prüfen
- `science.hypothesize` — Hypothesen ableiten

### 4.4 observer.py — Beobachten + Bewerten

Nimmt Results → prüft gegen Diary + Guidelines.

Zwei Outputs:
1. **Assessment** — Bewertung des Ergebnisses (OK / PARTIAL / FAILED / ANOMALY)
2. **Lektionen** — Extrahierte Arbeitsweisen für Procedural Memory (→ GUIDELINES/)

```python
class Assessment:
    status: str          # OK | PARTIAL | FAILED | ANOMALY
    needs_revision: bool # True wenn FAILED oder ANOMALY
    details: str         # Was genau passiert ist
```

Der Observer entscheidet ob der **Reflection-Loop** anspringt (`needs_revision`).

### 4.5 reflect() — Selbstkorrektur (RFL)

Neues Modul. Wird vom Observer getriggert wenn `needs_revision = True`.

```python
def reflect(assessment, results, original_plan):
    """Analysiert warum ein Plan gescheitert ist."""
    return {
        "what_wrong": "...",      # Was hat nicht funktioniert?
        "why_wrong": "...",       # Warum?
        "correction": "...",      # Was soll der Planner anders machen?
        "confidence": 0.0-1.0     # Wie sicher ist die Analyse?
    }
```

Datenfluss:
```
Observer → needs_revision? → reflect() → Planner (mit reflection_context)
    → Executor → Observer → (max 2 Retries, dann Eskalation)
```

Eskalation = Diary-Eintrag + nächster Tick mit frischem Kontext + optional menschliche Intervention.

### 4.6 registry/ — Tool-Registry (L4)

Verwaltet alle verfügbaren Tools als Whitelist. Implementiert in `core/registry/`.

**Implementiert (v0.1.0):**

```python
@dataclass
class Tool:
    name: str                              # Eindeutiger Identifier (snake_case)
    handler: Callable[..., Awaitable[Any]] # Async Handler-Funktion
    description: str = ""                   # Für LLM-Kontext
    security_level: int = 2                 # 1=read, 2=read+write, 3=full
    tags: list[str] = []                    # Kategorisierung

class ToolRegistry:
    def register(tool: Tool)               # Tool registrieren (Whitelist)
    def get(name: str) -> Tool | None      # Exact lookup
    def resolve(action: str) -> Tool | None # Fuzzy: exact → contains-match
    def is_allowed(tool: Tool) -> bool     # Prüft permission_level
    def list_tools() -> list[Tool]         # Alle Tools
    def list_available() -> list[Tool]     # Nur erlaubte Tools
    def get_tool_descriptions() -> str     # Für Planner System-Prompt
```

**9 registrierte Tools:**

| Tool | Kategorie | Level | Beschreibung |
|------|-----------|-------|------|
| `read_file` | filesystem | 1 | Datei lesen (Pfad-validiert) |
| `write_file` | filesystem | 2 | Datei schreiben |
| `append_file` | filesystem | 2 | An Datei anhängen |
| `list_dir` | filesystem | 1 | Verzeichnis auflisten |
| `workspace_status` | filesystem | 1 | AAMS Workspace-Struktur anzeigen |
| `query_memory` | memory | 1 | ltm-index.md durchsuchen |
| `log_diary` | memory | 2 | Diary-Eintrag (Pointer-only, Dedup + Rate-Limit max 3/Tag + 120 Zeichen) |
| `analyze` | analysis | 1 | LLM-gestützte Analyse |
| `summarize` | analysis | 1 | LLM-gestützte Zusammenfassung |

**Verdrahtung im Runtime:**
- `_register_tools()` erstellt alle Tools und registriert sie
- Handler werden automatisch in den Executor eingetragen
- Planner bekommt Tool-Beschreibungen als System-Prompt-Teil injiziert

**Geplant (Design in WH-TOOLS):**
- Agenda-basiertes Tool-Filtering (Rucksack-Metapher)
- Workspace-Tools (session, workpaper, ltm, context) — aktuell noch Core-Module
- SCIENCE-Tools, Network-Tools, Nostr-Tools

Der Executor ruft Tools **nur** über die Registry auf — nie direkt.
Details zur Tool-Architektur → **WH-TOOLS**.

### 4.7 skill_executor.py — Skill-Orchestrierung (L5)

Lädt Skill-Dateien aus `WORKING/TOOLS/skills/` und führt mehrstufige Workflows aus.
Ein Skill besteht aus YAML-Frontmatter + Markdown-Anleitung.
Der Skill-Executor löst Tool-Calls pro Schritt auf und delegiert an die Registry.

### 4.8 llm.py — LLM-Backend (L0)

Abstraktion über LLM-Provider. **Local-first** — keine externen Dependencies.

**Priorität:**
1. **LM Studio** (default) — OpenAI-kompatible API auf `localhost:1234/v1`
2. **Ollama** — REST API auf `localhost:11434`
3. **OpenAI** — Cloud, braucht `OPENAI_API_KEY`
4. **Anthropic** — Cloud, braucht `ANTHROPIC_API_KEY`

**Prinzip:** Reines `urllib` für HTTP. Kein externes LLM-Package nötig.

**Features:**
- `complete(messages, system)` — Chat Completion
- `complete_simple(prompt, system)` — Einzeiler-Shortcut
- `check_connection()` — Health-Check

### 4.9 session.py — Session-Management

> **Status:** Noch Core-Modul. Geplante Migration zu Registry-Tool (L4) ausstehend.

AAMS-konform: open → work → close → archive.
Erzeugt/schließt Workpapers automatisch (`auto_workpaper: true`).
Wird von runtime.py direkt importiert (noch nicht über Registry).

### 4.10 workpaper.py — Workpaper-Verwaltung

> **Status:** Noch Core-Modul. Geplante Migration zu Registry-Tool (L4) ausstehend.

Erstellt Workpapers nach AAMS-Naming (`{date}-{topic}-{subtopic}-{description}.md`).
Schreibt File Protocol. Verschiebt nach `closed/` bei Session-End.

### 4.11 ltm.py — Langzeitgedächtnis

> **Status:** Noch Core-Modul. Geplante Migration zu Registry-Tool (L4) ausstehend.
> Parallel existieren `query_memory` und `log_diary` als Registry-Tools in `core/registry/tools/memory.py`.

Ingestiert Workpapers in `MEMORY/ltm-index.md`.
Dual-Track: Markdown (default) oder Vector (ChromaDB, optional).

### 4.12 context.py — Context Loading

> **Status:** Noch Core-Modul. Geplante Migration zu Registry-Tool (L4) ausstehend.

Dreistufiges Loading:
- **Stufe 1 (Always):** Aktuelles Workpaper + LTM-Index (~3k Tokens)
- **Stufe 2 (Agenda):** Relevante Whitepapers + Guidelines (~8k Tokens)
- **Stufe 3 (Query):** Planner fragt on-demand nach (~5k Tokens)

Gesamt-Budget: ~16k Tokens statt 80k+ bei vollem Load. Details → WH-WORKING.
### 5.2 agenda.md — Wurzelknoten

Bestimmt den **Kontext**. Die Agenda filtert, welche Accounts, Kontakte und Trust-Level relevant sind.

### 5.3 account.md — Fähigkeits-Register

Wächst über die Lebenszeit. Jeder Account impliziert Plattform-Verhalten und Normen.

### 5.4 social.md — CRM-State

Beziehungsgraph, gekoppelt an Accounts. Jeder Account öffnet einen sozialen Raum.

### 5.5 decentral.md — Trust-Map

Vertrauen zu Infrastruktur-Knoten (Relays, Git-Hosts, APIs). Bewertung der Außenwelt.

### 5.6 hook.md — Trigger

Definiert, wann der Agent aktiv wird. Events → Aktionen.

---

## 5. Identity (L1)

Sechs Dimensionen: base, agenda, account, social, decentral, hook.
Die Agenda filtert alle anderen Dimensionen kontextabhängig.
Die Soul emergiert bei jedem Tick neu aus diesen Dimensionen + working_context.

Vollständige Beschreibung → **WH-IDENTITY**.

---

## 6. Working System (L2)

Fünf Memory-Schichten: Workpaper, Whitepaper, Diary, LTM, Guidelines (Procedural Memory).
Plus SCIENCE als epistemische Erweiterung.
JIT Context Loading für skalierbare Token-Nutzung.
Wissenskette: Workpaper → Whitepaper → LTM.

Vollständige Beschreibung → **WH-WORKING**.

---

## 7. Bootstrap-Prinzip

**"One File to Bootstrap"** — `.agent.json` genügt.

```
.agent.json gelesen
    → READ-AGENT.md lesen
    → WORKSPACE/ Struktur anlegen (idempotent)
    → Erste Session starten
    → Workpaper erstellen
```

Für Mantis-OS: `mantisagent.json` erweitert `.agent.json` um Agent-Registrierung und Integration-Mode.

---

## 8. Standalone vs. Mantis-OS

| Aspekt | Standalone | In Mantis-OS |
|--------|-----------|--------------|
| Identity | Lokale Dateien | Geteilte Identität möglich |
| Heartbeat | Eigener Loop | Orchestriert durch MOS |
| Netzwerk | Keins | MantisNostr (Nostr-Mesh) |
| Memory | Lokale Markdown-Dateien | Optional shared LTM |
| Agenten | Einer | Mehrere, koordiniert |

---

## 9. Dashboard

MantisClaw hat ein **Web-Dashboard** als Benutzeroberfläche.

**Stack:** FastAPI + Jinja2 + Vanilla JS + SQLite (aiosqlite)

**Architektur:**
- 3-Spalten CSS Grid: Left Sidebar (260px) | Chat (1fr) | Right Sidebar (260px)
- SSE-Streaming für Token-by-Token Chat-Anzeige
- Dark Theme mit CSS Variables
- SQLite-Persistenz: `conversations` + `messages` Tabellen

**Dateien:**
- `dashboard/app.py` — FastAPI-Routes, SSE-Endpoint, Runtime-API
- `dashboard/chat.py` — `stream_chat()` Generator, Model-Discovery (LM Studio + Ollama)
- `dashboard/db.py` — CRUD, aiosqlite, `data/dashboard.db`
- `dashboard/templates/index.html` — Single-Template Jinja2
- `dashboard/static/style.css` — Dark Theme

**Features (implementiert):**
- Chat mit SSE-Streaming + Thinking-Block-Rendering (`<think>` → collapsible `<details>`)
- Model-Switching (alle LM Studio / Ollama Modelle)
- Left Sidebar: Core-Info, Identity, Workspace-Tree, Workpaper
- Right Sidebar: Chat-History, Workpaper-Liste (klickbar), Runtime-Status (Polling), Tool-Liste
- Runtime API: `GET /api/runtime`, `GET /api/workpapers`, `GET /api/workpapers/{name}`
- System-Prompt aus Identity-Dateien (soul(t)-aware)

**Geplant:**
- Runtime + Dashboard gemeinsamer Prozess-Start
- Markdown-Rendering im Chat
- Chat-Management (Löschen, Umbenennen)

---

## 10. Architektur-Beziehungen

```
MantisClaw (Core + Identity + Working + Dashboard)
    ├── WH-CORE     — Runtime, Loop, Gehirn, Dashboard (dieses Dokument)
    ├── WH-IDENTITY  — Emergente Identität, soul(t)
    ├── WH-WORKING   — Arbeitsstruktur, Memory, AAMS
    ├── WH-TOOLS     — Tool-Registry, Skills, Körper-Interface (L4/L5)
    ├── AAMS         — Workspace-Standard (fest integriert, v1.3.0)
    └── MantisNostr  — Netzwerk (optional, L7)
```

---

## 11. Nächste Schritte

1. ~~Core-Module implementieren (runtime.py Loop zuerst)~~ → ✅ Grundgerüst vorhanden
2. ~~LLM-Backend-Abstraktion (llm.py)~~ → ✅ Fertig (LM Studio + Ollama + Cloud)
3. ~~Tool-Registry Skelett (core/registry/)~~ → ✅ 13 Tools registriert (filesystem 5 + memory 2 + analysis 2 + llm_management 2 + loop_monitor 2), Fuzzy-Matching
4. Body-Access-Tools registrieren (session, workpaper, ltm, context) → `core/` Module existieren, Migration zu Registry-Tools ausstehend
5. Skill-Executor (skill_executor.py) implementieren
6. Context Loader als Tool (JIT Loading über Registry)
7. ~~Planner/Executor/Observer~~ → ✅ Implementiert + Tool-Injection + Fuzzy-Matching
8. Reflection-Loop (RFL) implementieren — reflect.py ist Stub
9. Tests
10. Dashboard ↔ Runtime Integration vertiefen (gemeinsamer Prozess)

*Whitepaper. Stabile Architektur-Wahrheit. Wird bei Architektur-Entscheidungen aktualisiert.*
