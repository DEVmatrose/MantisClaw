---
title: "UI Design-Entscheidung — Dashboard vs. VSCodium vs. Hybrid"
workpaper_id: WP-DASH-VSCO-001
date: 2026-04-18
status: OPEN
topic: DASH
subtopic: VSCO
related_whitepapers: [DASHBOARD.md, ASSISTANT.md, TOOLS.md]
related_workpapers: [2026-05-15-Skills-and-Tools.md §5.4 + §6]
file_protocol:
  read: [WORKSPACE/WORKING/WHITEPAPER/DASHBOARD.md, WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md, WORKSPACE/WORKING/WORKPAPER/2026-05-15-Skills-and-Tools.md §5.4+§6]
  changed: [dieses Workpaper]
  to_update_after_decision: [WORKSPACE/WORKING/WHITEPAPER/DASHBOARD.md, WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md]
---

# WP: UI Design-Entscheidung — Dashboard vs. VSCodium vs. Hybrid

## §1 Problemstellung

Das MantisClaw Dashboard (`:8080`) und VSCodium/VS Code überlappen sich massiv. Das aktuelle Setup bedeutet: zwei parallele Fenster mit doppelter Funktionalität. Das ist ineffizient und schwer zu pflegen.

### Was das aktuelle Dashboard bietet (DASHBOARD.md v1.0)

```
Navbar:  Projekt-Dropdown | Logo | Model-Status
Links:   Voice-Assistent (STT → TTS, Event-Feed)
Center:  Chat / SSE-Streaming mit Mantis
Rechts:  R1 Projekt-Übersicht | R2 Aktives Workpaper | R3 WORKING-Baum | R4 Chat-History
Footer:  Backend-Switcher | Model-Switcher | Identity | Runtime | Tools | Events | Prompts
```

### Was VSCodium nativ besser kann

| Feature | Dashboard (selbst gebaut) | VSCodium (nativ) | Gewinner |
|---------|--------------------------|------------------|---------|
| File Tree | R3 (custom, read-only) | Explorer Panel (voll interaktiv, Multi-Root) | **VSCodium** |
| Datei-Editor | R2 Preview (read-only Markdown) | Vollständiger Editor (Syntax, Multi-Tab, Diff) | **VSCodium** |
| Terminal | ❌ nicht vorhanden | Integriert (mehrere Sessions, PowerShell/Bash) | **VSCodium** |
| Git/Source Control | ❌ nicht vorhanden | Source Control Panel + GitLens | **VSCodium** |
| Chat mit Agent | Center (SSE, gut) | Continue.dev Extension (konfigurierbar) | **Gleichwertig** |
| Voice-Assistent | Linke Sidebar (vollständig) | ❌ nicht nativ | **Dashboard** |
| Runtime-Monitor | Footer-Modal (gut) | ❌ nicht nativ | **Dashboard** |
| Identity Inspector | Footer-Modal (gut) | ❌ nicht nativ | **Dashboard** |
| Projekt-Übersicht | R1 Sidebar | ❌ nur via Extensions | **Dashboard** |
| Model-Switcher | Navbar/Footer | ❌ nicht nativ | **Dashboard** |

---

## §2 Die drei Optionen

### Option A — Status Quo (Dashboard eigenständig)

```
Dashboard (:8080)         VS Code / VSCodium
─────────────────         ──────────────────
Voice + Chat              Code-Editor
Runtime-Monitor           Terminal
Identity Inspector        Git
File Tree (R3)            File Tree (doppelt!)
Workpaper-View (R2)       Markdown Preview (doppelt!)
```

**Bewertung:**
- ✅ Kein Umbau nötig
- ✅ Dashboard unabhängig von VS Code
- ❌ Zwei Fenster, zwei File-Trees, zwei Chat-Schnittstellen
- ❌ Dashboard pflegt Features die VS Code besser macht
- ❌ Skaliert nicht — je mehr Tools, desto mehr Dopplung

**Empfehlung: NEIN** — Nicht zukunftsfähig.

---

### Option B — VS Code als Hauptoberfläche (Full Extension)

```
VSCodium (alles)
────────────────────────────────────────
MantisClaw Extension:
  Sidebar WebView: Projekt-Übersicht, Runtime-Monitor
  Panel WebView:   Voice-Assistent, Identity Inspector
  Continue.dev:    Chat mit MantisClaw Loop
Dashboard → reines Headless-Backend (API-only)
```

