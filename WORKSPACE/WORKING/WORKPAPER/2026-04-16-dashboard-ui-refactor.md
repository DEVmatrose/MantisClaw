# Dashboard UI Refactor — Fokus auf Arbeit

**Date:** 2026-04-16  
**Type:** Feature / Refactor  
**Status:** CLOSED — M1–M5 alle ✅  
**Severity:** Major — betrifft das gesamte Dashboard-Layout  
**Project:** MantisClaw Core

---

## Problem

Das aktuelle Dashboard zeigt viele Informationen in der linken Sidebar (L1–L5), die:
- Nur Anzeige sind, keine Funktion haben (L2 Identity = Showcase)
- Platz verschwenden (L1 Backend-Wahl, L4 Tool-Liste als statische Liste)
- Nicht auf die eigentliche Arbeit fokussiert sind
- Kein Projekt-Switching ermöglichen
- Kein Projektbewusstsein — Assistent weiß nicht, in welchem Projekt wir arbeiten

Das Dashboard muss **Arbeitsumgebung** werden, nicht Showcase.

---

## Kernprinzipien (aus Diskussion 2026-04-16)

1. **Projekt = Arbeitskontext.** Alles ist projektbezogen. Header-Dropdown wählt Projekt. R1–R4 filtern nach Projekt. Kein Mischen.
2. **Assistent = Fokus-Wächter.** Mantis verliert nie den Fokus: primär Workpaper, sekundär Projekt, tertiär sich selbst.
3. **Voice-Chat ≠ Chat-History.** Hart getrennt. Voice-Chats sind temporär/session-gebunden. Chat-History gehört zum Projekt.
4. **Kein Avatar.** Mantis hat kein Bild. Die linke Sidebar ist der Voice-Agent-Bereich.
5. **Projektwechsel = aktiver Event.** Beim Wechsel:
   - Soul wird neu berechnet (Projektdaten → Identity)
   - Assistent meldet sich: "Projekt gewechselt. Letzter Stand: ..."
   - Offene Arbeiten im alten Projekt werden abgeglichen (Observer)
   - Fragt ob analysiert/losgelegt werden soll (nicht automatisch starten)
6. **Workpaper = Arbeitsfokus.** R2 zeigt aktives Workpaper. Wechsel des WP → Assistent reagiert.
7. **Assistent narrated.** Wenn Voice AN: Identity Inspector öffnen → kurze Erklärung. Tools Modal → "Wir haben X Tools registriert, Y öffentliche, Z projektspezifische." Prompts → kurze Erklärung. Fehler → sofortige Warnung.
8. **WORKING-Ordner anklickbar.** Rechte Sidebar zeigt die AAMS-Struktur des Projekts (Workpapers, Whitepapers, etc.) als navigierbaren Baum.
9. **Desktop-only.** Kein Responsive/Mobile vorerst.
10. **Kompakt.** Footer-Buttons klein, simpel, kompakt. Kein Overflow-Menu nötig.

---

## Ziel-Layout

```
┌──────────────────────────────────────────────────────────────────────────┐
│ HEADER / NAVBAR                                                          │
│ 🦗 MantisClaw      [Projekt-Dropdown ▼]              ● qwen3-coder-30b  │
├──────────────┬───────────────────────────────┬───────────────────────────┤
│     L1       │                               │                           │
│  ASSISTENT   │        CHAT / CENTER          │  R1 · Project Overview    │
│   Mantis     │                               │       (Milestones, Status)│
│  ──────────  │                               │  R2 · Aktives Workpaper   │
│  Voice-Chat  │   Projekt-Chat mit Mantis     │       (Live-Preview/Edit) │
│     │        │   (SSE-Streaming)             │  R3 · WORKING-Baum        │
│     │        │                               │       (AAMS-Struktur)     │
│     │        │                               │  R4 · Chat-History        │
│  ──────────  │                               │       (Projekt-gefiltert) │
│  Events/Feed │                               │                           │
│  (letzte 3)  │                               │                           │
│  [mehr →]    │                               │                           │
├──────────────┴───────────────────────────────┴───────────────────────────┤
│ FOOTER                                                                   │
│ 🟢 LM Studio [Backend ▼] [Model ▼] │ 🧬 Identity │ ⚙️ Runtime │        │
│ 🔧 Tools │ 📋 Prompts │ 🎤 Voice ON/OFF │ MantisClaw v0.4.0            │
└──────────────────────────────────────────────────────────────────────────┘
```

