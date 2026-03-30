"""Tests for semantic_coherence module."""

import pytest
from skill.eval.semantic_coherence import (
    SemanticCoherenceResult,
    extract_section,
    extract_all_sections,
    jaccard_similarity,
    mean_pairwise_similarity,
    detect_identity_drift,
    semantic_coherence_score,
)


class TestExtractSection:
    def test_extracts_identity_section_by_paragraph_number(self):
        content = """# Skill Title

## 1.1 Identity
This is the identity section content.
It describes what the skill does.

## 1.2 Framework
This is the framework section.
"""
        result = extract_section(content, "§1\\.1|1\\.1 Identity|1\\.1\\s")
        assert "identity section" in result.lower()
        assert "framework" not in result.lower()

    def test_extracts_framework_section(self):
        content = """# Skill

## 1.2 Framework
The framework section describes the tooling.
Uses Python and fastapi.
"""
        result = extract_section(content, "§1\\.2|1\\.2 Framework|1\\.2\\s")
        assert "framework" in result.lower()
        assert "tooling" in result.lower()

    def test_extracts_workflow_section(self):
        content = """# Skill

## 3.1 Workflow
First step is to initialize.
Then process the data.
"""
        result = extract_section(content, "§3\\.|3\\.[0-9] |[Ww]orkflow")
        assert "workflow" in result.lower() or "initialize" in result.lower()

    def test_extracts_examples_section(self):
        content = """# Skill

## 4.1 Examples
Here is an example of usage.
Run the command like this.
"""
        result = extract_section(content, "§4\\.|4\\.[0-9] |[Ee]xample")
        assert "example" in result.lower() or "usage" in result.lower()

    def test_returns_empty_when_pattern_not_found(self):
        content = "# Just a title\n\nSome text without headers."
        result = extract_section(content, "§99\\.99|NonExistent")
        assert result == ""

    def test_limits_to_50_lines(self):
        content = "# Skill\n\n## 1.1 Identity\n" + "\n".join(
            [f"Line {i}" for i in range(100)]
        )
        result = extract_section(content, "§1\\.1|1\\.1 Identity|1\\.1\\s")
        lines = result.strip().split("\n")
        assert len(lines) <= 50


class TestExtractAllSections:
    def test_extracts_all_four_sections(self):
        content = """# Test Skill

## 1.1 Identity
This skill is about Python testing.

## 1.2 Framework
Uses pytest and unittest.

## 3.1 Workflow
First write tests, then write code.

## 4.1 Examples
Example: test_example()
"""
        sections = extract_all_sections(content)
        assert len(sections["identity"]) > 0
        assert len(sections["framework"]) > 0
        assert len(sections["workflow"]) > 0
        assert len(sections["examples"]) > 0

    def test_missing_sections_return_empty_strings(self):
        content = """# Skill

## 1.1 Identity
Only identity section present.
"""
        sections = extract_all_sections(content)
        assert sections["identity"] != ""
        assert sections["framework"] == ""
        assert sections["workflow"] == ""
        assert sections["examples"] == ""


class TestJaccardSimilarity:
    def test_identical_texts(self):
        text = "python programming language software development"
        result = jaccard_similarity(text, text)
        assert result == 1.0

    def test_completely_different_texts(self):
        text_a = "cat dog bird fish"
        text_b = "car vehicle truck automobile"
        result = jaccard_similarity(text_a, text_b)
        assert result == 0.0

    def test_partial_overlap(self):
        text_a = "python programming language development"
        text_b = "python software development engineering"
        result = jaccard_similarity(text_a, text_b)
        assert 0.2 < result < 0.6

    def test_filters_short_words(self):
        text_a = "the quick brown fox"
        text_b = "the slow green turtle"
        result = jaccard_similarity(text_a, text_b)
        assert result < 1.0

    def test_empty_text_returns_05(self):
        result = jaccard_similarity("", "some text")
        assert result == 0.5


class TestMeanPairwiseSimilarity:
    def test_single_text_returns_10(self):
        texts = ["only one text present"]
        result = mean_pairwise_similarity(texts)
        assert result == 1.0

    def test_two_similar_texts(self):
        texts = [
            "python programming language",
            "python programming language software",
        ]
        result = mean_pairwise_similarity(texts)
        assert result > 0.7

    def test_two_different_texts(self):
        texts = [
            "cat dog bird fish",
            "car truck vehicle automobile",
        ]
        result = mean_pairwise_similarity(texts)
        assert result < 0.3

    def test_three_texts_computes_all_pairs(self):
        texts = [
            "python code programming",
            "python software development",
            "python testing unittest",
        ]
        result = mean_pairwise_similarity(texts)
        assert 0.0 <= result <= 1.0


class TestDetectIdentityDrift:
    def test_coherent_identity_and_examples(self):
        identity = "python skill for web development using fastapi"
        examples = "example of fastapi route and python web handler"
        result = detect_identity_drift(identity, examples)
        assert "COHERENT" in result

    def test_drift_detected(self):
        identity = "python skill for cooking recipes"
        examples = "example of automotive repair and car maintenance"
        result = detect_identity_drift(identity, examples)
        assert "DRIFT" in result

    def test_empty_identity_returns_unknown(self):
        result = detect_identity_drift("", "some examples")
        assert "UNKNOWN" in result

    def test_empty_examples_returns_unknown(self):
        result = detect_identity_drift("some identity", "")
        assert "UNKNOWN" in result


class TestSemanticCoherenceScore:
    def test_file_not_found_returns_zero_score(self):
        result = semantic_coherence_score("/nonexistent/file.md")
        assert result.semantic_score == 0
        assert result.sections_analyzed == 0

    def test_single_section_returns_zero(self):
        content = """# Skill

## 1.1 Identity
Only identity section here.
"""
        result = semantic_coherence_score(content)
        assert result.semantic_score == 0
        assert result.cohesion_score == 0

    def test_processes_all_sections(self):
        content = """# Python Web Skill

## 1.1 Identity
A skill for building Python web applications using the FastAPI framework.
Learn how to develop scalable web services with Python programming.

## 1.2 Framework
FastAPI framework for Python web development.
Use FastAPI to create REST APIs and web services.

## 3.1 Workflow
Install FastAPI, create routes, run the development server.
Build web applications with Python using FastAPI.

## 4.1 Examples
Example: from fastapi import FastAPI
app = FastAPI()
"""
        result = semantic_coherence_score(content)
        assert result.sections_analyzed == 4
        assert result.cohesion_score > 0
        assert result.semantic_score >= 0

    def test_high_vocabulary_overlap_gets_higher_score(self):
        identity_text = "python programming language software development framework"
        framework_text = "python programming language development framework pytest"
        workflow_text = "python programming development testing framework"
        examples_text = "python programming example testing development"

        sections = {
            "identity": identity_text,
            "framework": framework_text,
            "workflow": workflow_text,
            "examples": examples_text,
        }

        texts = list(sections.values())
        cohesion = mean_pairwise_similarity(texts)

        assert cohesion > 0.5

    def test_cohesion_below_055_returns_zero(self):
        content = """# Cooking Skill

## 1.1 Identity
Python skill for data science and machine learning.

## 1.2 Framework
PyTorch and TensorFlow for neural networks.

## 3.1 Workflow
Train models, evaluate metrics.

## 4.1 Examples
Recipe: mix flour and water, bake bread.
"""
        result = semantic_coherence_score(content)
        assert result.cohesion_score < 0.55
        assert result.semantic_score == 0
