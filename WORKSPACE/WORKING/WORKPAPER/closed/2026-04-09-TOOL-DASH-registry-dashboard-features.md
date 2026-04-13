# WP — Tool Registry + Dashboard Features

**Datum:** 2026-04-09  
**Agent:** GitHub Copilot (Claude Opus 4.6)  
**Topic:** TOOL / DASH  
**Status:** OPEN  

---

## Session Goal

Vier zusammenhängende Features implementieren:
1. core/registry/ — Tool-Registry Skeleton (Kernregel L3→L4)
2. Dashboard: Thinking-Blocks — `<think>`-Tags collapsible rendern
3. Dashboard: Runtime-Integration — API zum Beobachten/Steuern des Runtime-Loops
4. Dashboard: Workpaper-Sidebar — R2 mit klickbaren Workpapers, R3 Runtime-Status, R4 Tools

---

## Ergebnisse

### 1. Tool Registry (`core/registry/`)

**Architektur:** 
- `core/registry/__init__.py` — Package, exportiert `ToolRegistry` + `Tool`
- `core/registry/registry.py` — Zentrales Registry mit Whitelist, Security-Levels, Action-Mapping
- `core/registry/tools/` — Built-in Tools:
  - `filesystem.py` — read_file, write_file, append_file, list_dir (path-validated)
  - `memory.py` — query_memory, log_diary (pointer-only format)
  - `analysis.py` — analyze, summarize (LLM-powered)

**Kernregel umgesetzt:** L3 (Runtime/Executor) greift auf L2 (AAMS/Workspace) NUR über L4 (Registry) zu.

**Features:**
- 8 Tools registriert, alle mit Security-Levels (1=read, 2=write, 3=full)
- Fuzzy Action-Matching: Planner kann freie Strings nutzen, Executor matched gegen Tool-Namen
- Tool-Beschreibungen werden in den Planner System-Prompt injiziert → LLM weiß welche Tools existieren
- Path-Validation verhindert Zugriff außerhalb erlaubter Pfade

### 2. Executor + Planner Updates

**Planner (`core/planner.py`):**
- `tool_descriptions` Parameter → LLM bekommt Tool-Liste im System-Prompt
- Prompt-Format aktualisiert: "Nutze NUR registrierte Tool-Namen als ACTION"

**Executor (`core/executor.py`):**
- Fuzzy-Matching in `_execute_step`: wenn exakter Match fehlschlägt, wird Tool-Name in Action-String gesucht
- Verhindert "No handler for action" bei leicht abweichenden LLM-Antworten

**Runtime (`core/runtime.py`):**
- `_register_tools()` Methode erstellt alle Tools und registriert sie
- Tools werden nach Erstellung in Executor als Handler gewired
- Tool-Beschreibungen werden in Planner injiziert
- Security-Level aus `config/default.yaml` (security.permission_level)

### 3. Dashboard: Thinking-Blocks

**HTML (`templates/index.html`):**
- `<think>` Tags werden zu `<details class="thinking-block">` konvertiert
- Collapsible: standardmäßig geschlossen, Klick öffnet
- Während SSE-Streaming: Live-Rendering mit unclosed-block-handling
- In gespeicherten Nachrichten: Jinja2-Filter mit `|safe`

**CSS (`static/style.css`):**
- `.thinking-block` — Dark border, rounded, subtle background
- `.thinking-content` — Max-height 300px, scrollbar, monospace-like
- Summary zeigt 💭 Thinking...

### 4. Dashboard: Runtime Integration

**Neue API-Endpoints:**
- `GET /api/runtime` — Tick-Count, Health, Heartbeat, registrierte Tools, Session-Info
- `GET /api/workpapers` — Liste aller Workpapers (open + closed)
- `GET /api/workpapers/{name}` — Einzelnes Workpaper lesen (mit Path-Traversal-Schutz)

**Dashboard-Referenz:**
- `set_runtime(instance)` — erlaubt dem Runtime-Loop sich beim Dashboard zu registrieren
- `_runtime_instance` — globale Referenz, None wenn Dashboard standalone läuft

### 5. Dashboard: Sidebar-Erweiterungen

**R2 · Workpapers:**
- Klickbar: Zeigt Workpaper-Inhalt in L4-Box (links)
- Tooltips mit vollem Dateinamen
- Count-Badge im Header

**R3 · Runtime:**
- Live-Status via Polling (alle 5s)
- Zeigt: Tick-Count, Health, Heartbeat
- Grüner/roter Dot für running/stopped

**R4 · Tools:**
- Liste aller registrierten Tools
- Zeigt Tool-Name (monospace, blau) + Security-Level
- Tooltips mit Tool-Beschreibung

---

## File Protocol

### Created
- `core/registry/__init__.py` — Tool Registry package
- `core/registry/registry.py` — ToolRegistry + Tool classes
- `core/registry/tools/__init__.py` — Tools package
- `core/registry/tools/filesystem.py` — 4 filesystem tools
- `core/registry/tools/memory.py` — 2 memory tools
- `core/registry/tools/analysis.py` — 2 LLM analysis tools

### Modified
- `core/runtime.py` — Registry import, _register_tools(), tool_descriptions injection
- `core/planner.py` — tool_descriptions parameter, updated system prompt with tool list
- `core/executor.py` — Fuzzy action matching in _execute_step
- `dashboard/app.py` — _runtime_instance, set_runtime(), /api/runtime, /api/workpapers endpoints
- `dashboard/templates/index.html` — Thinking-blocks, R2 clickable WPs, R3 runtime, R4 tools, pollRuntime JS
- `dashboard/static/style.css` — Thinking-block styles, tool-item styles, wp-item hover

---

## Decisions

- Tool Registry ist die **einzige** Brücke zwischen L3 und L2 (Kernregel)
- Fuzzy-Matching statt strikte Action-Names → robust gegen LLM-Varianz
- Dashboard Runtime-API ist optional → Dashboard läuft auch standalone
- Thinking-Blocks verwenden native `<details>` statt JS-Library
- 5s Polling für Runtime-Status statt WebSocket → simpler, reicht für Status

---

## Next Steps

- [ ] Runtime + Dashboard zusammen starten (gemeinsamer Prozess oder separate mit set_runtime)
- [ ] Skill Executor: Markdown+YAML Skills aus WORKING/TOOLS/skills/ als neue Tool-Kategorie
- [ ] Observer-Metriken in R3 anzeigen (success_rate, failed_actions etc.)
- [ ] Workpaper-Viewer: Markdown-Rendering statt raw text
- [ ] RFL Reflection-Loop in Observer → reflect → Planner integrieren

