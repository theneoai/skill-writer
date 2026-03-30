"""Tests for summarizer module."""

from __future__ import annotations

import json
import pytest

from skill.engine.summarizer import Summarizer, SummaryResult


class TestSummaryResult:
    """Test suite for SummaryResult dataclass."""

    def test_summary_result_creation(self):
        """Test SummaryResult stores all fields."""
        result = SummaryResult(
            priority_issues=[{"issue": "test", "section": "test", "severity": "high"}],
            key_findings=["finding1", "finding2"],
            improvement_plan=[
                {"action": "test", "section": "test", "rationale": "test"}
            ],
            expected_impact="test impact",
        )
        assert len(result.priority_issues) == 1
        assert len(result.key_findings) == 2
        assert len(result.improvement_plan) == 1
        assert result.expected_impact == "test impact"

    def test_summary_result_to_dict(self):
        """Test SummaryResult converts to dict."""
        result = SummaryResult(
            priority_issues=[],
            key_findings=[],
            improvement_plan=[],
            expected_impact="test",
        )
        data = result.to_dict()
        assert "priority_issues" in data
        assert "key_findings" in data
        assert "improvement_plan" in data
        assert "expected_impact" in data


class MockLLMCaller:
    """Mock LLM caller for testing."""

    def __init__(self, response: str | None = None, should_fail: bool = False):
        self.response = response
        self.should_fail = should_fail
        self.call_count = 0
        self.last_system_prompt = None
        self.last_user_prompt = None

    def __call__(self, system_prompt: str, user_prompt: str, model: str) -> str:
        self.call_count += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        if self.should_fail:
            raise RuntimeError("LLM call failed")
        return (
            self.response
            or '{"priority_issues": [], "key_findings": [], "improvement_plan": [], "expected_impact": "default"}'
        )


class TestSummarizer:
    """Test suite for Summarizer class."""

    def test_initialization(self):
        """Test Summarizer initializes correctly."""
        summarizer = Summarizer()
        assert summarizer.system_prompt is not None

    def test_summarize_success(self):
        """Test successful summarization."""
        mock_response = json.dumps(
            {
                "priority_issues": [
                    {"issue": "slow", "section": "instructions", "severity": "high"}
                ],
                "key_findings": ["findings1"],
                "improvement_plan": [
                    {
                        "action": "optimize",
                        "section": "instructions",
                        "rationale": "speed",
                    }
                ],
                "expected_impact": "faster execution",
            }
        )
        mock_caller = MockLLMCaller(response=mock_response)
        summarizer = Summarizer(llm_caller=mock_caller)

        result = summarizer.summarize("analysis content", "test_skill")

        assert len(result.priority_issues) == 1
        assert result.priority_issues[0]["issue"] == "slow"
        assert mock_caller.call_count == 1

    def test_summarize_llm_failure(self):
        """Test summarization handles LLM failure."""
        mock_caller = MockLLMCaller(should_fail=True)
        summarizer = Summarizer(llm_caller=mock_caller)

        result = summarizer.summarize("analysis content", "test_skill")
        assert result is None

    def test_summarize_for_human_success(self):
        """Test human-readable summarization."""
        mock_response = "This is a summary for humans."
        mock_caller = MockLLMCaller(response=mock_response)
        summarizer = Summarizer(llm_caller=mock_caller)

        result = summarizer.summarize_for_human("analysis content", "test_skill")
        assert result == mock_response

    def test_summarize_for_human_failure(self):
        """Test human summarization handles LLM failure."""
        mock_caller = MockLLMCaller(should_fail=True)
        summarizer = Summarizer(llm_caller=mock_caller)

        result = summarizer.summarize_for_human("analysis content", "test_skill")
        assert result is None

    def test_extract_key_insights_success(self):
        """Test extracting key insights."""
        mock_response = json.dumps(["insight1", "insight2", "insight3"])
        mock_caller = MockLLMCaller(response=mock_response)
        summarizer = Summarizer(llm_caller=mock_caller)

        insights = summarizer.extract_key_insights("analysis content")
        assert len(insights) == 3
        assert insights[0] == "insight1"

    def test_extract_key_insights_failure(self):
        """Test extract insights handles LLM failure."""
        mock_caller = MockLLMCaller(should_fail=True)
        summarizer = Summarizer(llm_caller=mock_caller)

        insights = summarizer.extract_key_insights("analysis content")
        assert insights is None

    def test_prompt_includes_skill_name(self):
        """Test that prompts include skill name."""
        mock_response = "{}"
        mock_caller = MockLLMCaller(response=mock_response)
        summarizer = Summarizer(llm_caller=mock_caller)

        summarizer.summarize("analysis", "my_skill")

        assert "my_skill" in mock_caller.last_user_prompt

    def test_summarize_parses_json_response(self):
        """Test that summarize correctly parses JSON LLM response."""
        mock_response = json.dumps(
            {
                "priority_issues": [
                    {"issue": "test", "section": "sec", "severity": "medium"}
                ],
                "key_findings": ["f1", "f2"],
                "improvement_plan": [{"action": "a", "section": "s", "rationale": "r"}],
                "expected_impact": "impact",
            }
        )
        mock_caller = MockLLMCaller(response=mock_response)
        summarizer = Summarizer(llm_caller=mock_caller)

        result = summarizer.summarize("analysis", "skill")

        assert isinstance(result, SummaryResult)
        assert len(result.key_findings) == 2
