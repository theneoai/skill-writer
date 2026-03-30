"""Tests for SKILL.md markdown generator."""

import pytest
from skill.md_generator import (
    SkillMetadata,
    generate_frontmatter,
    render_table,
    render_decision_tree,
    generate_skill_md,
)


class TestSkillMetadata:
    def test_create_metadata_with_required_fields(self):
        metadata = SkillMetadata(
            name="test-skill",
            description="A test skill for unit testing",
        )
        assert metadata.name == "test-skill"
        assert metadata.description == "A test skill for unit testing"
        assert metadata.license == "MIT"
        assert metadata.version == "0.1.0"

    def test_create_metadata_with_all_fields(self):
        metadata = SkillMetadata(
            name="full-skill",
            description="A skill with all fields populated",
            license="Apache-2.0",
            author="Test Author <test@example.com>",
            version="2.0.0",
            tags=["test", "unit", "example"],
            type="agent",
            triggers=["CREATE", "EVALUATE"],
        )
        assert metadata.license == "Apache-2.0"
        assert metadata.author == "Test Author <test@example.com>"
        assert metadata.version == "2.0.0"
        assert metadata.tags == ["test", "unit", "example"]
        assert metadata.type == "agent"
        assert metadata.triggers == ["CREATE", "EVALUATE"]


class TestGenerateFrontmatter:
    def test_frontmatter_basic(self):
        metadata = SkillMetadata(
            name="test-skill",
            description="A simple test",
        )
        frontmatter = generate_frontmatter(metadata)
        assert frontmatter.startswith("---")
        assert "name: test-skill" in frontmatter
        assert "description: A simple test" in frontmatter
        assert frontmatter.endswith("---")

    def test_frontmatter_with_tags(self):
        metadata = SkillMetadata(
            name="tagged-skill",
            description="A skill with tags",
            tags=["alpha", "beta", "gamma"],
        )
        frontmatter = generate_frontmatter(metadata)
        assert "tags:" in frontmatter
        assert "- alpha" in frontmatter
        assert "- beta" in frontmatter
        assert "- gamma" in frontmatter


class TestRenderTable:
    def test_render_table_basic(self):
        headers = ["Name", "Age", "City"]
        rows = [
            ["Alice", "30", "NYC"],
            ["Bob", "25", "LA"],
        ]
        table = render_table(headers, rows)
        assert "| Name" in table
        assert "| Age" in table
        assert "| City" in table
        assert "| Alice | 30  | NYC  |" in table
        assert "| Bob   | 25  | LA   |" in table
        assert "---" in table

    def test_render_table_empty_headers(self):
        table = render_table([], [["a", "b"]])
        assert table == ""

    def test_render_table_empty_rows(self):
        table = render_table(["A", "B"], [])
        assert table == ""

    def test_render_table_varying_column_widths(self):
        headers = ["Short", "Very Long Header Name"]
        rows = [["A", "B"]]
        table = render_table(headers, rows)
        assert "| Short" in table


class TestRenderDecisionTree:
    def test_render_decision_tree_simple(self):
        tree = {
            "text": "Start",
            "children": [
                {"text": "Option A"},
                {"text": "Option B"},
            ],
        }
        result = render_decision_tree(tree)
        assert "Start" in result
        assert "Option A" in result
        assert "Option B" in result

    def test_render_decision_tree_nested(self):
        tree = {
            "text": "Root",
            "children": [
                {
                    "text": "Branch 1",
                    "children": [
                        {"text": "Leaf 1.1"},
                        {"text": "Leaf 1.2"},
                    ],
                },
                {"text": "Branch 2"},
            ],
        }
        result = render_decision_tree(tree)
        assert "Root" in result
        assert "Branch 1" in result
        assert "Leaf 1.1" in result


