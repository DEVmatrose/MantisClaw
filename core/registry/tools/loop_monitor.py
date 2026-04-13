# L4: Loop Monitor Tool
"""
Runtime loop monitoring and token efficiency validation.
Queries LM Studio API + Dashboard API to detect anomalies.
First project-specific tool for mantisclaw-core.
"""

import logging
import json
from pathlib import Path
from datetime import datetime

import aiohttp

from core.registry.registry import Tool

logger = logging.getLogger("mantisclaw.tools.loop_monitor")

# Default endpoints
LM_STUDIO_BASE = "http://localhost:1234"
DASHBOARD_BASE = "http://localhost:8080"


def create_loop_monitor_tools(workspace_root: Path) -> list[Tool]:
    """Create loop monitoring and token validation tools."""

    async def _fetch_json(url: str, timeout: int = 5) -> dict | None:
        """Safe HTTP GET returning JSON or None."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    logger.warning("HTTP %d from %s", resp.status, url)
                    return None
        except Exception as e:
            logger.warning("Fetch failed %s: %s", url, e)
            return None

    async def loop_monitor(target: str, params: dict) -> str:
        """
        Run a full loop health check. Returns a structured report.
        Checks: tick history, token usage, plan format, repetition.
        """
        report_lines = []
        report_lines.append(f"=== Loop Monitor Report — {datetime.now().strftime('%H:%M:%S')} ===\n")

        anomalies = []
        stats = {
            "ticks_checked": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "format_errors": 0,
            "path_errors": 0,
            "repeated_plans": 0,
        }

        # --- 1. Runtime Status ---
        runtime = await _fetch_json(f"{DASHBOARD_BASE}/api/runtime")
        if runtime:
            report_lines.append(f"Runtime: {runtime.get('status', 'unknown')}")
            report_lines.append(f"Tick: {runtime.get('tick_count', '?')}")
            report_lines.append(f"Tools: {runtime.get('tool_count', '?')}")
        else:
            report_lines.append("Runtime: NICHT ERREICHBAR")
            anomalies.append("Dashboard/Runtime API nicht erreichbar")

        # --- 2. Tick History ---
        ticks_data = await _fetch_json(f"{DASHBOARD_BASE}/api/runtime/ticks?limit=20")
        if ticks_data:
            ticks = ticks_data.get("ticks", [])
            idle_repeats = ticks_data.get("idle_repeats", 0)
            stats["ticks_checked"] = len(ticks)

            if idle_repeats > 2:
                anomalies.append(f"Idle-Repeats hoch: {idle_repeats} (Agent wiederholt sich)")

            # Check for plan repetition
            goals = [t.get("goal", "") for t in ticks]
            if len(goals) >= 3:
                unique_goals = set(goals[-5:])
                if len(unique_goals) == 1 and goals:
                    stats["repeated_plans"] = len(goals)
                    anomalies.append(f"Plan-Wiederholung: {len(goals[-5:])}x identisches Goal")

            # Check step success
            for t in ticks:
                ok = t.get("steps_ok", 0)
                fail = t.get("steps_fail", 0)
                if fail > 0:
                    anomalies.append(f"Tick {t.get('tick', '?')}: {fail} failed steps")

            report_lines.append(f"\nTicks analysiert: {len(ticks)}")
            report_lines.append(f"Idle-Repeats: {idle_repeats}")
        else:
            report_lines.append("\nTick-History: nicht verfügbar")

        # --- 3. Prompt Log Analysis (Token Usage) ---
        prompts = await _fetch_json(f"{DASHBOARD_BASE}/api/logs/prompts?limit=10")
        if prompts and isinstance(prompts, list):
            report_lines.append(f"\nPrompt-Einträge analysiert: {len(prompts)}")

            for entry in prompts:
                resp_text = entry.get("response", "")
                sys_text = entry.get("system_prompt", "")

                # Estimate token counts (rough: 1 token ≈ 4 chars for German)
                resp_tokens = len(resp_text) // 4
                sys_tokens = len(sys_text) // 4
                stats["total_completion_tokens"] += resp_tokens
                stats["total_prompt_tokens"] += sys_tokens

                # Format check: response should start with GOAL:
                if resp_text and not resp_text.strip().startswith("GOAL:"):
                    stats["format_errors"] += 1
                    anomalies.append(f"Format-Fehler: Response beginnt nicht mit 'GOAL:'")

                # Path check: response should not contain WORKSPACE/ prefix
                if "WORKSPACE/" in resp_text and "WORKING/" not in resp_text.replace("WORKSPACE/WORKING/", ""):
                    stats["path_errors"] += 1
                    anomalies.append("Pfad-Fehler: 'WORKSPACE/' ohne 'WORKING/' gefunden")

                # Token explosion check
                if resp_tokens > 600:
                    anomalies.append(f"Token-Explosion: ~{resp_tokens} Tokens in Response (Limit: 500)")

            avg_completion = stats["total_completion_tokens"] // max(len(prompts), 1)
            report_lines.append(f"Ø Completion-Tokens: ~{avg_completion}")
            report_lines.append(f"Ø System-Prompt-Tokens: ~{stats['total_prompt_tokens'] // max(len(prompts), 1)}")
        else:
            report_lines.append("\nPrompt-Log: nicht verfügbar oder leer")

        # --- 4. LM Studio Model Check ---
        models = await _fetch_json(f"{LM_STUDIO_BASE}/v1/models")
        if models and "data" in models:
            loaded = [m.get("id", "?") for m in models["data"]]
            report_lines.append(f"\nLM Studio Modelle: {', '.join(loaded)}")
        else:
            report_lines.append("\nLM Studio: nicht erreichbar")
            anomalies.append("LM Studio API nicht erreichbar")

        # --- 5. Summary ---
        report_lines.append(f"\n--- Zusammenfassung ---")
        report_lines.append(f"Format-Fehler: {stats['format_errors']}")
        report_lines.append(f"Pfad-Fehler: {stats['path_errors']}")
        report_lines.append(f"Plan-Wiederholungen: {stats['repeated_plans']}")

        if anomalies:
            report_lines.append(f"\n⚠ {len(anomalies)} Anomalien gefunden:")
            for a in anomalies:
                report_lines.append(f"  - {a}")
        else:
            report_lines.append(f"\n✓ Keine Anomalien — Loop läuft sauber")

        # --- 6. RFL Feedback ---
        if anomalies:
            report_lines.append(f"\n--- RFL-Empfehlungen ---")
            if stats["format_errors"] > 0:
                report_lines.append("→ Planner System-Prompt VERBOTEN-Block prüfen")
            if stats["path_errors"] > 0:
                report_lines.append("→ _validate_path() Prefix-Stripping erweitern")
            if stats["repeated_plans"] > 2:
                report_lines.append("→ idle_skip_after Wert senken oder Agenda diversifizieren")
            if any("Token-Explosion" in a for a in anomalies):
                report_lines.append("→ max_tokens Limit im planner.plan() prüfen")

        # Save report to LOGS
        logs_dir = workspace_root / "WORKING" / "LOGS"
        logs_dir.mkdir(parents=True, exist_ok=True)
        report_file = logs_dir / f"loop_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_text = "\n".join(report_lines)
        report_file.write_text(report_text, encoding="utf-8")

        report_lines.append(f"\nReport gespeichert: WORKING/LOGS/{report_file.name}")
        return "\n".join(report_lines)

    async def token_budget(target: str, params: dict) -> str:
        """
        Show current token budget configuration and usage stats.
        Target: ignored. Returns token limits and recommendations.
        """
        budget = {
            "planner_heartbeat": {"max": 500, "context": "Idle/Heartbeat Ticks"},
            "planner_active": {"max": 1500, "context": "Active Task Planung"},
            "analyze": {"max": 300, "context": "Analyse-Aufgaben"},
            "summarize": {"max": 200, "context": "Zusammenfassungen"},
            "coding": {"max": "4000 (TODO)", "context": "Code-Generierung"},
        }

        lines = ["Token-Budget Übersicht:", ""]
        lines.append(f"{'Kontext':<25} {'Max Tokens':<15} {'Beschreibung'}")
        lines.append("-" * 65)
        for name, info in budget.items():
            lines.append(f"{name:<25} {str(info['max']):<15} {info['context']}")

        lines.append("")
        lines.append("WICHTIG: Coding-Tasks brauchen deutlich mehr Tokens.")
        lines.append("Token-Limits sind kontextabhängig — Loop spart, Arbeit investiert.")

        return "\n".join(lines)

    return [
        Tool(
            name="loop_monitor",
            handler=loop_monitor,
            description="Run full loop health check. Checks ticks, tokens, format, paths, repetition. Saves report to LOGS/.",
            security_level=1,
            tags=["monitoring", "testing", "project"],
        ),
        Tool(
            name="token_budget",
            handler=token_budget,
            description="Show current token budget limits and usage recommendations.",
            security_level=1,
            tags=["monitoring", "config", "project"],
        ),
    ]
