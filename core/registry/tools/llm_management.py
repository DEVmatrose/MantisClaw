# L4: LLM Management Tools
"""
Tools for managing LLM models via LM Studio Management API.
Allows MantisClaw to autonomously decide which model to load based on task.

Security Level 2 — only available with permission_level >= 2.
"""

import json
import logging
from urllib.request import Request, urlopen
from core.registry.registry import Tool

logger = logging.getLogger("mantisclaw.tools.llm_mgmt")

LMS_MGMT_BASE = "http://localhost:1234/api/v1"


def create_llm_management_tools(llm_backend=None) -> list[Tool]:
    """Create LLM management tools for model switching."""

    def _post(url: str, payload: dict, timeout: int = 60) -> dict:
        data = json.dumps(payload).encode("utf-8")
        req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}

    def _get(url: str, timeout: int = 10) -> dict:
        try:
            with urlopen(Request(url), timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}

    async def list_models(target: str, params: dict) -> str:
        """List available (loaded) models in LM Studio."""
        data = _get(f"{LMS_MGMT_BASE}/models")
        if "error" in data:
            return f"Fehler: {data['error']}"
        models = data if isinstance(data, list) else data.get("data", [])
        if not models:
            return "Keine Modelle geladen."
        lines = []
        for m in models:
            mid = m.get("identifier", m.get("id", "?"))
            lines.append(f"- {mid}")
        return "Geladene Modelle:\n" + "\n".join(lines)

    async def switch_model(target: str, params: dict) -> str:
        """
        Switch to a different model. Unloads current model first (VRAM management).
        Target: model identifier (e.g. 'qwen3-coder-30b-a3b-instruct' or 'google/gemma-4-26b-a4b')
        Params: {reason: str}  — optional reasoning for the switch
        """
        model_id = target.strip()
        if not model_id:
            return "Fehler: Kein Modell angegeben."

        reason = params.get("reason", "Kein Grund angegeben")
        logger.info(f"Model switch requested: {model_id} | Reason: {reason}")

        # Get currently loaded models
        current_data = _get(f"{LMS_MGMT_BASE}/models")
        current_models = current_data if isinstance(current_data, list) else current_data.get("data", [])
        loaded_ids = [m.get("identifier", m.get("id", "")) for m in current_models]

        # Already loaded?
        if model_id in loaded_ids:
            # Update llm_backend if provided
            if llm_backend:
                llm_backend.model = model_id
            return f"Modell bereits geladen: {model_id}"

        # Unload current models to free VRAM
        for mid in loaded_ids:
            result = _post(f"{LMS_MGMT_BASE}/models/unload", {"identifier": mid}, timeout=30)
            if "error" not in result:
                logger.info(f"Unloaded: {mid}")
            else:
                logger.warning(f"Unload failed for {mid}: {result['error']}")

        # Load new model
        result = _post(f"{LMS_MGMT_BASE}/models/load", {"identifier": model_id}, timeout=120)
        if "error" in result:
            return f"Fehler beim Laden von {model_id}: {result['error']}"

        # Update backend model reference
        if llm_backend:
            llm_backend.model = model_id

        logger.info(f"Model switched to: {model_id}")
        return f"Modell gewechselt: {model_id} | Grund: {reason}"

    return [
        Tool(
            name="list_models",
            handler=list_models,
            description="List currently loaded LLM models in LM Studio. No params needed.",
            security_level=1,
            tags=["llm", "management"],
        ),
        Tool(
            name="switch_model",
            handler=switch_model,
            description=(
                "Switch active LLM model. Unloads current model first (VRAM management). "
                "Target: model identifier. Params: {reason: str}. "
                "Available: qwen3-coder-30b-a3b-instruct (code/analysis), google/gemma-4-26b-a4b (reasoning/dialog)."
            ),
            security_level=2,
            tags=["llm", "management"],
        ),
    ]