**L1** = Voice-Agent. Primär Voice-Chat-Log. Sekundär Event-Feed (Ticks, Fehler, Aktionen).  
**Center** = Projekt-Chat (SSE-Streaming). Hier wird gearbeitet. Befehle, Diskussionen, Ergebnisse.  
**R1** = Projekt-Übersicht aus `project.yaml` (Name, Status, Scope, Milestones).  
**R2** = **Wichtigster Bereich.** Aktives Workpaper als Markdown-Preview + Inline-Edit.  
**R3** = WORKING-Ordner des Projekts als navigierbarer Baum (Workpapers, Whitepapers, Guidelines, etc.).  
**R4** = Chat-History, gefiltert nach aktivem Projekt (SQLite).  
**Footer** = Alle Controls: Backend, Model, Identity, Runtime, Tools, Prompts, Voice Toggle.

---

## Meilensteine

### M1 — Footer-Bar (Controls & Modals) ✅

**Status:** DONE (2026-04-16)  
**Was:** Alle L1–L5 Controls in den Footer verschieben. Sidebar wird frei.

| Element | Aktuell | Neu (Footer) |
|---------|---------|-------------|
| Backend-Wahl (LM Studio / Ollama) | L1 Sidebar | Footer Dropdown |
| Model-Selector | L1 Sidebar | Footer Dropdown |
| Connection-Status (🟢/🔴) | Footer (schon da) | Footer (bleibt) |
| 🧬 Identity Inspector | L2 Button | Footer Button → Modal |
| ⚙️ Runtime (Ticks, Health) | L3 Sidebar-Box | Footer Button → Modal |
| 🔧 Tools (Registry) | L4 Sidebar-Liste | Footer Button → Modal |
| 📋 Prompts | L3 Button | Footer Button → Modal |
| 🎤 Voice ON/OFF | L5 Box | Footer Toggle-Button |

**Ergebnis:** Linke Sidebar komplett frei für Assistent (M3).

**Modals:**
- Identity Inspector Modal → existiert, Button verschieben
- Runtime Modal → existiert (Tick-Detail, Health), Button verschieben
- Tools Modal → **NEU**: Registrierte Tools mit Name, Level, Status. Trennung: Projekt-Tools vs. Core-Tools.
- Prompts Modal → existiert, Button verschieben

**Voice-Narration (wenn Voice AN):**
- Modal öffnet → Mantis sagt kurz was zu sehen ist
- Identity: "Das ist die aktuelle Soul-Berechnung aus base, agenda und Projektkontext."
- Tools: "Wir haben X Tools registriert. Y öffentliche, Z projektspezifisch."
- Runtime: "Letzter Tick vor X Sekunden. Health: OK/WARN."
- Prompts: kurze Erklärung der Runtime-Prompts

---

### M2 — Header / Navbar (Projekt-Selector) ✅

**Status:** DONE (2026-04-16)  
**Was:** Projekt-Auswahl in den Header. **Das ist der Kontextwechsel-Mechanismus.**

- Dropdown liest `WORKING/PROJECT/*/project.yaml`
- Zeigt alle Projekte mit Name + Status (active/paused/done)
- Auswahl setzt aktives Projekt → steuert R1–R4 + Assistent-Fokus
- Aktuelles aktives Projekt aus `WORKING/PROJECT/_active.yaml`
- Wechsel schreibt `_active.yaml`