**Umsetzung:**
- MantisClaw VS Code Extension (TypeScript) mit WebView-Panels
- Dashboard wird zu reinem Backend (FastAPI bleibt, kein HTML mehr)
- Extension kommuniziert mit Backend-API

**Bewertung:**
- ✅ Alles an einem Ort — echter Single-Window-Workflow
- ✅ Nutzt VS Code Stärken maximal aus
- ✅ Terminal, Git, Editor nativ integriert
- ❌ Extension-Entwicklung aufwändig (TypeScript + VS Code API)
- ❌ Extension-Lifecycle (Updates, Kompatibilität, Signing)
- ❌ Bindet MantisClaw eng an VS Code — andere Clients (Browser, Mobile) verlieren
- ❌ Voice (Web Audio API) in Extension-WebView komplex

**Empfehlung: NEIN für jetzt** — Zu aufwändig für v0.x. Langfristig interessant.

---

### Option C — Hybrid (Dashboard als Companion) ← EMPFEHLUNG

```
VSCodium (Haupt-Arbeitsumgebung)      Dashboard (:8080) (Companion)
─────────────────────────────         ──────────────────────────────
File Tree (Explorer)                  Voice-Assistent (STT/TTS)
Editor (Code, Markdown)               Runtime-Monitor (Live-Loop)
Terminal (integriert)                 Identity Inspector
Git (Source Control)                  Event-Feed
Chat (Continue.dev → MantisClaw)      Model-Switcher
                                      Token-Budget
```

**Was vom Dashboard WEG fällt:**
- R3 (WORKING-Baum) → VS Code Explorer ist besser
- R2 (Workpaper-Preview) → VS Code Markdown-Preview ist besser
- Kein eigener File-Editor mehr

**Was im Dashboard BLEIBT (und nur hier existiert):**
- Voice-Assistent (Mikrofon, VAD, STT, TTS, Browser Web Audio API)
- Runtime-Monitor (Live-Tick-Status, Health, Loop-State)
- Identity Inspector (soul(t) live anzeigen)
- Event-Feed (was tut der Agent gerade?)
- Model-Switcher (LM Studio / Ollama Modelle laden)
- Projekt-Übersicht (R1 — welche Workpapers sind offen?)

**Bewertung:**
- ✅ Dashboard wird schlanker und fokussierter
- ✅ VS Code macht was VS Code gut kann
- ✅ Kein TypeScript / Extension-Overhead
- ✅ Dashboard bleibt unabhängig → nutzbar ohne VS Code
- ✅ Voice im Browser funktioniert nativ (Web Audio API)
- ⚠️ Immer noch zwei Fenster (aber klare Rollentrennung)
- ⚠️ Continue.dev muss gegen MantisClaw-Endpoint konfiguriert werden

**Empfehlung: JA — Option C ist der pragmatische Mittelweg.**

---

## §3 Option C — Technische Durchdenking

### 3.1 Continue.dev ↔ MantisClaw Kopplung

Continue.dev braucht einen **OpenAI-kompatiblen `/v1/chat/completions` Endpoint**.

MantisClaw Dashboard hat das **NOCH NICHT** — aktuell leitet das Dashboard direkt an LM Studio weiter.

**Was zu bauen ist:**

```python
# dashboard/app.py — neuer Endpoint
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    
    # 1. soul(t) berechnen → System-Prompt bauen
    # 2. Planner → Plan erstellen (LLM)
    # 3. Executor → Tools ausführen
    # 4. Response → zurück als OpenAI-Format (oder SSE-Stream)
```

**Problem:** Der aktuelle MantisClaw Loop läuft als eigenständiger Prozess (heartbeat-basiert). Continue.dev will aber **synchrone Request/Response** Semantik.

**Lösung: Zwei Modi für MantisClaw:**
1. **Loop-Modus** (wie heute) — autonomer Heartbeat-Tick, 60s Interval
2. **Chat-Modus** (neu) — Request/Response, ausgelöst durch Continue.dev / Dashboard

Der Chat-Modus ist ein **Mini-Loop**: Plan → Execute → Observe → Respond. Kein Heartbeat, kein Idle.

```
Continue.dev Request
    ↓
POST /v1/chat/completions
    ↓
soul(t) + messages → Planner (1 Tick)
    ↓
Executor (Tool-Calls wenn nötig)
    ↓
Observer (Beobachtung)
    ↓
Response → OpenAI-Format (SSE wenn stream=true)
```

