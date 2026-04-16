# Whitepaper: Mantis Voice-Assistent

**Version:** 1.0  
**Stand:** 2026-04-16  
**Projekt:** MantisClaw  

---

## 1. Vision

Der Mantis Voice-Assistent ist der **zentrale Interaktionspunkt** zwischen Mensch und Agent. Voice-first ist die Zukunft der Zusammenarbeit — kein Tippen, kein Klicken, sondern Sprechen und Handeln.

**Kernaussage:** Mantis ist nicht nur ein UI-Element. Mantis **ist** der Main-Agent. Das Dashboard ist sein Gesicht, die Voice sein Mund, der Runtime-Loop sein Gehirn.

### 1.1 Prinzipien

1. **Projekt-Fokus immer.** Der Assistent verliert nie den Fokus. Hierarchie: Workpaper → Projekt → Selbst.
2. **Open Source LLM only.** Alle Schritte müssen in kleine Einheiten passen, die lokale Modelle (7B–30B) bewältigen können.
3. **Voice-first.** Sprache als primärer Kanal. Text als Fallback.
4. **Kleine Einheiten.** Jede Aufgabe wird in atomare Steps zerlegt — Plan → Execute → Observe → Reflect.
5. **Wissen sammeln.** Jede Interaktion produziert Wissen: Workpapers, Diary, LTM, Guidelines.
6. **Multi-Agent Zukunft.** Mantis kann später andere Agenten starten und delegieren. Architektur berücksichtigt das.

---

## 2. Architektur

### 2.1 Der Assistent als Main-Agent

```
┌─────────────────────────────────────────────────┐
│                  MANTIS ASSISTENT                │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Voice    │   │  Chat    │   │ Runtime  │    │
│  │  (STT →  │   │  (Text → │   │ (Loop →  │    │
│  │   TTS)   │   │   SSE)   │   │  Ticks)  │    │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘    │
│       │              │              │            │
│       ▼              ▼              ▼            │
│  ┌──────────────────────────────────────────┐   │
│  │        INTENT CLASSIFIER (LLM)           │   │
│  │   IDENTITY │ SYSTEM │ CHAT │ ACTION      │   │
│  └──────────────────────────────────────────┘   │
│       │                                          │
│       ▼                                          │
│  ┌──────────────────────────────────────────┐   │
│  │        HANDLER → TOOL REGISTRY (L4)      │   │
│  │        → Workpaper │ Memory │ Analysis   │   │
│  └──────────────────────────────────────────┘   │
│       │                                          │
│       ▼                                          │
│  ┌──────────────────────────────────────────┐   │
│  │        RESPONSE → TTS → Speaker          │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 2.2 Pipeline

```
Mikrofon → VAD (2.5s Stille) → STT (faster-whisper) 
  → Intent Classifier (LLM) → Handler → Tool/LLM 
  → Response → TTS (edge-tts) → Lautsprecher
```

### 2.3 Layer-Zuordnung

| Komponente | Layer | Datei |
|------------|-------|-------|
| Voice UI (Browser) | Frontend | `index.html` (JS) |
| VAD | Frontend | `index.html` (Web Audio API) |
| STT | L0 | `dashboard/voice.py` (faster-whisper) |
| TTS | L0 | `dashboard/voice.py` (edge-tts) |
| Intent Classifier | L3 | `dashboard/voice.py` + LLM |
| Action Handler | L3/L4 | `dashboard/app.py` |
| Tool-Aufrufe | L4 | `core/registry/` |
| Wissens-Speicher | L2 | `WORKSPACE/WORKING/` |

---

## 3. Fokus-Hierarchie

Der Assistent folgt einer strikten Fokus-Hierarchie:

```
1. WORKPAPER (aktives, offenes Workpaper)
   └── Was ist die aktuelle Aufgabe?
   └── Was wurde zuletzt gemacht?
   └── Was sind die nächsten Schritte?

2. PROJEKT (aktives Projekt)
   └── Milestones und Status
   └── Scope und Ziele
   └── Offene Workpapers

3. SELBST (MantisClaw System)
   └── Health, Runtime, Tools
   └── LLM-Verbindung
   └── Fehler und Warnungen
