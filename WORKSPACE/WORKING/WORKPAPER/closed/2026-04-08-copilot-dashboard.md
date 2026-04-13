# WP-007 — MantisClaw Dashboard: Chat-Interface & Session-Persistence

**Workpaper:** WP-007  
**Erstellt:** 2026-04-08  
**Status:** OPEN  
**Autor:** ogerly (Mensch) + GitHub Copilot (Agent)  
**Kontext:** MantisClaw braucht ein eigenes Client-Dashboard — Chat mit dem Agent + History

---

## Session Goal

Konzept und Architektur für ein **MantisClaw Dashboard** erarbeiten:
- Web-basiertes Chat-Interface zum Agenten
- Chat-History persistent gespeichert
- Session-Management (mehrere Gespräche, fortsetzen, durchsuchen)

---

## Problemstellung

MantisClaw hat jetzt einen funktionierenden Runtime-Loop mit LLM-Backend (LM Studio local-first). Aber: **Es gibt kein Interface.** Der Agent läuft headless.

**Was fehlt:**
1. Ein Chat-Interface wo der Mensch mit dem Agenten reden kann
2. Persistent gespeicherte Chat-Verläufe (nicht nur in-memory)
3. Übersicht über vergangene Sessions / Gespräche
4. Möglichkeit, Kontext aus früheren Chats weiterzunutzen

**Referenz:** Open WebUI hat ein gutes Chat-UX, aber keine echte Chat-History-Persistenz die über die Browser-Session hinausgeht. Wir machen es besser.

---

## Architektur-Entscheidungen

### Stack: Python (FastAPI + Jinja/HTMX)

**Warum:**
- Bleibt im MantisClaw Python-Stack — kein zusätzlicher Build-Prozess
- FastAPI: async, modern, passt zur async Runtime
- Jinja2: Server-Side Rendering, kein JS-Framework nötig
- HTMX: Interaktivität ohne SPA-Overhead, Streaming-fähig (SSE)
- Leichtgewichtig: ein `pip install` und fertig

### Persistence: SQLite (lokal, zero-config)

**Warum:**
- Local-first (wie der Rest von MantisClaw)
- Zero-config, kein externer DB-Server
- Passt zur Memory-Klasse **OPS** aus LEGENDE.md
- Schnelle Suche über Chat-History
- Datei: `data/chats.db` (oder `WORKSPACE/WORKING/chats.db`)

---

## Feature-Scope (v0.1)

### Must-Have
- [ ] Chat-Seite: Nachrichten senden, Antwort empfangen (Streaming via SSE)
- [ ] Chat-History: Alle Nachrichten persistent in SQLite
- [ ] Session-Liste: Sidebar mit vergangenen Conversations
- [ ] Neue Session starten / bestehende fortsetzen
- [ ] MantisClaw Identity sichtbar (Name, Agenda aus base.md)

### Nice-to-Have (v0.2+)
- [ ] Chat durchsuchen (Volltext über SQLite FTS5)
- [ ] System-Prompt pro Session konfigurierbar
- [ ] File-Protocol Viewer (Workpapers, Diary als Read-Only)
- [ ] Observer-Metriken Dashboard (Health, Tick-Count)
- [ ] Multi-Model Umschaltung (LM Studio Models)
- [ ] Markdown-Rendering in Chat-Nachrichten
- [ ] Export: Chat → Workpaper (AAMS-Integration)

---

## Datenmodell (SQLite)

```sql
-- Conversations (= Chat-Sessions)
CREATE TABLE conversations (
    id          TEXT PRIMARY KEY,    -- UUID
    title       TEXT,                -- Auto-generiert oder manuell
    created_at  TEXT NOT NULL,       -- ISO 8601
    updated_at  TEXT NOT NULL,
    system_prompt TEXT,              -- Optional: Custom System-Prompt
    model       TEXT,                -- Welches LLM-Modell
    metadata    TEXT                 -- JSON: soul(t) snapshot, agenda, etc.
);

-- Messages
CREATE TABLE messages (
    id              TEXT PRIMARY KEY,    -- UUID
    conversation_id TEXT NOT NULL,
    role            TEXT NOT NULL,       -- user | assistant | system
    content         TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    tokens_used     INTEGER,
    model           TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Index für schnelle Abfragen
CREATE INDEX idx_messages_conv ON messages(conversation_id, created_at);
```

