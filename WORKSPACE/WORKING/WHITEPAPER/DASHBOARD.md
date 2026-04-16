# Whitepaper: Dashboard Style Guide

**Version:** 1.0  
**Stand:** 2026-04-16  
**Projekt:** MantisClaw  

---

## 1. Überblick

Das MantisClaw Dashboard ist eine **Desktop-only Single-Page-Anwendung** (FastAPI + Jinja2 + SSE), die als primäre Arbeitsumgebung für den Mantis-Assistenten dient. Es ist kein Showcase — es ist das Werkzeug.

**Technologie:**
- Backend: FastAPI + Starlette + uvicorn (--reload)
- Template: Jinja2 (Single-Page `index.html`)
- Styling: Vanilla CSS (kein Framework)
- Interaktivität: Vanilla JS (kein Framework)
- Daten: SQLite (aiosqlite) für Chat-History, YAML für Projekt-State
- Echtzeit: SSE für Chat-Streaming, Polling (5s) für Runtime-State

---

## 2. Layout-Architektur

### 2.1 Grid

```
┌──────────────────────────────────────────────────────────────────────────┐
│ NAVBAR  (44px)                                                           │
│ 🦗 MantisClaw      [Projekt-Dropdown ▼]              ● qwen3-coder-30b  │
├──────────────┬───────────────────────────────┬───────────────────────────┤
│  ASSISTENT   │        CHAT / CENTER          │  R1 · Projekt-Übersicht  │
│  (240px)     │        (1fr flex)             │  R2 · Aktives Workpaper  │
│              │                               │  R3 · WORKING-Baum       │
│  Voice-Chat  │   Projekt-Chat mit Mantis     │  R4 · Chat-History       │
│  Event-Feed  │   (SSE-Streaming)             │       (260px)            │
├──────────────┴───────────────────────────────┴───────────────────────────┤
│ FOOTER  (36px)                                                           │
│ 🟢 [Backend ▼] [Model ▼] │ 🧬 Identity │ ⚙️ Runtime │ 🔧 Tools │ 📋 │
└──────────────────────────────────────────────────────────────────────────┘
```

**CSS Grid:** `grid-template-columns: 240px 1fr 260px`

### 2.2 Hauptbereiche

| Bereich | Rolle | Höhe |
|---------|-------|------|
| Navbar | Projekt-Kontext + Logo + Model | 44px fest |
| Linke Sidebar | Mantis Voice-Assistent | flex (füllt) |
| Center | Chat mit SSE-Streaming | flex (füllt) |
| Rechte Sidebar | Projekt-Kontext (R1–R4) | flex (füllt) |
| Footer | Controls + Modals | 36px fest |

---

## 3. Design-System

### 3.1 Farbpalette

```css
:root {
    --bg:        #0d1117;    /* Hintergrund */
    --bg-card:   #161b22;    /* Cards, Sidebar, Footer */
    --bg-input:  #0d1117;    /* Input-Felder */
    --border:    #30363d;    /* Ränder */
    --text:      #c9d1d9;    /* Primärtext */
    --text-dim:  #8b949e;    /* Sekundärtext */
    --accent:    #58a6ff;    /* Primär-Akzent (Links, Highlights) */
    --accent2:   #3fb950;    /* Sekundär-Akzent (Erfolg, Online) */
    --danger:    #f85149;    /* Fehler, Offline */
    --radius:    6px;        /* Border-Radius */
    --gap:       8px;        /* Grid-Gap */
}
```

**Prinzip:** GitHub-Dark-Theme-inspiriert. Minimalistisch, kontrastarm, augenschonend.

### 3.2 Typografie

- **System-Font-Stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Monospace:** `monospace` (für Code, Formeln, Logs)
- **Größen:** 10px (Labels), 11px (Small), 12px (Body), 13px (Chat), 14px (Headers), 16px (Logo)

### 3.3 Komponenten

#### Box
```css
.box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
}
.box-header {
    font-size: 11px; font-weight: 700;
    text-transform: uppercase;
    color: var(--text-dim);
    letter-spacing: 0.5px;
}
```

#### Button-Hierarchie
| Klasse | Verwendung |
|--------|-----------|
| `.btn` | Standard (Ghost) |
| `.btn-primary` | Hauptaktion (Accent-Farbe) |
| `.btn-sm` / `.btn-xs` | Kompakte Varianten |
| `.footer-btn` | Footer-Controls (transparent, border) |

#### Modal
```
.modal-overlay → position: fixed, inset: 0, rgba(0,0,0,0.65)
  └── .modal-box → max-width: 860px, max-height: 85vh
      ├── .modal-header → Titel + Close-Button
      └── .modal-body → Scrollbar, Content
```

**Modals:** Identity Inspector, Runtime, Tools, Events, Prompts

#### Status-Indikatoren
| Element | Online/OK | Offline/Error | Warnung |
|---------|-----------|---------------|---------|
| Status-Dot | `var(--accent2)` | `var(--danger)` | `#d29922` |
| Event-Icon | ✅ | ❌ | ⚠️ |
| Badge | `.status-active` | — | `.status-paused` |

---

