# GUIDELINE: Release & Workpaper Lifecycle

- **Erstellt:** 2026-04-09
- **Quelle:** Session-Erkenntnis — Workpapers ohne Release-Zuordnung sind später schwer einzuordnen

## Regeln

- [2026-04-09] Bei jedem Release: Alle zugehörigen Workpapers schließen und mit `Release: vX.Y.Z` markieren
  → Quelle: Realitätscheck beim Durchgehen aller offenen WPs — keine Release-Zuordnung vorhanden

- [2026-04-09] Workpaper-Status beim Schließen enthält: `Status: CLOSED`, `Geschlossen: {date}`, `Release: vX.Y.Z`
  → Standardisiertes Format für Nachvollziehbarkeit

- [2026-04-09] Design-Workpapers (Konzept steht, Implementierung offen) bleiben OPEN bis Code existiert
  → Quelle: JIT + Procedural Memory WPs — Design erledigt, aber Next Steps sind Code-Tasks

- [2026-04-09] Workpapers die in ein Whitepaper überführt wurden: Status = `PROMOTED → WH-{NAME}`
  → Quelle: tools-skills-architecture WP → WH-TOOLS
