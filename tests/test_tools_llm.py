"""Unit tests for LLM management tools."""
import pytest
from pathlib import Path
from core.registry.tools.llm_management import create_llm_management_tools


@pytest.fixture
def llm_tools(workspace_root):
    return {t.name: t for t in create_llm_management_tools(workspace_root)}


@pytest.mark.asyncio
async def test_list_models(llm_tools):
    """list_models should return model info (requires LM Studio)."""
    tool = llm_tools["list_models"]
    result = await tool.handler("", {})
    # If LM Studio is up, should contain model names
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_token_budget(workspace_root):
    """token_budget should return budget table."""
    from core.registry.tools.loop_monitor import create_loop_monitor_tools
    tools = {t.name: t for t in create_loop_monitor_tools(workspace_root)}
    result = await tools["token_budget"].handler("", {})
    assert "planner_heartbeat" in result
    assert "500" in result
    assert "coding" in result
