# LTM Index — MantisClaw

> Long-term memory. Ingested from workpapers, decisions, architecture changes.

---

## Entries

### 2026-04-02 | WP-005 Bootstrap MantisClaw (CLOSED)

**Source:** `WORKPAPER/closed/2026-04-02-bootstrap-mantisclaw.md`  
**Agents:** ogerly (Mensch) + LOS (Agent)

**Kernentscheidungen:**
- MantisClaw ist ein **eigenständiges Agent-Loop-Framework** mit emergenter Identität
- Kernformel: `soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)`
- MantisClaw läuft standalone, wird in Mantis-OS zum Gehirn
- Bootstrap über **"One File" Prinzip**: `.agent.json` → `READ-AGENT.md` → `WORKSPACE/`
- Mantis-OS = Webstuhl-Metapher (Kette=Identität, Schuss=Agenden, Webrahmen=OS)

**Architektur:**
- `core/` — runtime.py, planner.py, executor.py, observer.py, llm.py, session.py, workpaper.py, ltm.py
- `identity/` — base.md, agenda.md, account.md, social.md, decentral.md, hook.md, memory.md, soul.md
- `config/` — default.yaml, .env.example
- AAMS-Workspace vollständig: WHITEPAPER, WORKPAPER, DIARY, MEMORY, LOGS, GUIDELINES, TOOLS, AGENT-MEMORY

**Abgrenzung Standalone vs. Mantis-OS:**
- Standalone: lokale Dateien, ein Agent, ein Heartbeat
- In Mantis-OS: mehrere Agenten, geteilte Identität, Nostr-Bridge, Plugin-Architektur

**Erledigte Nächste Schritte:**
- ✅ Repo lokal angelegt
- ✅ GitHub Repo erstellt (DEVmatrose/MantisClaw)
- ✅ README.md erstellt
- ✅ MantisClaw → MantisNostr Umbenennung erledigt (bestätigt 2026-04-08)

**Offene Fragen (Stand 2026-04-02):**
- Eigenes Whitepaper-Set oder Referenz auf Mantis-OS?
- Wissenskette standalone vs. in Mantis-OS?
- Git Submodules vs. Copy für Integration?

---

### 2026-04-08 | WP-006 Session Review (OPEN)

**Source:** `WORKPAPER/2026-04-08-copilot-session-review.md`  
**Agents:** ogerly (Mensch) + GitHub Copilot (Agent)

**Aktionen:**
- WP-005 geschlossen und archiviert
- MEMORY und DIARY initial befüllt
- mantisagent.json erstellt
- Statusabgleich aller offenen Punkte aus WP-005
- Whitepaper WH-CORE erstellt (Architektur-Wahrheit)
- Alle 8 Core-Module implementiert (waren reine Stubs)
- **LLM-Backend: Local-first Rewrite**
  - Default: LM Studio (localhost:1234, OpenAI-kompatibel)
  - Zweit: Ollama (localhost:11434, REST API)
  - Cloud: OpenAI + Anthropic optional
  - Zero externe Dependencies — reines urllib
  - `check_connection()` für Health-Checks
- Erster erfolgreicher LLM-Call: `qwen3-coder-30b-a3b-instruct` via LM Studio
- Config: backend=lmstudio, model=qwen3-coder-30b-a3b-instruct

**Architektur-Entscheidung: Local-first LLM**
- MantisClaw nutzt standardmäßig lokale LLMs (LM Studio / Ollama)
- Kein API-Key nötig für Default-Setup
- Kein externes Python-Package nötig (urllib statt openai/anthropic/ollama)
- Passt zur Ethik in base.md: Souveränität, eigene Daten

---

## Dashboard (WP-007, 2026-04-08)

**Stack:** FastAPI + Jinja2 + Vanilla JS + SQLite (aiosqlite)

**Architektur:**
- 8-Box Layout: 3-Spalten CSS Grid (Left 260px | Chat 1fr | Right 260px)
- L1: Core (Model-Switcher), L2: Identity, L3: Workspace-Tree, L4: Active Workpaper
- R1: Chat-History, R2: Workpapers, R3+R4: reserved
- SSE-Streaming (EventSource → Token-by-Token Anzeige)
- SQLite: conversations (id, title, model) + messages (id, conv_id, role, content)

**Dateien:**
- `dashboard/db.py` — CRUD, aiosqlite, `data/dashboard.db`
- `dashboard/chat.py` — `stream_chat()` Generator, `list_lmstudio_models()`, `list_ollama_models()`
- `dashboard/app.py` — FastAPI: 3 Page-Routes, 1 SSE-Route, 3 API-Routes, 1 DELETE
- `dashboard/templates/index.html` — Single-Template Jinja2
- `dashboard/static/style.css` — Dark Theme

