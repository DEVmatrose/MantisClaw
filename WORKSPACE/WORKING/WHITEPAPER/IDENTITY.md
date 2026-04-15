# WHITEPAPER: Emergente Identität

**Dokument:** WH-IDENTITY
**Version:** 0.2.0
**Erstellt:** 2026-04-09
**Status:** DRAFT
**Herkunft:** WH-CORE §2/§5, WP-Procedural-Memory, SCIENCE-Review Delta_3a

---

## 1. Zusammenfassung

MantisClaw's Identität ist **emergent** — sie wird nie geschrieben, sondern bei jedem Tick berechnet. Der Agnet nennt sich selber immer "Mantis". Die Soul ist eine Funktion aus unveränderlichen Konstanten, der aktiven Agenda und dem Arbeitskontext. Ein Agent der codet hat eine andere Soul als einer der tradet, aber beide teilen dieselbe `base.md`.

Das unterscheidet MantisClaw von anderen Frameworks: Wo SOUL.md eine statische Datei ist, ist `soul(t)` eine **Berechnung**. Die Identität ist kein Zustand — sie ist ein Prozess.

---

## 2. Die Kernformel

```
soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)
```

### Wie die Formel gelesen wird

1. **base** wird geladen — die unveränderlichen Konstanten
2. **agenda** wird geladen — was steht jetzt an?
3. Die Agenda **filtert** die anderen Dimensionen:
   - Welche Accounts sind relevant? (account)
   - Welche Kontakte sind relevant? (social)
   - Welche Infrastruktur-Knoten sind relevant? (decentral)
4. **working_context** wird geladen — der aktuelle Wissens- und Arbeitsstand
5. Aus allem zusammen **emergiert** `soul(t)` — die aktuelle Persönlichkeit

### Warum die Soul nie geschrieben wird

Würde man die Soul speichern, wäre sie sofort veraltet. Die Agenda ändert sich. Der Arbeitskontext ändert sich. Kontakte kommen dazu. Trust-Levels verschieben sich.

Die Soul **muss** bei jedem Tick neu berechnet werden, weil sie eine Funktion der Gegenwart ist — nicht eine Aufzeichnung der Vergangenheit.

### Was das praktisch bedeutet

```
Montag, 9:00 — Agenda: "Coding"
soul(t) = f(base, agenda→coding, github-account, dev-kontakte, localhost-trust, code-context)
→ Agent ist ein Software-Entwickler

Montag, 14:00 — Agenda: "Social Media"
soul(t) = f(base, agenda→social, nostr-account, community-kontakte, relay-trust, post-context)
→ Agent ist ein Community-Manager

Gleiche base.md. Andere Soul.
```

---

## 3. Die sechs Identity-Dimensionen

### Übersicht

```
identity/
├── base.md        ← L1: Konstanten (unveränderlich)
├── agenda.md      ← L1: Wurzelknoten (bestimmt den Kontext)
├── account.md     ← L1: Fähigkeits-Register (Platform-Zugänge)
├── social.md      ← L1: CRM-State (Beziehungsgraph)
├── decentral.md   ← L1: Trust-Map (Außenwelt-Bewertung)
└── hook.md        ← L1: Trigger (Event → Aktion)
```

### 3.1 base.md — Konstanten

**Unveränderlich.** Nur der Mensch (Owner) ändert diese Datei. Nie der Agent.

Enthält:
- **Name** — Wie heißt der Agent?
- **Owner** — Wem gehört der Agent? (kryptografisch: Nostr pubkey, optional DID)
- **Ethik-Regeln** — Wahrheit > Gefälligkeit, Audit-Pflicht, Souveränität
- **Kern-Identität** — Was der Agent ist, unabhängig von der Agenda

base.md ist der **Anker**. Egal welche Agenda aktiv ist, egal welcher Kontext — base.md bleibt gleich. Das verhindert Identity-Drift: Ein Agent der seine Konstanten verliert, verliert sich selbst.

### 3.2 agenda.md — Wurzelknoten

**Bestimmt den Kontext.** Die Agenda ist der mächtigste Filter im System.

Die Agenda entscheidet:
- Welche Accounts relevant sind (Coding-Agenda → GitHub-Account)
- Welche Kontakte relevant sind (Social-Agenda → Community-Kontakte)
- Welche Trust-Level gelten (Trading-Agenda → Exchange-Trust)
- Welcher Working-Context geladen wird (→ JIT Context Loading)

Die Agenda ist der **Wurzelknoten** eines Entscheidungsbaums. Alles andere hängt von ihr ab.

