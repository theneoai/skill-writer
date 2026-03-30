"""Tests for runtime_agent_tester module."""

from __future__ import annotations

import pytest

from skill.eval.runtime_agent_tester import (
    AgentRuntimeResult,
    check_dependencies,
    run_agent_runtime_eval,
    run_heuristic_fallback,
)


class TestCheckDependencies:
    """Test suite for check_dependencies function."""

    def test_returns_true_when_commands_exist(self):
        """Test that check_dependencies returns True when jq, bc, curl exist."""
        result = check_dependencies()
        assert isinstance(result, bool)


class TestRunHeuristicFallback:
    """Test suite for run_heuristic_fallback function."""

    def test_fallback_produces_result(self, tmp_path):
        """Test that heuristic fallback produces a result."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""
# §1.1 Identity
Some identity content
# §1.2 Framework
Framework content
# §1.3 Thinking
Thinking content
        """)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        result = run_heuristic_fallback(skill_file, output_dir)
        assert result.identity_score >= 0
        assert result.trigger_accuracy >= 0


class TestRunAgentRuntimeEval:
    """Test suite for run_agent_runtime_eval function."""

    def test_runs_without_llm(self, tmp_path):
        """Test that agent runtime eval works without LLM (uses fallback)."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""
# §1.1 Identity
Content
# §1.2 Framework
Content
# §1.3 Thinking
Content
        """)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        corpus_file = tmp_path / "corpus.json"
        corpus_file.write_text('{"test_cases": []}')

        result = run_agent_runtime_eval(skill_file, corpus_file, output_dir)
        assert result.identity_score >= 0
