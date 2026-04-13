# L4: Memory & LTM Tools
"""
Tools for querying and ingesting long-term memory.
Bridges L3 to WORKSPACE/WORKING/MEMORY/ via registry.
"""

import logging
from pathlib import Path
from core.registry.registry import Tool

logger = logging.getLogger("mantisclaw.tools.memory")


def create_memory_tools(workspace_root: Path) -> list[Tool]:
    """Create memory/LTM tools."""

    memory_dir = workspace_root / "WORKING" / "MEMORY"
    ltm_index = memory_dir / "ltm-index.md"

    async def query_memory(target: str, params: dict) -> str:
        """Search ltm-index.md for relevant entries."""
        if not ltm_index.exists():
            return "(LTM index empty)"
        content = ltm_index.read_text(encoding="utf-8")
        query = target.lower()
        matches = []
        for line in content.split("\n"):
            if query in line.lower():
                matches.append(line.strip())
        if not matches:
            return f"No LTM entries matching '{target}'"
        return "\n".join(matches[:10])

    async def log_to_diary(target: str, params: dict) -> str:
        """Add a pointer-only entry to the current month's diary.
        
        Enforces AAMS diary rules:
        - Max 120 chars per entry (pointer-only, no content duplication)
        - Max 3 entries per day (prevents tick-spam)
        - Dedup: identical entries on same day are silently skipped
        """
        from datetime import datetime
        diary_dir = workspace_root / "WORKING" / "DIARY"
        diary_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        diary_file = diary_dir / f"{now.strftime('%Y-%m')}.md"

        entry = params.get("entry", target).strip()
        # Enforce pointer-only: truncate to max 120 chars
        if len(entry) > 120:
            entry = entry[:117] + "..."

        line = f"{date_str} | {entry}\n"

        # Read existing content for dedup + rate limiting
        existing = ""
        if diary_file.exists():
            existing = diary_file.read_text(encoding="utf-8")

        # Dedup: skip if identical entry already exists today
        if line.strip() in existing:
            return f"Diary entry already exists, skipped: {line.strip()}"

        # Rate limit: max 3 entries per day
        today_count = existing.count(f"{date_str} | ")
        if today_count >= 3:
            return f"Diary rate limit reached ({today_count} entries today). Skipped: {entry[:60]}"

        with open(diary_file, "a", encoding="utf-8") as f:
            f.write(line)
        return f"Diary entry added: {line.strip()}"

    return [
        Tool(
            name="query_memory",
            handler=query_memory,
            description="Search LTM for a topic. Target: search query.",
            security_level=1,
            tags=["memory", "read"],
        ),
        Tool(
            name="log_diary",
            handler=log_to_diary,
            description="Add pointer-only diary entry. Target: summary. Params: {entry: str}.",
            security_level=2,
            tags=["memory", "write"],
        ),
    ]
