# WH-PROJECT — Projekt-Layer

> **Version:** 0.1.0  
> **Erstellt:** 2026-04-10  
> **Status:** DRAFT  
> **Abhängig von:** WH-WORKING (AAMS Body), WH-CORE (Runtime)

---

## §1 Zweck

Der PROJECT-Layer führt eine **Projektebene** zwischen Agenda und Workpapers ein.
Projekte bündeln Scope, Ziele, Meilensteine und ordnen Workpapers/Whitepapers zu.

**Kernprinzip:** Ein Agent kann viele Projekte haben, arbeitet aber immer nur an einem.

---

## §2 Abgrenzung

| Konzept | Zweck | Lebensdauer |
|---------|-------|-------------|
| **Agenda** | Taktische Aufgabenliste des Agenten | Langfristig, identitätsgebunden |
| **Projekt** | Scope + Ziele + Meilensteine für ein Vorhaben | Wochen bis Monate |
| **Workpaper** | Session-Artefakt (eine Arbeitssitzung) | Stunden |
| **Whitepaper** | Stabile Architektur-Wahrheit | Dauerhaft |

- Projekte ≠ Agenda. Agenda **referenziert** Projekte, ist aber eigenständig.
- Workpapers/Whitepapers **können** einem Projekt zugeordnet sein, **müssen** aber nicht.
- Projekte gehören **nicht** zur Identität (L1), sondern zum AAMS Body (L2).

---

## §3 Struktur

```
WORKSPACE/WORKING/
├── PROJECT/
│   ├── _active.yaml              ← Welches Projekt ist gerade aktiv?
│   ├── mantisclaw-core/
│   │   └── project.yaml          ← Manifest
│   ├── dashboard-integration/
│   │   └── project.yaml
│   └── ...
├── WORKPAPER/                     ← Zentral, WPs referenzieren Projekt per Slug
├── WHITEPAPER/                    ← Zentral, WHs referenzieren Projekt per Slug
└── ...
```

### §3.1 _active.yaml

```yaml
active_project: mantisclaw-core
since: 2026-04-10
```

Nur ein Projekt kann aktiv sein. Wechsel per Tool oder manuell.

### §3.2 project.yaml (Manifest)

```yaml
name: "MantisClaw Core"
slug: mantisclaw-core
status: active                # active | paused | completed | archived
created: 2026-04-02

scope: |
  Autonomer Agent-Loop Framework mit emergenter Identität.
  Core Runtime, Tool Registry, Reflection Loop, JIT Context.

goals:
  - "Vollständiger Planungs-/Handlungs-/Reflektionszyklus"
  - "Local-first: keine Cloud im Default"
  - "9+ Tools in der Registry"

milestones:
  - name: "Runtime Loop stabil"
    status: done
  - name: "RFL validiert"
    status: done
  - name: "PROJECT Layer"
    status: in-progress
  - name: "Dashboard Runtime-Integration"
    status: open

whitepapers:                  # Zugeordnete WHs (optional)
  - CORE.md
  - TOOLS.md
  - WORKING.md
  - IDENTITY.md
  - PROJECT.md

tags: [framework, core, runtime]
```

**Pflichtfelder:** `name`, `slug`, `status`, `created`, `scope`
**Optionale Felder:** `goals`, `milestones`, `whitepapers`, `tags`

---

## §4 Integration in soul(t)

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
                                                                    ↑
                                                            enthält jetzt:
                                                            - Aktives Projekt (Scope, Goals)
                                                            - Meilenstein-Status
```

### §4.1 Runtime-Integration

```python
# In runtime.py tick():
active_project = self._load_active_project()    # Liest _active.yaml + project.yaml
soul["project"] = active_project                 # Scope, Goals, Milestones
self.planner.set_project_context(active_project) # Planner plant im Projekt-Scope
```

### §4.2 Planner-Integration

Der Planner bekommt Projekt-Kontext als Teil des System-Prompts:
- Scope → Was gehört zum Projekt, was nicht
- Goals → Worauf hinarbeiten
- Milestones → Was ist schon done, was fehlt noch

### §4.3 Dashboard-Integration

Das Dashboard zeigt:
- Aktives Projekt + Status
- Zugeordnete Workpapers (per Slug-Match oder expliziter Referenz)
- Meilenstein-Fortschritt
- Projektliste in der Sidebar

---

## §5 Workpaper/Whitepaper-Zuordnung

### Explizit (im Workpaper-Header):
```markdown
**Project:** mantisclaw-core
```

### Implizit (kein Header):
Workpaper gehört zu keinem Projekt. Bleibt frei stehend.

### Whitepaper-Zuordnung:
Per `whitepapers:`-Liste im project.yaml. Ein Whitepaper kann zu mehreren Projekten gehören.

---

## §6 Lebenszyklus

```
created → active → paused → active → completed → archived
                     ↑                     │
                     └── kann reaktiviert ──┘
```

- **active:** Agent arbeitet daran (max 1 gleichzeitig aktiv)
- **paused:** Vorübergehend inaktiv, Kontext bleibt
- **completed:** Ziele erreicht, nur noch referenzierbar
- **archived:** In `PROJECT/_archived/` verschoben

---

## §7 Regeln

1. Projekte leben in `WORKSPACE/WORKING/PROJECT/` — ein Ordner pro Projekt.
2. Genau ein Projekt kann aktiv sein (`_active.yaml`).
3. Workpapers und Whitepapers bleiben in ihren zentralen Ordnern.
4. Zuordnung ist optional — freistehende WPs/WHs bleiben gültig.
5. Der Planner MUSS den Projekt-Scope respektieren wenn ein Projekt aktiv ist.
6. Projektwechsel wird im Diary geloggt.
