"""Tests for Evaluator Agent - Skill evaluator."""

import json
import os
import tempfile

import pytest
from unittest.mock import patch, MagicMock

from skill.agents.evaluator import (
    EvaluatorAgent,
    evaluate_file,
    evaluate_section,
    generate_suggestions,
    check_format,
    compare_versions,
)


class TestEvaluatorAgent:
    """Test suite for EvaluatorAgent."""

    def test_init(self):
        """Test evaluator agent initialization."""
        agent = EvaluatorAgent()
        assert agent is not None


class TestEvaluateFile:
    """Test suite for evaluate_file function."""

    def test_evaluate_missing_file(self):
        """Test evaluating non-existent file."""
        result = evaluate_file("/nonexistent/file.md", 0)
        assert result is not None
        assert "error" in result or result == ""


class TestEvaluateSection:
    """Test suite for evaluate_section function."""

    def test_evaluate_section_content(self):
        """Test evaluating section content."""
        content = "# Test Section\n\nThis is a test section."
        result = evaluate_section(content, 1)
        assert result is not None


class TestCheckFormat:
    """Test suite for check_format function."""

    def test_check_format_valid(self):
        """Test checking valid format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Skill\n\n## §1.1 Identity\n\nTest content")
            filepath = f.name
        try:
            result = check_format(filepath)
            assert result == "VALID"
        finally:
            os.unlink(filepath)

    def test_check_format_invalid(self):
        """Test checking invalid format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("No header or sections here")
            filepath = f.name
        try:
            result = check_format(filepath)
            assert "INVALID" in result or result == ""
        finally:
            os.unlink(filepath)


class TestCompareVersions:
    """Test suite for compare_versions function."""

    def test_compare_missing_file(self):
        """Test comparing when one file is missing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            filepath = f.name
        try:
            result = compare_versions(filepath, "/nonexistent/file.md")
            assert result is None or "error" in str(result).lower()
        finally:
            os.unlink(filepath)
