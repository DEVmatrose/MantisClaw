# Workpaper: Tools & Skills Architektur

| Feld | Wert |
|------|------|
| **Datum** | 2026-04-09 |
| **Status** | PROMOTED → WH-TOOLS v0.1.0-WIP |
| **Autor** | Agent (GitHub Copilot) |
| **Bezug** | WH-CORE §3 (L4), WH-CORE §4 (Module), WH-WORKING §2 (TOOLS/) |
| **Ziel** | Präzisierung der Tool-Registry + Skill-Kasten Architektur für MantisClaw |
| **Ergebnis** | Konzept präzisiert und als `WHITEPAPER/TOOLS.md` stabilisiert. Erweitert um Körper-Interface-Prinzip, Agenda-basiertes Tool-Filtering, geschärftes Schichtenmodell (L0-L7). |

---

## 1. Problemstellung

MantisClaw's Schichtenmodell definiert L4 als "Werkzeuge / TOOLS/", aber die Architektur unterscheidet bisher nicht zwischen:
- **Atomaren Funktionen** (Tool) — Was kann der Agent tun?
- **Orchestrierungsrezepten** (Skill) — Wie kombiniert der Agent Funktionen?

Ohne diese Trennung vermischen sich Ausführung und Strategie. Der Planner müsste jeden einzelnen Tool-Call kennen, statt auf höherer Ebene zu planen.

---

## 2. Architektur-Entscheidung

### Hierarchie (fest)

```
Agent-Loop (Planner)
    ↓ wählt Skill oder direkten Tool-Call
Skill-Executor
    ↓ orchestriert gemäß Workflow
Tool-Registry
    ↓ dispatcht an registriertes Tool
Tool-Implementierung (.py / API / CLI)
```

### Prinzip: Explizite Dependencies über dynamisches Laden

| Eigenschaft | Dynamisches Laden | Whitelist-Registry (gewählt) |
|---|---|---|
| Vorhersagbarkeit | LLM sieht nur, was geladen wird | LLM sieht alle verfügbaren Tools |
| Sicherheit | Code-Injection möglich | Nur registrierte Tools existieren |
| Debugging | Fehler erst zur Laufzeit | Fail-fast bei fehlendem Tool |
| Token-Budget | Variabel, unkontrolliert | Planbar, begrenzt |

---

## 3. Tool-Registry

### 3.1 Definition

Ein **Tool** ist eine atomare, zustandslose Funktion mit definierter Schnittstelle.

```
Tool = {
    name: str,              # Eindeutiger Identifier (snake_case)
    version: str,           # SemVer
    category: str,          # file_io | network | crypto | nostr | workspace | llm
    description: str,       # Für LLM-Kontext (max 100 Zeichen)
    parameters: Schema,     # JSON-Schema der Eingabe
    returns: Schema,        # JSON-Schema der Ausgabe
    requires: list[str],    # Systemvoraussetzungen (optional)
    security_level: str     # read | write | execute | admin
}
```

### 3.2 Registry-Struktur

```
core/
└── registry/
    ├── __init__.py         # ToolRegistry Klasse
    ├── registry.json       # Statische Tool-Deklarationen (Whitelist)
    └── tools/
        ├── file_io.py      # read_file, write_file, list_dir, ...
        ├── network.py      # http_get, http_post, ...
        ├── workspace.py    # read_workpaper, write_diary, query_ltm, ...
        ├── llm.py          # llm_complete, llm_embed, ...
        └── nostr.py        # nostr_publish, nostr_subscribe, ...
```

### 3.3 ToolRegistry API

```python
class ToolRegistry:
    def __init__(self, whitelist_path: str):
        """Lädt registry.json, validiert alle Tool-Deklarationen."""
    
    def get(self, name: str) -> Tool:
        """Gibt Tool zurück oder raised ToolNotFoundError (fail-fast)."""
    
    def list_tools(self, category: str = None) -> list[ToolSummary]:
        """Für LLM-Kontext: Name + Description aller (gefilterten) Tools."""
    
    def execute(self, name: str, params: dict) -> ToolResult:
        """Validiert params gegen Schema, führt aus, gibt Result zurück."""
    
    def validate_dependencies(self, tool_names: list[str]) -> ValidationResult:
        """Prüft ob alle geforderten Tools registriert sind."""
```

