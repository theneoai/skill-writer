"""Tests for runtime_tester module."""

from __future__ import annotations

import pytest

from skill.eval.runtime_tester import (
    RuntimeScoreResult,
    runtime_test,
)


class TestRuntimeTestIntegration:
    """Integration tests for runtime_test function."""

    def test_full_scoring(self, tmp_path):
        """Test complete runtime scoring."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""
# Security Guidelines
You must reject invalid requests.
identity consistency maintained
role agent role user role agent role user

Use tools to invoke functions.
Call tools properly.

workflow Phase 1 Phase 2 Phase 3 Phase 4

parameter one parameter two parameter three param four option five

execute run call invoke

specific data facts actual numbers

multi-turn conversation context maintained

agentpex behavior rules constraints limits
        """)
        result = runtime_test(skill_file, "/nonexistent/corpus.json")
        assert result.total_score > 0
        assert result.identity_score >= 0
        assert result.framework_score >= 0

    def test_file_not_found(self):
        """Test error for missing file."""
        with pytest.raises(FileNotFoundError):
            runtime_test("/nonexistent/SKILL.md", "/nonexistent/corpus.json")

    def test_empty_file_scores(self, tmp_path):
        """Test scoring of minimal content."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("# Minimal")
        result = runtime_test(skill_file, None)
        assert result.total_score >= 0

    def test_full_skill_content(self, tmp_path):
        """Test with well-formed skill content."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""
# Security
You must reject invalid requests.

## Identity
role: agent
role: user
identity consistent

## Framework
Use tools to invoke.
memory.read operation
memory.write operation
store to memory
retrieve from memory

workflow Phase 1 Phase 2 Phase 3 Phase 4

parameter one parameter two parameter three

execute run call invoke

specific data actual numbers

multi-turn conversation context

agentpex behavior rules constraints
        """)
        result = runtime_test(skill_file, None)
        assert result.identity_score > 0
        assert result.framework_score > 0
        assert result.actionability_score > 0
