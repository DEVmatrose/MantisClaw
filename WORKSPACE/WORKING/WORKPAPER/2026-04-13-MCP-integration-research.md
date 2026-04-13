# Workpaper — MCP Integration Research

**Erstellt:** 2026-04-13
**Status:** OPEN
**Agent:** copilot
**Project:** mantisclaw-core

---

## Session Goal

MCP (Model Context Protocol) für MantisClaw bewerten und Integrationsweg definieren.

**Kernfrage:** `mcp.json` (LM Studio-seitig) oder `mcp.md` (AAMS-seitig als Skill)?

---

## Was ist MCP?

Model Context Protocol (Anthropic/Open Standard) — standardisierte Tool-Schnittstelle für LLMs.
MCP-Server stellen Tools bereit, die ein LLM zur Laufzeit aufrufen kann.

LM Studio unterstützt MCP via `/api/v1/chat` (nicht `/v1/chat/completions`).

---

## LM Studio MCP API — Was verfügbar ist

### Endpoints
| Endpoint | Methode | Zweck |
|----------|---------|-------|
| `/api/v1/chat` | POST | Chat mit MCP-Support (stateful, kein Function-Calling nötig) |
| `/api/v1/models/load` | POST | Modell laden |
| `/api/v1/models/unload` | POST | Modell entladen |

### Zwei MCP-Modi in LM Studio

**1. Ephemeral MCP** (per-request, on-the-fly)
```json
{
  "integrations": [{
    "type": "ephemeral_mcp",
    "server_label": "mein-server",
    "server_url": "https://...",
    "allowed_tools": ["tool_name"]
  }]
}
```
- Gut für: einzelne Anfragen, Test, remote MCP
- Erfordert: "Allow per-request MCPs" in LM Studio Settings

**2. mcp.json** (pre-configured, persistent)
```json
{
  "integrations": [{
    "type": "plugin",
    "id": "mcp/playwright"
  }]
}
```
- Gut für: lokale Tools (Playwright, Filesystem, Shell), häufig genutzt
- Config liegt in `%APPDATA%/LM Studio/mcp.json` (Windows)

---

## Die Kernfrage: mcp.json vs mcp.md

### Option A: `mcp.json` — LM Studio-seitig
**Vorteile:**
- LM Studio managed den MCP-Server-Lifecycle
- Kein Custom-Code nötig — LM Studio handelt Tool Calls nativ
- Community-MCP-Server sofort nutzbar (Playwright, Filesystem, Git, Browser etc.)

**Nachteile:**
- Kopplung an LM Studio — funktioniert nur wenn LM Studio läuft
- MantisClaw verliert die Registry-Kontrolle (L4 bypassed)
- Kein fine-grained Permission System (unser L4-Security-Level)
- MantisClaw "sieht" die Tool-Calls nicht → kein Audit-Trail in AAMS

### Option B: `mcp.md` (AAMS Skill) — MantisClaw-seitig
**Vorteile:**
- Vollständige Kontrolle via L4 Registry
- Audit-Trail in Workpapers + Diary
- Permission System (L1-L3) greift
- Kein LM Studio-Lock-in

**Nachteile:**
- Mehr Implementierungsaufwand
- Community-MCP-Server nicht direkt nutzbar

### Option C: Hybrid (empfohlen)
- **Einfache/externe MCP-Server** → via LM Studio `mcp.json` (z.B. web-search, git)
- **AAMS-kritische Operationen** → via MantisClaw L4 Registry
- **Switch**: MantisClaw nutzt `/api/v1/chat` (nicht `/v1/chat/completions`) wenn MCP-Tools benötigt

---

## Konkrete Use Cases für MantisClaw

| Use Case | Empfohlener Weg | MCP-Server |
|----------|----------------|------------|
| Web-Suche | LM Studio mcp.json | Brave Search / DuckDuckGo MCP |
| Git-Operationen | LM Studio mcp.json | Git MCP |
| Browser-Automation | LM Studio mcp.json | Playwright MCP |
| AAMS-Workspace-Lesen | L4 Registry (read_file) | — |
| AAMS-Workspace-Schreiben | L4 Registry (write_file) | — |
| Modell-Wechsel | L4 Registry (switch_model) | — |
| External DB-Queries | L4 Registry (custom tool) oder MCP | je nach Scope |

---

## Technische Änderungen für MCP-Support

### 1. LLM Backend: `/api/v1/chat` statt `/v1/chat/completions`

Wenn MCP genutzt wird, muss `core/llm.py` auf den LM Studio-eigenen Chat-Endpoint wechseln:

```python
# Aktuell:
url = f"{base_url}/chat/completions"  # OpenAI-compat

# Mit MCP:
url = "http://localhost:1234/api/v1/chat"  # LM Studio native
payload = {
    "model": model_id,
    "input": user_message,  # statt "messages"
    "integrations": [...]   # MCP integration config
}
```

Achtung: Die Response-Struktur ist anders als OpenAI-compat! `output` Feld statt `choices[0].message.content`.

### 2. config/default.yaml Erweiterung

```yaml
llm:
  mcp:
    enabled: false          # MCP-Modus aktivieren
    use_native_endpoint: false  # /api/v1/chat statt /v1/chat/completions
    integrations: []        # Liste der plugin-IDs aus mcp.json
```

### 3. Planner-Erweiterung

Wenn MCP aktiv: Planner bekommt MCP-Tools als zusätzliche verfügbare Actions.

---

## Entscheidung (pending)

**Sofortige Priorität:** Hybrid-Ansatz
1. `mcp.json` für LM Studio-Server konfigurieren (web search, git)
2. `core/llm.py` um `/api/v1/chat` erweitern (conditional je nach MCP-Bedarf)
3. Kein AAMS-seitiger MCP-Server nötig — L4 Registry ist unser "MCP"

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| RESEARCH | — | MCP LM Studio Docs analysiert |
| PENDING | core/llm.py | /api/v1/chat Endpoint + MCP payload |
| PENDING | config/default.yaml | mcp config block |
| PENDING | WHITEPAPER/MCP.md | Falls MCP systemisch integriert wird |
| | | |

---

## Next Steps

- [ ] LM Studio mcp.json mit Brave-Search MCP testen (hands-on)
- [ ] core/llm.py: /api/v1/chat Modus implementieren
- [ ] Response-Format `/api/v1/chat` vs `/v1/chat/completions` vergleichen
- [ ] Entscheiden: Wann soll MantisClaw selbst MCP-Tools triggern vs. Planner?
