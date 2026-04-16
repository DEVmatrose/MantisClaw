# Runtime ↔ Dashboard Bridge

**Date:** 2026-04-16  
**Type:** Feature  
**Status:** OPEN  
**Related:** WP-VOICE (2026-04-15), BUG-dashboard-import (2026-04-16)

---

## Problem

Runtime und Dashboard laufen als **separate Prozesse**. `dashboard/app.py` hat eine `set_runtime()` Funktion für In-Process-Kopplung, die aber nie aufgerufen wird. Daher:

- L3 Sidebar zeigt immer "Runtime not connected"
- Live-Ticks bleiben leer
- Voice-Tick-Ansagen (core/voice.py) laufen nur im Terminal, nicht steuerbar vom Dashboard

## Lösung: File-basierte Bridge

Runtime schreibt State in `data/runtime_state.json`. Dashboard liest diese Datei.

### Architektur

```
core/runtime.py                    dashboard/app.py
     │                                  │
     │ ← write after each tick          │ ← read on /api/runtime poll
     │                                  │
     └──► data/runtime_state.json ◄─────┘
              │
              ├── running: bool
              ├── tick_count: int
              ├── health: str
              ├── heartbeat: int
              ├── voice_enabled: bool    ← Dashboard can toggle this
              ├── session: {workpaper, agent}
              ├── tools: [{name, desc, level}]
              ├── ticks: [{tick, ts, goal, steps, ok, fail, anomalies}]
              ├── tick_summaries: [str]
              ├── idle_repeats: int
              └── updated_at: ISO timestamp
```

### Voice-Toggle

- Runtime liest `voice_enabled` aus der Bridge-Datei vor jedem `voice.speak()`
- Dashboard schreibt `voice_enabled` via POST `/api/runtime/voice`
- Default: `true` (Voice an)

## File Protocol

| # | File | Action | Notiz |
|---|------|--------|-------|
| 1 | `core/runtime.py` | MODIFY | Bridge-Writer nach jedem Tick + Voice-Toggle |
| 2 | `dashboard/app.py` | MODIFY | `/api/runtime` + `/api/runtime/ticks` lesen Bridge-File |
| 3 | `data/runtime_state.json` | CREATE (auto) | Bridge-File, wird von Runtime geschrieben |

---

## Decisions

- [x] Option A gewählt: File-basierte Bridge (robust, einfach)
- [ ] Implementierung
- [ ] Test: Runtime + Dashboard gleichzeitig

## Next Steps

1. Bridge-Writer in runtime.py
2. Bridge-Reader in app.py
3. Voice-Toggle Endpoint
4. Test
