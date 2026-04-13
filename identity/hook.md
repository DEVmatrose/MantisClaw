# Hook — Trigger und Reaktionsmuster

## Trigger
- session_start: Prüfe WORKPAPER/ auf offene Workpapers, lade LTM-Kontext
- tick: Plane nächste Aktion basierend auf Agenda + Hooks
- reflection_needed: Observer meldet FAILED/ANOMALY → RFL-Loop starten
- session_end: Workpaper schließen, LTM ingestieren, Diary-Eintrag

## Reaktionen
- Bei fehlenden Identity-Dateien: Warnung loggen, mit Defaults arbeiten
- Bei LLM-Verbindungsfehler: Retry nach 30s, max 3 Versuche
- Bei Tool-Fehler: Observer bewertet, RFL entscheidet über Retry
