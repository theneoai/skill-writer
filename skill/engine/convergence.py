"""Convergence detection module."""

from __future__ import annotations

import math
from typing import Any


def check_volatility(scores: Any, threshold: float) -> str:
    """Check if score volatility is below threshold."""
    if not scores:
        return "UNKNOWN"

    if isinstance(scores, str):
        import json

        try:
            scores = json.loads(scores)
        except json.JSONDecodeError:
            return "UNKNOWN"

    if len(scores) < 2:
        return "UNKNOWN"

    score_values = [s["score"] if isinstance(s, dict) else s for s in scores]

    count = len(score_values)
    total = sum(score_values)
    sum_sq = sum(v * v for v in score_values)

    mean = total / count
    variance = (sum_sq / count) - (mean * mean)
    stddev = math.sqrt(variance) if variance > 0 else 0

    if stddev < threshold:
        return "CONVERGED"
    return f"VOLATILE(stddev={stddev})"


def check_plateau(scores: Any, threshold: float) -> str:
    """Check if scores are in a plateau (small deltas)."""
    if not scores:
        return "UNKNOWN"

    if isinstance(scores, str):
        import json

        try:
            scores = json.loads(scores)
        except json.JSONDecodeError:
            return "UNKNOWN"

    if len(scores) < 3:
        return "UNKNOWN"

    score_values = [s["score"] if isinstance(s, dict) else s for s in scores]
    deltas = [score_values[i] - score_values[i - 1] for i in range(1, len(score_values))]

    small_deltas = sum(1 for d in deltas if abs(d) < threshold)
    plateau_ratio = small_deltas / len(deltas) if deltas else 0
    total_delta = sum(deltas)

    if plateau_ratio > 0.7 and total_delta <= 0:
        return "CONVERGED"
    return f"ACTIVE(delta={total_delta}, plateau_ratio={plateau_ratio})"


def check_trend(scores: Any) -> str:
    """Check trend direction of scores."""
    if not scores or len(scores) < 4:
        return "UNKNOWN"

    score_values = [s["score"] if isinstance(s, dict) else s for s in scores]
    mid = len(score_values) // 2
    first_half = score_values[:mid]
    second_half = score_values[mid:]

    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    trend = second_avg - first_avg

    if trend > 1.0:
        return "IMPROVING"
    elif trend < -1.0:
        return "DIVERGING"
    return "STABLE"


def check_convergence(
    skill_name: str,
    window_size: int = 10,
    volatility_threshold: float = 2.0,
    plateau_threshold: float = 0.5,
    min_rounds: int = 5,
) -> str:
    """Check if evolution has converged."""
    from skill.engine.storage import storage_get_all_scores

    scores = storage_get_all_scores(skill_name)

    if len(scores) < min_rounds:
        return "NOT_CONVERGED: insufficient_data"

    recent_scores = scores[-window_size:] if len(scores) > window_size else scores

    volatility_status = check_volatility(recent_scores, volatility_threshold)
    plateau_status = check_plateau(recent_scores, plateau_threshold)
    trend_status = check_trend(recent_scores)

    if volatility_status == "CONVERGED" and plateau_status == "CONVERGED":
        return f"CONVERGED: volatility={volatility_status}, plateau={plateau_status}, trend={trend_status}"

    if trend_status == "DIVERGING":
        return "NOT_CONVERGED: trend=diverging"

    return f"NOT_CONVERGED: volatility={volatility_status}, plateau={plateau_status}, trend={trend_status}"


def should_continue_evolution(
    skill_name: str,
    max_rounds: int = 100,
    min_score_improvement: float = 5,
) -> str:
    """Decide if evolution should continue."""
    pass
