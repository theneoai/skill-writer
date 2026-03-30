"""Learner module for pattern extraction from usage data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_improvement_hints(patterns_file: str) -> dict[str, Any]:
    """Get improvement hints from patterns file."""
    skill_name = Path(patterns_file).stem.replace("_patterns", "")

    try:
        with open(patterns_file) as f:
            patterns = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"skill": skill_name, "hint_count": 0, "hints": ["No data yet."]}

    skill_name = patterns.get("skill", skill_name)

    try:
        with open(patterns_file) as f:
            patterns = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"skill": skill_name, "hint_count": 0, "hints": ["No data yet."]}

    trigger_f1 = patterns.get("metrics", {}).get("trigger_f1", 1.0)
    task_rate = patterns.get("metrics", {}).get("task_completion_rate", 1.0)
    weak_triggers = patterns.get("patterns", {}).get("weak_triggers", [])

    hints = []

    if trigger_f1 < 0.85 and weak_triggers:
        weak_str = ", ".join(weak_triggers)
        hints.append(
            f"Trigger confusion detected: {weak_str}. Consider adding disambiguation examples."
        )

    if task_rate < 0.80:
        hints.append("Task completion issues detected. Review workflow steps and error handling.")

    if not hints:
        hints.append("No specific issues found. Continue normal optimization.")

    return {
        "skill": skill_name,
        "hint_count": len(hints),
        "hints": hints,
    }


def learn_from_usage(skill_file: str, rounds: int = 10) -> dict[str, Any]:
    """Learn patterns from usage data."""
    pass


def consolidate_knowledge(skill_name: str) -> str:
    """Consolidate knowledge into markdown file."""
    pass
