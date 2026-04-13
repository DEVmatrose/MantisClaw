# SCIENCE REVIEW: MantisClaw vs. State of the Art

- **Datum:** 2026-04-09
- **Typ:** review
- **Trigger:** Manuell — Erste Systemvalidierung nach Bootstrap
- **Scope:** MantisClaw-Gesamtarchitektur gegen aktuellen Stand der Forschung (Agent-Loop, Memory, Identity, Planning)
- **Quellbasis:** `SCIENCE/2026-04-09-Erkenntnisse und neuen Forschungsbereiche.md` (Claude, ChatGPT, Kimi — drei unabhängige LLM-Perspektiven)

---

## 1. Summary

MantisClaw ist architektonisch **nahe am State of the Art** und in mehreren Bereichen **ahead of the curve**. Die emergente Soul-Berechnung, die dateibasierte Memory-Architektur und die AAMS-Integration sind konzeptionell solide und decken sich mit den dominanten Trends 2025/2026. Es gibt drei Bereiche mit Lücken: Procedural Memory, Multi-Agent-Koordination und Reflection-Loop-Integration. Insgesamt: Ein Framework das auf dem richtigen Fundament baut.

---

## 2. Key Claims (extrahiert aus CORE.md, README.md, .agent.json)

| # | Claim | Quelle |
|---|-------|--------|
| C1 | Die Soul wird nie geschrieben — sie emergiert bei jedem Tick | CORE.md §2 |
| C2 | `soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)` ist die Kernformel | CORE.md §2 |
| C3 | AAMS ist als Struktur fest in MantisClaw integriert | CORE.md §1 |
| C4 | File-basiertes Memory (Markdown + Ordnerstruktur) ist der primäre Speicher | CORE.md §6, §7 |
| C5 | Local-first LLM-Backend (LM Studio > Ollama > Cloud) | CORE.md §4.5 |
| C6 | Heartbeat-Loop mit Plan → Execute → Observe Cycle | CORE.md §4.1 |
| C7 | Wissenskette: Workpaper → Whitepaper → LTM | CORE.md §6 |
| C8 | MantisClaw kann standalone oder als Teil von Mantis-OS laufen | CORE.md §9 |
| C9 | Identity-Dimensionen (base, agenda, account, social, decentral, hook) bilden die Persönlichkeit | CORE.md §5 |
| C10 | "One File to Bootstrap" — `.agent.json` genügt | CORE.md §8 |

---

## 3. Validation

| Claim | Status | Confidence | Evidence | Notes |
|-------|--------|-----------|----------|-------|
| **C1 — Emergente Soul** | **confirmed** | 0.85 | B, C | Deckt sich mit SOUL.md-Trend und Personalization-Layer-Ansatz. Kimi bestätigt: "Personalization Layer (Wer der Agent ist)" ist State of the Art. MantisClaw geht weiter: Soul ist nicht statisch sondern **berechnet**. Das ist innovativer als die meisten Ansätze. |
| **C2 — Kernformel** | **confirmed** | 0.80 | C, D | Kein direktes Pendant in der Literatur. Aber konzeptionell konsistent mit CoALA-Framework (Princeton): Agent = Procedural Memory + Semantic Memory + Working Memory. MantisClaw's Formel ist eine **kompaktere Darstellung** desselben Konzepts — base=procedural, agenda.resolve()=semantic filtering, working_context=working memory. |
| **C3 — AAMS integriert** | **confirmed** | 0.90 | B | AAMS als Workspace-Standard ist vergleichbar mit Claude Code's Dateistruktur, Manus' File-System und OpenClaw's Memory-Layout. Die Integration (statt externe Abhängigkeit) ist der richtige Ansatz. |
| **C4 — File-based Memory** | **confirmed** | 0.95 | B, C | Alle drei Quellen bestätigen unabhängig: "Files are all you need" (Manus-Prinzip), "Markdown + Files sind kein Hack, sondern ernstzunehmender Ansatz" (Claude 2), "Memory as Documentation vs. Memory as Database" (Kimi). MantisClaw ist hier **voll im Trend**. |
| **C5 — Local-first LLM** | **confirmed** | 0.75 | C, D | Nicht direkt in der Forschung adressiert (Fokus liegt auf Cloud-APIs). Aber konsistent mit Souveränitäts-Trend und Framework-Unabhängigkeit. Riskant bei Modellqualität — local models sind schwächer als Frontier-Models. |
| **C6 — Plan→Execute→Observe Loop** | **confirmed** | 0.90 | A, B | Exakt das dominierende Pattern 2026. Kimi: "Ideal Agent = Global Planning (Plan) + Flexible Execution (ReAct) + Continuous Optimization (Reflexion)". MantisClaw's Planner→Executor→Observer bildet das ab. |
| **C7 — Wissenskette WP→WH→LTM** | **confirmed** | 0.80 | C, D | Kein direktes Pendant in der Literatur, aber konzeptionell verwandt mit Summarization Pipelines und Memory-Konsolidierung. Die explizite Kette (flüchtig → stabil → persistent) ist ein **sauberer Formalismus** der in anderen Systemen implizit, aber nicht explizit existiert. |
| **C8 — Standalone + Mantis-OS** | **unverified** | 0.60 | D | Mantis-OS existiert als Konzept. Multi-Agent-Orchestration ist State of the Art, aber MantisClaw's Integration in ein größeres OS ist noch nicht implementiert. Die Architektur erlaubt es — ob es funktioniert ist offen. |
| **C9 — Identity-Dimensionen** | **confirmed** | 0.85 | C | Geht über SOUL.md hinaus. Die meisten Systeme haben 1-2 Identity-Files. MantisClaw hat 6 Dimensionen (base, agenda, account, social, decentral, hook) die **kontextabhängig gefiltert** werden. Das ist innovativer als der Mainstream. |
| **C10 — One File Bootstrap** | **confirmed** | 0.90 | B | Konsistent mit AGENTS.md-Standard (Linux Foundation). Single-file-bootstrap mit `.agent.json` ist clean und standards-konform. |

