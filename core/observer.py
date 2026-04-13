# L3: Metriken, Health
"""
Observer — bewertet Execution-Results, prüft gegen Guidelines,
meldet Anomalien, aktualisiert Metriken.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from core.executor import ExecutionResult

logger = logging.getLogger("mantisclaw.observer")


@dataclass
class TickMetrics:
    tick_number: int
    timestamp: str
    plan_goal: str
    steps_total: int
    steps_succeeded: int
    steps_failed: int
    anomalies: list[str] = field(default_factory=list)


class Observer:
    """Observes execution results, tracks health, flags anomalies."""

    def __init__(self):
        self.history: list[TickMetrics] = []
        self.total_ticks: int = 0
        self.total_failures: int = 0

    def observe(self, result: ExecutionResult, tick_number: int) -> TickMetrics:
        succeeded = sum(1 for r in result.results if r.success)
        failed = sum(1 for r in result.results if not r.success)

        anomalies = []
        for r in result.results:
            if not r.success:
                anomalies.append(f"FAILED: {r.step.action} -> {r.step.target}: {r.error}")
            if r.retries > 0 and r.success:
                anomalies.append(f"RETRY: {r.step.action} -> {r.step.target} (took {r.retries + 1} attempts)")

        metrics = TickMetrics(
            tick_number=tick_number,
            timestamp=datetime.now().isoformat(),
            plan_goal=result.plan.goal,
            steps_total=len(result.results),
            steps_succeeded=succeeded,
            steps_failed=failed,
            anomalies=anomalies,
        )

        self.history.append(metrics)
        self.total_ticks += 1
        self.total_failures += failed

        if anomalies:
            for a in anomalies:
                logger.warning(f"[Tick {tick_number}] {a}")
        else:
            logger.info(f"[Tick {tick_number}] Clean: {succeeded}/{len(result.results)} steps OK")

        return metrics

    @property
    def health(self) -> str:
        if self.total_ticks == 0:
            return "IDLE"
        failure_rate = self.total_failures / max(1, sum(m.steps_total for m in self.history))
        if failure_rate > 0.5:
            return "CRITICAL"
        elif failure_rate > 0.2:
            return "DEGRADED"
        return "HEALTHY"