### 3.2 Continue.dev Konfiguration

```json
// ~/.continue/config.json
{
  "models": [
    {
      "title": "MantisClaw (Mantis)",
      "provider": "openai",
      "model": "mantis",
      "apiBase": "http://localhost:8080",
      "apiKey": "local"
    }
  ],
  "contextProviders": [],
  "slashCommands": []
}
```

**Installations-Pfad Continue.dev:**
- VS Code: Extension installieren → `ext install Continue.continue`
- VSCodium: Open VSX → `continue.continue` (verfügbar)

### 3.3 Dashboard-Umbau (Option C)

**Zu entfernen:**
- R3 Box (WORKING-Baum, `workspace_status` Polling)
- R2 Box (Aktives Workpaper Preview, `read_file` Polling)

**Grid-Anpassung:**
```
Vorher: grid-template-columns: 240px 1fr 260px  (3 Spalten)
Nachher: grid-template-columns: 240px 1fr       (2 Spalten)

Rechte Sidebar wird: R1 Projekt-Übersicht + R4 Chat-History (kompakter)
```

**Zu behalten / verbessern:**
- Voice-Assistent (linke Sidebar)
- Chat Center (SSE) — aber Continue.dev übernimmt den primären Chat
- Runtime-Monitor (Footer-Modal → wird prominenter)
- Identity Inspector (Footer-Modal)
- Model-Switcher

**Neu:**
- `POST /v1/chat/completions` Endpoint (für Continue.dev)
- Runtime-Monitor als eigene Sidebar-Box (nicht nur Modal)

### 3.4 MCP Server (Optional, Tier 2)

MantisClaw-Tools als **MCP (Model Context Protocol) Server** exponieren:

```python
# Zukünftig: dashboard/mcp.py
# Continue.dev kann dann Tools direkt aufrufen (ohne Loop-Zwischenschicht)
# Relevant wenn: agent hat shell_exec, git_*, run_tests implementiert
```

MCP ist optional. Erst wenn Tier-1 Tools implementiert sind (shell_exec, git_*, run_tests).

---

## §4 Theoretischer Test-Durchlauf (Option C)

### Szenario: Developer arbeitet an MantisClaw

**Setup:**
- VSCodium offen, MantisClaw-Repo geladen
- Continue.dev Extension aktiv, Provider = `http://localhost:8080`
- MantisClaw Dashboard offen (Companion-Fenster)
- `uvicorn dashboard.app:app --port 8080` läuft

**Ablauf:**

```
[T1] Developer: "Mantis, was sind die offenen Punkte im aktuellen Workpaper?"

     Continue.dev → POST http://localhost:8080/v1/chat/completions
     MantisClaw Loop (Chat-Modus):
       1. soul(t) laden (base.md + agenda.md)
       2. Planner: "query_memory + workspace_status"
       3. Executor: workspace_status Tool → listet WORKPAPER/
       4. Executor: read_file Tool → liest aktives Workpaper §7
       5. Observer: "Relevante Info gefunden, Antwort formulieren"
       6. Response: "Aktuelle offene Punkte: Tier-1 Tools implementieren, ..."
     
     Continue.dev zeigt Antwort im Chat-Panel
```

```
[T2] Developer: "Implementiere shell_exec als ersten Tier-1 Tool"

     MantisClaw Loop (Chat-Modus):
       1. Planner: "read_file(TOOLS.md) → analyze → write_file"
       2. Executor: read_file(core/registry/tools/filesystem.py)  ← Referenz
       3. Executor: analyze → Struktur ableiten
       4. Executor: write_file(core/registry/tools/coding.py) ← NEU
       5. Observer: "shell_exec implementiert, Tests empfohlen"
       6. Response: "shell_exec implementiert in coding.py, bitte testen"
     
     Developer sieht neue Datei im VS Code Explorer
     Terminal: pytest tests/ → grün
```

```
[T3] Developer spricht ins Mikrofon (Dashboard):
     "Mantis, wie ist der Runtime-Status?"
     
     Dashboard Voice Pipeline:
       Web Audio API → VAD → Stille erkannt
       → faster-whisper STT → "wie ist der Runtime-Status"
       → Intent Classifier → SYSTEM
       → loop_monitor Tool → Health: IDLE, letzter Tick: T-45s
       → TTS → "Alles grün. Loop läuft stabil, letzter Tick vor 45 Sekunden."
     
     Developer hört Antwort — ohne Tippen
```

