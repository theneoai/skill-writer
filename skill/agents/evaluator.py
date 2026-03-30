"""Evaluator Agent - Skill evaluator."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path
from typing import Optional

from skill.agents.agent import AgentBase, call_llm, load_prompt


class EvaluatorAgent(AgentBase):
    """Agent for evaluating SKILL.md quality."""

    def __init__(self) -> None:
        """Initialize Evaluator agent."""
        super().__init__()


def evaluate_skill(skill_file: str, mode: str = "fast") -> dict:
    """Evaluate a skill file.

    Args:
        skill_file: Path to skill file.
        mode: Evaluation mode (fast or full).

    Returns:
        Dictionary with evaluation results.
    """
    if not os.path.exists(skill_file):
        return {"error": "Skill file not found", "total_score": 0}

    try:
        with open(skill_file, "r") as f:
            content = f.read()
    except IOError:
        return {"error": "Could not read file", "total_score": 0}

    score = 0
    tier = "UNKNOWN"

    has_header = bool(re.search(r"^#\s+\w+", content, re.MULTILINE))
    if has_header:
        score += 10

    section_count = len(re.findall(r"^## §[0-9]", content, re.MULTILINE))
    score += min(section_count * 5, 50)

    if "---" in content:
        score += 5

    if "Version" in content and "Date" in content:
        score += 5

    if mode == "full":
        score = min(score * 1.2, 100)

    if score >= 70:
        tier = "GOLD"
    elif score >= 50:
        tier = "SILVER"
    elif score >= 30:
        tier = "BRONZE"

    return {
        "total_score": score,
        "tier": tier,
        "has_header": has_header,
        "section_count": section_count,
    }


def evaluate_file(skill_file: str, section_num: int = 0) -> dict:
    """Evaluate a skill file and generate suggestions.

    Args:
        skill_file: Path to skill file.
        section_num: Section number being evaluated.

    Returns:
        Dictionary with score, tier, and suggestions.
    """
    if not os.path.exists(skill_file):
        return {"error": "Skill file not found"}

    eval_result = evaluate_skill(skill_file, "fast")

    if "error" in eval_result:
        return eval_result

    score = eval_result.get("total_score", 0)
    tier = eval_result.get("tier", "UNKNOWN")

    suggestions = generate_suggestions(skill_file, score, section_num)

    return {
        "score": score,
        "tier": tier,
        "suggestions": suggestions,
        "evaluated_section": section_num,
    }


def evaluate_section(section_content: str, section_num: int = 0) -> dict:
    """Evaluate section content.

    Args:
        section_content: Content of section to evaluate.
        section_num: Section number.

    Returns:
        Dictionary with evaluation results.
    """
    temp_fd, temp_path = tempfile.mkstemp(suffix=".md")
    try:
        os.write(temp_fd, section_content.encode())
        os.close(temp_fd)
        result = evaluate_file(temp_path, section_num)
        return result
    except IOError:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return {"error": "Could not evaluate section"}
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def generate_suggestions(skill_file: str, current_score: float, section_num: int = 0) -> str:
    """Generate improvement suggestions for a skill.

    Args:
        skill_file: Path to skill file.
        current_score: Current evaluation score.
        section_num: Section being developed.

    Returns:
        String with suggestions.
    """
    if not os.path.exists(skill_file):
        return "Unable to generate suggestions at this time."

    try:
        with open(skill_file, "r") as f:
            content = f.read()
    except IOError:
        return "Unable to generate suggestions at this time."

    normalized_score = int(current_score * 1000 / 1155)

    prompt = f"""Based on the current SKILL.md content and a score of {current_score} (normalized: {normalized_score}/1000), generate specific improvement suggestions.

Current section being developed: §{section_num}

Read the SKILL.md file and identify:
1. Missing or incomplete sections
2. Unclear instructions or parameters
3. Missing error handling
4. Missing edge case coverage
5. Quality issues in existing content

Provide 3-5 concrete, actionable suggestions. Each suggestion should:
- Be specific (not "improve the documentation")
- Include what to add or change
- Explain why it matters

Format your response as a numbered list."""

    system_prompt = load_prompt("evaluator-system")

    response = call_llm(system_prompt, prompt, "auto", "kimi-code")

    if response.get("status") != "success" or not response.get("content"):
        return "Unable to generate suggestions at this time."

    return response["content"]


def check_format(skill_file: str) -> str:
    """Check if skill file has valid format.

    Args:
        skill_file: Path to skill file.

    Returns:
        "VALID" if format is valid, error message otherwise.
    """
    if not os.path.exists(skill_file):
        return "ERROR: File not found"

    try:
        with open(skill_file, "r") as f:
            content = f.read()
    except IOError:
        return "ERROR: Could not read file"

    has_header = bool(re.search(r"^#\s+\w+", content, re.MULTILINE))
    has_sections = bool(re.search(r"^## §[0-9]", content, re.MULTILINE))

    if has_header and has_sections:
        return "VALID"
    else:
        return "INVALID: Missing header or sections"


def compare_versions(old_file: str, new_file: str) -> Optional[dict]:
    """Compare two versions of a skill file.

    Args:
        old_file: Path to old version.
        new_file: Path to new version.

    Returns:
        Dictionary with old_score, new_score, and delta, or None on error.
    """
    if not os.path.exists(old_file) or not os.path.exists(new_file):
        return None

    old_result = evaluate_skill(old_file, "fast")
    new_result = evaluate_skill(new_file, "fast")

    old_score = old_result.get("total_score", 0)
    new_score = new_result.get("total_score", 0)
    delta = new_score - old_score

    return {"old_score": old_score, "new_score": new_score, "delta": delta}
