"""Tests for Creator Agent - Section generator."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from skill.agents.creator import (
    CreatorAgent,
    generate_section,
    init_skill_file,
    extract_inherited_sections,
    inherit_sections,
    get_next_section_prompt,
)


class TestCreatorAgent:
    """Test suite for CreatorAgent."""

    def test_init(self):
        """Test creator agent initialization."""
        agent = CreatorAgent()
        assert agent is not None


class TestGenerateSection:
    """Test suite for generate_section function."""

    @pytest.fixture
    def context_file(self):
        """Create a temporary context file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "user_prompt": "Create a skill for testing",
                    "current_section": 1,
                    "evaluator_feedback": "",
                },
                f,
            )
            filepath = f.name
        yield filepath
        os.unlink(filepath)

    @patch("skill.agents.creator.call_llm")
    def test_generate_section_success(self, mock_call_llm, context_file):
        """Test successful section generation."""
        mock_call_llm.return_value = {
            "status": "success",
            "content": "# Test Section\n\nThis is a test.",
        }
        result = generate_section(context_file)
        assert result is not None
        assert "content" in result

    @patch("skill.agents.creator.call_llm")
    def test_generate_section_both_llms_fail(self, mock_call_llm, context_file):
        """Test when both LLM calls fail."""
        mock_call_llm.return_value = {"status": "error", "content": ""}
        result = generate_section(context_file)
        assert result is None or "content" not in result


class TestInitSkillFile:
    """Test suite for init_skill_file function."""

    def test_init_skill_file(self):
        """Test skill file initialization."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            filepath = f.name
        os.unlink(filepath)

        try:
            init_skill_file(filepath, "TestSkill")
            with open(filepath, "r") as f:
                content = f.read()
            assert "# TestSkill" in content
            assert "Version" in content
            assert "DRAFT" in content
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestExtractInheritedSections:
    """Test suite for extract_inherited_sections function."""

    def test_extract_from_missing_file(self):
        """Test extracting from non-existent file."""
        result = extract_inherited_sections("/nonexistent/file.md")
        assert result is None or result == ""


class TestGetNextSectionPrompt:
    """Test suite for get_next_section_prompt function."""

    def test_section_1_prompt(self):
        """Test section 1 prompt."""
        result = get_next_section_prompt(1, "default")
        assert "§1.1" in result or "Identity" in result

    def test_section_2_prompt(self):
        """Test section 2 prompt."""
        result = get_next_section_prompt(2, "default")
        assert "§1.2" in result or "Framework" in result

    def test_unknown_section_prompt(self):
        """Test unknown section prompt."""
        result = get_next_section_prompt(99, "default")
        assert "Continue" in result or result is not None
