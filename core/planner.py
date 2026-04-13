# L3: Task-Dekomposition
"""
Planner — nimmt soul(t) + hooks + memory → erzeugt einen Plan.
Ein Plan ist eine Liste von Steps.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger("mantisclaw.planner")


@dataclass
class Step:
    action: str
    target: str
    params: dict = field(default_factory=dict)
    description: str = ""


@dataclass
class Plan:
    goal: str
    steps: list[Step] = field(default_factory=list)
    reasoning: str = ""


class Planner:
    """Creates execution plans from soul context and triggers."""

    def __init__(self, llm_backend, tool_descriptions: str = ""):
        self.llm = llm_backend
        self.tool_descriptions = tool_descriptions
        self._valid_tool_names: set[str] = set()  # Set by runtime after registry init
        self._workspace_context: str = ""  # Injected workspace structure for grounding
        self._project_context: dict | None = None  # Active project manifest

    def set_valid_tools(self, tool_names: list[str]):
        """Set the list of valid tool names for post-parse validation."""
        self._valid_tool_names = set(tool_names)

    async def plan(self, soul: dict, hooks: list[dict], memory_context: list[str]) -> Plan:
        system_prompt = self._build_system_prompt(soul)
        user_prompt = self._build_user_prompt(hooks, memory_context)

        response = await self.llm.complete_simple(user_prompt, system=system_prompt)

        return self._parse_plan(response)

    def _build_system_prompt(self, soul: dict) -> str:
        base = soul.get("base", {})
        agenda = soul.get("agenda", "")
        name = base.get("name", "MantisClaw Agent")

        return f"""Du bist {name}. Deine Aufgabe: Erstelle einen Aktionsplan.
Agenda: {agenda}
Ethik: {base.get('ethik', 'Wahrheit > Gefälligkeit, Audit-Pflicht')}
{self._format_project_block()}
Verfügbare Tools (nutze NUR diese als ACTION):
{self.tool_descriptions or '(keine Tools registriert)'}

REGELN:
- MAXIMAL 5 Steps pro Plan. Priorisiere die wichtigsten Aktionen.
- Nutze NUR die oben gelisteten Tool-Namen als ACTION.
- Erfinde KEINE Dateipfade — nutze workspace_status oder list_dir zuerst, um echte Pfade zu ermitteln.
- Jeder STEP muss einen KONKRETEN, existierenden Pfad oder Inhalt als Target haben.
- Plane NUR Aktionen die zum aktiven Projekt-Scope passen (falls Projekt aktiv).

REASONING: <Warum>
STEP: <tool_name> | <target> | <beschreibung>
STEP: <tool_name> | <target> | <beschreibung>
"""

    def _format_project_block(self) -> str:
        if not self._project_context:
            return ""
        p = self._project_context
        milestones = p.get("milestones", [])
        open_ms = [m["name"] for m in milestones if m.get("status") in ("open", "in-progress")]
        done_ms = [m["name"] for m in milestones if m.get("status") == "done"]
        parts = [
            f"\nAktives Projekt: {p.get('name', '?')} ({p.get('slug', '?')})",
            f"Scope: {p.get('scope', '').strip()[:300]}",
        ]
        if open_ms:
            parts.append(f"Offene Meilensteine: {', '.join(open_ms)}")
        if done_ms:
            parts.append(f"Erledigte Meilensteine: {', '.join(done_ms)}")
        goals = p.get("goals", [])
        if goals:
            parts.append(f"Ziele: {', '.join(goals[:3])}")
        return "\n".join(parts) + "\n"

    def _build_user_prompt(self, hooks: list[dict], memory_context: list[str]) -> str:
        parts = []
        if hooks:
            parts.append("Aktive Trigger:\n" + "\n".join(str(h) for h in hooks))
        if memory_context:
            parts.append("Relevanter Kontext:\n" + "\n".join(memory_context))
        if self._workspace_context:
            parts.append(f"Workspace-Status:\n{self._workspace_context}")
        if not parts:
            parts.append("Kein spezifischer Trigger. Prüfe ob Wartungsaufgaben anstehen.")
        return "\n\n".join(parts)

    def set_workspace_context(self, context: str):
        """Inject workspace structure so LLM knows real paths."""
        self._workspace_context = context

    def set_project_context(self, project: dict):
        """Inject active project manifest for scope-aware planning."""
        self._project_context = project

    def _parse_plan(self, response: str) -> Plan:
        lines = response.strip().split("\n")
        goal = ""
        reasoning = ""
        steps = []

        for line in lines:
            line = line.strip()
            if line.startswith("GOAL:"):
                goal = line[5:].strip()
            elif line.startswith("REASONING:"):
                reasoning = line[10:].strip()
            elif line.startswith("STEP:"):
                parts = line[5:].split("|")
                if len(parts) >= 2:
                    action = parts[0].strip()
                    # Validate tool name against registry
                    if self._valid_tool_names and action not in self._valid_tool_names:
                        # Try fuzzy: check if any valid tool is contained in action
                        matched = False
                        for valid in self._valid_tool_names:
                            if valid in action.lower():
                                action = valid
                                matched = True
                                break
                        if not matched:
                            logger.warning(f"Planner: dropping invalid tool '{action}' (not in registry)")
                            continue
                    steps.append(Step(
                        action=action,
                        target=parts[1].strip(),
                        description=parts[2].strip() if len(parts) > 2 else "",
                    ))

        # Enforce step limit
        if len(steps) > 5:
            logger.warning(f"Planner: truncating plan from {len(steps)} to 5 steps")
            steps = steps[:5]

        return Plan(goal=goal, steps=steps, reasoning=reasoning)
