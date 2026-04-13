# L2: Workpaper-Verwaltung
"""
AAMS Workpaper-Management.
Erstellt, aktualisiert, schließt und archiviert Workpapers.
"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mantisclaw.workpaper")


class WorkpaperManager:
    """Manages AAMS workpaper lifecycle."""

    def __init__(self, workspace_root: Path):
        self.workpaper_dir = workspace_root / "WORKING" / "WORKPAPER"
        self.closed_dir = self.workpaper_dir / "closed"
        self.workpaper_dir.mkdir(parents=True, exist_ok=True)
        self.closed_dir.mkdir(parents=True, exist_ok=True)

    def create(self, agent: str, topic: str) -> Path:
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}-{agent}-{topic}.md"
        path = self.workpaper_dir / filename

        header = f"""# WP — {topic}

**Erstellt:** {date_str}
**Status:** OPEN
**Agent:** {agent}

---

## Session Goal

{topic}

---

## File Protocol

| Aktion | Datei | Notiz |
|--------|-------|-------|
"""
        path.write_text(header, encoding="utf-8")
        logger.info(f"Workpaper created: {filename}")
        return path

    def log_file_action(self, wp_path: Path, action: str, target: str, note: str = ""):
        line = f"| {action} | `{target}` | {note} |\n"
        with open(wp_path, "a", encoding="utf-8") as f:
            f.write(line)

    def close(self, wp_path: Path, decisions: list[str], next_steps: list[str]):
        content = wp_path.read_text(encoding="utf-8")
        content = content.replace("**Status:** OPEN", f"**Status:** CLOSED\n**Geschlossen:** {datetime.now().strftime('%Y-%m-%d')}")

        sections = "\n---\n\n## Decisions\n\n"
        for d in decisions:
            sections += f"- {d}\n"

        sections += "\n---\n\n## Next Steps\n\n"
        for s in next_steps:
            sections += f"- {s}\n"

        sections += "\n---\n\n*Workpaper closed.*\n"
        content += sections

        wp_path.write_text(content, encoding="utf-8")
        logger.info(f"Workpaper closed: {wp_path.name}")

    def archive(self, wp_path: Path) -> Path:
        dest = self.closed_dir / wp_path.name
        if dest.exists():
            # Append counter to avoid collision
            stem = dest.stem
            suffix = dest.suffix
            counter = 2
            while dest.exists():
                dest = self.closed_dir / f"{stem}-{counter}{suffix}"
                counter += 1
        wp_path.rename(dest)
        logger.info(f"Workpaper archived: {dest.name}")
        return dest
