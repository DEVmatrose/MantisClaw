# L5: Skill-Orchestrierung
"""
SkillExecutor — Lädt und führt Skills aus WORKING/TOOLS/skills/ aus.

Ein Skill ist ein Markdown+YAML Workflow:
  - YAML Frontmatter: name, requires_tools, trigger, max_retries
  - Markdown Body: System-Prompt + Workflow Steps
  - Each Step: tool call with input/output/conditions

Skills sind Procedural Memory in Aktion — Rezepte die der Agent gelernt hat.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("mantisclaw.skill_executor")


@dataclass
class SkillStep:
    """One step in a skill workflow."""
    number: int
    name: str
    tool: str
    input_template: str
    output_var: str = ""
    on_failure: str = "abort"  # abort | skip_and_note | retry
    condition: str = ""


@dataclass
class Skill:
    """A parsed skill definition."""
    name: str
    version: str
    description: str
    requires_tools: list[str]
    category: str = "general"
    trigger: str = "manual"  # manual | planner | hook
    max_retries: int = 2
    system_prompt: str = ""
    steps: list[SkillStep] = field(default_factory=list)
    source_path: Path | None = None


@dataclass
class SkillResult:
    """Result of executing a skill."""
    skill_name: str
    success: bool
    steps_completed: int
    steps_total: int
    outputs: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    @property
    def summary(self) -> str:
        status = "OK" if self.success else "FAILED"
        return f"{self.skill_name}: {status} ({self.steps_completed}/{self.steps_total} steps)"


class SkillExecutor:
    """Loads and executes Markdown+YAML skills via the Tool Registry."""

    def __init__(self, registry, skill_dir: Path):
        self.registry = registry
        self.skill_dir = skill_dir
        self._skills: dict[str, Skill] = {}
        self._load_all_skills()

    def _load_all_skills(self):
        """Load all .md skill files from skill directory."""
        if not self.skill_dir.exists():
            logger.info(f"Skill directory not found: {self.skill_dir}")
            return

        for skill_file in sorted(self.skill_dir.glob("*.md")):
            try:
                skill = self._parse_skill(skill_file)
                self._skills[skill.name] = skill
                logger.debug(f"Loaded skill: {skill.name} ({len(skill.steps)} steps)")
            except Exception as e:
                logger.warning(f"Failed to parse skill {skill_file.name}: {e}")

        logger.info(f"Skills loaded: {len(self._skills)} from {self.skill_dir}")

    def _parse_skill(self, path: Path) -> Skill:
        """Parse a Markdown+YAML skill file."""
        content = path.read_text(encoding="utf-8")

        # Extract YAML frontmatter
        frontmatter = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = self._parse_yaml_simple(parts[1])
                body = parts[2].strip()

        skill = Skill(
            name=frontmatter.get("name", path.stem),
            version=frontmatter.get("version", "0.1.0"),
            description=frontmatter.get("description", ""),
            requires_tools=frontmatter.get("requires_tools", []),
            category=frontmatter.get("category", "general"),
            trigger=frontmatter.get("trigger", "manual"),
            max_retries=int(frontmatter.get("max_retries", 2)),
            source_path=path,
        )

        # Extract system prompt (## System-Prompt section)
        sp_match = re.search(r'## System-Prompt\s*\n(.*?)(?=\n## |\Z)', body, re.DOTALL)
        if sp_match:
            skill.system_prompt = sp_match.group(1).strip()

        # Extract workflow steps (### Step N: lines with - tool:, - input:, etc.)
        step_blocks = re.findall(r'### Step (\d+)[:\s]*(.*?)\n(.*?)(?=\n### |\Z)', body, re.DOTALL)
        for num, name, block in step_blocks:
            step = self._parse_step(int(num), name.strip(), block)
            skill.steps.append(step)

        return skill

    def _parse_step(self, number: int, name: str, block: str) -> SkillStep:
        """Parse a workflow step block."""
        tool = ""
        input_template = ""
        output_var = ""
        on_failure = "abort"
        condition = ""

        for line in block.strip().split("\n"):
            line = line.strip()
            if line.startswith("- tool:"):
                tool = line[7:].strip()
            elif line.startswith("- input:"):
                input_template = line[8:].strip()
            elif line.startswith("- output:"):
                output_var = line[9:].strip().lstrip("$")
            elif line.startswith("- on_failure:"):
                on_failure = line[13:].strip()
            elif line.startswith("- condition:"):
                condition = line[12:].strip()

        return SkillStep(
            number=number,
            name=name or f"Step {number}",
            tool=tool,
            input_template=input_template,
            output_var=output_var,
            on_failure=on_failure,
            condition=condition,
        )

    def _parse_yaml_simple(self, yaml_text: str) -> dict:
        """Minimal YAML parser for frontmatter (no external deps)."""
        result = {}
        current_list_key = None

        for line in yaml_text.strip().split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # List item
            if stripped.startswith("- ") and current_list_key:
                result[current_list_key].append(stripped[2:].strip().strip('"'))
                continue

            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip().strip('"')
                if not val:
                    # Start of a list
                    result[key] = []
                    current_list_key = key
                else:
                    result[key] = val
                    current_list_key = None

        return result

    def validate(self, skill: Skill) -> tuple[bool, list[str]]:
        """Check if all required tools are registered."""
        missing = []
        for tool_name in skill.requires_tools:
            if not self.registry.get(tool_name):
                missing.append(tool_name)

        if missing:
            return False, [f"Missing tools: {', '.join(missing)}"]
        return True, []

    async def execute(self, skill_name: str, context: dict | None = None) -> SkillResult:
        """Execute a skill by name."""
        skill = self._skills.get(skill_name)
        if not skill:
            return SkillResult(
                skill_name=skill_name,
                success=False,
                steps_completed=0,
                steps_total=0,
                error=f"Skill not found: {skill_name}",
            )

        # Validate dependencies
        valid, errors = self.validate(skill)
        if not valid:
            return SkillResult(
                skill_name=skill_name,
                success=False,
                steps_completed=0,
                steps_total=len(skill.steps),
                error="; ".join(errors),
            )

        logger.info(f"Executing skill: {skill.name} ({len(skill.steps)} steps)")

        state = dict(context or {})
        completed = 0

        for step in skill.steps:
            # Check condition
            if step.condition and not self._eval_condition(step.condition, state):
                logger.info(f"  Step {step.number} skipped (condition: {step.condition})")
                completed += 1
                continue

            # Resolve tool
            tool = self.registry.get(step.tool)
            if not tool:
                if step.on_failure == "skip_and_note":
                    logger.warning(f"  Step {step.number}: tool '{step.tool}' not found, skipping")
                    state[f"_skip_{step.number}"] = f"Tool {step.tool} not found"
                    completed += 1
                    continue
                return SkillResult(
                    skill_name=skill_name,
                    success=False,
                    steps_completed=completed,
                    steps_total=len(skill.steps),
                    error=f"Step {step.number}: tool '{step.tool}' not found",
                )

            # Resolve input (simple variable substitution)
            resolved_input = self._resolve_vars(step.input_template, state)

            # Execute
            try:
                output = await tool.handler(resolved_input, {})
                if step.output_var:
                    state[step.output_var] = output
                completed += 1
                logger.info(f"  Step {step.number} ({step.tool}): OK")
            except Exception as e:
                logger.error(f"  Step {step.number} ({step.tool}): FAILED — {e}")
                if step.on_failure == "skip_and_note":
                    state[f"_error_{step.number}"] = str(e)
                    completed += 1
                elif step.on_failure == "abort":
                    return SkillResult(
                        skill_name=skill_name,
                        success=False,
                        steps_completed=completed,
                        steps_total=len(skill.steps),
                        outputs=state,
                        error=f"Step {step.number} failed: {e}",
                    )

        result = SkillResult(
            skill_name=skill_name,
            success=True,
            steps_completed=completed,
            steps_total=len(skill.steps),
            outputs=state,
        )
        logger.info(f"Skill complete: {result.summary}")
        return result

    def list_skills(self) -> list[Skill]:
        return list(self._skills.values())

    def get_skill_descriptions(self) -> str:
        """Format skill list for planner context."""
        lines = []
        for skill in self._skills.values():
            steps_info = f"{len(skill.steps)} steps"
            lines.append(f"- SKILL:{skill.name}: {skill.description} ({steps_info})")
        return "\n".join(lines) if lines else "(keine Skills geladen)"

    def _resolve_vars(self, template: str, state: dict) -> str:
        """Replace $var_name with state values."""
        result = template
        for key, value in state.items():
            result = result.replace(f"${key}", str(value))
        return result

    def _eval_condition(self, condition: str, state: dict) -> bool:
        """Simple condition evaluation (e.g. '$validation.passed == true')."""
        # Replace variables
        resolved = self._resolve_vars(condition, state)
        # Simple equality check
        if "==" in resolved:
            left, right = resolved.split("==", 1)
            return left.strip() == right.strip()
        if "!=" in resolved:
            left, right = resolved.split("!=", 1)
            return left.strip() != right.strip()
        # Truthy check
        return bool(resolved.strip())