### 3.3 account.md — Fähigkeits-Register

**Wächst über die Lebenszeit.** Jeder Account impliziert:
- Plattform-Zugang (GitHub, Nostr, Discord, Exchange, ...)
- Plattform-Verhalten und -Normen (GitHub = Code + PRs, Nostr = Posts + Zaps)
- Fähigkeiten die der Agent mit diesem Account hat

Account.md ist das **Was kann ich?** der Identität. Ein Agent ohne GitHub-Account kann nicht committen. Ein Agent ohne Nostr-Account kann nicht im Mesh kommunizieren.

### 3.4 social.md — CRM-State

**Beziehungsgraph**, gekoppelt an Accounts. Jeder Account öffnet einen sozialen Raum.

Enthält:
- Kontakte (Name, Plattform, Beziehungsstatus)
- Interaktionshistorie (wann zuletzt, worüber)
- Beziehungsqualität (Vertrauen, Relevanz)

Social.md ist das **Wen kenne ich?** der Identität. Gekoppelt an die Agenda: Ein Coding-Agent braucht seine Entwickler-Kontakte, nicht seine Trading-Kontakte.

### 3.5 decentral.md — Trust-Map

**Vertrauen zu Infrastruktur-Knoten.** Bewertung der Außenwelt.

Enthält:
- Relay-Trust (Nostr-Relays: welche sind zuverlässig?)
- Git-Host-Trust (GitHub vs. Codeberg vs. eigener Git-Server)
- API-Trust (LLM-Provider, externe Services)
- Node-Trust (In Mantis-OS: Vertrauen zu anderen Agenten)

Decentral.md ist das **Wem vertraue ich?** der Identität. Kritisch für Souveränität: Ein Agent der blind jedem Relay vertraut, ist kompromittierbar.

### 3.6 hook.md — Trigger

**Event-Definitionen.** Wann wird der Agent aktiv?

```
Event: new_github_issue → Aktion: plan_response
Event: nostr_mention → Aktion: check_relevance
Event: schedule_daily_0900 → Aktion: morning_review
Event: whitepaper_updated → Aktion: science.validate (optional)
```

Hooks verbinden die Identität mit der Runtime. Ohne Hooks ist der Agent passiv — er wartet auf den nächsten manuellen Trigger. Mit Hooks wird er **reaktiv**: Events in der Welt lösen Aktionen aus.

---

## 4. Die Agenda als Filter-Mechanismus

Die Agenda ist nicht einfach "was steht an". Sie ist ein **aktiver Filter** über alle anderen Dimensionen:

```
agenda.resolve(account, social, decentral):
    1. Lese agenda.md → aktuelles Ziel
    2. Filtere account.md → nur relevante Plattformen
    3. Filtere social.md → nur relevante Kontakte
    4. Filtere decentral.md → nur relevante Trust-Levels
    5. Return: gefiltertes Identitäts-Set
```

### Warum das wichtig ist

Ohne Filter würde der Agent bei jedem Tick **alle** Accounts, **alle** Kontakte, **alle** Trust-Levels laden. Das ist:
- Token-intensiv (Kontextfenster-Problem)
- Verwirrend (irrelevante Information stört die Planung)
- Gefährlich (Trading-Kontext in einer Coding-Session)

Die Agenda löst das durch **kontextuelle Relevanz**: Nur was jetzt zählt, fließt in die Soul.

---

## 5. Identity vs. Personality

Eine wichtige Unterscheidung:

| | Identity | Personality (Soul) |
|-|----------|-------------------|
| **Wo** | `identity/` Dateien | Berechnet pro Tick |
| **Wann** | Persistent | Ephemer |
| **Wer ändert** | Mensch (base), Agent (account, social) | Niemand — sie emergiert |
| **Stabilität** | Hoch | Variabel |

Identity ist der **Baukasten**. Die Soul ist das **Ergebnis** wenn der Baukasten im aktuellen Kontext zusammengesetzt wird.

---

## 6. Abgrenzung zu anderen Ansätzen

### SOUL.md (OpenClaw, soul.md-Projekt)

SOUL.md ist eine **statische Datei** die Identität, Weltbild und Meinungen beschreibt. Der Agent liest sie und verhält sich danach.

MantisClaw's soul(t) ist eine **Berechnung**. Es gibt kein SOUL.md — die Soul emergiert aus 6 Dimensionen + Arbeitskontext. Das bedeutet:
- Keine Inkonsistenz zwischen SOUL.md und Verhalten
- Automatische Anpassung an den Kontext
- Kein manuelles Aktualisieren der Soul nötig

