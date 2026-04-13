# L3: Heartbeat-Loop, Hauptprozess
"""
MantisClaw Runtime — der zentrale Heartbeat-Loop.
Koordiniert Identity-Loading, Planning, Execution und Observation.

Aufruf: python -m core.runtime
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from core.llm import LLMBackend
from core.planner import Planner
from core.executor import Executor
from core.observer import Observer
from core.reflect import Reflector
from core.context import ContextLoader
from core.skill_executor import SkillExecutor
from core.session import Session
from core.ltm import LTMManager
from core.registry import ToolRegistry
from core.registry.tools.filesystem import create_filesystem_tools
from core.registry.tools.memory import create_memory_tools
from core.registry.tools.analysis import create_analysis_tools

logger = logging.getLogger("mantisclaw.runtime")

# Project root = parent of core/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Identity:
    """Loads and resolves identity dimensions into soul(t)."""

    def __init__(self, identity_dir: Path):
        self.identity_dir = identity_dir

    def load_file(self, name: str) -> str:
        path = self.identity_dir / name
        if path.exists():
            return path.read_text(encoding="utf-8")
        example = self.identity_dir / f"{name}.example"
        if example.exists():
            return example.read_text(encoding="utf-8")
        return ""

    def compute_soul(self, working_context: str = "") -> dict:
        base_raw = self.load_file("base.md")
        agenda_raw = self.load_file("agenda.md")
        account_raw = self.load_file("account.md")
        social_raw = self.load_file("social.md")
        decentral_raw = self.load_file("decentral.md")

        base = self._parse_base(base_raw)

        return {
            "base": base,
            "agenda": agenda_raw,
            "account": account_raw,
            "social": social_raw,
            "decentral": decentral_raw,
            "working_context": working_context,
            "formula": "soul(t) = f(base, agenda.resolve(account, social, decentral), working_context)",
        }

    def _parse_base(self, raw: str) -> dict:
        result = {"name": "", "owner": "", "ethik": "", "raw": raw}
        for line in raw.split("\n"):
            line = line.strip()
            if line.startswith("name:"):
                result["name"] = line.split(":", 1)[1].strip().strip('"')
            elif line.startswith("owner:"):
                result["owner"] = line.split(":", 1)[1].strip().strip('"')
        return result

    def load_hooks(self) -> list[dict]:
        hook_raw = self.load_file("hook.md")
        if not hook_raw.strip():
            return []
        return [{"raw": hook_raw}]


class MantisClaw:
    """The main runtime engine."""

    def __init__(self, config_path: Path | None = None):
        self.project_root = PROJECT_ROOT
        self.config = self._load_config(config_path)
        self.running = False
        self.tick_count = 0

        # L0: LLM
        self.llm = LLMBackend(self.config.get("llm", {}))

        # L1: Identity
        self.identity = Identity(self.project_root / "identity")

        # L2: AAMS
        workspace_path = self.project_root / self.config.get("aams", {}).get("workspace_path", "./WORKSPACE")
        self.session = Session(workspace_path, agent_name="mantisclaw")
        self.ltm = LTMManager(workspace_path)

        # L3: Brain
        self.planner = Planner(self.llm)
        self.executor = Executor(max_retries=self.config.get("runtime", {}).get("max_retries", 3))
        self.observer = Observer()

        # L3: Reflection-Loop (RFL)
        rfl_config = self.config.get("reflection", {})
        self.reflector = Reflector(
            self.llm,
            max_retries=rfl_config.get("max_retries", 2),
            cooldown_ticks=rfl_config.get("cooldown_ticks", 3),
        )

        # L2→L3: JIT Context Loader
        self.context_loader = ContextLoader(workspace_path)

        # L4: Tool Registry — the gate between L3 and L2
        security_config = self.config.get("security", {})
        self.registry = ToolRegistry(permission_level=security_config.get("permission_level", 2))
        self._register_tools(workspace_path)

# Inject tool descriptions into planner so LLM knows available actions
        self.planner.tool_descriptions = self.registry.get_tool_descriptions()
        # Set valid tool names for post-parse validation
        self.planner.set_valid_tools([t.name for t in self.registry.list_tools()])

        # L5: Skill Executor
        skill_dir = workspace_path / "WORKING" / "TOOLS" / "skills"
        self.skill_executor = SkillExecutor(self.registry, skill_dir)
        skill_descs = self.skill_executor.get_skill_descriptions()
        if skill_descs and "keine Skills" not in skill_descs:
            self.planner.tool_descriptions += "\n\nVerfügbare Skills:\n" + skill_descs

        # L2: Project layer
        self.workspace_path = workspace_path

        # Config
        self.heartbeat_interval = self.config.get("runtime", {}).get("heartbeat_interval", 10)
        self.session_timeout = self.config.get("runtime", {}).get("session_timeout", 3600)

    def _load_config(self, config_path: Path | None) -> dict:
        if config_path is None:
            config_path = self.project_root / "config" / "default.yaml"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _register_tools(self, workspace_path: Path) -> None:
        """Register all built-in tools with the registry."""
        tools_config = self.config.get("tools", {})

        # Filesystem tools
        if tools_config.get("filesystem", {}).get("enabled", True):
            allowed = tools_config.get("filesystem", {}).get("allowed_paths", [str(workspace_path)])
            for tool in create_filesystem_tools(workspace_path, [str(self.project_root / p) for p in allowed]):
                self.registry.register(tool)

        # Memory tools
        for tool in create_memory_tools(workspace_path):
            self.registry.register(tool)

        # Analysis tools (LLM-powered)
        for tool in create_analysis_tools(self.llm):
            self.registry.register(tool)

        # Wire all registered tools into executor
        for tool in self.registry.list_available():
            self.executor.register_handler(tool.name, tool.handler)

        logger.info(f"Registry: {len(self.registry.list_tools())} tools registered, "
                     f"{len(self.registry.list_available())} available at level {self.registry.permission_level}")

    def _load_active_project(self) -> dict | None:
        """Load the active project manifest from PROJECT/_active.yaml + project.yaml."""
        active_path = self.workspace_path / "WORKING" / "PROJECT" / "_active.yaml"
        if not active_path.exists():
            return None
        try:
            with open(active_path, encoding="utf-8") as f:
                active = yaml.safe_load(f) or {}
            slug = active.get("active_project")
            if not slug:
                return None
            manifest_path = self.workspace_path / "WORKING" / "PROJECT" / slug / "project.yaml"
            if not manifest_path.exists():
                logger.warning(f"Project manifest not found: {manifest_path}")
                return None
            with open(manifest_path, encoding="utf-8") as f:
                project = yaml.safe_load(f) or {}
            project["slug"] = slug
            return project
        except Exception as e:
            logger.error(f"Failed to load active project: {e}")
            return None

    async def tick(self):
        self.tick_count += 1
        logger.info(f"=== TICK {self.tick_count} ===")

        # 1. Identity → soul(t)
        soul = self.identity.compute_soul()
        logger.debug(f"Soul computed. Agent: {soul['base'].get('name', 'unnamed')}")

        # 1b. Active Project → soul(t)
        active_project = self._load_active_project()
        if active_project:
            soul["project"] = active_project
            logger.debug(f"Active project: {active_project.get('name', '?')}")

        # 2. Hooks → Trigger?
        hooks = self.identity.load_hooks()

        # 3. JIT Context Loading (Stage 1 + 2)
        working_context = self.context_loader.load_always(self.session.workpaper_path)
        soul["working_context"] = working_context

        # 3b. Inject workspace structure into planner to prevent path hallucination
        self.planner.set_workspace_context(working_context[:2000] if working_context else "")

        # 3c. Inject project context into planner
        if active_project:
            self.planner.set_project_context(active_project)

        # 4. Memory context
        memory_context = self.ltm.query("current", max_results=3)

        # 5. Plan
        try:
            plan = await self.planner.plan(soul, hooks, memory_context)
            logger.info(f"Plan: {plan.goal} ({len(plan.steps)} steps)")
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return

        # 6. Execute
        if plan.steps:
            # Check if any step is a skill call
            for step in plan.steps:
                if step.action.startswith("SKILL:"):
                    skill_name = step.action[6:].strip()
                    skill_result = await self.skill_executor.execute(skill_name, {"target": step.target})
                    logger.info(f"Skill result: {skill_result.summary}")

            result = await self.executor.execute(plan)

            # 7. Observe
            metrics = self.observer.observe(result, self.tick_count)

            # 8. Reflection-Loop (RFL)
            if self.reflector.needs_reflection(metrics, self.tick_count):
                reflection = await self.reflector.reflect(result, metrics, self.tick_count)

                if reflection.should_retry:
                    # Re-plan with reflection context
                    reflection_ctx = self.reflector.build_reflection_context(reflection)
                    logger.info(f"RFL: Replanning with correction (attempt {self.reflector._retry_count})")

                    # Inject reflection into memory context for replanning
                    retry_memory = memory_context + [reflection_ctx]
                    try:
                        retry_plan = await self.planner.plan(soul, hooks, retry_memory)
                        logger.info(f"RFL Replan: {retry_plan.goal} ({len(retry_plan.steps)} steps)")
                        if retry_plan.steps:
                            retry_result = await self.executor.execute(retry_plan)
                            retry_metrics = self.observer.observe(retry_result, self.tick_count)
                            metrics = retry_metrics  # Use retry metrics for logging
                    except Exception as e:
                        logger.error(f"RFL Replanning failed: {e}")

                if reflection.escalate:
                    logger.warning(f"RFL ESCALATION: {reflection.what_wrong} — {reflection.correction}")
                    self.session.log_action("ESCALATE", f"tick-{self.tick_count}",
                                            f"RFL escalation: {reflection.what_wrong}")

            # 9. Log to session
            self.session.log_action("TICK", f"tick-{self.tick_count}", f"Plan: {plan.goal} | {result.summary}")
        else:
            logger.info("No steps to execute this tick.")

    async def run(self):
        logger.info("MantisClaw starting...")
        logger.info(f"Health: {self.observer.health}")
        logger.info(f"Heartbeat: {self.heartbeat_interval}s")

        self.running = True

        # Open AAMS session
        if self.config.get("aams", {}).get("auto_workpaper", True):
            self.session.open(topic="runtime-loop")

        try:
            while self.running:
                await self.tick()
                await asyncio.sleep(self.heartbeat_interval)
        except asyncio.CancelledError:
            logger.info("Runtime cancelled.")
        finally:
            self._shutdown()

    def _shutdown(self):
        logger.info(f"Shutting down. Total ticks: {self.tick_count}. Health: {self.observer.health}")
        if self.session.workpaper_path:
            self.session.close(
                decisions=[f"Runtime stopped after {self.tick_count} ticks"],
                next_steps=["Review observation metrics", "Check for anomalies"],
            )

    def stop(self):
        self.running = False


def main():
    load_dotenv(PROJECT_ROOT / ".env")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    claw = MantisClaw()

    def handle_signal(sig, frame):
        logger.info(f"Signal {sig} received. Stopping...")
        claw.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    asyncio.run(claw.run())


if __name__ == "__main__":
    main()
