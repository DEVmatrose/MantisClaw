# L3: Selbstkorrektur (RFL — Reflection-Loop)
"""
Reflect — analysiert warum ein Plan gescheitert ist und liefert
correction_context an den Planner für einen Replan.

Datenfluss:
  Observer → needs_revision? → reflect() → Planner (mit reflection_context)
    → Executor → Observer → (max 2 Retries, dann Eskalation)
"""

import logging
from dataclasses import dataclass

from core.executor import ExecutionResult
from core.observer import TickMetrics

logger = logging.getLogger("mantisclaw.reflect")


@dataclass
class ReflectionResult:
    what_wrong: str
    why_wrong: str
    correction: str
    confidence: float  # 0.0 - 1.0
    should_retry: bool
    escalate: bool = False


class Reflector:
    """Analyzes failed executions and produces correction context for the Planner."""

    def __init__(self, llm_backend, max_retries: int = 2, cooldown_ticks: int = 3):
        self.llm = llm_backend
        self.max_retries = max_retries
        self.cooldown_ticks = cooldown_ticks
        self._retry_count: int = 0
        self._last_reflect_tick: int = 0

    def needs_reflection(self, metrics: TickMetrics, current_tick: int) -> bool:
        """Check if the tick result warrants reflection."""
        if metrics.steps_failed == 0:
            self._retry_count = 0  # Reset on success
            return False

        # Cooldown: don't reflect too often
        if (current_tick - self._last_reflect_tick) < self.cooldown_ticks and self._last_reflect_tick > 0:
            logger.debug(f"Reflection cooldown active (last: tick {self._last_reflect_tick})")
            return False

        # Max retries exceeded → escalate instead
        if self._retry_count >= self.max_retries:
            logger.warning(f"Max reflection retries ({self.max_retries}) exceeded. Escalating.")
            return False

        return True

    def should_escalate(self) -> bool:
        """True if we've exhausted reflection retries."""
        return self._retry_count >= self.max_retries

    async def reflect(self, result: ExecutionResult, metrics: TickMetrics, current_tick: int) -> ReflectionResult:
        """Analyze why a plan failed and suggest corrections."""
        self._last_reflect_tick = current_tick
        self._retry_count += 1

        # Build failure summary
        failures = []
        for r in result.results:
            if not r.success:
                failures.append(f"- {r.step.action} | {r.step.target}: {r.error}")

        successes = []
        for r in result.results:
            if r.success:
                successes.append(f"- {r.step.action} | {r.step.target}: OK")

        prompt = f"""Analysiere warum dieser Plan teilweise oder ganz gescheitert ist.

Plan-Ziel: {result.plan.goal}
Plan-Reasoning: {result.plan.reasoning}

Erfolgreiche Schritte:
{chr(10).join(successes) if successes else '(keine)'}

Gescheiterte Schritte:
{chr(10).join(failures) if failures else '(keine)'}

Anomalien: {', '.join(metrics.anomalies) if metrics.anomalies else '(keine)'}

Antworte EXAKT in diesem Format:
WHAT_WRONG: <Was hat nicht funktioniert?>
WHY_WRONG: <Warum? Root Cause?>
CORRECTION: <Was soll der Planner beim nächsten Versuch anders machen?>
CONFIDENCE: <0.0-1.0 wie sicher bist du?>
SHOULD_RETRY: <true|false>
"""

        system = "Du bist ein Debugging-Agent. Analysiere Fehler präzise und kurz."

        try:
            response = await self.llm.complete_simple(prompt, system=system)
            reflection = self._parse_response(response)
        except Exception as e:
            logger.error(f"Reflection LLM call failed: {e}")
            reflection = ReflectionResult(
                what_wrong="Reflection itself failed",
                why_wrong=str(e),
                correction="Retry with fresh context",
                confidence=0.1,
                should_retry=True,
            )

        # Check if we should escalate
        if self._retry_count >= self.max_retries:
            reflection.escalate = True
            reflection.should_retry = False
            logger.warning("Reflection: max retries reached → escalate")

        logger.info(f"Reflection (attempt {self._retry_count}/{self.max_retries}): "
                     f"confidence={reflection.confidence:.1f}, retry={reflection.should_retry}, "
                     f"escalate={reflection.escalate}")

        return reflection

    def build_reflection_context(self, reflection: ReflectionResult) -> str:
        """Format reflection result as context for the Planner's next attempt."""
        return (
            f"=== REFLECTION (Korrektur-Hinweis) ===\n"
            f"Problem: {reflection.what_wrong}\n"
            f"Ursache: {reflection.why_wrong}\n"
            f"Korrektur: {reflection.correction}\n"
            f"Konfidenz: {reflection.confidence:.1f}\n"
        )

    def reset(self):
        """Reset retry counter (e.g. on new agenda or manual reset)."""
        self._retry_count = 0
        self._last_reflect_tick = 0

    def _parse_response(self, response: str) -> ReflectionResult:
        what = ""
        why = ""
        correction = ""
        confidence = 0.5
        should_retry = True

        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("WHAT_WRONG:"):
                what = line[11:].strip()
            elif line.startswith("WHY_WRONG:"):
                why = line[10:].strip()
            elif line.startswith("CORRECTION:"):
                correction = line[11:].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line[11:].strip())
                    confidence = max(0.0, min(1.0, confidence))
                except ValueError:
                    confidence = 0.5
            elif line.startswith("SHOULD_RETRY:"):
                val = line[13:].strip().lower()
                should_retry = val in ("true", "yes", "ja", "1")

        return ReflectionResult(
            what_wrong=what or "Unknown failure",
            why_wrong=why or "Could not determine root cause",
            correction=correction or "Retry with different approach",
            confidence=confidence,
            should_retry=should_retry,
        )
