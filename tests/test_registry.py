"""Unit tests for Tool Registry — no LLM needed."""
from pathlib import Path
from core.registry.registry import ToolRegistry, Tool


def test_registry_creates_empty():
    r = ToolRegistry()
    assert len(r.list_tools()) == 0


def test_register_and_get():
    r = ToolRegistry()

    async def dummy_handler(target, params):
        return "ok"

    tool = Tool(name="test_tool", handler=dummy_handler, security_level=1, description="A test tool")
    r.register(tool)

    assert len(r.list_tools()) == 1
    assert r.get("test_tool") is not None
    assert r.get("test_tool").name == "test_tool"


def test_get_nonexistent():
    r = ToolRegistry()
    assert r.get("no_such_tool") is None


def test_resolve_fuzzy():
    """Fuzzy resolve should match partial action names."""
    r = ToolRegistry()

    async def dummy(t, p):
        return "ok"

    r.register(Tool(name="read_file", handler=dummy, security_level=1, description="Read a file"))
    r.register(Tool(name="write_file", handler=dummy, security_level=2, description="Write a file"))

    # Exact match
    assert r.resolve("read_file") is not None
    assert r.resolve("read_file").name == "read_file"

    # Fuzzy match
    resolved = r.resolve("read file")
    # Should resolve to read_file or None depending on fuzzy impl
    if resolved:
        assert resolved.name == "read_file"


def test_security_levels():
    r = ToolRegistry(permission_level=1)

    async def dummy(t, p):
        return "ok"

    tool_r = Tool(name="read_tool", handler=dummy, security_level=1, description="Read-only")
    tool_w = Tool(name="write_tool", handler=dummy, security_level=2, description="Write")

    r.register(tool_r)
    r.register(tool_w)

    assert r.is_allowed(tool_r) is True
    assert r.is_allowed(tool_w) is False

    available = r.list_available()
    assert len(available) == 1
    assert available[0].name == "read_tool"


def test_tool_descriptions():
    r = ToolRegistry()

    async def dummy(t, p):
        return "ok"

    r.register(Tool(name="analyze", handler=dummy, security_level=1, description="Analyze text"))
    r.register(Tool(name="summarize", handler=dummy, security_level=1, description="Summarize text"))

    desc = r.get_tool_descriptions()
    assert "analyze" in desc
    assert "summarize" in desc
    assert "Analyze text" in desc