**API:**
- `GET /api/projects` — Liste aller Projekte
- `POST /api/projects/active` — Aktives Projekt setzen
- `GET /api/projects/active` — Aktives Projekt lesen

**Projektwechsel-Logik (kritisch):**
1. User wählt neues Projekt im Dropdown
2. `POST /api/projects/active` → Backend schreibt `_active.yaml`
3. Dashboard reloaded R1–R4 mit neuem Projektkontext
4. **Soul wird neu berechnet** — `soul(t) = f(base, agenda, project_context)`
5. **Assistent reagiert** (wenn Voice AN):
   - "Projekt gewechselt zu {Name}."
   - "Letzter Stand: {neuestes offenes Workpaper, Titel + Datum}."
   - "Soll ich den Stand analysieren oder wollen wir erstmal schauen?"
6. **Observer prüft altes Projekt**: Offene Arbeiten? Ungespeichertes im Voice-Chat?
   - Wenn ja: "Im alten Projekt {Name} gibt es noch offene Punkte: {Liste}."
   - Observer schreibt Notiz ins alte Projekt-Workpaper falls relevant

**Querverweise:**
- → WP `2026-04-13-project-scoped-aams.md`: AAMS-Struktur pro Projekt
- → WP `2026-04-15-voice-integration-dashboard.md` Phase 3: Intent-Router

---

### M3 — Linke Sidebar → Mantis Voice-Assistent ✅

**Status:** DONE (2026-04-16)  
**Implementiert:**
- `.assistant-focus` Header (Name + aktives Projekt)
- Voice-Chat-Log (flexibel, füllt Hauptbereich)
- Event-Feed (letzte 3 Events, Typen: ✅/❌/⚠️ mit Goal)
- Event Log Modal (▶ Button, bis 50 Events mit Goal-Text)
- `_allEvents[]` Array als globaler Event-Speicher
- `showEventModal()` + erweitertes `updateEventFeed()` mit richer Event-Types
- CSS: `.assistant-focus`, `.assistant-name`, `.assistant-project`, `.assistant-voice-area`, `.event-more-btn`

**Was:** Die gesamte linke Sidebar wird zum Voice-Assistenten.

**Aufbau:**
```
┌─────────────────────┐
│  MantisClaw          │
│  Fokus: {Projekt}   │
│─────────────────────│
│                     │
│  Voice-Chat-Log     │
│  (scrollbar)        │
│                     │
│  🔵 User: ...       │
│  🟢 Mantis: ...     │
│  🔵 User: ...       │
│  🟢 Mantis: ...     │
│                     │
│─────────────────────│
│  Event-Feed         │
│  ● Tick #12 OK      │
│  ● WP gespeichert   │
│  ● Error: LLM...    │
│  [mehr anzeigen →]  │
└─────────────────────┘
```

**Primär: Voice-Chat**
- Voice-Chat-Log (von L5 hierher migriert)
- VAD (Voice Activity Detection) — 2.5s Stille → STT → Verarbeitung
- Temporär/Session-gebunden. Nicht persistent.
- Observer beobachtet Voice-Chat auf projekt-relevante Inhalte
  → Relevant? → Workpaper-Update vorschlagen (→ Phase 3 Voice WP)

**Sekundär: Event-Feed**
- Letzte 3 Events/Ticks/Aktionen sichtbar
- [mehr →] Button öffnet Modal mit vollständigem Event-Log
- Events kommen aus Runtime-Bridge (`data/runtime_state.json`)
- Event-Typen:
  - ✅ Tick abgeschlossen (Nr, Goal, Dauer)
  - ⚠️ Warnung (LLM nicht erreichbar, Tool-Fehler, etc.)
  - ❌ Error (mit Layer-Erkennung: L0/L3/L4/L2)
  - 📝 Workpaper gespeichert/gewechselt
  - 🔄 Projektwechsel