**Entscheidungen:**
- HTMX nicht verwendet — Vanilla JS + SSE reicht für v0.1
- Blocking urllib-Calls via `asyncio.to_thread()` / `run_in_executor()` entkoppelt
- Chat-History persistent in SQLite (besser als Open WebUI Browser-only)
- System-Prompt baut sich aus Identity-Dateien (soul(t)-aware)

**Bekannte Lücken:**
- `identity/base.md` nicht befüllt → Name/Owner zeigt "(not set)"
- Kein Markdown-Rendering im Chat
- R3/R4 Boxen leer (reserved)

---

### 2026-04-09 | Architektur-Vertiefung Session 1+2 (OPEN→CLOSED)

**Source:** `WORKPAPER/2026-04-09-architektur-vertiefung-session2.md` + 7 weitere Workpapers  
**Agents:** ogerly (Mensch) + GitHub Copilot (Agent)

**Kernentscheidungen:**
- **AAMS-Korrektur:** "braucht AAMS" → "AAMS fest integriert"
- **SCIENCE:** Knowledge Validation Layer als MantisClaw-Feature (nicht AAMS-Spec). Drei Executor-Aktionen: science.research, science.validate, science.hypothesize. Quellengewichtung A/B/C/D.
- **Procedural Memory:** GUIDELINES/ als lernbare Arbeitsweise. Observer extrahiert Lektionen → write_guidelines Tool.
- **Reflection-Loop (RFL):** Observer→reflect()→Planner Rückkanal. Max 2 Retries, dann Eskalation. Cooldown 3 Ticks.
- **JIT Context Loading:** 3-Stage — Always (~3k) + Agenda (~8k) + Query (~5k). Context ist jetzt Tool-Chain, nicht Core-Modul.

**Whitepaper-Restrukturierung:**
- CORE.md → v0.2.0: Nur noch Runtime/Loop (planner, executor, observer, reflect, runtime)
- IDENTITY.md → v0.2.0: Emergente Identität, soul(t), 6 Dimensionen, Abgrenzung
- WORKING.md → v0.2.0: AAMS Body, 5 Memory-Schichten (Working, Episodic, Semantic, Procedural, Epistemisch/SCIENCE), JIT, Wissenskette
- TOOLS.md → v0.1.0-WIP: **Neues Whitepaper**

**WH-TOOLS — Tool-Registry & Skills (v0.1.0-WIP):**
- **Körper-Interface-Prinzip:** L3 (Loop) berührt L2 (Körper) nie direkt → nur über registrierte Tools (L4)
- **Tool-Registry:** Whitelist in `core/registry/`, atomar, stateless, Security-Levels (read/write/execute/admin)
- **Skills:** Orchestrierungs-Rezepte in `WORKING/TOOLS/skills/` (Markdown+YAML), Procedural Memory
- **Schichtenmodell geschärft:** L0 (LLM) → L1 (Identity) → L2 (Body) → L3 (Loop) → L4 (Tools) → L5 (Skills) → L6 (Security) → L7 (Network)
- **Agenda-basiertes Tool-Filtering:** Agenda bestimmt welche Tool-Kategorien sichtbar sind (always/primary/optional/excluded). ~60-70% Token-Einsparung. Integration in JIT Stage 2.
- **Core-Refactoring:** context.py, session.py, workpaper.py, ltm.py → werden zu workspace-Tools in Registry

**Analogie (Rucksack-Metapher):**
- Gehirn = Core/Loop (denken)
- Rucksäcke = Tool-Kategorien (workspace, memory, llm, science, nostr...)
- Werkzeuge = Einzelne Tools (atomar, stateless)
- Bauanleitungen = Skills (Rezepte, Workflows)
- Körper = WORKING/ (passiv, wird über Tools bespielt)
- Agenda bestimmt welche Rucksäcke mitgenommen werden

**SCIENCE Review: MantisClaw vs. State of the Art (~80% Alignment):**
- 10 Claims validiert, 6 Risiken, 6 Hypothesen
- Drei Gaps identifiziert und gelöst: Procedural Memory, RFL, JIT
- CoALA Framework Mapping: Alle 4 Memory-Typen abgedeckt

**Offene Fragen (WH-TOOLS §9):**
- F1: Skill-Generierung durch Agent (Procedural Memory in Aktion?)
- F2: Skill-Versionierung & Lifecycle
- F3: Tool-Kontext-Budget (~2-3k Token?)
- F4: Verschachtelte Skills
- F5: Context-Loading als Tool vs. Bootstrap-Sonderfall
- F6: Core-Refactoring Tiefe (schrittweise empfohlen)