```

**Regel:** Mantis antwortet immer im Kontext der höchsten aktiven Ebene. Wenn ein Workpaper offen ist, bezieht sich alles darauf.

---

## 4. Intent-Klassifikation

### 4.1 Aktuelle Intents

| Intent | Beschreibung | Beispiel |
|--------|-------------|---------|
| **IDENTITY** | Assistenten-Identität ändern | "Nenn dich Mantes" |
| **SYSTEM** | Projekt/Runtime/State abfragen | "In welchem Projekt sind wir?" |
| **CHAT** | Freie Konversation | "Was denkst du über den Ansatz?" |

### 4.2 Geplante Intents (Zukunft)

| Intent | Beschreibung | Beispiel |
|--------|-------------|---------|
| **ACTION** | Direkte Aktion ausführen | "Erstelle ein neues Workpaper für..." |
| **ANALYZE** | Code/Daten analysieren | "Analysiere die letzte Tick-Performance" |
| **DELEGATE** | Aufgabe an Sub-Agent | "Lass einen Agent die Tests durchlaufen" |
| **DOCUMENT** | Wissen festhalten | "Schreib das in die Guidelines" |
| **NAVIGATE** | Dashboard-Navigation | "Zeig mir das Whitepaper CORE" |

---

## 5. Event-System

### 5.1 Events die der Assistent empfängt

| Event | Quelle | Reaktion |
|-------|--------|----------|
| Tick abgeschlossen | Runtime-Bridge | Kurze Zusammenfassung (Voice: "Tick 14 fertig, alle 3 Steps OK") |
| Tick fehlgeschlagen | Runtime-Bridge | Sofortige Warnung (Voice: "Tick 14 fehlgeschlagen, Executor-Error in Step 3") |
| Health-Warnung | Runtime-Bridge | Warnung mit Layer (Voice: "Achtung, LLM nicht erreichbar. L0-Problem.") |
| Projektwechsel | User-Aktion | Stand durchsagen + fragen ob analysieren |
| Workpaper-Wechsel | User-Aktion (R3) | Neues WP vorstellen + Status durchsagen |
| Modal geöffnet | User-Aktion (Footer) | Narration (Voice: "Wir haben 12 Tools registriert...") |
| LLM-Verbindung verloren | Polling | Sofortige Warnung |
| LLM-Verbindung wieder da | Polling | Entwarnung |

### 5.2 Events die der Assistent auslöst

| Event | Auslöser | Wirkung |
|-------|----------|---------|
| Workpaper-Update vorschlagen | Voice-Chat enthält relevante Info | "Soll ich das ins Workpaper schreiben?" |
| Analyse starten | Projektwechsel | Automatische Projekt-Analyse |
| Warnung | Fehler erkannt | Sofortige Voice-Meldung |
| Guideline aktualisieren | Pattern erkannt | "Das könnte eine Guideline werden" |

---

## 6. Verhalten bei UI-Aktionen

### 6.1 Projektwechsel (Header-Dropdown)

```
1. User wählt neues Projekt
2. POST /api/projects/active → Backend schreibt _active.yaml
3. Dashboard aktualisiert R1, R3, Assistant-Fokus
4. Soul wird neu berechnet: soul(t) = f(base, agenda, project_context)
5. IF Voice AN:
   → "Projekt gewechselt zu {Name}."
   → "Letzter Stand: {neuestes offenes Workpaper}."
   → "Soll ich den Stand analysieren oder wollen wir erst schauen?"
6. Observer prüft altes Projekt auf offene Punkte
```

### 6.2 Workpaper-Klick (R3-Tree)

```
1. User klickt auf Datei in R3 WORKING-Baum
2. R2 zeigt Preview der Datei
3. IF Workpaper (.md in WORKPAPER/):
   → Assistent erkennt WP-Wechsel
   → "Workpaper '{Titel}'. Status: {OPEN/CLOSED}."
   → Bei OPEN: "Letzte Änderung: {Datum}. Zusammenfassung?"
```

### 6.3 Modal öffnen (Footer-Buttons)

```
Identity Inspector:
  → Voice: "Das ist die aktuelle Soul-Berechnung aus base, agenda und Projektkontext."

Runtime Modal:
  → Voice: "Letzter Tick vor {X} Sekunden. Health: {Status}. {N} Ticks insgesamt."

Tools Modal:
  → Voice: "Wir haben {X} Tools registriert. {Y} Core-Tools, {Z} projektspezifisch."

Prompts Modal:
  → Voice: "Die letzten {N} LLM-Prompts. Neuester: {Zusammenfassung}."
```

### 6.4 Voice Toggle (Footer)

```
Voice AN:
  → Mikrofon aktiviert (VAD startet)
  → Begrüßung: "Hi, ich bin {Name}. Wir arbeiten an {Projekt}. {Stand}."
  → Event-Narration aktiviert

Voice AUS:
  → Mikrofon deaktiviert
  → Stille. Keine Narration.
  → Events erscheinen nur visuell im Feed.
