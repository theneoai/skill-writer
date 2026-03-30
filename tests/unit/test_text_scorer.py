"""Tests for text_scorer module."""

from __future__ import annotations

import pytest

from skill.eval.text_scorer import (
    TextScoreResult,
    text_score,
    score_system_prompt,
    score_domain_knowledge,
    score_workflow,
    score_error_handling,
    score_examples,
    score_metadata,
)


class TestScoreSystemPrompt:
    """Test suite for score_system_prompt function."""

    def test_finds_section_markers(self):
        """Test detection of §1.1, §1.2, §1.3 section markers."""
        content = """
# §1.1 Identity
Content for identity
# §1.2 Framework
Content for framework
# §1.3 Thinking
Content for thinking
"""
        result = score_system_prompt(content)
        assert result == 60

    def test_finds_must_never_patterns(self):
        """Test detection of must/never/do-not patterns."""
        content = "You must never do this, always follow these rules"
        result = score_system_prompt(content)
        assert result == 10


class TestScoreDomainKnowledge:
    """Test suite for score_domain_knowledge function."""

    def test_quantitative_count(self):
        """Test scoring based on quantitative elements."""
        content = """
        95% accuracy
        10x faster
        $100 cost
        3.14 value
        2000ms latency
        1TB storage
        99.9% uptime
        """
        result = score_domain_knowledge(content)
        assert result >= 10

    def test_framework_count(self):
        """Test scoring based on framework terminology."""
        content = """
        ReAct agent
        CoT prompting
        ToT reasoning
        RAG retrieval
        Chain of thought
        """
        result = score_domain_knowledge(content)
        assert result >= 10


class TestScoreWorkflow:
    """Test suite for score_workflow function."""

    def test_workflow_keywords(self):
        """Test detection of workflow-related keywords."""
        content = """
        Phase 1: Planning
        Phase 2: Execution
        Phase 3: Validation
        Phase 4: Deployment
        Done successfully
        Fail gracefully
        """
        result = score_workflow(content)
        assert result > 0

    def test_decision_keywords(self):
        """Test detection of decision-related keywords."""
        content = "if condition then action else fallback"
        result = score_workflow(content)
        assert result >= 5


class TestScoreErrorHandling:
    """Test suite for score_error_handling function."""

    def test_failure_count(self):
        """Test scoring based on failure/error mentions."""
        content = """
        error handling
        failure recovery
        exception cases
        problem detection
        fail gracefully
        retry on failure
        """
        result = score_error_handling(content)
        assert result >= 20

    def test_recovery_patterns(self):
        """Test scoring based on recovery patterns."""
        content = """
        retry on failure
        fallback to backup
        circuit breaker
        recovery plan
        """
        result = score_error_handling(content)
        assert result >= 20


class TestScoreExamples:
    """Test suite for score_examples function."""

    def test_example_count(self):
        """Test scoring based on example mentions."""
        content = """
        for example, consider
        another example
        case study
        scenario
        """
        result = score_examples(content)
        assert result >= 12


class TestScoreMetadata:
    """Test suite for score_metadata function."""

    def test_metadata_fields(self):
        """Test scoring based on metadata fields."""
        content = """
---
name: test-skill
description: A test skill
license: MIT
version: 1.0.0
author: Test Author
---
"""
        result = score_metadata(content)
        assert result >= 25


class TestTextScore:
    """Test suite for text_score main function."""

    def test_full_scoring(self, tmp_path):
        """Test complete text scoring."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill
license: MIT
version: 1.0.0
author: Test
tags:
  - test
---

# §1.1 Identity
You must never expose secrets.

# §1.2 Framework
Use ReAct pattern for reasoning.

# §1.3 Thinking
Think step by step.

## Workflow
Phase 1: Plan
Phase 2: Execute
Done successfully

## Error Handling
Handle failure gracefully with retry.

## Examples
For example, consider this case.
""")
        result = text_score(skill_file)
        assert result.total_score > 0
        assert result.system_prompt_score > 0

    def test_file_not_found(self):
        """Test error for missing file."""
        with pytest.raises(FileNotFoundError):
            text_score("/nonexistent/SKILL.md")