**Assistent-Verhalten (Kernregeln):**
- **Fokus-Hierarchie:** 1. Workpaper → 2. Projekt → 3. Selbst
- **Nie den Fokus verlieren.** Egal was vorher besprochen wurde — nach Projektwechsel = neuer Kontext.
- **Fehler sofort melden.** Wenn Voice AN: schnell, knapp, Layer benennen.
  - "Achtung, LLM nicht erreichbar. L0-Problem."
  - "Tick 14 fehlgeschlagen. Executor-Error in Schritt 3."
  - "Tool read_file hat einen Fehler. Pfad existiert nicht."
- **Proaktiv bei Events:** Tick fertig → kurze Zusammenfassung. WP-Wechsel → Stand durchsagen.

**Querverweise:**
- → WP `2026-04-15-voice-integration-dashboard.md` Phase 2+3: VAD, Intent-Router, Observer
- → WP `2026-04-16-runtime-dashboard-bridge.md`: Event-Daten aus Bridge-File

---

### M4 — Rechte Sidebar (Projekt-Kontext) ✅

**Status:** DONE (2026-04-16)  
**Was:** R1–R4 zeigen ausschließlich Daten des aktiven Projekts.

| Box | Inhalt | Quelle |
|-----|--------|--------|
| R1 | Project Overview | `project.yaml` — Name, Status, Scope, Milestones |
| R2 | **Aktives Workpaper** | Markdown-Preview + Inline-Edit |
| R3 | WORKING-Baum | AAMS-Struktur des Projekts, navigierbar |
| R4 | Chat-History | Projekt-Conversations (SQLite, gefiltert) |

**R2 — Aktives Workpaper (Kernstück)**
- Auto-Select: Neuestes offenes WP wird automatisch geladen
- Markdown-Rendering (marked.js oder similar)
- **Inline-Edit:** Direkt im Browser bearbeitbar
- Wechsel in R3 (Workpaper anklicken) → R2 zeigt neues WP
- Workpaper-Wechsel → Assistent reagiert:
  - "Workpaper gewechselt zu '{Titel}'. Status: {OPEN/DONE}."
  - Bei OPEN: "Letzte Änderung: {Datum}. Soll ich den Stand zusammenfassen?"

**R3 — WORKING-Baum (AAMS-Struktur)**
- Navigierbarer Dateibaum des Projekt-WORKING-Ordners
- Ordner: WORKPAPER/, WHITEPAPER/, GUIDELINES/, DIARY/, MEMORY/, SCIENCE/
- Klick auf Datei → Preview in R2 (nicht nur Workpapers, auch Whitepapers etc.)
- Zeigt Dateicount pro Ordner
- **Wichtig:** Zeigt nur Daten des aktiven Projekts

**R4 — Chat-History**
- Gefiltert nach aktivem Projekt
- Conversations aus SQLite (`dashboard/db.py`)
- Klick auf Conversation → Center-Chat lädt diese History

**API-Endpoints (neu):**
- `GET /api/projects/{slug}/workpapers` — Liste Workpapers
- `GET /api/projects/{slug}/workpaper/{name}` — Workpaper-Inhalt (Markdown)
- `PUT /api/projects/{slug}/workpaper/{name}` — Workpaper speichern (Inline-Edit)
- `GET /api/projects/{slug}/tree` — WORKING-Ordner als JSON-Baum
- `GET /api/projects/{slug}/file?path=...` — Beliebige Datei aus WORKING lesen

**Querverweise:**
- → WP `2026-04-13-project-scoped-aams.md`: Phase 2 plant Migration der WORKING-Ordner in PROJECT/<slug>/
- → WH `WORKING.md`: 5-Layer Memory System definiert die Ordnerstruktur

---

### M5 — Aufräumen & Entfernen ✅

**Status:** DONE (2026-04-16)  
**Was:** Alten Sidebar-Code entfernen, konsolidieren.