**Dateien aktualisiert:**
- README.md: Architektur-Tree, Loop-Code, Schichtenmodell, Whitepaper-Tabelle
- AGENTS.md: Workspace-Struktur, Kernregel, Core-Module
- READ-AGENT.md: Core-Module, GUIDELINES/TOOLS/SCIENCE Beschreibung, AAMS-Korrektur
- LEGENDE.md: L4-L7, RFL, JIT, SCIENCE, WH-TOOLS

---

### 2026-04-09 | 2026-04-09-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-09-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-09T23:27:42.349224

_Workpaper auto-ingested at session close._

---

### 2026-04-10 | Whitepaper-Sync & Open Points Consolidation

**Source:** Session 2026-04-10 (Whitepaper-Update + WP-Closures)
**Agents:** ogerly (Mensch) + GitHub Copilot (Agent)

**Whitepaper Updates (2026-04-10):**
- WH-CORE: v0.2.0 → v0.3.0 — Registry-Implementierung, Dashboard §9, §4.9-4.12 ehrlicher Status, Nächste Schritte aktualisiert
- WH-TOOLS: v0.1.0-WIP → v0.2.0 — Design vs. Implementierung synchronisiert, 8 Tools dokumentiert, Security-Levels int statt string
- WH-WORKING: v0.2.0 → v0.3.0 — WH-TOOLS in Whitepaper-Liste, AAMS v1.3.0 Diary Reform + Version Centralization

**Konsolidierte Open Points (aus 9 geschlossenen Workpapers):**

1. **Dashboard:**
   - Identity-Dateien befüllen (base.md, agenda.md — nur .example vorhanden)
   - Markdown-Rendering im Chat
   - Chat-Lösch-Button + Conversation-Umbenennung
   - Runtime + Dashboard gemeinsamer Prozess-Start

2. **Tool-Registry (Erweiterung):**
   - Skill Executor (Markdown+YAML Skills parsen + ausführen)
   - Observer-Metriken in R3 Dashboard-Sidebar
   - Workpaper-Viewer mit Markdown-Rendering
   - Workspace-Tools: session, workpaper, ltm, context → Migration von Core zu Registry

3. **Architektur (noch nicht implementiert):**
   - JIT Context Loading — 3-Stage Loader (Design fertig, Code fehlt)
   - Reflection-Loop (RFL) — Observer→reflect→Planner, max 2 Retries (reflect.py ist Stub)
   - Procedural Memory — GUIDELINES/ System (Observer extrahiert Lektionen)
   - SCIENCE Knowledge Validation Layer (Executor-Aktionen: research, validate, hypothesize)

4. **WH-TOOLS Offene Fragen (§9):**
   - F1: Skill-Generierung durch Agent?
   - F2: Skill-Versionierung & Lifecycle
   - F3: Tool-Kontext-Budget (~2-3k Token?)
   - F4: Verschachtelte Skills
   - F5: Context-Loading als Tool vs. Bootstrap-Sonderfall
   - F6: Core-Refactoring Tiefe

---

### 2026-04-10 | 2026-04-10-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-10-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-10T21:02:49.696281
**Note:** 1252 Ticks (tick-987 bis tick-1638), alle erfolgreich. Loop-Stabilität bewiesen. Plan-Beschreibungen fehlten (Bug). Tick-IDs nicht-sequentiell.

_Workpaper auto-ingested at session close._

---

### 2026-04-15 | 2026-04-15-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-15-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-15T19:20:33.048378

_Workpaper auto-ingested at session close._

---

### 2026-04-15 | 2026-04-15-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-15-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-15T19:35:26.643766

_Workpaper auto-ingested at session close._

---

### 2026-04-15 | 2026-04-15-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-15-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-15T19:36:42.631904

_Workpaper auto-ingested at session close._

---

### 2026-04-15 | 2026-04-15-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-15-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-15T19:51:23.815310

_Workpaper auto-ingested at session close._

---

### 2026-04-15 | Voice Integration L5 (WP-VOICE)

**Source:** `WORKPAPER/2026-04-15-voice-integration-dashboard.md`
**Status:** DONE

- Voice Assistant als L5 Layer im Dashboard (TTS/STT/VAD)
- 2-Stage Action Classification Pipeline: IDENTITY / SYSTEM / CHAT
- Identity-Handler: Name, Stimme, Persönlichkeit per Sprache konfigurierbar
- System-Context: Projekt, Workpapers, Whitepapers in LLM-Prompts
- VAD-Bugfix: Warmup, loudCount, Echo-Vermeidung
- Whitepapers aktualisiert: CORE v0.4.0, TOOLS v0.4.0, IDENTITY §9
- README v0.4.0: dashboard/ Baum, Layer-Model-Korrektur, Voice-Sektion

