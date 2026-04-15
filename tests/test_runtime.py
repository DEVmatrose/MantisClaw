"""Unit tests for MantisClaw runtime initialization — no LLM needed."""
from core.runtime import MantisClaw


def test_runtime_init():
    m = MantisClaw()
    assert m.running is False
    assert m.tick_count == 0
    assert m.registry is not None
    assert m.planner is not None
    assert m.executor is not None
    assert m.observer is not None


def test_runtime_has_13_tools():
    m = MantisClaw()
    tools = m.registry.list_tools()
    assert len(tools) == 13
    tool_names = {t.name for t in tools}
    assert "read_file" in tool_names
    assert "write_file" in tool_names
    assert "loop_monitor" in tool_names
    assert "token_budget" in tool_names
    assert "list_models" in tool_names
    assert "query_memory" in tool_names


def test_runtime_llm_configured():
    m = MantisClaw()
    assert m.llm.backend == "lmstudio"
    assert m.llm.base_url == "http://localhost:1234/v1"


def test_runtime_identity():
    m = MantisClaw()
    soul = m.identity.compute_soul()
    assert "base" in soul
    assert soul["base"].get("name") == "MantisClaw"


def test_runtime_workspace_path():
    m = MantisClaw()
    assert m.workspace_path.exists()
    assert "WORKSPACE" in str(m.workspace_path)