## 4. Navbar

- **Links:** Logo `🦗 MantisClaw`
- **Mitte:** Projekt-Dropdown (`.project-select`) — wählt aktives Projekt, löst dynamisches Update der Sidebar aus
- **Rechts:** Model-Name (`.nav-model`) + Connection-Dot

---

## 5. Linke Sidebar — Mantis Voice-Assistent

### 5.1 Struktur
```
.sidebar.left
  ├── .assistant-focus       → Name + Projekt-Fokus
  ├── .assistant-voice-area  → Voice-Chat-Log (flex: 1)
  └── .assistant-events      → Event-Feed (max-height: 130px)
      └── [▶ mehr] Button    → Event Log Modal
```

### 5.2 Event-Typen
| Icon | Typ | Quelle |
|------|-----|--------|
| ✅ | Tick OK | Runtime-Bridge |
| ❌ | Tick Fehler | Runtime-Bridge |
| ⚠️ | Health-Warnung | Runtime-Bridge |
| 📝 | WP-Änderung | (geplant) |
| 🔄 | Projektwechsel | (geplant) |

---

## 6. Rechte Sidebar — Projekt-Kontext

### 6.1 R1 — Projekt-Übersicht
Dynamisch via `GET /api/projects/active`. Zeigt: Name, Status-Badge, Scope-Text, Milestones, Tags.

### 6.2 R2 — Aktives Workpaper
Auto-Select des neuesten offenen WP. Preview via `GET /api/workpapers/{name}`. Klick aus R3-Tree aktualisiert R2.

### 6.3 R3 — WORKING-Baum
Aufklappbare Ordner via `GET /api/projects/{slug}/tree`. Klick auf Datei → Preview in R2 via `GET /api/projects/{slug}/file`.

### 6.4 R4 — Chat-History
Conversations aus SQLite. Link zu `/chat/{id}`.

---

## 7. Footer — Controls

```
[🟢 Backend ▼] [Model ▼] │ 🧬 Identity │ ⚙️ Runtime │ 🔧 Tools │ 📋 Prompts │ 🎤 Voice │ v0.4.0
```

- **Backend-Dropdown:** LM Studio / Ollama
- **Model-Dropdown:** Verfügbare Modelle (live von API)
- **Buttons:** Öffnen jeweils ein Modal (Identity Inspector, Runtime, Tools, Prompts)
- **Voice Toggle:** ON/OFF für Sprachsteuerung

---

## 8. API-Endpunkte (Dashboard)

### Projekt-Management
| Endpoint | Method | Beschreibung |
|----------|--------|-------------|
| `/api/projects` | GET | Liste aller Projekte |
| `/api/projects/active` | GET | Aktives Projekt (vollständig) |
| `/api/projects/active` | POST | Projekt wechseln |
| `/api/projects/{slug}/tree` | GET | WORKING-Ordner als Baum |
| `/api/projects/{slug}/file` | GET | Datei aus WORKING lesen |

### Runtime & Tools
| Endpoint | Method | Beschreibung |
|----------|--------|-------------|
| `/api/runtime` | GET | Runtime-State (Bridge-File) |
| `/api/runtime/ticks` | GET | Tick-History |
| `/api/models` | GET | Verfügbare LLM-Modelle |
| `/api/model` | POST | Modell wechseln |
| `/api/workpapers` | GET | Alle Workpapers |
| `/api/workpapers/{name}` | GET | Workpaper-Inhalt |
| `/api/identity` | GET | Identity-Dateien + Soul |

### Voice
| Endpoint | Method | Beschreibung |
|----------|--------|-------------|
| `/api/tts` | POST | Text-to-Speech |
| `/api/stt` | POST | Speech-to-Text |
| `/api/voice/config` | GET/POST | Voice-Konfiguration |
| `/api/voice/greeting` | GET | Kontext-Begrüßung |
| `/api/voice/talk` | POST | Full Pipeline |
| `/api/runtime/voice` | POST | Voice via Runtime |

---

## 9. Konventionen

### CSS-Klassen-Namensgebung
- **Bereich:** `.assistant-*`, `.project-*`, `.tree-*`, `.footer-*`, `.event-*`
- **Modifier:** `.voice-on`, `.status-active`, `.event-error`
- **Zustand:** `.active`, `.muted`, `.online`

### JS-Funktionen
- **Load:** `loadProjects()`, `loadProjectOverview()`, `loadWorkingTree()`
- **Show:** `showWorkpaper()`, `showWorkingFile()`, `showEventModal()`, `showRuntimeModal()`, `showToolsModal()`
- **Render:** `renderRuntimeModal()`, `renderToolsModal()`
- **Toggle:** `toggleTreeFolder()`, `toggleVoice()`
- **Polling:** `pollRuntime()` (5s), `pollTicks()` (10s)

### ID-Konventionen
- Boxes: `#box-R1` bis `#box-R4`
- Modals: `#modal-identity`, `#modal-runtime`, `#modal-tools`, `#modal-events`
- Dynamic: `#projectSelect`, `#projectOverview`, `#workpaperPreview`, `#workingTree`, `#eventFeedList`
