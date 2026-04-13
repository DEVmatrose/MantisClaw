# L4: Filesystem Tools — gated access to WORKSPACE
"""
Tools for reading and writing files within the WORKSPACE directory.
All paths are validated against allowed_paths from config.
"""

import logging
from pathlib import Path
from core.registry.registry import Tool

logger = logging.getLogger("mantisclaw.tools.filesystem")


def create_filesystem_tools(workspace_root: Path, allowed_paths: list[str] | None = None) -> list[Tool]:
    """Create filesystem tools scoped to the workspace."""

    if allowed_paths is None:
        allowed_paths = [str(workspace_root)]

    def _validate_path(target: str) -> Path:
        """Ensure path is within allowed boundaries."""
        resolved = (workspace_root / target).resolve()
        for allowed in allowed_paths:
            allowed_resolved = Path(allowed).resolve()
            if str(resolved).startswith(str(allowed_resolved)):
                return resolved
        raise PermissionError(f"Path outside allowed boundaries: {target}")

    async def read_file(target: str, params: dict) -> str:
        path = _validate_path(target)
        if not path.exists():
            return f"[ERROR] File not found: {target}"
        content = path.read_text(encoding="utf-8")
        max_len = params.get("max_length", 4000)
        if len(content) > max_len:
            content = content[:max_len] + f"\n... (truncated, {len(content)} chars total)"
        return content

    async def write_file(target: str, params: dict) -> str:
        content = params.get("content", "")
        if not content:
            return "[ERROR] No content provided"
        path = _validate_path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Written {len(content)} chars to {target}"

    async def list_dir(target: str, params: dict) -> str:
        path = _validate_path(target)
        if not path.exists() or not path.is_dir():
            return f"[ERROR] Not a directory: {target}"
        entries = []
        for item in sorted(path.iterdir()):
            prefix = "📁" if item.is_dir() else "📄"
            entries.append(f"{prefix} {item.name}")
        return "\n".join(entries) if entries else "(empty)"

    async def append_file(target: str, params: dict) -> str:
        content = params.get("content", "")
        if not content:
            return "[ERROR] No content provided"
        path = _validate_path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Appended {len(content)} chars to {target}"

    async def workspace_status(target: str, params: dict) -> str:
        """Return a summary of the current workspace state."""
        lines = [f"Workspace: {workspace_root}"]
        working = workspace_root / "WORKING"
        if working.exists():
            for folder in sorted(working.iterdir()):
                if folder.is_dir():
                    count = len(list(folder.rglob("*.md")))
                    lines.append(f"  {folder.name}/: {count} .md files")
        # Active workpapers
        wp_dir = working / "WORKPAPER"
        if wp_dir.exists():
            active = [f.name for f in wp_dir.glob("*.md")]
            lines.append(f"Active workpapers: {len(active)}")
            for a in active[:5]:
                lines.append(f"  - {a}")
        return "\n".join(lines)

    return [
        Tool(
            name="read_file",
            handler=read_file,
            description="Read a file from WORKSPACE. Target: relative path.",
            security_level=1,
            tags=["filesystem", "read"],
        ),
        Tool(
            name="write_file",
            handler=write_file,
            description="Write content to a file in WORKSPACE. Target: relative path. Params: {content: str}.",
            security_level=2,
            tags=["filesystem", "write"],
        ),
        Tool(
            name="append_file",
            handler=append_file,
            description="Append content to a file. Target: relative path. Params: {content: str}.",
            security_level=2,
            tags=["filesystem", "write"],
        ),
        Tool(
            name="list_dir",
            handler=list_dir,
            description="List directory contents. Target: relative path.",
            security_level=1,
            tags=["filesystem", "read"],
        ),
        Tool(
            name="workspace_status",
            handler=workspace_status,
            description="Get workspace overview: folders, file counts, active workpapers.",
            security_level=1,
            tags=["filesystem", "read"],
        ),
    ]
