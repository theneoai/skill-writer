"""Storage module for usage log operations."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


USAGE_LOG = os.environ.get("USAGE_LOG", "/tmp/usage.jsonl")

EVOLUTION_THRESHOLD_NEW = 10
EVOLUTION_THRESHOLD_GROWING = 5
EVOLUTION_THRESHOLD_STABLE = 2


def get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory(path: str) -> None:
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def storage_get_eval_count(skill_name: str) -> int:
    """Get count of evaluations for a skill."""
    if not Path(USAGE_LOG).exists():
        return 0

    count = 0
    with open(USAGE_LOG) as f:
        for line in f:
            if f'"skill_name":"{skill_name}"' in line:
                count += 1
    return count


def storage_get_last_score(skill_name: str) -> float:
    """Get last score for a skill."""
    if not Path(USAGE_LOG).exists():
        return 0

    last_score = 0
    with open(USAGE_LOG) as f:
        for line in f:
            if f'"skill_name":"{skill_name}"' in line:
                try:
                    entry = json.loads(line)
                    last_score = entry.get("score", 0)
                except json.JSONDecodeError:
                    continue
    return last_score


def storage_get_all_scores(skill_name: str) -> list[dict[str, Any]]:
    """Get all score entries for a skill."""
    if not Path(USAGE_LOG).exists():
        return []

    scores = []
    with open(USAGE_LOG) as f:
        for line in f:
            if f'"skill_name":"{skill_name}"' in line:
                try:
                    entry = json.loads(line)
                    scores.append(entry)
                except json.JSONDecodeError:
                    continue
    return scores


def storage_log_usage(
    skill_name: str,
    score: float,
    tier: str,
    iterations: int,
) -> None:
    """Log usage entry."""
    ensure_directory(str(Path(USAGE_LOG).parent))
    entry = {
        "timestamp": get_timestamp(),
        "skill_name": skill_name,
        "score": score,
        "tier": tier,
        "iterations": iterations,
    }
    with open(USAGE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def storage_calculate_threshold(eval_count: int) -> int:
    """Calculate threshold based on evaluation count."""
    if eval_count < 10:
        return EVOLUTION_THRESHOLD_NEW
    elif eval_count < 50:
        return EVOLUTION_THRESHOLD_GROWING
    return EVOLUTION_THRESHOLD_STABLE
