"""Trigger analyzer - Calculate F1, MRR, and Trigger Accuracy from corpus test results.

Input: corpus JSON with test cases and results
Output: F1_SCORE, MRR_SCORE, TRIGGER_ACCURACY
"""

from __future__ import annotations

import json
import math
from typing import Dict, List, Optional


F1_THRESHOLD = 0.90
MRR_THRESHOLD = 0.85
TRIGGER_ACCURACY_THRESHOLD = 0.99


def _compute_metrics(json_data: str) -> Dict[str, float]:
    """Compute F1, MRR, and trigger accuracy from JSON data.

    Args:
        json_data: JSON string with array of test cases

    Returns:
        Dictionary with f1_score, mrr_score, trigger_accuracy
    """
    try:
        data = json.loads(json_data)
    except (json.JSONDecodeError, TypeError):
        data = []

    total_queries = len(data)

    if total_queries == 0:
        return {"f1_score": 0.0, "mrr_score": 0.0, "trigger_accuracy": 0.0}

    true_positives = 0
    false_positives = 0
    false_negatives = 0
    reciprocal_ranks_sum = 0.0

    for item in data:
        expected_trigger = item.get("expected_trigger")
        predicted_triggers = item.get("predicted_triggers", [])
        rank = item.get("rank", 0)

        if not expected_trigger or expected_trigger == "null":
            continue

        if isinstance(predicted_triggers, str):
            predicted_triggers = [predicted_triggers]

        if expected_trigger in predicted_triggers:
            true_positives += 1
            if rank > 0:
                reciprocal_ranks_sum += 1.0 / rank
        else:
            if predicted_triggers and predicted_triggers != ["null"] and predicted_triggers != []:
                false_positives += 1
            false_negatives += 1

    if true_positives + false_positives > 0:
        precision = true_positives / (true_positives + false_positives)
    else:
        precision = 0.0

    if true_positives + false_negatives > 0:
        recall = true_positives / (true_positives + false_negatives)
    else:
        recall = 0.0

    if precision + recall > 0:
        f1_score = 2 * precision * recall / (precision + recall)
    else:
        f1_score = 0.0

    mrr_score = reciprocal_ranks_sum / total_queries if total_queries > 0 else 0.0
    trigger_accuracy = true_positives / total_queries if total_queries > 0 else 0.0

    return {
        "f1_score": round(f1_score, 4),
        "mrr_score": round(mrr_score, 4),
        "trigger_accuracy": round(trigger_accuracy, 4),
    }


def analyze_triggers(corpus_file: str) -> Dict[str, float]:
    """Analyze triggers from corpus file.

    Args:
        corpus_file: Path to corpus JSON file

    Returns:
        Dictionary with f1_score, mrr_score, trigger_accuracy
    """
    if not corpus_file or not isinstance(corpus_file, str):
        return {"f1_score": 0.0, "mrr_score": 0.0, "trigger_accuracy": 0.0}

    try:
        with open(corpus_file) as f:
            json_data = f.read()
    except (FileNotFoundError, OSError):
        return {"f1_score": 0.0, "mrr_score": 0.0, "trigger_accuracy": 0.0}

    return _compute_metrics(json_data)


def analyze_triggers_from_json(json_data: str) -> Dict[str, float]:
    """Analyze triggers from JSON string.

    Args:
        json_data: JSON string with corpus data

    Returns:
        Dictionary with f1_score, mrr_score, trigger_accuracy
    """
    return _compute_metrics(json_data)


def check_thresholds(f1_score: float, mrr_score: float, trigger_accuracy: float) -> Dict[str, bool]:
    """Check if scores meet thresholds.

    Args:
        f1_score: F1 score
        mrr_score: MRR score
        trigger_accuracy: Trigger accuracy

    Returns:
        Dictionary with threshold check results
    """
    return {
        "f1": f1_score >= F1_THRESHOLD,
        "mrr": mrr_score >= MRR_THRESHOLD,
        "trigger_accuracy": trigger_accuracy >= TRIGGER_ACCURACY_THRESHOLD,
        "all_pass": (
            f1_score >= F1_THRESHOLD
            and mrr_score >= MRR_THRESHOLD
            and trigger_accuracy >= TRIGGER_ACCURACY_THRESHOLD
        ),
    }


def format_threshold_report(f1_score: float, mrr_score: float, trigger_accuracy: float) -> str:
    """Format threshold check results as string report.

    Args:
        f1_score: F1 score
        mrr_score: MRR score
        trigger_accuracy: Trigger accuracy

    Returns:
        Formatted string report
    """
    checks = check_thresholds(f1_score, mrr_score, trigger_accuracy)

    lines = [
        "=== Threshold Checks ===",
        f"F1: {f1_score:.4f} >= {F1_THRESHOLD} -> {'PASS' if checks['f1'] else 'FAIL'}",
        f"MRR: {mrr_score:.4f} >= {MRR_THRESHOLD} -> {'PASS' if checks['mrr'] else 'FAIL'}",
        f"Trigger Accuracy: {trigger_accuracy:.4f} >= {TRIGGER_ACCURACY_THRESHOLD} -> {'PASS' if checks['trigger_accuracy'] else 'FAIL'}",
    ]

    return "\n".join(lines)
