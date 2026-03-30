"""Creator Agent - Section generator for SKILL.md files."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from skill.agents.agent import AgentBase, call_llm, call_llm_json, load_prompt


class CreatorAgent(AgentBase):
    """Agent for generating SKILL.md sections."""

    def __init__(self) -> None:
        """Initialize Creator agent."""
        super().__init__()


def generate_section(context_file: str) -> Optional[dict]:
    """Generate a section for SKILL.md based on context.

    Args:
        context_file: Path to JSON file containing context.

    Returns:
        Dictionary with content and deliberation, or None on failure.
    """
    try:
        with open(context_file, "r") as f:
            context = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    user_prompt = context.get("user_prompt", "")
    section_num = context.get("current_section", 1)
    evaluator_feedback = context.get("evaluator_feedback", "")

    system_prompt = load_prompt("creator-system")

    prompt = f"""Create section §{section_num} of the SKILL.md file.

User's original request: {user_prompt}

Current section number: {section_num}

Evaluator feedback from previous iteration (if any):
{evaluator_feedback if evaluator_feedback else "No feedback yet. This is the first section."}

"""

    r1 = call_llm(system_prompt, prompt, "auto", "kimi-code")
    r2 = call_llm(system_prompt, prompt, "auto", "minimax")

    status1 = r1.get("status", "ERROR")
    status2 = r2.get("status", "ERROR")

    content1 = r1.get("content", "")
    content2 = r2.get("content", "")

    if status1 != "success" and status2 != "success":
        return None

    if status1 != "success":
        return {"content": content2, "deliberation": "single_llm"}

    if status2 != "success":
        return {"content": content1, "deliberation": "single_llm"}

    if not content1 or content1 == "null":
        return {"content": content2, "deliberation": "single_llm"}

    if not content2 or content2 == "null":
        return {"content": content1, "deliberation": "single_llm"}

    if content1 == content2:
        return {"content": content1, "deliberation": "unanimous"}

    deliberation_prompt = f"""Compare two proposed sections for §{section_num} and determine the better one.

Proposal A:
{content1}

Proposal B:
{content2}

User request: {user_prompt}

Respond with JSON:
{{"chosen": "A" or "B", "reason": "brief explanation"}}"""

    decision = call_llm_json(
        "You are a skill architecture expert. Select the better section implementation.",
        deliberation_prompt,
        "auto",
        "kimi",
    )

    if decision and decision.get("chosen"):
        chosen = decision.get("chosen")
        reason = decision.get("reason", "")
        if chosen == "A":
            return {"content": content1, "deliberation": "deliberated", "reason": reason}
        else:
            return {"content": content2, "deliberation": "deliberated", "reason": reason}

    len1, len2 = len(content1), len(content2)
    if len1 >= len2:
        return {"content": content1, "deliberation": "conflict_length_fallback"}
    else:
        return {"content": content2, "deliberation": "conflict_length_fallback"}


def init_skill_file(skill_file: str, skill_name: str, parent_skill: Optional[str] = None) -> bool:
    """Initialize a new SKILL.md file.

    Args:
        skill_file: Path to the skill file to create.
        skill_name: Name of the skill.
        parent_skill: Optional parent skill to inherit from.

    Returns:
        True if successful, False otherwise.
    """
    content = f"""# {skill_name}

> **Version**: 0.1.0
> **Date**: {datetime.now().strftime("%Y-%m-%d")}
> **Status**: DRAFT

---

"""

    try:
        with open(skill_file, "w") as f:
            f.write(content)

        if parent_skill:
            inherit_sections(parent_skill, skill_file)

        return True
    except IOError:
        return False


def extract_inherited_sections(parent_skill: str) -> str:
    """Extract sections to inherit from parent skill.

    Args:
        parent_skill: Path to parent skill file.

    Returns:
        Extracted section content or empty string.
    """
    if not os.path.exists(parent_skill):
        return ""

    try:
        with open(parent_skill, "r") as f:
            content = f.read()
    except IOError:
        return ""

    lines = content.split("\n")
    result = []
    in_section = False
    section_start = None

    for i, line in enumerate(lines):
        if re.match(r"^## §1\.1", line):
            in_section = True
            section_start = i
        elif in_section and re.match(r"^## [^§]", line):
            break
        elif in_section:
            result.append(line)

    identity_section = "\n".join(result)

    result = []
    in_section = False

    for i, line in enumerate(lines):
        if "**Red Lines" in line or "严禁" in line:
            in_section = True
        elif in_section and re.match(r"^## [^§]", line):
            break
        elif in_section:
            result.append(line)

    redlines_section = "\n".join(result)

    result = []
    in_section = False

    for i, line in enumerate(lines):
        if re.match(r"^## §6", line):
            in_section = True
        elif in_section and re.match(r"^## [^§]", line):
            break
        elif in_section:
            result.append(line)

    if result and result[-1] == "":
        result = result[:-1]

    evolution_section = "\n".join(result)

    sections = []
    if identity_section.strip():
        sections.append(identity_section)
    if redlines_section.strip():
        sections.append(redlines_section)
    if evolution_section.strip():
        sections.append(evolution_section)

    return "\n".join(sections)


def inherit_sections(parent_skill: str, target_file: str) -> bool:
    """Inherit sections from parent skill to target file.

    Args:
        parent_skill: Path to parent skill file.
        target_file: Path to target skill file.

    Returns:
        True if sections were inherited, False otherwise.
    """
    inherited = extract_inherited_sections(parent_skill)

    if not inherited:
        return False

    try:
        with open(target_file, "a") as f:
            f.write("\n" + inherited + "\n")
        return True
    except IOError:
        return False


SECTION_PROMPTS = {
    1: "§1.1 Identity - Define the skill's name, purpose, and core characteristics",
    2: "§1.2 Framework - Describe the operating principles",
    3: "§1.3 Thinking - Define the cognitive framework",
    4: "§2.1 Invocation - How to activate this skill",
    5: "§2.2 Recognition - Pattern matching rules",
    6: "§3.1 Process - Main workflow steps",
    7: "§4.1 Tool Set - Available tools",
    8: "§5.1 Validation - Quality checks",
    9: "§8.1 Metrics - Success criteria",
}


def get_next_section_prompt(section_num: int, skill_type: str = "default") -> str:
    """Get the prompt for the next section to generate.

    Args:
        section_num: Section number.
        skill_type: Type of skill (unused, for compatibility).

    Returns:
        Prompt description for the section.
    """
    return SECTION_PROMPTS.get(
        section_num, "Continue developing the skill with additional sections"
    )
