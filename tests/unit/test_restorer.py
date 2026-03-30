"""Tests for Restorer Agent - Skill repair."""

import json
import os
import tempfile

import pytest
from unittest.mock import patch, MagicMock

from skill.agents.restorer import (
    RestorerAgent,
    restore_skill,
    multi_llm_diagnose,
    cross_validate_issues,
    multi_llm_propose_fixes,
    cross_validate_fixes,
    apply_fixes,
)


class TestRestorerAgent:
    """Test suite for RestorerAgent."""

    def test_init(self):
        """Test restorer agent initialization."""
        agent = RestorerAgent()
        assert agent is not None


class TestRestoreSkill:
    """Test suite for restore_skill function."""

    def test_restore_missing_file(self):
        """Test restoring non-existent file."""
        result = restore_skill("/nonexistent/file.md")
        assert result is not None
        assert "error" in str(result).lower() or result == ""


class TestMultiLlmDiagnose:
    """Test suite for multi_llm_diagnose function."""

    @patch("skill.agents.restorer.call_llm")
    def test_diagnose_with_content(self, mock_call_llm):
        """Test diagnosis with content."""
        mock_call_llm.return_value = {
            "status": "success",
            "content": json.dumps({"issues": [], "overall_health": "GOOD"}),
        }
        content = "# Test Skill\n\nTest content."
        result = multi_llm_diagnose(content)
        assert result is not None
        assert "issues" in result or "llm_diagnoses" in result


class TestCrossValidateIssues:
    """Test suite for cross_validate_issues function."""

    def test_cross_validate_empty_issues(self):
        """Test cross-validation with empty issues."""
        result = cross_validate_issues("[]", "[]", "[]")
        assert result is not None
        assert "issues" in result


class TestApplyFixes:
    """Test suite for apply_fixes function."""

    def test_apply_fixes_missing_file(self):
        """Test applying fixes to non-existent file."""
        fixes = json.dumps({"fixes": []})
        result = apply_fixes("/nonexistent/file.md", fixes)
        assert result is False or result is None