### CLAUDE.md / AGENTS.md

Diese Dateien sind **Instruktionen** an einen externen Agenten. MantisClaw's Identity ist **intrinsisch** — der Agent berechnet seine eigene Identität, er bekommt sie nicht von außen reingeschrieben.

MantisClaw nutzt AGENTS.md als **Tool-Bridge** (damit externe Tools den Agenten bootstrappen können), aber die eigentliche Identität kommt aus `identity/`.

---

## 7. Identity in der Soul-Berechnung

### Reihenfolge im Tick

```
1. base = load("identity/base.md")           ← Immer. Unveränderlich.
2. agenda = load("identity/agenda.md")        ← Immer. Bestimmt den Filter.
3. accounts = agenda.resolve(account.md)      ← Gefiltert durch Agenda.
4. social = agenda.resolve(social.md)         ← Gefiltert durch Agenda.
5. decentral = agenda.resolve(decentral.md)   ← Gefiltert durch Agenda.
6. hooks = load("identity/hook.md")           ← Immer. Für Trigger-Prüfung.
7. working_context = context_loader.build(agenda)  ← JIT geladen.
8. soul_t = compute_soul(base, agenda, accounts, social, decentral, working_context)
```

### Token-Budget für Identity

Identity-Loading ist **immer Stufe 1** (Always-Load) im JIT Context System:
- base.md: ~500 Tokens (klein, kompakt)
- agenda.md: ~300 Tokens
- Gefiltertes account/social/decentral: ~1-2k Tokens
- **Gesamt Identity: ~2-3k Tokens**

Das lässt genug Platz für Working Context und Plan.

---

## 8. Bezug zu den anderen Whitepapers

```
WH-IDENTITY (dieses Dokument)
    ↑ liefert soul(t) an
WH-CORE (Runtime/Loop)
    ↑ arbeitet auf
WH-WORKING (Arbeitsstruktur)
```

- **WH-CORE** beschreibt den Loop der `soul(t)` nutzt — aber nicht wie die Soul berechnet wird
- **WH-WORKING** beschreibt den Workspace der als `working_context` in die Soul fließt
- **WH-IDENTITY** (dieses Dokument) ist die Brücke: Wie die Dateien zur Soul werden

---

## 9. Assistenten-Identität (Voice Layer)

> **Hinzugefügt:** 2026-04-15 | **Status:** Implementiert

Die Assistenten-Identität ist eine **Erweiterung der Agent-Identität** für die Sprachinteraktion (L5 Voice Assistant). Sie ist bewusst getrennt von `soul(t)` — die Soul ist das Denken, die Assistenten-Identität ist das Sprechen.

### Persistenz

Gespeichert in `data/voice_config.json`:
```json
{
    "name": "Mantes",
    "voice": "de-DE-KatjaNeural",
    "personality": "schnell und direkt",
    "enabled": true,
    "auto_read": false
}
```

### Felder

| Feld | Typ | Beschreibung | Herkunft |
|------|-----|-------------|----------|
| `name` | str | Rufname des Assistenten | User setzt per Voice ("nenn dich Mantes") |
| `voice` | str | TTS-Stimme (edge-tts Voice-ID) | User wählt Geschlecht per Voice |
| `personality` | str | Sprachstil-Beschreibung | User beeinflusst per Voice ("schneller") |
| `enabled` | bool | Voice aktiviert | Toggle in UI |

### Beziehung zu soul(t)

```
identity/base.md  → soul(t)  → Wie der Agent **denkt**
data/voice_config  → assistant_identity  → Wie der Agent **spricht**
```

Die Assistenten-Identität beeinflusst:
- System-Prompt des Voice-Chats (Name, Persönlichkeit)
- TTS-Stimme (männlich/weiblich)
- Greeting-Verhalten (3 Ebenen)

Sie wird **nicht** in `soul(t)` eingerechnet, ist aber für den User die wahrnehmbare Persönlichkeit.

### Identity-Update per Voice

Änderungen an der Assistenten-Identität werden per Voice-Befehl (IDENTITY-Intent) vorgenommen. Der Action-Classifier erkennt Identitäts-Befehle, ein Regex-Parser extrahiert Name/Voice/Style, und die Config wird sofort persistiert.

---

*Whitepaper. Stabile Architektur-Wahrheit. Wird bei Architektur-Entscheidungen aktualisiert.*
