# L2: LTM-Index + Ingest
"""
Long-Term Memory Manager.
Ingestiert Workpapers in ltm-index.md (Markdown-Modus).
"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mantisclaw.ltm")


class LTMManager:
    """Manages the long-term memory index."""

    def __init__(self, workspace_root: Path):
        self.memory_dir = workspace_root / "WORKING" / "MEMORY"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.memory_dir / "ltm-index.md"

    def _ensure_index(self):
        if not self.index_path.exists():
            header = """# LTM Index — MantisClaw

> Long-term memory. Ingested from workpapers, decisions, architecture changes.

---

## Entries

"""
            self.index_path.write_text(header, encoding="utf-8")

    def ingest_workpaper(self, wp_path: Path):
        self._ensure_index()

        content = wp_path.read_text(encoding="utf-8")
        date_str = datetime.now().strftime("%Y-%m-%d")
        wp_name = wp_path.stem

        entry = f"""
### {date_str} | {wp_name} (AUTO-INGEST)

**Source:** `WORKPAPER/closed/{wp_path.name}`
**Ingested at:** {datetime.now().isoformat()}

_Workpaper auto-ingested at session close._

---
"""
        with open(self.index_path, "a", encoding="utf-8") as f:
            f.write(entry)

        logger.info(f"LTM ingested: {wp_path.name}")

    def query(self, topic: str, max_results: int = 5) -> list[str]:
        if not self.index_path.exists():
            return []

        content = self.index_path.read_text(encoding="utf-8")
        entries = content.split("### ")[1:]  # skip header

        results = []
        topic_lower = topic.lower()
        for entry in entries:
            if topic_lower in entry.lower():
                results.append(entry.strip())
            if len(results) >= max_results:
                break

        return results
