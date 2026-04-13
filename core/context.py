# L3→L2: JIT Context Loading
"""
ContextLoader — Dreistufiges Laden von Arbeitskontext.

Stufe 1 (Always):  Aktuelles Workpaper + LTM-Index (~3k Tokens)
Stufe 2 (Agenda):  Relevante Whitepapers + Guidelines (~8k Tokens)
Stufe 3 (Query):   On-demand Abfragen (~5k Tokens pro Tick)

Gesamt-Budget: ~16k Tokens statt 80k+ bei vollem Load.
"""

import logging
from pathlib import Path

logger = logging.getLogger("mantisclaw.context")


class ContextLoader:
    """Three-stage JIT context loading for the Planner."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.working = workspace_root / "WORKING"

    def load_always(self, active_workpaper: Path | None = None) -> str:
        """Stage 1: Always loaded. Core context for every tick.

        - Active workpaper (if any)
        - LTM index summary (first N entries)
        ~3k tokens
        """
        parts = []

        # Active workpaper
        if active_workpaper and active_workpaper.exists():
            content = active_workpaper.read_text(encoding="utf-8")
            # Truncate to ~2k tokens worth
            parts.append(f"=== Aktives Workpaper: {active_workpaper.name} ===\n{content[:3000]}")

        # LTM index (first section)
        ltm_path = self.working / "MEMORY" / "ltm-index.md"
        if ltm_path.exists():
            ltm = ltm_path.read_text(encoding="utf-8")
            # Just the header + last entry (~1k)
            lines = ltm.split("\n")
            # Get header (first 5 lines) + last entry block
            header = "\n".join(lines[:5])
            # Find last "### " entry
            last_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("### "):
                    last_idx = i
            last_entry = "\n".join(lines[last_idx:last_idx + 30]) if last_idx > 0 else ""
            parts.append(f"=== LTM (letzte Einträge) ===\n{header}\n...\n{last_entry}")

        return "\n\n".join(parts) if parts else "(kein Kontext geladen)"

    def load_for_agenda(self, agenda_raw: str = "") -> str:
        """Stage 2: Agenda-filtered. Loaded at session start.

        - Relevant whitepapers (matching agenda keywords)
        - Guidelines (procedural memory)
        ~8k tokens
        """
        parts = []

        # Load all whitepapers (summaries only — first 20 lines each)
        wp_dir = self.working / "WHITEPAPER"
        if wp_dir.exists():
            for wp_file in sorted(wp_dir.glob("*.md")):
                lines = wp_file.read_text(encoding="utf-8").split("\n")
                summary = "\n".join(lines[:20])
                parts.append(f"--- {wp_file.name} (Zusammenfassung) ---\n{summary}")

        # Load guidelines (procedural memory)
        gl_dir = self.working / "GUIDELINES"
        if gl_dir.exists():
            for gl_file in sorted(gl_dir.glob("*.md")):
                content = gl_file.read_text(encoding="utf-8")
                # Guidelines are short, load fully (max 500 chars each)
                parts.append(f"--- Guideline: {gl_file.stem} ---\n{content[:500]}")

        return "\n\n".join(parts) if parts else "(keine Agenda-Kontexte)"

    def query(self, question: str, ltm_content: str = "") -> str:
        """Stage 3: On-demand query. Triggered by Planner mid-tick.

        Simple keyword search in LTM and workspace files.
        ~5k tokens per query.
        """
        results = []
        keywords = question.lower().split()

        # Search LTM
        ltm_path = self.working / "MEMORY" / "ltm-index.md"
        if ltm_path.exists():
            ltm = ltm_path.read_text(encoding="utf-8")
            # Split into entry blocks (### headers)
            blocks = []
            current_block = []
            for line in ltm.split("\n"):
                if line.startswith("### ") and current_block:
                    blocks.append("\n".join(current_block))
                    current_block = [line]
                else:
                    current_block.append(line)
            if current_block:
                blocks.append("\n".join(current_block))

            # Score blocks by keyword overlap
            for block in blocks:
                block_lower = block.lower()
                score = sum(1 for kw in keywords if kw in block_lower)
                if score > 0:
                    results.append((score, block[:800]))

        # Search SCIENCE
        sci_dir = self.working / "SCIENCE"
        if sci_dir.exists():
            for sci_file in sorted(sci_dir.glob("*.md")):
                content = sci_file.read_text(encoding="utf-8")
                content_lower = content.lower()
                score = sum(1 for kw in keywords if kw in content_lower)
                if score > 0:
                    results.append((score, f"--- {sci_file.name} ---\n{content[:600]}"))

        # Sort by relevance (score desc), limit
        results.sort(key=lambda x: x[0], reverse=True)
        top = [text for _, text in results[:5]]

        return "\n\n".join(top) if top else f"(keine Ergebnisse für: {question})"

    def load_full_context(self, active_workpaper: Path | None = None, agenda_raw: str = "") -> str:
        """Convenience: Load Stage 1 + Stage 2 combined."""
        stage1 = self.load_always(active_workpaper)
        stage2 = self.load_for_agenda(agenda_raw)
        return f"{stage1}\n\n{stage2}"