---

## 4. External Context — Wo MantisClaw im Feld steht

### 4.1 Vergleich mit bekannten Ansätzen

| System / Pattern | Fokus | MantisClaw-Äquivalent | Delta |
|-----------------|-------|----------------------|-------|
| **Claude Code** | File-Memory, CLAUDE.md, Hooks | AAMS + identity/, hook.md | MantisClaw hat reichere Identity-Dimensionen |
| **Manus** | "Files are all you need", Plain-Text Memory | WORKING/ Struktur | Sehr ähnlich. MantisClaw hat explizitere Wissenskette. |
| **OpenClaw** | File-based Agent, SOUL.md | identity/base.md | MantisClaw: Soul wird berechnet, nicht geschrieben |
| **Mem0** | Vector + Graph Memory, 4 Scopes | LTM (Markdown, optional ChromaDB) | MantisClaw fehlt Graph-Memory. Aber bewusste Entscheidung (local-first). |
| **Letta/MemGPT** | OS-inspirierte Memory-Hierarchie | WORKING/ Schichten | Konzeptionell verwandt. Letta ist code-basiert, MantisClaw datei-basiert. |
| **CoALA Framework** | 4 Memory-Typen (Working, Episodic, Semantic, Procedural) | Workpaper=Working, Diary=Episodic, Memory=Semantic, ???=Procedural | **Lücke: Procedural Memory fehlt explizit** |
| **AGENTS.md Standard** | Single-file agent manifest | .agent.json + AGENTS.md | Kompatibel. MantisClaw nutzt beides. |

### 4.2 Trends die MantisClaw bereits abdeckt

- **"Memory > Model"** — MantisClaw's gesamte Architektur ist Memory-zentrisch (WORKING/) 
- **"Context Engineering"** — soul(t) ist im Kern Context Engineering: welche Information fließt wann in die Identität
- **"Files are all you need"** — Markdown + Ordnerstruktur, versionierbar, transparent
- **"Stateful Agents"** — Workpapers, LTM, Diary = Agent hat echten Zustand über Sessions

### 4.3 Trends die MantisClaw NICHT abdeckt (noch)

- **Graph Memory** — Kein Knowledge Graph. Nur flache Markdown-Dateien + optional ChromaDB.
- **Actor-Aware Memory** — In Multi-Agent-Setting: Wer hat was geschrieben? Nicht getaggt.
- **Procedural Memory** — Agent kann seine eigenen Prompt-Strategien nicht selbst ändern.
- **Auto-Compaction** — Keine automatische Kontext-Komprimierung bei Token-Overflow.
- **RL-based Memory Optimization** — Kein Reinforcement Learning für Memory-Management.

---

## 5. Differences (Delta_3) — MantisClaw vs. externe Realität

### Delta_3a: Emergente Identity vs. Statische Identity

| Aspekt | Industrie-Standard | MantisClaw |
|--------|--------------------|-----------|
| Identity-Speicher | `SOUL.md` (statische Datei) | `soul(t)` (berechnet pro Tick) |
| Kontextabhängigkeit | Keine — gleiche Persona immer | Agenda filtert relevante Dimensionen |
| Dimensionen | 1-2 Files (Soul, Style) | 6 Dimensionen (base, agenda, account, social, decentral, hook) |

