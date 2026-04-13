# LEGENDE — Abkürzungen & Begriffe in Mantis-OS

**Pflichtlektüre bei Session-Start. Keine Abkürzung ohne Eintrag hier.**

---

## Dokument-Typen

| Kürzel | Bedeutung | Ort | Beispiel |
|--------|-----------|-----|----------|
| **WP** | **W**ork**p**aper | `WORKSPACE/WORKING/WORKPAPER/` | WP-004-EMERGENT-IDENTITY.md |
| **WH** | **W**hite**p**aper (**H** für Hauptdokument) | `WORKSPACE/WORKING/WHITEPAPER/` | CORE.md, IDENTITY.md |
| **LTM** | **L**ong-**T**erm **M**emory | `WORKSPACE/WORKING/MEMORY/` + `AGENT-MEMORY/` | ltm-index.md |
| **GL** | **G**uide**l**ines | `WORKSPACE/WORKING/GUIDELINES/` | — |
| **DI** | **Di**ary | `WORKSPACE/WORKING/DIARY/` | 2026-04.md |
| **WH-TOOLS** | Whitepaper Werkzeuge | `WORKSPACE/WORKING/WHITEPAPER/` | TOOLS.md |

## Schichten (Layer)

| Kürzel | Bedeutung | Ort |
|--------|-----------|-----|
| **L0** | Hardware / LLM-Backend | `core/llm.py` + `config/` |
| **L1** | Identität | `identity/` |
| **L2** | AAMS Body (Körper) | `WORKSPACE/WORKING/` |
| **L3** | Runtime / Loop (Gehirn) | `core/` (runtime, planner, executor, observer, reflect) |
| **L4** | Tool-Registry (Fähigkeiten) | `core/registry/` — Whitelist aller Tools |
| **L5** | Skills (Procedural Memory) | `WORKING/TOOLS/skills/` — Orchestrierungs-Rezepte |
| **L6** | Security | Querschnitt — Security-Levels in Registry |
| **L7** | Netzwerk / MantisNostr | `core/registry/tools/nostr.py` |

## Systeme & Standards

| Kürzel | Bedeutung | Referenz |
|--------|-----------|----------|
| **AAMS** | **A**utonomous **A**gent **M**anifest **S**pecification | github.com/DEVmatrose/AAMS |
| **MN** | **M**antis**N**ostr (Nostr-Mesh) | github.com/DEVmatrose/MantisNostr |
| **MC** | **M**antis**C**law (Identity + Agent-Loop) | github.com/DEVmatrose/MantisClaw |
| **MOS** | **M**antis-**OS** (Integration: AAMS + MC + MN) | Dieses Repo |

## Dateien

| Datei | Bedeutung | Scope |
|-------|-----------|-------|
| `.agent.json` | AAMS Bootstrap — "One File" | Jedes Repo |
| `mantisagent.json` | Mantis-OS Bootstrap — "One File to weave them all" | Nur Mantis-OS |

## Identity-Dimensionen

| Kürzel | Bedeutung | Datei |
|--------|-----------|-------|
| **base** | Konstanten (Name, Ethik, Keys) | `identity/base.md` |
| **soul(t)** | Emergente Persönlichkeit zum Zeitpunkt t | Berechnet, keine Datei |
| **AG** | **Ag**enda (Wurzelknoten) | `identity/agenda.md` + `WORKSPACE/AGENDA/` |
| **ACC** | **Acc**ount-Register | `identity/account.md` |
| **SOC** | **Soc**ial / CRM-State | `identity/social.md` |
| **DEC** | **Dec**entral / Trust-Map | `identity/decentral.md` |

## Prozesse

| Kürzel | Bedeutung | Beschreibung |
|--------|-----------|--------------|
| **WK** | **W**issens**k**ette | WP → WH → LTM (strenge Reihenfolge) |
| **DTR** | **D**ual-**Tr**ack | LTM-Modus: Markdown (A) + Vector (B) |
| **RFL** | **R**e**fl**ection-Loop | Observer→reflect()→Planner Rückkanal, max 2 Retries |
| **JIT** | **J**ust-**I**n-**T**ime Context Loading | 3-Stufen: Always (~3k) + Agenda (~8k) + Query (~5k) |
| **SCIENCE** | **S**cience, **I**nsights, **N**ovelty, **C**ontext, **E**vidence | Knowledge Validation Layer |

## Memory-Klassen

| Kürzel | Bedeutung | Speicher | Format |
|--------|-----------|----------|--------|
| **BAU** | Bau-Memory | `WORKSPACE/WORKING/` | Markdown (WP, WH, DI, GL) |
| **OPS** | Operations-Memory | `WORKSPACE/AGENDA/` | SQLite (agenda.db) |

---

## Regeln

1. **Keine neue Abkürzung ohne Eintrag hier.**
2. **WP ≠ Whitepaper.** WP = Workpaper. Whitepaper = WH. Immer.
3. **Diese Datei wird bei Session-Start gelesen** — zusammen mit GUIDELINES.
4. **Ausgeschrieben > Abgekürzt** — im Zweifel ausschreiben.

---

*Kernel-Datei. Wird bei neuen Konzepten erweitert, nie gelöscht.*
