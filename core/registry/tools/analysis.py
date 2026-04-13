# L4: Analysis Tools
"""
Tools that use the LLM for analysis tasks.
These wrap LLM calls as structured tool invocations.
"""

import logging
from core.registry.registry import Tool

logger = logging.getLogger("mantisclaw.tools.analysis")


def create_analysis_tools(llm_backend) -> list[Tool]:
    """Create LLM-powered analysis tools."""

    async def analyze(target: str, params: dict) -> str:
        """Ask the LLM to analyze content, enriched with prior step outputs."""
        prompt = params.get("prompt", f"Analysiere folgendes: {target}")

        # Enrich with prior step outputs from chain context
        prior = params.get("_prior_outputs", [])
        if prior:
            context_block = "\n".join(prior[-3:])
            prompt = f"Kontext aus vorherigen Schritten:\n{context_block}\n\nAufgabe: {prompt}"

        result = await llm_backend.complete_simple(prompt, max_tokens=300)
        return result

    async def summarize(target: str, params: dict) -> str:
        """Summarize content using the LLM, enriched with prior step outputs."""
        content = target

        # Enrich with prior step outputs if target is generic
        prior = params.get("_prior_outputs", [])
        if prior and len(target) < 50:
            content = "\n".join(prior[-3:])

        result = await llm_backend.complete_simple(
            f"Fasse zusammen (max 5 Sätze):\n\n{content}", max_tokens=200
        )
        return result

    return [
        Tool(
            name="analyze",
            handler=analyze,
            description="Analyze content with LLM. Target: content to analyze. Params: {prompt: str}.",
            security_level=1,
            tags=["llm", "analysis"],
        ),
        Tool(
            name="summarize",
            handler=summarize,
            description="Summarize content with LLM. Target: content to summarize.",
            security_level=1,
            tags=["llm", "analysis"],
        ),
    ]