**Bewertung:** MantisClaw ist hier **ahead of the curve**. Die Berechnung statt Speicherung der Identität ist ein genuiner Beitrag. Confidence: 0.85.

### Delta_3b: Memory-Architektur

| Aspekt | Industrie-Standard | MantisClaw |
|--------|--------------------|-----------|
| Primärer Speicher | Hybrid (Vector + Graph + Files) | Files (Markdown) + optional ChromaDB |
| Memory-Typen | 4+ (Working, Episodic, Semantic, Procedural) | 3 explizit (Workpaper≈Working, Diary≈Episodic, Memory≈Semantic) |
| Retrieval | Embedding-Search + Graph-Traversal | File-Read + LTM-Index-Query |
| Procedural Memory | Agent ändert eigene Strategien | Fehlt |

**Bewertung:** MantisClaw ist **solide aber nicht komplett**. File-based Memory ist validiert und der richtige Ansatz. Die fehlende Procedural-Memory-Dimension ist die größte Lücke. Confidence: 0.80.

### Delta_3c: Planning-Loop

| Aspekt | Industrie-Standard | MantisClaw |
|--------|--------------------|-----------|
| Pattern | Plan + ReAct + Reflexion (kombiniert) | Plan → Execute → Observe |
| Reflexion | Expliziter Reflection-Step nach Execution | Observer bewertet, aber kein expliziter Self-Correction-Loop |
| Plan-Revision | Agent kann Plan mid-execution ändern | Noch nicht spezifiziert |

**Bewertung:** Das Grundmuster stimmt. Der Observer ist da, aber ein expliziter **Reflexion-Loop** (Observer findet Problem → Planner revidiert → neuer Versuch) ist nicht formalisiert. Confidence: 0.75.

### Delta_3d: AAMS als Workspace-Standard

| Aspekt | Industrie-Standard | MantisClaw/AAMS |
|--------|--------------------|----------------|
| Workspace-Struktur | Jedes Framework eigenes Schema | Standardisiert (WORKING/ mit festen Ordnern) |
| Session-Protokoll | Implizit oder proprietär | Explizit (Workpaper mit File Protocol) |
| Audit-Trail | Logging-basiert | Diary + Workpaper-Archiv |
| Bootstrap | Verschiedene (requirements.txt, Dockerfile, etc.) | Single-file (.agent.json) |

**Bewertung:** AAMS als integrierte Struktur ist **ein Differenzierungsmerkmal**. Kein anderes Framework hat eine so explizite, standardisierte Workspace-Architektur. Confidence: 0.90.

---

## 6. Risks — Blinde Flecken und falsche Annahmen

| # | Risiko | Schwere | Mitigation |
|---|--------|---------|-----------|
| R1 | **Procedural Memory fehlt** — Agent kann nicht aus eigenen Fehlern seine Arbeitsweise ändern | Mittel | GUIDELINES/ könnte als Proto-Procedural-Memory dienen. Explizit machen. |
| R2 | **Local-first LLM-Qualität** — LM Studio/Ollama-Modelle sind signifikant schwächer als Frontier-Models für komplexes Planning | Hoch | Fallback-Kette ist da (Config). Aber Planner-Qualität hängt direkt am Modell. Testen mit verschiedenen Backends. |
| R3 | **Kein Graph-Memory** — Beziehungen zwischen Entitäten (Personen↔Projekte↔Entscheidungen) gehen in flachen Dateien verloren | Niedrig (jetzt), Hoch (bei Skalierung) | Für Einzelagent okay. Bei Mantis-OS mit mehreren Agenten wird das relevant. |
| R4 | **Reflexion-Loop nicht formalisiert** — Observer meldet Anomalien, aber es gibt keinen definierten Pfad zurück zum Planner | Mittel | Observer→Planner-Feedback-Pfad definieren. Eventuell als RFL-Protokollschritt. |
| R5 | **Token-Management nicht adressiert** — working_context kann bei großen Workspaces das Kontextfenster sprengen | Mittel | Selektives Laden (JIT Context) implementieren. Nicht alles in jeden Tick laden. |
| R6 | **Wissenskette hat keinen Rückkanal** — WP→WH→LTM ist one-way. LTM kann nicht WH korrigieren. | Niedrig | Bewusste Design-Entscheidung. Korrektur geht über neue Workpapers. |

---

## 7. Hypothesen — Was aus der Analyse folgt

