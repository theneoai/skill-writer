"""Tests for dimension analyzer module."""

from __future__ import annotations

import json

import pytest


class TestAnalyzeDimensions:
    """Test suite for analyze_dimensions."""

    def test_identifies_weak_dimensions(self):
        """Test that weak dimensions are identified."""
        from skill.eval.dimension_analyzer import analyze_dimensions

        dimensions = {
            "system_prompt": 45,
            "domain_knowledge": 60,
            "workflow": 50,
        }
        result = analyze_dimensions(json.dumps(dimensions))

        assert "weak_dimensions" in result
        assert len(result["weak_dimensions"]) > 0

    def test_ignores_strong_dimensions(self):
        """Test that dimensions above threshold are not included."""
        from skill.eval.dimension_analyzer import analyze_dimensions

        dimensions = {
            "system_prompt": 70,
            "domain_knowledge": 70,
        }
        result = analyze_dimensions(json.dumps(dimensions))

        assert len(result["weak_dimensions"]) == 0

    def test_sorts_by_score(self):
        """Test that weak dimensions are sorted by score."""
        from skill.eval.dimension_analyzer import analyze_dimensions

        dimensions = {
            "system_prompt": 40,
            "domain_knowledge": 50,
            "workflow": 30,
        }
        result = analyze_dimensions(json.dumps(dimensions))

        weak_dims = result["weak_dimensions"]
        assert weak_dims[0]["dimension"] == "workflow"  # lowest score first
        assert weak_dims[-1]["dimension"] == "domain_knowledge"  # highest among weak


class TestGetRecommendations:
    """Test suite for get_recommendations."""

    def test_returns_recommendation(self):
        """Test that recommendations are returned for weak dimensions."""
        from skill.eval.dimension_analyzer import get_recommendation

        rec = get_recommendation("system_prompt")
        assert isinstance(rec, str)
        assert len(rec) > 0

    def test_unknown_dimension_default(self):
        """Test default recommendation for unknown dimensions."""
        from skill.eval.dimension_analyzer import get_recommendation

        rec = get_recommendation("unknown_dimension")
        assert "Review and improve" in rec
