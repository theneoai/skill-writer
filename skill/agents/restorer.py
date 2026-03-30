"""Restorer Agent - Skill repair with multi-LLM validation."""

from __future__ import annotations

import json
import os
import re
import tempfile
from typing import Any, Optional

from skill.agents.agent import AgentBase, call_llm, call_llm_json, validate_json


class RestorerAgent(AgentBase):
    """Agent for restoring and repairing broken skills."""

    def __init__(self) -> None:
        """Initialize Restorer agent."""
        super().__init__()


def restore_skill(skill_file: str) -> dict:
    """Restore a broken or degraded skill file.

    Args:
        skill_file: Path to skill file to restore.

    Returns:
        Dictionary with restoration status and details.
    """
    if not os.path.exists(skill_file):
        return {"error": "Skill file not found"}

    try:
        with open(skill_file, "r") as f:
            content = f.read()
    except IOError:
        return {"error": "Could not read skill file"}

    old_score_result = evaluate_skill_fast(skill_file)
    old_score = old_score_result.get("total_score", 0)

    diagnosis = multi_llm_diagnose(content)

    issues = diagnosis.get("issues", [])
    issues_count = len(issues) if isinstance(issues, list) else 0

    if issues_count == 0:
        return {
            "status": "NO_ISSUES",
            "old_score": old_score,
            "new_score": old_score,
            "issues_found": 0,
            "fixes_applied": [],
        }

    fixes = multi_llm_propose_fixes(content, diagnosis)

    temp_fd, temp_path = tempfile.mkstemp(suffix=".md")
    try:
        with open(skill_file, "r") as f:
            original_content = f.read()
        os.write(temp_fd, original_content.encode())
        os.close(temp_fd)
    except IOError:
        return {"error": "Could not create temp file"}

    apply_fixes(temp_path, fixes)

    new_score_result = evaluate_skill_fast(temp_path)
    new_score = new_score_result.get("total_score", 0)

    score_delta = new_score - old_score

    if score_delta >= 0.5:
        try:
            with open(temp_path, "r") as f:
                restored_content = f.read()
            with open(skill_file, "w") as f:
                f.write(restored_content)
        except IOError:
            pass

        fixes_applied = []
        if isinstance(fixes, dict) and "fixes" in fixes:
            fixes_applied = [f.get("description", "") for f in fixes["fixes"]]

        os.unlink(temp_path)

        return {
            "status": "RESTORED",
            "old_score": old_score,
            "new_score": new_score,
            "score_delta": score_delta,
            "issues_found": issues_count,
            "fixes_applied": fixes_applied,
            "verification": "MULTI_LLM_APPROVED",
        }
    else:
        os.unlink(temp_path)

        return {
            "status": "RESTORATION_FAILED",
            "old_score": old_score,
            "new_score": new_score,
            "score_delta": score_delta,
            "issues_found": issues_count,
            "recommendation": "HUMAN_REVIEW_REQUIRED",
        }


def evaluate_skill_fast(skill_file: str) -> dict:
    """Fast evaluation of skill file.

    Args:
        skill_file: Path to skill file.

    Returns:
        Dictionary with total_score and tier.
    """
    if not os.path.exists(skill_file):
        return {"total_score": 0, "tier": "UNKNOWN"}

    try:
        with open(skill_file, "r") as f:
            content = f.read()
    except IOError:
        return {"total_score": 0, "tier": "UNKNOWN"}

    score = 0

    has_header = bool(re.search(r"^#\s+\w+", content, re.MULTILINE))
    if has_header:
        score += 10

    section_count = len(re.findall(r"^## §[0-9]", content, re.MULTILINE))
    score += min(section_count * 5, 50)

    tier = "UNKNOWN"
    if score >= 70:
        tier = "GOLD"
    elif score >= 50:
        tier = "SILVER"
    elif score >= 30:
        tier = "BRONZE"

    return {"total_score": score, "tier": tier}