| # | Hypothese | Begründung | Priorität |
|---|-----------|-----------|-----------|
| H1 | **GUIDELINES/ ist Proto-Procedural-Memory** — Wenn der Agent GUIDELINES/ aktiv lesen und schreiben kann, hat MantisClaw implizit Procedural Memory | GUIDELINES existiert bereits im Workspace. Fehlt nur die Loop-Integration. | Hoch |
| H2 | **soul(t) ist Context Engineering** — Die Kernformel ist nichts anderes als systematisches Context Engineering. Das sollte explizit so benannt werden. | Alle drei Quellen bestätigen: Context Engineering ist DAS Paradigma 2026. MantisClaw tut es, nennt es aber nicht so. | Mittel |
| H3 | **Observer + Reflection = RFL** — Ein formalisierter Reflection-Step nach dem Observer könnte MantisClaw's Loop State-of-the-Art-komplett machen | Kimi: "Ideal Agent = Plan + ReAct + Reflexion". MantisClaw hat Plan + Execute + Observe, aber nicht den expliziten Reflexion-Rückkanal. | Hoch |
| H4 | **SCIENCE als Delta_3-Sensor** — SCIENCE-Dokumente machen MantisClaw zum einzigen Framework das systematisch prüft ob die eigenen Entscheidungen noch State of the Art sind | Kein anderes bekanntes Framework hat einen vergleichbaren Mechanismus. | Mittel |
| H5 | **JIT Context Loading** — Statt alles in working_context zu laden, sollte der Planner selektiv `memory_query(topic)` nutzen. Das ist bereits in CORE.md §4.1 angedeutet. | Standard-Pattern 2026: "search_memory() statt mega prompt mit allem" | Hoch |
| H6 | **Actor-Tagging in Workpapers** — Für Mantis-OS Multi-Agent: Jeder Workpaper-Eintrag sollte den Quell-Agent taggen | Actor-Aware Memory ist ein identifiziertes Problem in Multi-Agent-Systemen. | Niedrig (wird erst bei Multi-Agent relevant) |

---

## 8. Quellen

| # | Quelle | Level | Kernaussage |
|---|--------|-------|-------------|
| S1 | LangChain — Context Engineering Formalisierung | B | Vier Operationen: Write, Select, Compress, Forget. Context Engineering > Prompt Engineering. |
| S2 | AGENTS.md Standard (Linux Foundation / Agentic AI Foundation) | B | Single-file agent manifest, framework-unabhängig. MantisClaw ist kompatibel. |
| S3 | CoALA Framework (Princeton, 2023) | A | Vier Memory-Typen: Working, Episodic, Semantic, Procedural. Referenz-Taxonomie. |
| S4 | Mem0 (2026) | B | 26% bessere Accuracy, 91% niedrigere Latenz. Hybrid Vector+Graph. |
| S5 | Manus — "Files are all you need" | C | File-basierte Memory als Wettbewerbsvorteil. Persistent, transparent, debugbar. |
| S6 | OpenClaw / soul.md Projekt | C | SOUL.md als komponierbares Identity-Artefakt. Widersprüche machen identifizierbar. |
| S7 | Letta/MemGPT | B | OS-inspirierte Memory-Hierarchie. Agents editieren eigene Memory via Tool Calls. |
| S8 | MIRIX (arXiv) | A | 6 Memory-Typen parallel. Multi-Agent Memory-System. |
| S9 | MemFactory (arXiv) | A | RL für Memory-Management: wann speichern, was löschen, was priorisieren. |
| S10 | Gartner 2025/2026 Reports | B | 33% Enterprise-Software mit Agentic AI bis 2028. 40% Failure-Rate bei schlechtem Memory. |
| S11 | Claude, ChatGPT, Kimi — Drei LLM-Perspektiven (manuell gesammelt 2026-04-09) | D | Konvergente Einschätzung zum State of the Art. Basis dieser Analyse. |

---

## 9. Gesamtbewertung

```
MantisClaw Alignment mit State of the Art: ~80%

Bereiche wo MantisClaw überdurchschnittlich ist:
  ★ Emergente Identity (soul(t) berechnet, nicht geschrieben)
  ★ AAMS als integrierte Workspace-Struktur (kein anderes Framework hat das)
  ★ Explizite Wissenskette (WP→WH→LTM)
  ★ File-based Memory als Kernansatz

Bereiche wo MantisClaw nachziehen sollte:
  △ Procedural Memory (GUIDELINES/ als Basis nutzen)
  △ Reflection-Loop formalisieren (Observer→Planner Rückkanal)
  △ JIT Context Loading (selektiv statt alles laden)

Bereiche die erst bei Skalierung relevant werden:
  ○ Graph Memory
  ○ Actor-Aware Memory
  ○ Multi-Agent Orchestration
```

---

*SCIENCE Review. Erstellt 2026-04-09. Basiert auf drei unabhängigen LLM-Perspektiven und MantisClaw CORE.md v0.1.0.*
