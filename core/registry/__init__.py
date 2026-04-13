# L4: Tool Registry
"""
Tool Registry — the gate between L3 (Brain) and L2 (AAMS Body).

Kernregel: L3 berührt L2 nie direkt — jeder Zugriff über registrierte Tools (L4).

Tools are:
  - Atomic (one action per call)
  - Stateless (no side-channel state)
  - Security-leveled (permission_level gates access)
  - Whitelisted (only registered tools can be called)
"""

from core.registry.registry import ToolRegistry, Tool

__all__ = ["ToolRegistry", "Tool"]