def multi_llm_diagnose(content: str) -> dict:
    """Diagnose skill issues using multiple LLMs.

    Args:
        content: Skill file content.

    Returns:
        Dictionary with issues and LLM diagnoses.
    """
    r1 = llm_diagnose_single("anthropic", content)
    r2 = llm_diagnose_single("openai", content)
    r3 = llm_diagnose_single("kimi", content)

    issues1 = r1.get("issues", []) if isinstance(r1, dict) else []
    issues2 = r2.get("issues", []) if isinstance(r2, dict) else []
    issues3 = r3.get("issues", []) if isinstance(r3, dict) else []

    cross_validated = cross_validate_issues(
        json.dumps(issues1), json.dumps(issues2), json.dumps(issues3)
    )

    return {**cross_validated, "llm_diagnoses": [r1, r2, r3]}


def llm_diagnose_single(provider: str, content: str) -> dict:
    """Diagnose skill issues using a single LLM.

    Args:
        provider: LLM provider to use.
        content: Skill file content.

    Returns:
        Dictionary with issues and overall_health.
    """
    prompt = f"""Diagnose this skill file for problems:

Check for:
1. Parse errors (YAML frontmatter, section structure)
2. Missing required sections (§1.1, §1.2, §1.3)
3. Score regression causes
4. Security vulnerabilities
5. Incomplete workflows
6. Missing error handling
7. Vague instructions

Content:
{content}

Respond with JSON:
{{
  "issues": [
    {{
      "type": "PARSE_ERROR|MISSING_SECTION|SECURITY|INCOMPLETE|VAGUE",
      "severity": "P0|P1|P2|P3",
      "location": "line number or section",
      "description": "what is wrong",
      "suggestion": "how to fix"
    }}
  ],
  "overall_health": "GOOD|FAIR|POOR"
}}"""

    system_prompt = "You are a skill restoration expert. Diagnose issues in SKILL.md files."

    response = call_llm(system_prompt, prompt, "auto", provider)

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"issues": [], "overall_health": "UNKNOWN"}
    return {"issues": [], "overall_health": "UNKNOWN"}


def cross_validate_issues(issues1: str, issues2: str, issues3: str) -> dict:
    """Cross-validate issues from multiple LLMs.

    Args:
        issues1: JSON string of issues from first LLM.
        issues2: JSON string of issues from second LLM.
        issues3: JSON string of issues from third LLM.

    Returns:
        Dictionary with consensus issues.
    """
    try:
        list1 = json.loads(issues1) if issues1 else []
        list2 = json.loads(issues2) if issues2 else []
        list3 = json.loads(issues3) if issues3 else []
    except json.JSONDecodeError:
        return {"issues": [], "confidence": 0.5}

    types1 = {issue.get("type") for issue in list1 if isinstance(issue, dict)}
    types2 = {issue.get("type") for issue in list2 if isinstance(issue, dict)}
    types3 = {issue.get("type") for issue in list3 if isinstance(issue, dict)}

    all_types = types1 | types2 | types3

    consensus_issues = []

    for issue_type in all_types:
        found_in = 0
        matching_issue = None

        if issue_type in types1:
            found_in += 1
            for issue in list1:
                if isinstance(issue, dict) and issue.get("type") == issue_type:
                    matching_issue = issue
                    break

        if issue_type in types2:
            found_in += 1
            if matching_issue is None:
                for issue in list2:
                    if isinstance(issue, dict) and issue.get("type") == issue_type:
                        matching_issue = issue
                        break

        if issue_type in types3:
            found_in += 1
            if matching_issue is None:
                for issue in list3:
                    if isinstance(issue, dict) and issue.get("type") == issue_type:
                        matching_issue = issue
                        break

        if found_in >= 2 and matching_issue is not None:
            consensus_issues.append(matching_issue)

    confidence = 0.9 if consensus_issues else 0.5

    return {
        "issues": consensus_issues,
        "llm_agreement": [
            {"provider": "anthropic", "issues": len(list1)},
            {"provider": "openai", "issues": len(list2)},
            {"provider": "kimi", "issues": len(list3)},
        ],
        "confidence": confidence,
    }


