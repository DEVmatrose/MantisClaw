# L2: Session-Lifecycle (open/close/archive)
"""
AAMS-konformer Session-Manager.
Erzeugt/schließt Workpapers automatisch.
"""

import logging
from datetime import datetime
from pathlib import Path

from core.workpaper import WorkpaperManager
from core.ltm import LTMManager

logger = logging.getLogger("mantisclaw.session")


class Session:
    """Manages one agent session from open to close."""

    def __init__(self, workspace_root: Path, agent_name: str = "mantisclaw"):
        self.workspace_root = workspace_root
        self.agent_name = agent_name
        self.workpaper_mgr = WorkpaperManager(workspace_root)
        self.ltm_mgr = LTMManager(workspace_root)
        self.workpaper_path: Path | None = None
        self.started_at: datetime | None = None
        self.topic: str = "session"

    def open(self, topic: str = "session") -> Path:
        self.topic = topic
        self.started_at = datetime.now()
        self.workpaper_path = self.workpaper_mgr.create(
            agent=self.agent_name,
            topic=topic,
        )
        logger.info(f"Session opened: {self.workpaper_path.name}")
        return self.workpaper_path

    def log_action(self, action: str, target: str, note: str = ""):
        if self.workpaper_path:
            self.workpaper_mgr.log_file_action(self.workpaper_path, action, target, note)

    def close(self, decisions: list[str] | None = None, next_steps: list[str] | None = None):
        if not self.workpaper_path:
            logger.warning("No active session to close")
            return

        self.workpaper_mgr.close(
            self.workpaper_path,
            decisions=decisions or [],
            next_steps=next_steps or [],
        )

        self.ltm_mgr.ingest_workpaper(self.workpaper_path)

        archived = self.workpaper_mgr.archive(self.workpaper_path)
        logger.info(f"Session closed and archived: {archived.name}")

        self.workpaper_path = None
        self.started_at = None