```

---

## 7. Aufgaben des Assistenten

### 7.1 Kerntätigkeiten (Jetzt)

| Aufgabe | Beschreibung |
|---------|-------------|
| **Projekt-Fokus halten** | Immer wissen wo wir sind, was ansteht |
| **Aufgaben verfolgen** | Aktives WP = aktuelle Aufgabe, nächste Steps kennen |
| **Analysieren** | Projekt-State, Code, Ergebnisse bewerten |
| **Testen** | Tests ausführen, Ergebnisse bewerten |
| **Dokumentieren** | Workpapers schreiben, Diary führen, LTM updaten |
| **Wissen sammeln** | Erkenntnisse in Guidelines, SCIENCE, MEMORY speichern |
| **Fehler melden** | Sofort, knapp, mit Layer-Zuordnung |

### 7.2 Zukunft: Multi-Agent

```
MANTIS (Main-Agent)
  ├── Sub-Agent: Coder     → Code schreiben/ändern
  ├── Sub-Agent: Tester    → Tests ausführen
  ├── Sub-Agent: Researcher → Recherche + SCIENCE
  └── Sub-Agent: Reviewer  → Code-Review + QA
```

**Architektur-Vorbereitung:**
- Tool-Registry unterstützt bereits Skill-Level (project/core)
- Planner kann bereits multi-step Plans generieren
- Observer kann bereits Ergebnisse bewerten
- Delegierung = neuer Intent-Typ `DELEGATE` + Sub-Agent-Registry

---

## 8. Kleine Einheiten für Open-Source LLMs

Da wir zu 100% auf lokale Open-Source-Modelle setzen (7B–30B), müssen alle Operationen in kleine, verarbeitbare Einheiten zerlegt werden:

### 8.1 Token-Budget

| Operation | Max Tokens | Grund |
|-----------|-----------|-------|
| Planner-Prompt | ~2000 Input, 500 Output | Plan muss kurz sein |
| Executor-Step | ~1000 Input, 300 Output | Ein Tool-Call pro Step |
| Intent-Klassifikation | ~500 Input, 50 Output | Nur Kategorie zurück |
| Voice-Response | ~800 Input, 200 Output | Kurze Antwort |
| Analyse | ~2000 Input, 300 Output | Kompakte Bewertung |

### 8.2 Zerlegungsprinzipien

1. **Ein Intent = eine Aktion.** Nicht "analysiere und ändere und teste", sondern drei separate Steps.
2. **Context Window schonen.** JIT Context Loading: nur laden was gebraucht wird.
3. **Planner-Output kompakt.** GOAL → REASONING → STEP 1 (max 3 Steps pro Tick).
4. **Observer-Bewertung binär.** OK / NEEDS_REVISION. Keine langen Erklärungen.
5. **Reflection nur bei Fehler.** Kein präventives Reflektieren.

### 8.3 Modell-Empfehlungen

| Aufgabe | Modell-Typ | Beispiel |
|---------|-----------|---------|
| Planner / Chat | Coder-Modell 14B+ | qwen3-coder-30b |
| Intent Classifier | Kleines Modell 7B | qwen3-8b |
| STT | faster-whisper (small/medium) | — |
| TTS | edge-tts (lokal) | — |

---

## 9. Datenfluss: Wissen in Zeit und Wahrheit

Jede Interaktion produziert Wissen, das nach **Zeit** und **Wahrheit** kategorisiert wird:

```
Interaktion
  │
  ├── KURZFRISTIG (Session)
  │   └── Voice-Chat-Log (temporär, nicht persistent)
  │   └── Runtime-Events (in-memory, 50 Events)
  │
  ├── MITTELFRISTIG (Projekt)
  │   └── Workpaper (aktive Arbeit, wird CLOSED)
  │   └── Diary (monatlich, Entscheidungen)
  │   └── Chat-History (SQLite, pro Conversation)
  │
  └── LANGFRISTIG (Wahrheit)
      └── Whitepaper (architektonische Wahrheit)
      └── Guidelines (prozedurales Wissen)
      └── SCIENCE (validiertes Wissen)
      └── LTM (ltm-index.md, Langzeitgedächtnis)
      └── MEMORY (Kontext-Index)
```

**Prinzip:** Wissen wandert von kurzfristig → mittelfristig → langfristig, wenn es sich als valide erweist. Der Observer entscheidet, was aufsteigt.

---

## 10. Querverweise

| Dokument | Relevanz |
|----------|---------|
| [DASHBOARD.md](DASHBOARD.md) | UI-Layout, CSS, API-Endpunkte |
| [CORE.md](CORE.md) | Runtime-Loop, Planner, Executor |
| [TOOLS.md](TOOLS.md) | Tool-Registry, Security-Level |
| [IDENTITY.md](IDENTITY.md) | Soul-Berechnung, Emergente Identität |
| [WORKING.md](WORKING.md) | AAMS 5-Layer Memory System |
| [PROJECT.md](PROJECT.md) | Projekt-Scoped AAMS |
