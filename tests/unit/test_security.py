"""Tests for Security Agent - OWASP AST10 audit."""

import json
import os
import tempfile

import pytest
from unittest.mock import patch, MagicMock

from skill.agents.security import (
    SecurityAgent,
    OWASP_AST10_ITEMS,
    audit_security,
    cross_validate_results,
)


class TestSecurityAgent:
    """Test suite for SecurityAgent."""

    def test_init(self):
        """Test security agent initialization."""
        agent = SecurityAgent()
        assert agent is not None


class TestOwaspAst10Items:
    """Test suite for OWASP AST10 items."""

    def test_items_count(self):
        """Test OWASP AST10 has 10 items."""
        assert len(OWASP_AST10_ITEMS) == 10

    def test_items_include_credential_scan(self):
        """Test items include Credential Scan."""
        assert "Credential Scan" in OWASP_AST10_ITEMS

    def test_items_include_security_checks(self):
        """Test items include security checks."""
        expected = [
            "Input Validation",
            "Command Injection Prevention",
            "SQL Injection Prevention",
        ]
        for item in expected:
            assert item in OWASP_AST10_ITEMS


class TestAuditSecurity:
    """Test suite for audit_security function."""

    def test_audit_missing_file(self):
        """Test auditing non-existent file."""
        result = audit_security("/nonexistent/file.md")
        assert result is not None
        assert "error" in str(result).lower() or result == ""


class TestCrossValidateResults:
    """Test suite for cross_validate_results function."""

    def test_cross_validate_matching_results(self):
        """Test cross-validation with matching results."""
        r1 = json.dumps({"status": "PASS", "severity": "NONE"})
        r2 = json.dumps({"status": "PASS", "severity": "NONE"})
        result = cross_validate_results(r1, r2, "", "test")
        assert result is not None

    def test_cross_validate_conflicting_results(self):
        """Test cross-validation with conflicting results."""
        r1 = json.dumps({"status": "PASS", "severity": "NONE"})
        r2 = json.dumps({"status": "FAIL", "severity": "P0"})
        result = cross_validate_results(r1, r2, "", "test")
        assert result is not None
