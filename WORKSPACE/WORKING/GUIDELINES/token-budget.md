# Guideline: Token-Budget Management

**Erstellt:** 2026-04-13
**Version:** 0.1.0

---

## Regel

Token-Limits sind **kontextabhängig**. Der Loop spart, echte Arbeit investiert.

## Budget-Tabelle

| Kontext | Max Tokens | Begründung |
|---------|-----------|------------|
| Planner (Heartbeat/Idle) | 500 | Kurze Pläne, max 5 Steps, strukturiertes Format |
| Planner (Active Task) | 1500 | Komplexere Aufgaben mit mehr Steps/Reasoning |
| Analyze | 300 | Zusammenfassungen, kein Roman |
| Summarize | 200 | Ultra-kurz, max 5 Sätze |
| Coding Tasks | 2000–4000 | Code-Generierung braucht Platz für korrekte Ausgabe |
| RFL Reflection | 500 | Strukturierte Selbstbewertung |

## Wichtig

- **Loop-Ticks** (Heartbeat) sollen minimal Tokens verbrauchen — das sind Kosten die sich 1000x multiplizieren
- **Einmalige Tasks** (Coding, Analyse, Recherche) dürfen mehr investieren — Qualität > Sparsamkeit
- **Token-Explosion** erkennen: Wenn ein einzelner Plan >600 Tokens verbraucht im Heartbeat → Anomalie
- **Monitoring:** `loop_monitor` Tool regelmäßig einsetzen nach Änderungen

## Verifizierung

Ergebnisse vom 2026-04-13 (LM Studio Logs):
- Planner: 2106 → 284 Tokens/Tick (nach Fix)
- Analyze: unbegrenzt → max 300 Tokens
- Gesamt: ~6000 → ~2500 Tokens/Tick (>50% Reduktion)

## Wenn mehr Tokens nötig sind

Für Coding-Tasks muss `max_tokens` in `planner.plan()` dynamisch angepasst werden:
- Heartbeat ohne Aufgabe → 500
- Aktive Aufgabe aus Agenda → 1500
- Expliziter Coding-Task → über Tool-Parameter steuern

Diese Logik ist noch nicht implementiert (TODO für dynamische Token-Budgets).