class TestGenerateSkillMd:
    def test_generate_skill_md_identity_section(self):
        metadata = SkillMetadata(
            name="identity-test",
            description="Testing identity section generation",
        )
        sections = {
            "identity": {
                "name": "identity-test",
                "role": "Test Role",
                "purpose": "Testing identity generation",
                "design_patterns": [
                    {"name": "Pattern A", "description": "Description A"},
                    {"name": "Pattern B", "description": "Description B"},
                ],
                "core_principles": [
                    {"name": "Principle A", "description": "Principle description A"},
                ],
                "red_lines": [
                    "No hardcoding",
                    "No injection",
                ],
            }
        }
        result = generate_skill_md(metadata, sections)
        assert "§1.1 Identity" in result
        assert "**Name**: identity-test" in result
        assert "**Role**: Test Role" in result
        assert "Pattern A" in result
        assert "Principle A" in result
        assert "No hardcoding" in result

    def test_generate_skill_md_table_in_loop(self):
        metadata = SkillMetadata(
            name="loop-test",
            description="Testing loop section with table",
        )
        sections = {
            "loop": {
                "phases": [
                    {"values": ["1", "PARSE", "Parse input", "Keywords extracted"]},
                    {"values": ["2", "ROUTE", "Route mode", "Mode identified"]},
                ],
                "exit_conditions": ["SUCCESS", "HUMAN_REVIEW"],
                "done_criteria": "All phases complete",
            }
        }
        result = generate_skill_md(metadata, sections)
        assert "§1.3 LOOP" in result
        assert "| Phase | Name  | Description | Exit Criteria      |" in result
        assert "| 1     | PARSE | Parse input | Keywords extracted |" in result
        assert "SUCCESS" in result

    def test_generate_skill_md_mode_router_tree(self):
        metadata = SkillMetadata(
            name="router-test",
            description="Testing mode router with decision tree",
        )
        sections = {
            "mode_router": {
                "tree": {
                    "text": "User Input",
                    "children": [
                        {"text": "CREATE keywords"},
                        {"text": "EVALUATE keywords"},
                    ],
                },
                "note": "confidence >= 0.85 → auto-route",
            }
        }
        result = generate_skill_md(metadata, sections)
        assert "§1.4 Mode Router Decision Tree" in result
        assert "User Input" in result
        assert "CREATE keywords" in result

    def test_generate_skill_md_optimize_triggers(self):
        metadata = SkillMetadata(
            name="trigger-test",
            description="Testing OPTIMIZE triggers",
        )
        sections = {
            "optimize_triggers": {
                "table": {
                    "headers": ["Trigger Source", "Threshold", "Action"],
                    "rows": [
                        ["F1 Score", "< 0.90", "Auto-flag for refactor"],
                        ["MRR Score", "< 0.85", "Auto-flag for refactor"],
                    ],
                },
                "full_ref": "refs/triggers.md",
            }
        }
        result = generate_skill_md(metadata, sections)
        assert "§1.5 OPTIMIZE Trigger Conditions" in result
        assert "F1 Score" in result
        assert "refs/triggers.md" in result

    def test_generate_skill_md_complete_sections(self):
        metadata = SkillMetadata(
            name="complete-test",
            description="Testing all sections",
            version="1.0.0",
            tags=["test"],
        )
        sections = {
            "identity": {
                "name": "complete-test",
                "role": "Test",
                "purpose": "Full generation test",
                "design_patterns": [],
                "core_principles": [],
                "red_lines": [],
            },
            "framework": {
                "architecture": "Test Architecture",
                "diagram": "User → Router",
            },
            "loop": {
                "phases": [
                    {"values": ["1", "STEP", "Desc", "Exit"]},
                ],
                "exit_conditions": [],
                "done_criteria": "Done",
            },
            "mode_router": {
                "tree": {"text": "Start", "children": []},
            },
            "optimize_triggers": {
                "table": {"headers": [], "rows": []},
            },
        }
        result = generate_skill_md(metadata, sections)
        assert "---" in result
        assert "§1.1 Identity" in result
        assert "§1.2 Framework" in result
        assert "§1.3 LOOP" in result
        assert "§1.4 Mode Router Decision Tree" in result
        assert "§1.5 OPTIMIZE Trigger Conditions" in result