- L1 Core Box → entfernt (→ Footer)
- L2 Identity Box → entfernt (→ Footer Modal)
- L3 Runtime Box → entfernt (→ Footer Modal)
- L4 Tools Box → entfernt (→ Footer Modal)
- L5 Voice Box → entfernt (→ L1 Assistent)
- CSS: Altes Grid entfernen, neues 3-Column-Layout
- JS: Event-Handler konsolidieren, tote Funktionen entfernen
- HTML: Alte IDs/Klassen aufräumen

---

## Abhängigkeiten

```
M1 (Footer) ─────────────────► M5 (Aufräumen)
                                   ▲
M2 (Header/Projekt) ──────────────┤
                                   │
M3 (Assistent Links) ─────────────┤
       ▲                           │
       │                           │
M4 (Rechts Projekt) ──────────────┘
       ▲
       │
M2 ────┘  (M3 + M4 brauchen aktives Projekt aus M2)
```

**Reihenfolge:**
1. **M1** (Footer) — kann sofort starten, keine Abhängigkeit
2. **M2** (Header/Projekt) — parallel zu M1
3. **M3** (Assistent) — nach M2 (braucht Projekt-Kontext)
4. **M4** (Rechte Sidebar) — nach M2 (braucht Projekt-API)
5. **M5** (Cleanup) — nach M1–M4

---

## Entschiedene Fragen

| # | Frage | Entscheidung |
|---|-------|-------------|
| 1 | Mantis Avatar | **Kein Avatar.** Nie geplant. |
| 2 | Action-Buttons | Agentisch + systemisch + voice-getriggert. Alles was der Assistent ausführt/ändert/aufruft. Primär Voice-Chat. |
| 3 | R2 Workpaper-Edit | **Inline-Edit.** Preview + direktes Bearbeiten im Browser. |
| 4 | Voice-Chat vs. Chat-History | **Hart getrennt.** Voice = temporär/session. Chat-History = Projekt-persistent. Observer beobachtet Voice auf Relevanz. |
| 5 | Mobile/Responsive | **Desktop-only** vorerst. |
| 6 | Footer Overflow | **Kompakt halten.** Klein, simpel. Kein Overflow-Menu. |
| 7 | Fehler-Meldung | **Sofort, schnell, knapp.** Layer benennen (L0/L3/L4). Immer wenn Voice AN. |
| 8 | Projektwechsel | **Aktiver Event.** Soul neu berechnen, Stand durchsagen, Observer prüft altes Projekt. Fragt ob loslegen oder nur schauen. |
| 9 | R3 Inhalt | **WORKING-Baum** (AAMS-Struktur, navigierbar), nicht nur Workpaper-Liste. |

---

## Querverweise zu offenen Workpapers

| Workpaper | Relevanz für dieses Refactoring |
|-----------|---------------------------------|
| `2026-04-15-voice-integration-dashboard.md` | Phase 3 (Intent-Router, Observer) betrifft M3 direkt |
| `2026-04-13-project-scoped-aams.md` | Phase 2 (Ordner-Migration) betrifft M2+M4 Pfade |
| `2026-04-16-runtime-dashboard-bridge.md` | Bridge-Daten für Event-Feed in M3, Runtime-Modal in M1 |
| `2026-04-15-workspace-health-diagnostic.md` | Könnte als Modal im Footer (M1) oder als Event im Assistent |
| `2026-04-13-MCP-integration-research.md` | Backend-Dropdown ggf. MCP-aware (M1 Footer) |

---

## File Protocol