---

## Ordner-Struktur

> **Stand 2026-04-09:** Vereinfacht gegenüber dem ursprünglichen Plan — kein HTMX, kein models.py, ein einziges Template.

```
MantisClaw/
├── dashboard/                    ← Web-Dashboard
│   ├── __init__.py
│   ├── app.py                    ← FastAPI App + Routes + SSE
│   ├── chat.py                   ← Chat-Logik (LLM + Streaming)
│   ├── db.py                     ← SQLite Persistence
│   ├── templates/
│   │   └── index.html            ← 8-Box Layout (alles-in-eins)
│   └── static/
│       └── style.css             ← Dark Theme, CSS Grid
├── data/                         ← Persistenz
│   └── chats.db                  ← SQLite (gitignored)
```

**Nicht umgesetzt (Plan → Realität):**
- `models.py` — Pydantic Models inline in app.py gehalten
- `base.html` / `chat.html` — alles in `index.html` konsolidiert
- `htmx.min.js` — Vanilla JS + SSE reichte aus

---

## API-Endpunkte (FastAPI)

```
GET  /                           → Session-Übersicht (alle Conversations)
GET  /chat/{conversation_id}     → Chat-Interface für eine Conversation
POST /chat/{conversation_id}     → Nachricht senden (HTMX partial)
GET  /chat/{conversation_id}/stream → SSE Stream für LLM-Antwort
POST /conversations              → Neue Conversation anlegen
DELETE /conversations/{id}       → Conversation löschen

GET  /api/health                 → Runtime + LLM Health-Check
GET  /api/identity               → Aktuelle soul(t) Informationen
```

---

## Streaming-Architektur

```
Browser (HTMX)                    FastAPI                     LM Studio
     │                               │                            │
     ├── POST /chat/{id} ──────────► │                            │
     │   (user message)              ├── save to SQLite           │
     │                               ├── POST /v1/chat/completions│
     │                               │   (stream: true) ─────────►│
     │◄── SSE /chat/{id}/stream ◄────┤◄── chunk ◄─────────────────┤
     │   (token by token)            │◄── chunk ◄─────────────────┤
     │   ...                         │◄── [DONE] ◄────────────────┤
     │◄── final message ◄────────────┤── save assistant msg ──────│
     │                               │                            │
```

---

## Abhängigkeiten (neu)

```
fastapi>=0.100
uvicorn[standard]>=0.20
jinja2>=3.1
python-multipart>=0.0.5
aiosqlite>=0.19               # Async SQLite
```

> **⚠ Offen:** Diese Dependencies sind noch NICHT in `requirements.txt` eingetragen — nur manuell installiert. Muss nachgeholt werden.

---

## Abgrenzung zu Open WebUI

| Feature | Open WebUI | MantisClaw Dashboard |
|---------|-----------|---------------------|
| Chat-History | Browser-basiert, geht bei Clear verloren | SQLite persistent, bleibt immer |
| Multi-Session | Ja | Ja |
| AAMS-Integration | Nein | Ja — soul(t), Workpapers, LTM sichtbar |
| Identity | Keins | Agent-Name, Agenda, Ethik aus base.md |
| Export | Begrenzt | Chat → Workpaper Export (v0.2) |
| Search | Nein | FTS5 Volltextsuche (v0.2) |
| Stack | Svelte + Python | Python-only (FastAPI + HTMX) |

---

## Offene Fragen → Beantwortet