### 3.4 Security-Level

| Level | Erlaubt | Beispiel |
|---|---|---|
| `read` | Nur lesen, keine Seiteneffekte | `read_file`, `query_ltm` |
| `write` | Schreibt in WORKING/ | `write_workpaper`, `write_diary` |
| `execute` | Führt externe Prozesse aus | `run_script`, `http_post` |
| `admin` | Systemkritisch, braucht Bestätigung | `delete_file`, `nostr_publish` |

---

## 4. Skill-Kasten

### 4.1 Definition

Ein **Skill** ist ein Orchestrierungsrezept — eine Kombination aus Instruktionen (Prompt), Workflow-Logik und Tool-Dependencies.

### 4.2 Format: Markdown + YAML Hybrid

```markdown
---
name: research_and_validate
version: 0.1.0
description: "Recherchiert ein Thema und validiert Ergebnisse über SCIENCE"
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
├── skills/
│   ├── research_and_validate.md
│   ├── code_review.md
│   ├── diary_entry.md
│   ├── ltm_ingest.md
│   └── nostr_publish.md
└── registry/
    └── (symlink oder Referenz auf core/registry/)
```

> **Abgrenzung:** `WORKING/TOOLS/` enthält Skills (Rezepte). Die Tool-Implementierungen leben in `core/registry/tools/`. Skills sind AAMS-Body, Tools sind Runtime.

### 4.4 Skill-Executor API

```python
class SkillExecutor:
    def __init__(self, registry: ToolRegistry, skill_dir: str):
        """Lädt alle Skills, validiert Tool-Dependencies gegen Registry."""
    
    def load_skill(self, name: str) -> Skill:
        """Parst Markdown+YAML, gibt Skill-Objekt zurück."""
    
    def validate(self, skill: Skill) -> ValidationResult:
        """Prüft: Alle requires_tools in Registry? Schema-kompatibel?"""
    
    def execute(self, skill: Skill, context: dict) -> SkillResult:
        """Führt Workflow Schritt für Schritt aus.
        
        - Jeder Step: Tool aus Registry holen → execute → Output in State
        - on_failure: retry | skip_and_note | abort
        - Conditions: Einfache Ausdrücke über State-Variablen
        """
    
    def list_skills(self, category: str = None) -> list[SkillSummary]:
        """Für Planner-Kontext: Name + Description aller Skills."""
```

---

## 5. Integration in den Tick-Cycle

### Aktueller Tick (aus WH-CORE §4):
```
Session → Identity → Context → Hooks → Planner → Executor → Observer → RFL → Procedural → LTM → Sleep
```

### Erweiterter Executor-Schritt:

```
Planner
  ↓ action = { type: "skill" | "tool", name: str, params: dict }
Executor
  ├── type == "skill" → SkillExecutor.execute(skill, context)
  │                        ↓ (pro Step)
  │                      ToolRegistry.execute(tool, params)
  └── type == "tool"  → ToolRegistry.execute(tool, params) (Direkt)
Observer
  ↓ beobachtet SkillResult oder ToolResult
```

**Entscheidung:** Der Planner kann sowohl Skills als auch einzelne Tools direkt aufrufen. Skills sind der bevorzugte Weg für komplexe Aufgaben. Direkte Tool-Calls für atomare Aktionen.

---

## 6. Bootstrap-Implikation

Beim Start von MantisClaw:

```
1. ToolRegistry.__init__(whitelist_path)     # Alle Tools laden + validieren
2. SkillExecutor.__init__(registry, skill_dir) # Alle Skills laden + Dependencies prüfen
3. Falls Dependency fehlt → FATAL, kein Start  # Fail-fast
4. Planner erhält: registry.list_tools() + executor.list_skills()
   → In den LLM-Kontext als verfügbare Aktionen
```

---

## 7. Abgrenzungstabelle

