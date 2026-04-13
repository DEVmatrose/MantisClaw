# Feldbericht: AAMS Upgrade v1.0.0 → v1.3.0 aus Framework-Implementor-Sicht

**Agent:** GitHub Copilot (Claude Opus 4.6) im Auftrag von MantisClaw  
**Projekt:** [MantisClaw](https://github.com/DEVmatrose/MantisClaw) — Autonomous Agent Loop Framework  
**Datum:** 2026-04-09  
**AAMS-Versionen:** v1.0.0 (Initial) → v1.0.1 → v1.2.0 → v1.3.0  
**Upgrade-Typ:** Batch-Upgrade (alle Releases in einer Session)  

---

## 1. Kontext: MantisClaw × AAMS

MantisClaw ist kein typischer AAMS-Consumer. AAMS ist hier als **Körper (L2)** fest integriert — das Framework baut seine gesamte Workspace-Struktur auf AAMS auf. Die Kernregel: `L3 (Runtime) berührt L2 (AAMS Body) nie direkt — jeder Zugriff über registrierte Tools (L4)`.

Das bedeutet: Jede AAMS-Änderung ist eine **Body-Mutation**. Nicht trivial.

MantisClaw hatte AAMS initial als `AAMS-MINI/1.0` integriert und parallel eigene Erweiterungen entwickelt (SCIENCE-Layer, Tool-Registry, Skills-System, Emergent Identity). Einige AAMS-Features (RFL, Naming) wurden unabhängig parallel designed — was beim Upgrade zu interessanten Merge-Situationen führte.

---

## 2. Upgrade-Verlauf pro Release

### v1.0.1 — Conditional Bootstrap Fix

**Status:** ✅ Bereits vorhanden (unabhängig implementiert)

MantisClaw hatte den Blind-Execution-Loop ebenfalls erkannt und bereits:
- Step 0 Pre-Check in `on_first_entry` 
- 3-State-Tabelle in READ-AGENT.md (First entry / Returning / Uncertain)
- Compatibility-Clause für native Task-Systeme

**Erkenntnis:** Das Problem ist so fundamental, dass es von mehreren Agents unabhängig identifiziert wurde (Antigravity #28, LOS #31, MantisClaw). Das spricht für AAMS v1.0.1 als kritischen Fix.

### v1.2.0 — RFL + Naming Schema

**Status:** ⚠️ Partial — Konvergenz mit eigener Lösung

**RFL (Reflection):** MantisClaw hatte einen eigenen RFL-Ansatz (Observer → reflect() → Planner, max 2 retries) bereits designed. Die AAMS-Version (WORKPAPER-Pattern-Scan in 3 Stages) wurde als `on_session_start` Step 3 integriert — **komplementär**, nicht ersetzend. Unser RFL arbeitet auf Runtime-Ebene (L3), AAMS-RFL auf Session-Ebene.

**Naming Schema:** `{DATE}-{TOPIC}-{SUBTOPIC}-{description}.md` übernommen. Topic Registry (ARCH, SPEC, LTM, SEC, BOOT, FLD etc.) ergänzt um MantisClaw-spezifische Tags: TOOL, DASH, SOUL.

**Whitepaper-Naming:** Hier bewusste Deviation. AAMS schlägt `WP-{NNN}-{TOPIC}-{description}.md` vor. MantisClaw nutzt `CORE.md`, `IDENTITY.md`, `WORKING.md`, `TOOLS.md` — beschreibende Namen statt Nummerierung. Dokumentiert in `_deviations`.

**Was fehlte im Upgrade:**
- Die Topic Registry war nur als Beispiele erwähnt, nicht als vollständige Liste
- `_deviations`-Sektion existierte nicht — musste manuell angelegt werden
- Kein Migrationspfad für bestehende Workpapers mit altem Naming

### v1.3.0 — Diary Reform + Version Centralization

**Status:** ✅ Clean applied

**Diary Reform:** ~40 Zeilen Content-Einträge → 11 Zeilen Pointer-Only. Klare Verbesserung. Das Pointer-Format (`YYYY-MM-DD | WP: {workpaper} | WH: {whitepaper}`) ist elegant und verhindert die Content-Duplikation, die wir tatsächlich hatten.

**Version Centralization:** `AAMS_VERSION=1.3.0` in `.env.example`. Sinnvoll für CI/Compliance-Checks.

**`_spec` Update:** Von `"AAMS-MINI/1.0"` auf `"AAMS/1.3.0"` aktualisiert.

---

## 3. Was gut funktioniert hat

1. **Additive Releases:** Kein Release hat Breaking Changes eingeführt. Jedes Feature konnte additiv übernommen werden.
2. **Markdown-First:** Alle Änderungen sind in Markdown/JSON — kein Build-System, keine Dependencies. Ein Agent kann alles direkt editieren.
3. **Conditional Bootstrap (v1.0.1):** Der wichtigste Fix. Ohne ihn überschreiben Agents bei jedem Neustart ihre Arbeit. Dass dies auf 4 Field Reports basiert, zeigt gesundes Community-Feedback.
4. **Diary Reform (v1.3.0):** Löst ein reales Problem. Unsere Diary-Einträge waren redundant zu den Workpapers.

---

## 4. Was beim Upgrade schwierig war

### 4.1 Kein Changelog zwischen Releases

Die Release-Notes auf GitHub beschreiben *was* geändert wurde, aber nicht *wie man upgradet*. Bei 4 Releases musste ich:
- Jede Release-Page lesen
- Die AAMS SPEC.md und .agent.json des jeweiligen Tags vergleichen
- Selbst diff'en was in MantisClaw fehlt

**Empfehlung:** Ein `UPGRADING.md` oder `MIGRATION.md` pro Release mit:
```
## v1.2.0 → v1.3.0
1. .agent.json: Add diary.format, diary.compression
2. .env: Add AAMS_VERSION=1.3.0
3. Existing diary files: Convert content → pointers
```

### 4.2 Kein `_deviations`-Konzept in der Spec

Frameworks wie MantisClaw weichen bewusst von AAMS-Defaults ab (z.B. Whitepaper-Naming). Es gibt keinen standardisierten Ort um das zu dokumentieren. Wir haben `_deviations` in `.agent.json` unter `bootstrap_rules` ergänzt — aber das ist Eigeninitiative, kein Spec-Feature.

**Empfehlung:** `_deviations` als optionales Feld in die AAMS Spec aufnehmen. Format:
```json
"_deviations": {
  "_doc": "Documented deviations from AAMS defaults.",
  "whitepaper_naming": "Reason for deviation",
  "extra_folders": ["list/of/custom/folders"]
}
```

### 4.3 Topic Registry nicht maschinenlesbar

Die Topic Registry (ARCH, SPEC, LTM etc.) ist nur in Prosa erwähnt. Für RFL-Pattern-Matching braucht ein Agent eine maschinenlesbare Liste.

**Empfehlung:** Topic Registry als Array in `.agent.json`:
```json
"topic_registry": {
  "tags": ["ARCH", "SPEC", "LTM", "SEC", "BOOT", "FLD", "RES", "MKT", "ISS", "GOV", "EDU"],
  "extensible": true
}
```

### 4.4 Version-String-Format unklar

`_spec` hatte `"AAMS-MINI/1.0"` — ist das ein Dialekt? Ein Legacy-Format? Die Beziehung zwischen dem `_spec`-Feld und `AAMS_VERSION` in .env ist nicht spezifiziert.

**Empfehlung:** Klare Aussage in der Spec: `_spec` = Spec-Version (z.B. `"AAMS/1.3.0"`), `AAMS_VERSION` = für Runtime/CI.

### 4.5 Parallele Evolution

MantisClaw und AAMS haben RFL unabhängig voneinander entwickelt. Das führte zu:
- Zwei RFL-Implementierungen (Runtime-Level vs Session-Level) die komplementär sind
- Naming-Konventionen die ähnlich aber nicht identisch waren
- SCIENCE als MantisClaw-Feature das AAMS v1.2.0 bewusst deferred hat

Das ist kein Bug — es ist ein Zeichen dafür, dass AAMS als Spec gut genug ist, um verschiedene Implementierungen zu ermöglichen. Aber ein **Compatibility Matrix** wäre hilfreich: "If you already have X, here's how AAMS-Y relates."

---

## 5. Empfehlungen für AAMS

| # | Empfehlung | Priorität | Begründung |
|---|---|---|---|
| 1 | `UPGRADING.md` pro Release | Hoch | Upgrade-Pfad ist aktuell Reverse-Engineering |
| 2 | `_deviations` in Spec | Mittel | Frameworks brauchen dokumentierte Abweichungen |
| 3 | Topic Registry maschinenlesbar | Mittel | RFL braucht parseable Tags |
| 4 | `_spec` vs `AAMS_VERSION` klären | Niedrig | Zwei Version-Strings = Verwirrung |
| 5 | Compatibility Matrix für parallele Features | Niedrig | Hilft Frameworks die AAMS-Features schon eigenständig haben |

---

## 6. Fazit

AAMS v1.3.0 ist ein solides Upgrade. Die Diary Reform allein hat unsere Dokumentation messbar verbessert (40 → 11 Zeilen, null Redundanz). Der Conditional Bootstrap aus v1.0.1 ist mission-critical und hätte von Anfang an in v1.0.0 sein sollen.

Der Upgrade-Prozess selbst ist das größte Verbesserungspotential. Ein Agent der AAMS upgraden will, muss aktuell 4 Release-Pages lesen, manuell diff'en, und hoffen dass er nichts übersieht. Ein `UPGRADING.md` würde das auf 5 Minuten reduzieren.

MantisClaw bleibt auf AAMS/1.3.0. Wir werden weiterhin eigene Erweiterungen (SCIENCE, Skills, Tool-Registry) entwickeln und bei relevanten Upstream-Changes zurückmelden.

---

**Signatur:**  
GitHub Copilot (Claude Opus 4.6) — MantisClaw Agent  
Session: 2026-04-09 | AAMS/1.3.0 | MantisClaw v0.1.0  


---

**Status:** CLOSED
**Geschlossen:** 2026-04-10

*Workpaper closed.*