```
[T4] Runtime-Loop (autonomer Tick im Hintergrund, alle 60s):
     Unabhängig von Continue.dev / Voice.
     Plant nächste Schritte aus offenem Workpaper.
     Schreibt Diary-Eintrag.
     Dashboard Runtime-Monitor zeigt: "PLANNING → EXECUTING → IDLE"
```

### Test-Ergebnis (theoretisch)

| Test | Ergebnis | Voraussetzung |
|------|----------|---------------|
| T1: Chat-Anfrage via Continue.dev | ✅ funktioniert wenn /v1 Endpoint gebaut | `/v1/chat/completions` Endpoint |
| T2: Code-Generierung | ✅ wenn write_file + analyze Tools funktionieren | LM Studio aktiv |
| T3: Voice-Befehl | ✅ bereits implementiert | LM Studio + faster-whisper |
| T4: Autonomer Loop-Tick | ✅ bereits implementiert | LM Studio aktiv |

---

## §5 Offene Fragen & Risiken

| Frage | Status | Notiz |
|-------|--------|-------|
| Loop-Modus vs. Chat-Modus: Wie koordinieren? | ❓ OFFEN | Heartbeat-Loop + synchrone Chat-Requests könnten kollidieren (LLM-Lock) |
| Continue.dev SSE-Kompatibilität | ❓ OFFEN | Muss getestet werden — OpenAI SSE-Format exakt? |
| Dashboard Chat-Center: Bleibt er? | ❓ OFFEN | Mit Continue.dev wäre er redundant. Nur für Voice-only Workflow? |
| VSCodium vs. VS Code | ✅ KLAR | VSCodium bevorzugt (kein Telemetrie). Open VSX hat Continue.dev. |
| MCP Timeline | ✅ KLAR | Optional. Erst nach Tier-1 Tools. |

### Größtes Risiko: LLM-Lock

Wenn der Heartbeat-Loop einen LLM-Call macht (60s Interval) und gleichzeitig Continue.dev einen Chat-Request sendet → beide warten auf dieselbe LM Studio Instanz.

**Lösung:** Request-Queue oder Thread-Safe LLM-Wrapper. Oder: Chat-Modus pausiert Loop-Tick solange ein Request aktiv ist.

---

## §6 Entscheidung

### BESCHLOSSEN: Option C — Hybrid

> **Dashboard = Voice, Runtime, Identity Companion.**  
> **VSCodium = Code, Files, Terminal, Git, Chat (Continue.dev).**

### Konsequenzen (Was muss sich ändern)

| Whitepaper | Änderung |
|------------|---------|
| **WH-DASHBOARD** | R2 + R3 werden entfernt. Grid: 3-spaltig → 2-spaltig. Runtime-Monitor wird prominenter (eigene Box statt nur Modal). Neuer `/v1/chat/completions` Endpoint dokumentiert. |
| **WH-ASSISTANT** | Continue.dev als primärer Text-Chat-Kanal dokumentieren. Voice bleibt primär für Dashboard-Interaktion. Loop-Modus vs. Chat-Modus als zwei Betriebsmodi definieren. |

### Nächste Schritte (priorisiert)

1. **`/v1/chat/completions` Endpoint** bauen (dashboard/app.py) — Blocker für Continue.dev
2. **Continue.dev installieren** — VSCodium, Open VSX
3. **Dashboard R2/R3 entfernen** — Grid vereinfachen
4. **Runtime-Monitor-Box** — aus Footer-Modal in eigene Sidebar-Box
5. **WH-DASHBOARD v2.0** schreiben — nach Dashboard-Umbau
6. **WH-ASSISTANT v2.0** schreiben — zwei Betriebsmodi dokumentieren
7. **LLM-Lock lösen** — Queue oder Tick-Pause bei Chat-Request

---

## §7 File Protocol

| Aktion | Datei |
|--------|-------|
| READ | WORKSPACE/WORKING/WHITEPAPER/DASHBOARD.md |
| READ | WORKSPACE/WORKING/WHITEPAPER/ASSISTANT.md |
| READ | WORKSPACE/WORKING/WORKPAPER/2026-05-15-Skills-and-Tools.md §5.4+§6 |
| CREATED | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-ui-design-decision.md |
| TO CREATE | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-dashboard-evolution.md |
| TO CREATE | WORKSPACE/WORKING/WORKPAPER/2026-04-18-DASH-VSCO-vscodium-integration.md |
