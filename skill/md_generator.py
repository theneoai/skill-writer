"""Markdown generator for SKILL.md files."""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from typing import Any

from skill.schema import SkillMetadata as BaseSkillMetadata


@dataclass
class SkillMetadata(BaseSkillMetadata):
    """Skill metadata for markdown generation."""

    triggers: list[str] = field(default_factory=list)

    @classmethod
    def from_base(cls, base: BaseSkillMetadata, triggers: list[str] | None = None) -> SkillMetadata:
        """Create SkillMetadata from base schema."""
        return cls(
            name=base.name,
            description=base.description,
            version=base.version,
            license=base.license,
            author=base.author,
            tags=base.tags,
            type=base.type,
            modes=base.modes,
            tier=base.tier,
            signoff=base.signoff,
            created=base.created,
            updated=base.updated,
            interface=base.interface,
            extends=base.extends,
            triggers=triggers or [],
        )


def generate_frontmatter(metadata: SkillMetadata) -> str:
    """Generate YAML frontmatter block from metadata."""
    data = {
        "name": metadata.name,
        "description": metadata.description,
        "license": metadata.license,
        "author": metadata.author,
        "version": metadata.version,
        "tags": metadata.tags,
        "type": metadata.type.value if hasattr(metadata.type, "value") else metadata.type,
    }
    if metadata.created:
        data["created"] = metadata.created
    if metadata.updated:
        data["updated"] = metadata.updated
    if metadata.interface:
        data["interface"] = {
            "input": metadata.interface.input,
            "output": metadata.interface.output,
            "modes": metadata.interface.modes,
        }
    if metadata.extends:
        data["extends"] = {
            "evaluation": {
                "metrics": metadata.extends.evaluation.metrics,
                "thresholds": metadata.extends.evaluation.thresholds,
                "external": [
                    {"id": e.id, "name": e.name, "url": e.url, "metrics": e.metrics}
                    for e in metadata.extends.evaluation.external
                ],
            },
            "security": {
                "standard": metadata.extends.security.standard,
                "scan_on_delivery": metadata.extends.security.scan_on_delivery,
            },
            "evolution": {
                "triggers": metadata.extends.evolution.triggers,
            },
        }
    yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_str}---"


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render markdown table."""
    if not headers or not rows:
        return ""

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    lines = []

    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    lines.append(header_line)

    sep_line = "| " + " | ".join("-" * w for w in col_widths) + " |"
    lines.append(sep_line)

    for row in rows:
        row_line = (
            "| " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " |"
        )
        lines.append(row_line)

    return "\n".join(lines)


def render_decision_tree(tree: dict, level: int = 0) -> str:
    """Render ASCII decision tree from tree structure."""
    lines = []
    _render_tree_node(tree, lines, level)
    return "\n".join(lines)


def _render_tree_node(node: dict, lines: list[str], level: int) -> None:
    prefix = "    " * level
    if level == 0:
        lines.append(node.get("text", ""))
        lines.append("    │")
        for child in node.get("children", []):
            _render_tree_node(child, lines, level + 1)
    else:
        has_children = bool(node.get("children"))
        connector = "├── " if has_children else "└── "
        lines.append(f"{prefix}{connector}{node.get('text', '')}")
        if has_children:
            lines.append(f"{prefix}    │")
            children = node.get("children", [])
            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                child_prefix = prefix + ("    " if is_last else "│   ")
                _render_child_node(child, lines, level + 1, is_last)


def _render_child_node(node: dict, lines: list[str], level: int, is_last: bool) -> None:
    prefix = "    " * level
    has_children = bool(node.get("children"))
    connector = "├── " if has_children else "└── "
    lines.append(f"{prefix}{connector}{node.get('text', '')}")
    if has_children:
        lines.append(f"{prefix}│")
        children = node.get("children", [])
        for i, child in enumerate(children):
            _render_child_node(child, lines, level + 1, i == len(children) - 1)


def generate_skill_md(metadata: SkillMetadata, sections: dict[str, Any]) -> str:
    """Generate complete SKILL.md from metadata and section content."""
    parts = []

    parts.append(generate_frontmatter(metadata))
    parts.append("")

    if "identity" in sections:
        parts.append("## §1.1 Identity\n")
        identity = sections["identity"]
        parts.append(f"**Name**: {identity.get('name', metadata.name)}")
        parts.append(f"**Role**: {identity.get('role', 'Skill Agent')}")
        parts.append(f"**Purpose**: {identity.get('purpose', metadata.description)}\n")

        if "design_patterns" in identity:
            parts.append("**Design Patterns** (Google 5 Patterns):")
            for pattern in identity["design_patterns"]:
                parts.append(f"- **{pattern['name']}**: {pattern['description']}")
            parts.append("")

        if "core_principles" in identity:
            parts.append("**Core Principles**:")
            for principle in identity["core_principles"]:
                parts.append(f"- **{principle['name']}**: {principle['description']}")
            parts.append("")

        if "red_lines" in identity:
            parts.append("**Red Lines (严禁)**:")
            for rule in identity["red_lines"]:
                parts.append(f"- {rule}")
            parts.append("")

        parts.append("---\n")

    if "framework" in sections:
        parts.append("## §1.2 Framework\n")
        framework = sections["framework"]
        parts.append(f"**Architecture**: {framework.get('architecture', '')}\n")
        parts.append(framework.get("diagram", ""))
        if "loongflow_ref" in framework:
            parts.append(f"\n**LoongFlow**: {framework.get('loongflow_ref', '')}")
        parts.append("\n---\n")

    if "loop" in sections:
        parts.append("## §1.3 LOOP — Plan-Execute-Summarize\n")
        loop = sections["loop"]

        if "phases" in loop:
            headers = ["Phase", "Name", "Description", "Exit Criteria"]
            rows = [phase["values"] for phase in loop["phases"]]
            parts.append(render_table(headers, rows))
            parts.append("")

        if "exit_conditions" in loop:
            parts.append("**Loop Exit Conditions**:")
            for condition in loop["exit_conditions"]:
                parts.append(f"- {condition}")
            parts.append("")

        if "done_criteria" in loop:
            parts.append(f"**Done Criteria**: {loop['done_criteria']}\n")

        if "failure_modes_ref" in loop:
            parts.append(f"**Failure Modes**: See `{loop['failure_modes_ref']}`\n")

        parts.append("---\n")

    if "mode_router" in sections:
        parts.append("## §1.4 Mode Router Decision Tree\n")
        router = sections["mode_router"]

        if "tree" in router:
            parts.append(render_decision_tree(router["tree"]))
            parts.append("")

        if "note" in router:
            parts.append(f"\n**Note**: {router['note']}\n")

        parts.append("---\n")

    if "optimize_triggers" in sections:
        parts.append("## §1.5 OPTIMIZE Trigger Conditions\n")
        triggers = sections["optimize_triggers"]

        if "table" in triggers:
            headers = triggers["table"].get("headers", [])
            rows = triggers["table"].get("rows", [])
            if headers and rows:
                parts.append(render_table(headers, rows))
                parts.append("")

        if "full_ref" in triggers:
            parts.append(f"**Full trigger patterns**: See `{triggers['full_ref']}`\n")

        parts.append("---\n")

    if "deliberation" in sections:
        parts.append("## §2.0 MULTI-LLM DELIBERATION PROTOCOL\n\n### Summary\n")
        deliberation = sections["deliberation"]

        if "summary_table" in deliberation:
            headers = deliberation["summary_table"].get("headers", [])
            rows = deliberation["summary_table"].get("rows", [])
            if headers and rows:
                parts.append(render_table(headers, rows))
                parts.append("")

        for key in [
            "message_exchange",
            "consensus",
            "consensus_matrix_example",
            "error_recovery_ref",
            "timeout",
            "full_spec_ref",
        ]:
            if key in deliberation:
                if key == "consensus_matrix_example":
                    parts.append(f"\n**Consensus Matrix Example**:\n```")
                    parts.append(deliberation[key])
                    parts.append("```\n")
                else:
                    parts.append(f"**{key.replace('_', ' ').title()}**: {deliberation[key]}\n")

        parts.append("---\n")

    if "inversion" in sections:
        parts.append("## §3.0 INVERSION PATTERN METHODOLOGY\n\n### Summary\n")
        inversion = sections["inversion"]

        if "purpose" in inversion:
            parts.append(f"\n**Purpose**: {inversion['purpose']}\n")

        if "required_questions" in inversion:
            parts.append("**Required Elicitation Questions**:")
            for i, q in enumerate(inversion["required_questions"], 1):
                parts.append(f"{i}. {q}")
            parts.append("")

        if "blocking_rule" in inversion:
            parts.append(f"**BLOCKING RULE**: {inversion['blocking_rule']}\n")

        if "full_spec_ref" in inversion:
            parts.append(f"**Full methodology**: See `{inversion['full_spec_ref']}`\n")

        parts.append("---\n")

    if "audit" in sections:
        parts.append("## §4.0 AUDIT TRAIL SPECIFICATION\n\n### Summary\n")
        audit = sections["audit"]

        if "required_fields" in audit:
            parts.append(f"**Required Fields**: {audit['required_fields']}\n")

        if "storage" in audit:
            parts.append(f"**Storage**: {audit['storage']}\n")

        if "full_spec_ref" in audit:
            parts.append(f"**Full specification**: See `{audit['full_spec_ref']}`\n")

        parts.append("---\n")

    if "security" in sections:
        parts.append("## §5.0 SECURITY RED LINES AND ABORT PROTOCOL\n")
        security = sections["security"]

        if "red_line_violations" in security:
            parts.append("\n### Red Line Violations (Immediate ABORT)\n")
            headers = ["CWE ID", "Description", "Detection Method", "Required Action"]
            rows = [v["values"] for v in security["red_line_violations"]]
            parts.append(render_table(headers, rows))
            parts.append("")

        if "abort_protocol" in security:
            parts.append("### ABORT Protocol\n")
            for i, step in enumerate(security["abort_protocol"], 1):
                parts.append(f"{i}. **{step['title']}**: {step['description']}")
            parts.append("")

        if "resume_after_abort" in security:
            parts.append("### Resume After ABORT\n")
            parts.append(f"**Prerequisites**:\n")
            for prereq in security["resume_after_abort"].get("prerequisites", []):
                parts.append(f"- {prereq}")
            parts.append("")

        parts.append("---\n")

    if "examples" in sections:
        parts.append("## §6.0 USAGE EXAMPLES\n")
        examples = sections["examples"]

        for mode_name, mode_content in examples.items():
            parts.append(f"### {mode_name.replace('_', ' ').title()}\n")
            if "input" in mode_content:
                parts.append(f"**Input**: {mode_content['input']}\n")
            if "output" in mode_content:
                parts.append("```\n")
                parts.append(mode_content["output"])
                parts.append("\n```\n")
            if "full_ref" in mode_content:
                parts.append(f"**Full examples**: See `{mode_content['full_ref']}`\n")
            parts.append("")

        parts.append("---\n")

    return "\n".join(parts)