def multi_llm_propose_fixes(content: str, diagnosis: dict) -> dict:
    """Propose fixes using multiple LLMs.

    Args:
        content: Skill file content.
        diagnosis: Diagnosis results.

    Returns:
        Dictionary with fixes.
    """
    issues = diagnosis.get("issues", [])

    r1 = llm_propose_fixes_single("anthropic", content, issues)
    r2 = llm_propose_fixes_single("openai", content, issues)
    r3 = llm_propose_fixes_single("kimi", content, issues)

    return cross_validate_fixes(
        json.dumps(r1) if isinstance(r1, dict) else r1,
        json.dumps(r2) if isinstance(r2, dict) else r2,
        json.dumps(r3) if isinstance(r3, dict) else r3,
    )


def llm_propose_fixes_single(provider: str, content: str, issues: list) -> dict:
    """Propose fixes using a single LLM.

    Args:
        provider: LLM provider to use.
        content: Skill file content.
        issues: List of issues to fix.

    Returns:
        Dictionary with fixes.
    """
    prompt = f"""Propose fixes for these skill issues:

Issues found:
{json.dumps(issues, indent=2)}

Skill content:
{content}

For each issue, propose:
1. Exact text to change
2. Line/section to modify
3. New content to insert

Respond with JSON:
{{
  "fixes": [
    {{
      "issue_type": "matching issue type",
      "description": "what will be changed",
      "target_section": "§X.X",
      "old_content": "current text (if applicable)",
      "new_content": "replacement text"
    }}
  ]
}}"""

    system_prompt = "You are a skill restoration expert. Propose specific fixes."

    response = call_llm(system_prompt, prompt, "auto", provider)

    if response.get("status") == "success" and response.get("content"):
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"fixes": []}
    return {"fixes": []}


def cross_validate_fixes(fixes1: str, fixes2: str, fixes3: str) -> dict:
    """Cross-validate fixes from multiple LLMs.

    Args:
        fixes1: JSON string of fixes from first LLM.
        fixes2: JSON string of fixes from second LLM.
        fixes3: JSON string of fixes from third LLM.

    Returns:
        Dictionary with consensus fixes.
    """
    try:
        dict1 = json.loads(fixes1) if fixes1 else {"fixes": []}
        dict2 = json.loads(fixes2) if fixes2 else {"fixes": []}
        dict3 = json.loads(fixes3) if fixes3 else {"fixes": []}
    except json.JSONDecodeError:
        return {"fixes": []}

    list1 = dict1.get("fixes", []) if isinstance(dict1, dict) else []
    list2 = dict2.get("fixes", []) if isinstance(dict2, dict) else []
    list3 = dict3.get("fixes", []) if isinstance(dict3, dict) else []

    max_count = max(len(list1), len(list2), len(list3))

    consensus_fixes = []

    for i in range(max_count):
        fix1 = list1[i] if i < len(list1) else None
        fix2 = list2[i] if i < len(list2) else None
        fix3 = list3[i] if i < len(list3) else None

        if fix1 and fix2 and fix3:
            desc1 = fix1.get("description", "")
            desc2 = fix2.get("description", "")
            desc3 = fix3.get("description", "")

            if desc1 == desc2 or desc1 == desc3:
                consensus_fixes.append(fix1)
            elif desc2 == desc3:
                consensus_fixes.append(fix2)

    return {"fixes": consensus_fixes}


def apply_fixes(skill_file: str, fixes: dict) -> bool:
    """Apply fixes to a skill file.

    Args:
        skill_file: Path to skill file.
        fixes: Dictionary with fixes to apply.

    Returns:
        True if fixes were applied, False otherwise.
    """
    if not os.path.exists(skill_file):
        return False

    fixes_list = fixes.get("fixes", []) if isinstance(fixes, dict) else []

    if not fixes_list:
        return False

    try:
        with open(skill_file, "r") as f:
            content = f.read()
    except IOError:
        return False

    for fix in fixes_list:
        target_section = fix.get("target_section", "")
        new_content = fix.get("new_content", "")

        if not target_section or not new_content:
            continue

        section_pattern = target_section.replace(".", "\\.")

        if re.search(rf"## {section_pattern}", content):
            pattern = rf"(## {re.escape(target_section)}.*?\n)(.*?)(?=\n## |\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                section_header = match.group(1)
                replacement = section_header + new_content + "\n"
                content = content[: match.start()] + replacement + content[match.end() :]

    try:
        with open(skill_file, "w") as f:
            f.write(content)
        return True
    except IOError:
        return False
