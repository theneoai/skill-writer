"""Variance analyzer - Calculate variance between Text Score and Runtime Score.

Variance = |Text Score - Runtime Score|
Using 1000pts system: variance = |text_score - runtime_score|
Returns: VARIANCE_SCORE
If variance < 20: PASS
If variance 20-30: WARNING
If variance > 30: FAIL
"""

from __future__ import annotations

from typing import Dict, Optional


def analyze_variance(text_score: float, runtime_score: float) -> Dict[str, any]:
    """Analyze variance between text score and runtime score.

    Args:
        text_score: Text score (out of 350 in original, normalized to 1000)
        runtime_score: Runtime score (out of 450 in original, normalized to 1000)

    Returns:
        Dictionary with variance and status
    """
    if text_score is None or runtime_score is None:
        return {"variance": 0.0, "status": "FAIL", "error": "Scores required"}

    try:
        text_score = float(text_score)
        runtime_score = float(runtime_score)
    except (ValueError, TypeError):
        return {"variance": 0.0, "status": "FAIL", "error": "Scores must be numeric"}

    variance = abs(text_score - runtime_score)

    if variance < 20:
        status = "PASS"
        status_code = 0
    elif variance < 30:
        status = "WARNING"
        status_code = 1
    else:
        status = "FAIL"
        status_code = 2

    return {"variance": round(variance, 2), "status": status, "status_code": status_code}


def analyze_variance_from_json(json_str: str) -> Dict[str, any]:
    """Analyze variance from JSON string.

    Args:
        json_str: JSON string with text_score and runtime_score

    Returns:
        Dictionary with variance and status
    """
    import json

    try:
        data = json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        data = {}

    text_score = data.get("text_score", data.get("text", 0))
    runtime_score = data.get("runtime_score", data.get("runtime", 0))

    return analyze_variance(text_score, runtime_score)


def get_variance_points(variance: float) -> int:
    """Get variance points based on variance value.

    Args:
        variance: Variance value

    Returns:
        Points awarded (0-40)
    """
    if variance is None:
        return 0

    try:
        variance = float(variance)
    except (ValueError, TypeError):
        return 0

    if variance < 10:
        return 40
    elif variance < 20:
        return 30
    elif variance < 30:
        return 15
    else:
        return 0