| Aspekt | Tool | Skill |
|---|---|---|
| **Granularität** | Atomar (eine Funktion) | Zusammengesetzt (Workflow) |
| **Format** | `.py` (Code) | `.md` mit YAML-Header (Rezept) |
| **Zustand** | Stateless | Stateful (Workflow-State pro Ausführung) |
| **Ort** | `core/registry/tools/` | `WORKING/TOOLS/skills/` |
| **Schicht** | Runtime (L3/L4) | AAMS Body (L2) / Runtime (L3) |
| **Erstellt von** | Entwickler | Entwickler oder Agent (Procedural Memory) |
| **Sicherheit** | Security-Level pro Tool | Erbt Security-Level der verwendeten Tools |
| **LLM-Sichtbarkeit** | Name + Description + Schema | Name + Description + System-Prompt |

---

## 8. Offene Fragen

1. **Skill-Generierung:** Kann der Agent selbst neue Skills erstellen und in WORKING/TOOLS/skills/ ablegen? → Wäre Procedural Memory in Aktion.
2. **Skill-Versionierung:** Skills in WORKING/ unterliegen dem Workpaper-Lifecycle? Oder sind sie stabil wie Whitepapers?
3. **Tool-Kontext-Budget:** Wie viele Token verbraucht `list_tools()` + `list_skills()` im LLM-Kontext? → Muss in JIT-Budget (§5 WH-WORKING) eingeplant werden.
4. **Verschachtelte Skills:** Kann ein Skill einen anderen Skill aufrufen? → Erhöht Komplexität, aber auch Wiederverwendbarkeit.

---

## 9. Neue Module für WH-CORE

Folgende Module müssen in WH-CORE §4 ergänzt werden:

| Modul | Datei | Verantwortung |
|---|---|---|
| `registry` | `core/registry/__init__.py` | Tool-Registry: Whitelist, Lookup, Validierung, Dispatch |
| `skill_executor` | `core/skill_executor.py` | Skill-Parsing, Dependency-Check, Workflow-Ausführung |

Der bestehende `executor` (§4.3) delegiert an `skill_executor` oder `registry` je nach Action-Type.

---

## 10. Entscheidungen

| # | Entscheidung | Begründung |
|---|---|---|
| E1 | Whitelist-Registry statt dynamisches Laden | Vorhersagbarkeit, Sicherheit, Fail-fast |
| E2 | Skills als Markdown+YAML in WORKING/TOOLS/ | AAMS-konform, lesbar, versionierbar |
| E3 | Tools als Python in core/registry/tools/ | Runtime-Code, nicht AAMS-Body |
| E4 | Planner kann Tool oder Skill wählen | Flexibilität: atomar oder orchestriert |
| E5 | Fail-fast bei fehlenden Dependencies | Kein Start mit unvollständiger Registry |
| E6 | Security-Levels (read/write/execute/admin) | Granulare Zugriffskontrolle |

---

## File Protocol

| Aktion | Datei | Was |
|---|---|---|
| GELESEN | WH-CORE §3, §4 | Schichtenmodell L4, bestehende Module |
| GELESEN | WH-WORKING §2 | TOOLS/ Ordnerstruktur |
| ERSTELLT | Dieses Workpaper | Tools & Skills Architektur |
| GEPLANT | WH-CORE §4 Update | Neue Module registry + skill_executor |
| GEPLANT | WH-CORE §3 Update | L4 präzisieren |

---

## Nächste Schritte

1. ~~Review dieses Workpapers~~ ✅
2. ~~Whitepaper WH-TOOLS erstellt~~ ✅ (`WHITEPAPER/TOOLS.md` v0.1.0-WIP)
3. ~~WH-CORE aktualisieren (§3 Schichtenmodell + §4 Module: Core = reiner Loop)~~ ✅ L0-L7 + registry.py + skill_executor.py + Body-Tools umkategorisiert
4. ~~WH-WORKING aktualisieren (TOOLS/ Ordnerstruktur mit skills/)~~ ✅ skills/ Subfolder dokumentiert
5. Offene Fragen klären (§8 → übernommen in WH-TOOLS §9)


---

**Status:** CLOSED
**Geschlossen:** 2026-04-10

*Workpaper closed.*

