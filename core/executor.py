# L3: Ausführung + Retry
"""
Executor — nimmt einen Plan, führt Steps aus, gibt Results zurück.
Retry-Logik bei Fehlern.
"""

import logging
from dataclasses import dataclass, field
from core.planner import Plan, Step

logger = logging.getLogger("mantisclaw.executor")


@dataclass
class StepResult:
    step: Step
    success: bool
    output: str = ""
    error: str = ""
    retries: int = 0


@dataclass
class ExecutionResult:
    plan: Plan
    results: list[StepResult] = field(default_factory=list)

    @property
    def all_succeeded(self) -> bool:
        return all(r.success for r in self.results)

    @property
    def summary(self) -> str:
        total = len(self.results)
        ok = sum(1 for r in self.results if r.success)
        return f"{ok}/{total} steps succeeded"


class Executor:
    """Executes plans step by step with retry logic."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._handlers: dict[str, callable] = {}

    def register_handler(self, action: str, handler: callable):
        self._handlers[action] = handler

    async def execute(self, plan: Plan) -> ExecutionResult:
        result = ExecutionResult(plan=plan)
        logger.info(f"Executing plan: {plan.goal} ({len(plan.steps)} steps)")

        # Step-Output-Chain: accumulate outputs so later steps can use prior results
        # Seed with plan goal+reasoning so even the first step has context
        chain_context: list[str] = []
        if plan.goal or plan.reasoning:
            chain_context.append(f"[PLAN] Ziel: {plan.goal}. Reasoning: {plan.reasoning}")

        for step in plan.steps:
            # Inject chain context into step params so handlers can access prior outputs
            if chain_context:
                step.params["_prior_outputs"] = chain_context[-3:]  # Last 3 outputs max

            step_result = await self._execute_step(step)
            result.results.append(step_result)

            # Accumulate successful outputs for chaining (truncated to prevent bloat)
            if step_result.success and step_result.output:
                summary = step_result.output[:500]
                chain_context.append(f"[{step.action}] {summary}")

            if not step_result.success:
                logger.warning(f"Step failed: {step.action} -> {step.target}: {step_result.error}")

        logger.info(f"Plan complete: {result.summary}")
        return result

    async def _execute_step(self, step: Step) -> StepResult:
        handler = self._handlers.get(step.action)
        if not handler:
            # Try fuzzy match: check if any handler name is in the action string
            action_lower = step.action.lower()
            for name, h in self._handlers.items():
                if name.lower() in action_lower:
                    handler = h
                    break
        if not handler:
            return StepResult(
                step=step,
                success=False,
                error=f"No handler for action: {step.action}",
            )

        last_error = ""
        for attempt in range(self.max_retries + 1):
            try:
                output = await handler(step.target, step.params)
                return StepResult(step=step, success=True, output=str(output), retries=attempt)
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Step {step.action} attempt {attempt + 1} failed: {e}")

        return StepResult(step=step, success=False, error=last_error, retries=self.max_retries)
