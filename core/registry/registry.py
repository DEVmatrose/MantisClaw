# L4: Tool Registry — Core
"""
Registry for all tools available to the executor.
Tools are registered with a name, handler, security level, and description.
The executor resolves planner actions to registered tools via the registry.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

logger = logging.getLogger("mantisclaw.registry")


@dataclass
class Tool:
    """A registered tool that the executor can invoke."""
    name: str
    handler: Callable[..., Awaitable[Any]]
    description: str = ""
    security_level: int = 2  # 1=read, 2=read+write, 3=full
    tags: list[str] = field(default_factory=list)

    def __repr__(self):
        return f"Tool({self.name}, level={self.security_level})"


class ToolRegistry:
    """
    Central registry for all tools. Enforces:
    - Whitelist: only registered tools can execute
    - Security levels: tools above current permission are blocked
    - Action mapping: planner actions are resolved to tool names
    """

    def __init__(self, permission_level: int = 2):
        self._tools: dict[str, Tool] = {}
        self.permission_level = permission_level

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting.")
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name} (level={tool.security_level})")

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def resolve(self, action: str) -> Tool | None:
        """Resolve a planner action string to a registered tool.
        
        Tries exact match first, then checks if any tool name is contained
        in the action string (case-insensitive).
        """
        # Exact match
        if action in self._tools:
            return self._tools[action]

        # Fuzzy: tool name contained in action
        action_lower = action.lower()
        for name, tool in self._tools.items():
            if name.lower() in action_lower:
                return tool

        return None

    def is_allowed(self, tool: Tool) -> bool:
        return tool.security_level <= self.permission_level

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def list_available(self) -> list[Tool]:
        """List tools available at current permission level."""
        return [t for t in self._tools.values() if self.is_allowed(t)]

    def get_tool_descriptions(self) -> str:
        """Format tool list for inclusion in planner system prompt."""
        lines = []
        for tool in self.list_available():
            tags = f" [{', '.join(tool.tags)}]" if tool.tags else ""
            lines.append(f"- {tool.name}: {tool.description}{tags}")
        return "\n".join(lines) if lines else "(keine Tools registriert)"
