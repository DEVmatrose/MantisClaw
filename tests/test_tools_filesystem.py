"""Unit tests for filesystem tools."""
import pytest
from pathlib import Path
from core.registry.tools.filesystem import create_filesystem_tools


@pytest.fixture
def fs_tools(workspace_root):
    return {t.name: t for t in create_filesystem_tools(workspace_root / "WORKSPACE")}


@pytest.mark.asyncio
async def test_list_dir(fs_tools):
    tool = fs_tools["list_dir"]
    result = await tool.handler("WORKING", {})
    assert "WHITEPAPER" in result or "whitepaper" in result.lower()


@pytest.mark.asyncio
async def test_read_file(fs_tools, workspace_root):
    tool = fs_tools["read_file"]
    result = await tool.handler("WORKING/WHITEPAPER/CORE.md", {})
    assert "MantisClaw" in result


@pytest.mark.asyncio
async def test_workspace_status(fs_tools):
    tool = fs_tools["workspace_status"]
    result = await tool.handler("", {})
    assert "WHITEPAPER" in result or "whitepaper" in result.lower()


@pytest.mark.asyncio
async def test_read_file_outside_workspace(fs_tools):
    """Should not read files outside workspace — path traversal blocked."""
    tool = fs_tools["read_file"]
    with pytest.raises(PermissionError):
        await tool.handler("../../etc/passwd", {})