- ~~Soll das Dashboard den Runtime-Loop starten/stoppen können?~~ → **JA.** Plus Model-Wechsel (alle LM Studio / Ollama Modelle).
- ~~Brauchen wir Auth?~~ → Nein. Localhost = Zugang.
- ~~SQLite in `data/` oder `WORKSPACE/WORKING/`?~~ → `data/` (OPS-Memory, kein BAU-Memory)
- **NEU:** Aktives Workpaper lesbar im Dashboard anzeigen.
- **NEU:** 8-Box Dashboard-Layout (4 links, 4 rechts, Chat mittig).

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  NAVBAR — MantisClaw Dashboard              [Status] [Model ▼]     │
├──────────┬──────────────────────────────────────────┬───────────────┤
│ L1 CORE  │                                          │ R1 CHAT-     │
│ Runtime  │                                          │ HISTORY      │
│ Start/   │                                          │ Sessions     │
│ Stop     │                                          │              │
│ Model ▼  │                                          │              │
├──────────┤                                          ├───────────────┤
│ L2       │          CHAT AGENT FENSTER              │ R2 WORK-     │
│ IDENTITY │                                          │ PAPERS       │
│ soul(t)  │        [Nachrichten-Verlauf]              │ Aktive WPs   │
│ Name     │                                          │              │
│ Agenda   │                                          │              │
├──────────┤                                          ├───────────────┤
│ L3       │                                          │ R3           │
│ WORKSPACE│                                          │ (reserved)   │
│ Ordner   │                                          │              │
│ Status   │        [Eingabefeld]  [Senden]           │              │
├──────────┤                                          ├───────────────┤
│ L4       │                                          │ R4           │
│ WORKING  │                                          │ (reserved)   │
│ Aktives  │                                          │              │
│ Workpaper│                                          │              │
│ (lesbar) │                                          │              │
├──────────┴──────────────────────────────────────────┴───────────────┤
│  FOOTER — Health: HEALTHY | Ticks: 0 | LLM: qwen3-coder           │
└─────────────────────────────────────────────────────────────────────┘
```

### Box-Nummern (für spätere Befüllung)

| # | Position | Name | Inhalt v0.1 |
|---|----------|------|-------------|
| L1 | Links oben | **Core** | Runtime Start/Stop, Model-Switcher (LM Studio + Ollama Modelle), Connection Status |
| L2 | Links 2 | **Identity** | Name, Owner, Agenda aus base.md, soul(t) Formel-Anzeige |
| L3 | Links 3 | **Workspace** | Ordner-Baum (`WORKSPACE/WORKING/`), Datei-Anzahl pro Ordner |
| L4 | Links unten | **Working** | Aktives Workpaper — Inhalt lesbar (Markdown rendered) |
| R1 | Rechts oben | **Chat-History** | Liste aller Conversations, anklickbar, neue Session erstellen |
| R2 | Rechts 2 | **Workpapers** | Liste offener Workpapers, Status (OPEN/CLOSED) |
| R3 | Rechts 3 | *(reserved)* | Platzhalter — z.B. Observer-Metriken, Diary, LTM-Suche |
| R4 | Rechts unten | *(reserved)* | Platzhalter — z.B. Tools, Hooks, Decentral Trust-Map |

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
| CREATE | `WORKPAPER/2026-04-08-copilot-dashboard.md` | Dieses Workpaper |
| CREATE | `dashboard/__init__.py` | Package-Init |
| CREATE | `dashboard/db.py` | SQLite CRUD (conversations + messages) |
| CREATE | `dashboard/chat.py` | LM Studio/Ollama Streaming + Model-Listing |
| CREATE | `dashboard/app.py` | FastAPI App — Routes, Templates, SSE, State |
| CREATE | `dashboard/templates/index.html` | 8-Box Layout (L1-L4, R1-R4, Center Chat) — enthält alles (kein base.html/chat.html nötig) |
| CREATE | `dashboard/static/style.css` | Dark Theme, CSS Grid 3-Spalten |
| SKIP   | `dashboard/models.py` | Nicht umgesetzt — Pydantic Models inline in app.py |
| SKIP   | `dashboard/templates/base.html` | Nicht umgesetzt — konsolidiert in index.html |
| SKIP   | `dashboard/templates/chat.html` | Nicht umgesetzt — konsolidiert in index.html |
| SKIP   | `dashboard/static/htmx.min.js` | Nicht umgesetzt — Vanilla JS + SSE reichte aus |
| EDIT   | `dashboard/app.py` | Blocking-Fixes: asyncio.to_thread für Connection-Checks, run_in_executor für stream_chat |
| INSTALL | `fastapi uvicorn jinja2 python-multipart aiosqlite` | Dependencies |
| RUN    | `uvicorn dashboard.app:app --reload --port 8080` | Dashboard gestartet, erster Chat erfolgreich |

---

## Ergebnisse

### Dashboard v0.1 — Lauffähig ✅

- **8-Box Layout** funktioniert komplett: L1 Core (Model-Switcher), L2 Identity, L3 Workspace-Tree, L4 aktives Workpaper, R1 Chat-History, R2 Workpapers, R3+R4 reserved
- **Chat mit LM Studio**: SSE-Streaming funktioniert Token-by-Token, Antworten werden persistent in SQLite gespeichert
- **Model-Switching**: Dropdown wechselt zwischen LM Studio/Ollama + Modellen live
- **Identity**: MantisClaw antwortet mit soul(t)-bewusstem System-Prompt
- **Connection-Status**: Grüne/rote Dots für LM Studio + Ollama in Navbar + Footer
- **Dark Theme**: Professionelles Design, responsive CSS Grid
- **Erster erfolgreicher Chat**: Agent erkennt sich als MantisClaw, kennt seine Formel

### Architektur-Highlights

- **Zero JS-Framework**: Vanilla JS + SSE, kein HTMX nötig geworden
- **Blocking-Fix**: `_check_connection()` → `asyncio.to_thread()`, `stream_chat` → `run_in_executor()`
- **SQLite**: Persistent Chat-History über Browser-Sessions hinaus (besser als Open WebUI)

---

## Next Steps

1. ~~Grundgerüst: `dashboard/` Ordner + FastAPI App + SQLite Schema~~ ✅
2. ~~Chat-Interface: Jinja2 Template + HTMX für Messaging~~ ✅
3. ~~SSE Streaming: LM Studio Token-by-Token ins Frontend~~ ✅
4. ~~Session-Management: Conversations erstellen, auflisten, fortsetzen~~ ✅
5. ~~Identity-Integration: soul(t) als System-Prompt~~ ✅
6. Identity-Dateien befüllen (base.md, agenda.md) — aktuell nur `.example`-Dateien vorhanden
7. Markdown-Rendering im Chat (aktuell plain text)
8. R3/R4 Boxen befüllen (Observer-Metriken, Diary, LTM-Suche)
9. Chat-Lösch-Button + Umbenennung von Conversations
10. Favicon + Branding
11. Dashboard-Dependencies in `requirements.txt` eintragen
12. Dashboard als registrierbares Tool in Tool-Registry einordnen (→ WH-TOOLS §3)
13. Architektur-Alignment: Dashboard greift auf WORKING/ (L2) zu — Kernregel beachten (L3→L4→L2)

---

---

## Architektur-Alignment (Stand 2026-04-09)

Seit Erstellung dieses Workpapers hat sich die MantisClaw-Architektur weiterentwickelt:

- **Schichtenmodell L0-L7** (WH-TOOLS v0.1.0-WIP): Dashboard ist ein L3-Werkzeug das über L4 (Tool-Registry) auf L2 (WORKING/) zugreift
- **Kernregel**: L3 berührt L2 nie direkt — Dashboard muss Workspace-Zugriffe (Workpapers, Identity, Diary) über registrierte Tools abwickeln
- **Tool-Registry**: Dashboard-Endpunkte (`/api/identity`, Workspace-Browser) sollten als Tools registrierbar sein
- **AAMS ist fest in MantisClaw integriert** (nicht "braucht AAMS")
- **Identity**: Nur `.example`-Dateien vorhanden — Dashboard zeigt korrekt "(not set)" bis diese befüllt werden

---

*Workpaper. Wird bei Session-Close archiviert.*