| # | File | Action | Notiz |
|---|------|--------|-------|
| 1 | `dashboard/templates/index.html` | MODIFY | Hauptarbeit: Layout-Umbau (alle Meilensteine) |
| 2 | `dashboard/static/style.css` | MODIFY | Neues 3-Column-Grid, Footer, Modals |
| 3 | `dashboard/app.py` | MODIFY | Neue API-Endpoints (Projekte, Workpapers, Tree) |
| 4 | `dashboard/static/main.js` | CREATE? | JS auslagern wenn zu groß für inline |
| 5 | `WORKING/PROJECT/_active.yaml` | CREATE | Aktives Projekt tracker |
| 6 | Dieses Workpaper | CREATE | Plan & Tracking |

---

## Implementation Log

### M1 — Implementiert 2026-04-16
- Footer mit 7 Controls: Backend-Dropdown, Model-Dropdown, Identity/Runtime/Tools/Prompts Buttons, Voice Toggle
- Runtime Modal (`#modal-runtime`): Tick-Tabelle, Health, Phase, Steps-Detail
- Tools Modal (`#modal-tools`): Projekt-Tools vs. Core-Tools, Skill-Marker
- `_lastRuntimeData` Cache für Modal-Updates
- `pollRuntime()` aktualisiert Footer + Event-Feed + Modal wenn offen

### M2 — Implementiert 2026-04-16
- Navbar: Logo links, Projekt-Dropdown zentriert (`.nav-center`), Model-Name rechts
- 3 API-Endpoints: `GET /api/projects`, `GET /api/projects/active`, `POST /api/projects/active`
- Backend-Helfer: `_list_projects()`, `_get_active_project_slug()`, `_set_active_project()`
- `_active.yaml` als Projekt-Tracker
- JS: `loadProjects()` → Dropdown populieren, `switchProject()` → POST + Reload

### M3 — Implementiert 2026-04-16
- Left Sidebar: `.assistant-focus` (Name + Projekt), `.assistant-voice-area`, `.assistant-events`
- Event-Feed: `_allEvents[]` global, `updateEventFeed()` mit ✅/❌/⚠️ + Goal
- Event Log Modal: `showEventModal()` mit 50-Event-History
- CSS für alle neuen Klassen

### M4 — Implementiert 2026-04-16
- R1: Projekt-Übersicht dynamisch via `GET /api/projects/active` (Name, Status-Badge, Scope, Milestones, Tags)
- R2: Aktives Workpaper Preview (Markdown, klickbar aus R3-Tree)
- R3: WORKING-Baum via `GET /api/projects/{slug}/tree` — aufklappbare Ordner mit Dateien
- R4: Chat-History (unverändert, jetzt Position R4)
- File-Viewer: `GET /api/projects/{slug}/file?path=...` mit Path-Traversal-Schutz
- `showWorkingFile(path)` — klick auf Datei in R3 → Preview in R2
- `loadProjectOverview()` + `loadWorkingTree()` — init + bei Projektwechsel
- `switchProject()` dynamisch statt `window.location.reload()` — aktualisiert R1, R3, Assistant-Fokus
- CSS: `.project-header`, `.project-status-badge`, `.project-scope`, `.project-tags`, `.tag`, `.tree-folder`, `.tree-files`, `.tree-file`, `.wp-preview-name`

### M5 — Implementiert 2026-04-16
- CSS entfernt: `.ws-folder`, `.ws-folder.agent-scope`, `.scope-tag`, `.scope-tag.agent`, `.ws-project`, `.project-status`, `.ws-milestones`, `.workpaper-content`, `#box-L5`
- JS entfernt: `toggleClosedWPs()` (keine Aufrufer mehr)
- Kommentare bereinigt: `L5 Voice Assistant` → `Voice Assistant`
- `.bak`-Dateien bleiben als Referenz (index.html.bak, style.css.bak)

---

## Next Steps

1. ~~M1 umsetzen~~ ✅
2. ~~M2 umsetzen~~ ✅
3. ~~M3 umsetzen~~ ✅
4. ~~M4 umsetzen~~ ✅
5. ~~M5 Cleanup~~ ✅

**Alle Meilensteine abgeschlossen.** Workpaper CLOSED.
