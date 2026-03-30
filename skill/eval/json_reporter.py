"""JSON report generation module."""

from __future__ import annotations

import json


def generate_json_report(
    output_file: str,
    skill_name: str,
    skill_version: str,
    evaluated_at: str,
    parse_score: int,
    text_score: int,
    runtime_score: int,
    certify_score: int,
    total_score: int,
    f1_score: float,
    mrr_score: float,
    trigger_accuracy: float,
    variance: float,
    tier: str,
    certified: str,
    dimension_json: str,
    recommendations_json: str,
) -> None:
    """Generate JSON evaluation report.

    Args:
        output_file: Output JSON file path
        skill_name: Name of the skill
        skill_version: Version of the skill
        evaluated_at: Evaluation timestamp
        parse_score: Phase 1 score
        text_score: Phase 2 score
        runtime_score: Phase 3 score
        certify_score: Phase 4 score
        total_score: Total score
        f1_score: F1 score metric
        mrr_score: MRR metric
        trigger_accuracy: Trigger accuracy metric
        variance: Variance value
        tier: Certification tier
        certified: Certification status
        dimension_json: JSON string of dimension scores
        recommendations_json: JSON string of recommendations
    """
    f1_threshold = 0.90
    mrr_threshold = 0.85
    ta_threshold = 0.99
    text_threshold = 280
    runtime_threshold = 360
    variance_threshold = 20

    f1_met = f1_score >= f1_threshold
    mrr_met = mrr_score >= mrr_threshold
    ta_met = trigger_accuracy >= ta_threshold
    text_met = text_score >= text_threshold
    runtime_met = runtime_score >= runtime_threshold
    variance_met = variance < variance_threshold

    report = {
        "skill_name": skill_name,
        "version": skill_version,
        "evaluated_at": evaluated_at,
        "scores": {
            "parse_validate": parse_score,
            "text_score": text_score,
            "runtime_score": runtime_score,
            "certify": certify_score,
            "total": total_score,
        },
        "metrics": {
            "f1_score": f1_score,
            "mrr": mrr_score,
            "trigger_accuracy": trigger_accuracy,
            "variance": variance,
        },
        "tier": tier,
        "certified": certified == "true",
        "dimensions": json.loads(dimension_json) if dimension_json else {},
        "weakest_dimensions": json.loads(recommendations_json) if recommendations_json else [],
        "thresholds_met": {
            "f1": f1_met,
            "mrr": mrr_met,
            "trigger_accuracy": ta_met,
            "text_score": text_met,
            "runtime_score": runtime_met,
            "variance": variance_met,
        },
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def generate_dimension_json(
    system_prompt_score: int,
    domain_knowledge_score: int,
    workflow_score: int,
    error_handling_score: int,
    examples_score: int,
    metadata_score: int,
    identity_consistency_score: int,
    framework_execution_score: int,
    output_actionability_score: int,
    knowledge_accuracy_score: int,
    conversation_stability_score: int,
    trace_compliance_score: int,
    long_document_score: int,
    multi_agent_score: int,
    trigger_accuracy_score: int,
) -> str:
    """Generate dimension JSON string.

    Args:
        All dimension scores as individual parameters

    Returns:
        JSON string of dimension scores
    """
    dimensions = {
        "system_prompt": {"score": system_prompt_score, "max": 70},
        "domain_knowledge": {"score": domain_knowledge_score, "max": 70},
        "workflow": {"score": workflow_score, "max": 70},
        "error_handling": {"score": error_handling_score, "max": 55},
        "examples": {"score": examples_score, "max": 55},
        "metadata": {"score": metadata_score, "max": 30},
        "identity_consistency": {"score": identity_consistency_score, "max": 80},
        "framework_execution": {"score": framework_execution_score, "max": 70},
        "output_actionability": {"score": output_actionability_score, "max": 70},
        "knowledge_accuracy": {"score": knowledge_accuracy_score, "max": 50},
        "conversation_stability": {"score": conversation_stability_score, "max": 50},
        "trace_compliance": {"score": trace_compliance_score, "max": 50},
        "long_document": {"score": long_document_score, "max": 30},
        "multi_agent": {"score": multi_agent_score, "max": 25},
        "trigger_accuracy_score": {"score": trigger_accuracy_score, "max": 25},
    }

    return json.dumps(dimensions, indent=2)
