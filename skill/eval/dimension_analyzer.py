"""Dimension analyzer - Identify weakest dimensions for improvement recommendations.

Input: all dimension scores
Output: sorted list of weakest dimensions with specific recommendations
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional


DIMENSION_WEIGHTS = {
    "system_prompt": 20,
    "domain_knowledge": 20,
    "workflow": 20,
    "error_handling": 15,
    "examples": 15,
    "metadata": 10,
    "identity_consistency": 18,
    "framework_execution": 16,
    "output_actionability": 16,
    "knowledge_accuracy": 11,
    "conversation_stability": 11,
    "trace_compliance": 11,
    "long_document": 7,
    "multi_agent": 5,
    "trigger_accuracy": 5,
}

DIMENSION_THRESHOLDS = {
    "system_prompt": 56,
    "domain_knowledge": 56,
    "workflow": 56,
    "error_handling": 44,
    "examples": 44,
    "metadata": 24,
    "identity_consistency": 64,
    "framework_execution": 56,
    "output_actionability": 56,
    "knowledge_accuracy": 40,
    "conversation_stability": 40,
    "trace_compliance": 40,
    "long_document": 24,
    "multi_agent": 20,
    "trigger_accuracy": 20,
}

DIMENSION_RECOMMENDATIONS = {
    "system_prompt": "Enhance system prompt with more context from §1.1, §1.2, §1.3 and explicit constraints",
    "domain_knowledge": "Add more specific data and facts (≥10 concrete data points required)",
    "workflow": "Expand workflow to 4-6 clear stages with explicit Done/Fail conditions",
    "error_handling": "Add ≥5 named failure cases with specific recovery strategies",
    "examples": "Include ≥5 complete scenarios with input/output/verification",
    "metadata": "Ensure agentskills-spec compliance for metadata section",
    "identity_consistency": "Strengthen role definition to prevent identity drift in long conversations",
    "framework_execution": "Improve tool call patterns and memory structure access",
    "output_actionability": "Enhance parameter completeness in generated outputs",
    "knowledge_accuracy": "Reduce hallucination by adding factual grounding references",
    "conversation_stability": "Improve MultiTurnPassRate to ≥85%",
    "trace_compliance": "Align behavior with AgentPex rules (≥90% compliance)",
    "long_document": "Test and stabilize 100K token processing",
    "multi_agent": "Strengthen collaboration patterns for multi-agent scenarios",
    "trigger_accuracy": "Improve trigger matching with synonym coverage",
}

DIMENSION_MAX_SCORES = {
    "system_prompt": 70,
    "domain_knowledge": 70,
    "workflow": 70,
    "error_handling": 55,
    "examples": 55,
    "metadata": 30,
    "identity_consistency": 80,
    "framework_execution": 70,
    "output_actionability": 70,
    "knowledge_accuracy": 50,
    "conversation_stability": 50,
    "trace_compliance": 50,
    "long_document": 30,
    "multi_agent": 25,
    "trigger_accuracy": 25,
}


def analyze_dimensions(json_dimensions: str) -> Dict[str, any]:
    """Analyze dimensions and identify weakest ones.

    Args:
        json_dimensions: JSON string with dimension scores

    Returns:
        Dictionary with weak_dimensions list and recommendations
    """
    try:
        dimensions = json.loads(json_dimensions)
    except (json.JSONDecodeError, TypeError):
        return {"weak_dimensions": [], "recommendations": [], "error": "Invalid JSON"}

    if not dimensions:
        return {"weak_dimensions": [], "recommendations": [], "error": "No dimensions provided"}

    weak_dimensions = []

    for dim_name, score in dimensions.items():
        threshold = DIMENSION_THRESHOLDS.get(dim_name, 0)
        weight = DIMENSION_WEIGHTS.get(dim_name, 10)

        if score < threshold:
            recommendation = DIMENSION_RECOMMENDATIONS.get(
                dim_name, "Review and improve this dimension"
            )
            weak_dimensions.append(
                {
                    "dimension": dim_name,
                    "score": score,
                    "threshold": threshold,
                    "weight": weight,
                    "recommendation": recommendation,
                }
            )

    weak_dimensions.sort(key=lambda x: x["score"])

    return {
        "weak_dimensions": weak_dimensions,
        "recommendations": [w["recommendation"] for w in weak_dimensions],
    }


def analyze_dimensions_from_file(score_file: str) -> Dict[str, any]:
    """Analyze dimensions from a file.

    Args:
        score_file: Path to JSON file with dimension scores

    Returns:
        Dictionary with weak_dimensions list and recommendations
    """
    try:
        with open(score_file) as f:
            json_data = f.read()
    except (FileNotFoundError, OSError):
        return {"weak_dimensions": [], "recommendations": [], "error": "File not found"}

    return analyze_dimensions(json_data)


def get_recommendation(dimension: str) -> str:
    """Get recommendation for a dimension.

    Args:
        dimension: Dimension name

    Returns:
        Recommendation string
    """
    return DIMENSION_RECOMMENDATIONS.get(dimension, "Review and improve this dimension")


def format_dimension_report(dimensions_json: str) -> str:
    """Format dimension analysis as a string report.

    Args:
        dimensions_json: JSON string with dimension scores

    Returns:
        Formatted report string
    """
    result = analyze_dimensions(dimensions_json)

    lines = ["=== Dimension Analysis ===", ""]

    if not result["weak_dimensions"]:
        lines.append("No weak dimensions found.")
        return "\n".join(lines)

    lines.append("Weakest dimensions requiring improvement:")
    lines.append("")

    for i, dim in enumerate(result["weak_dimensions"], 1):
        lines.append(f"[{i}] {dim['dimension']} (score: {dim['score']})")
        lines.append(f"    -> {dim['recommendation']}")
        lines.append("")

    return "\n".join(lines)
