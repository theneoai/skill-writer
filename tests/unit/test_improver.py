"""Tests for improver module."""

from __future__ import annotations

import json
import pytest

from skill.engine.improver import Improver, ImprovementResult


class TestImprovementResult:
    """Test suite for ImprovementResult dataclass."""

    def test_improvement_result_creation(self):
        """Test ImprovementResult stores content."""
        result = ImprovementResult(content="# Improved Skill")
        assert result.content == "# Improved Skill"

    def test_improvement_result_to_dict(self):
        """Test ImprovementResult converts to dict."""
        result = ImprovementResult(content="# Test")
        data = result.to_dict()
        assert data["content"] == "# Test"


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
        return self.response or '{"content": "# Improved"}'


class TestImprover:
    """Test suite for Improver class."""

    def test_initialization(self):
        """Test Improver initializes correctly."""
        improver = Improver()
        assert improver.system_prompt is not None
        assert "improvement" in improver.system_prompt.lower()

    def test_generate_success(self, tmp_path):
        """Test successful improvement generation."""
        mock_response = json.dumps({"content": "# Improved Skill\n\nNew content."})
        mock_caller = MockLLMCaller(response=mock_response)
        improver = Improver(llm_caller=mock_caller)

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original Skill")

        result = improver.generate("improvement summary", skill_file)

        assert result is not None
        assert result.content == "# Improved Skill\n\nNew content."
        assert mock_caller.call_count == 1

    def test_generate_llm_failure(self, tmp_path):
        """Test generation handles LLM failure."""
        mock_caller = MockLLMCaller(should_fail=True)
        improver = Improver(llm_caller=mock_caller)

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        result = improver.generate("summary", skill_file)
        assert result is None

    def test_generate_file_not_found(self, tmp_path):
        """Test generate handles missing file."""
        improver = Improver()
        skill_file = tmp_path / "nonexistent.md"

        result = improver.generate("summary", skill_file)
        assert result is None

    def test_generate_prompt_includes_content(self, tmp_path):
        """Test prompt includes skill file content."""
        mock_response = '{"content": "# Improved"}'
        mock_caller = MockLLMCaller(response=mock_response)
        improver = Improver(llm_caller=mock_caller)

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original Content")

        improver.generate("summary", skill_file)

        assert "# Original Content" in mock_caller.last_user_prompt
        assert "summary" in mock_caller.last_user_prompt

    def test_generate_targeted_success(self, tmp_path):
        """Test targeted improvement generation."""
        mock_response = json.dumps({"content": "# Improved with targeted change"})
        mock_caller = MockLLMCaller(response=mock_response)
        improver = Improver(llm_caller=mock_caller)

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        result = improver.generate_targeted(
            skill_file, "instructions", "make it better"
        )

        assert result is not None
        assert (
            "targeted" in result.content.lower() or "improved" in result.content.lower()
        )
        assert mock_caller.call_count == 1

    def test_generate_targeted_includes_section(self, tmp_path):
        """Test targeted prompt includes section info."""
        mock_response = '{"content": "# Improved"}'
        mock_caller = MockLLMCaller(response=mock_response)
        improver = Improver(llm_caller=mock_caller)

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        improver.generate_targeted(skill_file, "instructions", "guide")

        assert "instructions" in mock_caller.last_user_prompt
        assert "guide" in mock_caller.last_user_prompt

    def test_generate_targeted_file_not_found(self, tmp_path):
        """Test targeted generation handles missing file."""
        improver = Improver()
        skill_file = tmp_path / "nonexistent.md"

        result = improver.generate_targeted(skill_file, "section", "guide")
        assert result is None

    def test_validate_improvement_success(self, tmp_path):
        """Test validation returns scores."""
        improver = Improver()
        improver.evaluator = lambda f, mode="fast": {"total_score": 85}

        original = tmp_path / "original.md"
        original.write_text("# Original")

        improved = tmp_path / "improved.md"
        improved.write_text("# Improved")

        result = improver.validate_improvement(original, improved)

        assert result is not None
        assert "original_score" in result
        assert "improved_score" in result
        assert "delta" in result

    def test_validate_improvement_no_change(self, tmp_path):
        """Test validation with no score change."""
        improver = Improver()
        improver.evaluator = lambda f, mode="fast": {"total_score": 80}

        original = tmp_path / "original.md"
        original.write_text("# Same")

        improved = tmp_path / "improved.md"
        improved.write_text("# Same")

        result = improver.validate_improvement(original, improved)

        assert result["delta"] == 0

    def test_validate_improvement_positive_delta(self, tmp_path):
        """Test validation with positive delta."""
        improver = Improver()
        improver.evaluator = lambda f, mode="fast": {
            "total_score": 90 if "Improved" in f.read_text() else 80
        }

        original = tmp_path / "original.md"
        original.write_text("# Original")

        improved = tmp_path / "improved.md"
        improved.write_text("# Improved")

        result = improver.validate_improvement(original, improved)

        assert result["delta"] == 10

    def test_apply_with_validation_positive_delta(self, tmp_path):
        """Test applying improvement when score improves."""
        mock_response = json.dumps({"content": "# Improved Score"})
        mock_caller = MockLLMCaller(response=mock_response)
        improver = Improver(llm_caller=mock_caller)
        improver.evaluator = lambda f, mode="fast": {
            "total_score": 90 if "Improved" in f.read_text() else 80
        }

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        result = improver.apply_with_validation(skill_file, mock_response)

        assert result is not None
        assert skill_file.read_text() == "# Improved Score"

    def test_apply_with_validation_negative_delta(self, tmp_path):
        """Test improvement rejected when score decreases."""
        mock_response = json.dumps({"content": "# Worse Score"})
        mock_caller = MockLLMCaller(response=mock_response)
        improver = Improver(llm_caller=mock_caller)
        improver.evaluator = lambda f, mode="fast": {
            "total_score": 70 if "Worse" in f.read_text() else 80
        }

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")
        original_content = skill_file.read_text()

        result = improver.apply_with_validation(skill_file, mock_response)

        assert result is not None
        assert skill_file.read_text() == original_content

    def test_apply_with_validation_invalid_content(self, tmp_path):
        """Test apply with invalid improvement content."""
        improver = Improver()

        skill_file = tmp_path / "test.md"
        skill_file.write_text("# Original")

        result = improver.apply_with_validation(skill_file, '{"invalid": true}')
        assert result is None