---

### 2026-04-16 | 2026-04-16-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-16-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-16T07:01:11.831382

_Workpaper auto-ingested at session close._

---

### 2026-04-16 | BUG: Dashboard Import Error — faster_whisper

**Source:** `WORKPAPER/2026-04-16-BUG-dashboard-import-error.md`
**Status:** RESOLVED

**Problem:** Dashboard crashte beim Start mit `ModuleNotFoundError: No module named 'faster_whisper'`.  
Import-Chain: `app.py` → `dashboard/voice.py:15` → `from faster_whisper import WhisperModel`.

**Ursache:** In der Voice-Session (15.04.) wurden `faster-whisper` und `edge-tts` implementiert und getestet, aber nie in `requirements.txt` aufgenommen. Gestern lief alles über globales Python (pyenv), wo die Packages installiert waren. Heute im `.venv` fehlten sie.

**Abgrenzung:** `core/voice.py` nutzt nur `edge_tts` (TTS) — daher lief `python -m core.runtime` immer fehlerfrei. Nur das Dashboard (STT via `faster-whisper`) war betroffen.

**Fix:**  
- `requirements.txt` ergänzt: `edge-tts>=6.1`, `faster-whisper>=1.0`
- `faster-whisper` + 15 Abhängigkeiten ins `.venv` installiert

**Lektion:** Bei Feature-Abschluss IMMER `requirements.txt` im File-Protocol prüfen. Testen auf globalem Python ≠ Testen im venv.

---

### 2026-04-16 | 2026-04-16-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-16-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-16T07:03:30.174397

_Workpaper auto-ingested at session close._

---

### 2026-04-16 | 2026-04-16-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-16-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-16T07:10:06.222898

_Workpaper auto-ingested at session close._

---

### 2026-04-16 | 2026-04-16-mantisclaw-runtime-loop (AUTO-INGEST)

**Source:** `WORKPAPER/closed/2026-04-16-mantisclaw-runtime-loop.md`
**Ingested at:** 2026-04-16T10:01:42.578759

_Workpaper auto-ingested at session close._

---

### 2026-04-18 | UI Design-Entscheidung: Option C Hybrid

**Source:** `WORKPAPER/2026-04-18-DASH-VSCO-ui-design-decision.md` + 2 weitere WPs
**Agents:** ogerly (Mensch) + GitHub Copilot (Agent)
**Status:** OPEN (Design beschlossen, Implementierung ausstehend)

**Kernentscheidung: Option C — Hybrid UI**
- **VSCodium** = primäre Arbeitsumgebung (Code, Files, Terminal, Git, Chat via Continue.dev)
- **Dashboard** = Companion für Voice, Runtime, Identity (was VS Code nicht kann)
- Dashboard verliert R2 (Workpaper-Preview) + R3 (File-Tree) → VS Code macht das besser
- Dashboard behält: Voice-Assistent, Runtime-Monitor, Identity Inspector, Event-Feed, Model-Switcher

**Zwei Betriebsmodi für MantisClaw:**
- **Loop-Modus** (autonom): Heartbeat 60s, Plan → Execute → Observe → Reflect → Idle
- **Chat-Modus** (reaktiv): HTTP Request → soul(t) → LLM → Response (für Continue.dev)

**Technische Entscheidungen:**
- `/v1/chat/completions` Endpoint (OpenAI-kompatibel) als Blocker für Continue.dev
- `asyncio.Lock` in llm.py gegen LLM-Kollision zwischen Loop und Chat
- Continue.dev Config: Custom Provider → http://localhost:8080
- VSCodium bevorzugt (kein Telemetrie, Open VSX, Continue.dev verfügbar)

**Drei Workpapers erstellt:**
1. WP-DASH-VSCO-001: UI Design-Entscheidung (Optionen A/B/C verglichen)
2. WP-DASH-VSCO-002: Dashboard-Evolution (was geht, was bleibt, Grid-Umbau)
3. WP-DASH-VSCO-003: VSCodium + Continue.dev Integration (Setup, Config, LLM-Lock)

**Nächste Schritte (priorisiert):**
1. `/v1/chat/completions` Endpoint implementieren
2. `asyncio.Lock` in llm.py
3. Continue.dev installieren + testen
4. Dashboard R2/R3 entfernen
5. WH-DASHBOARD v2.0, WH-ASSISTANT v2.0

**Größtes Risiko:** LLM-Lock — Loop-Tick + Chat-Request gleichzeitig auf derselben LM Studio Instanz.

---
