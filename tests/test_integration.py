"""Integration test: Full tick with LLM. Requires LM Studio running."""
import pytest
import asyncio
from core.runtime import MantisClaw


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_single_tick():
    """Execute one full tick and verify it completes."""
    m = MantisClaw()
    assert m.llm.check_connection(), "LM Studio must be running for this test"

    await m.tick()

    assert m.tick_count == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_llm_simple_completion():
    """Test direct LLM completion."""
    m = MantisClaw()
    assert m.llm.check_connection(), "LM Studio must be running"

    result = await m.llm.complete_simple("Say only: OK", max_tokens=10)
    assert len(result) > 0
    assert len(result) < 100  # Should be very short
