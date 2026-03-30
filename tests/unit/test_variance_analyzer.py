"""Tests for variance analyzer module."""

from __future__ import annotations

import pytest


class TestAnalyzeVariance:
    """Test suite for analyze_variance."""

    def test_zero_variance(self):
        """Test zero variance when scores are equal."""
        from skill.eval.variance_analyzer import analyze_variance

        result = analyze_variance(300, 300)
        assert result["variance"] == 0.0
        assert result["status"] == "PASS"

    def test_small_variance_pass(self):
        """Test PASS status for variance < 20."""
        from skill.eval.variance_analyzer import analyze_variance

        result = analyze_variance(285, 300)  # variance = 15 < 20
        assert result["variance"] == 15.0
        assert result["status"] == "PASS"

    def test_medium_variance_warning(self):
        """Test WARNING status for variance 20-30."""
        from skill.eval.variance_analyzer import analyze_variance

        result = analyze_variance(280, 300)  # variance = 20, not < 20 so WARNING
        assert result["variance"] == 20.0
        assert result["status"] == "WARNING"

    def test_large_variance_fail(self):
        """Test FAIL status for variance > 30."""
        from skill.eval.variance_analyzer import analyze_variance

        result = analyze_variance(250, 300)
        assert result["variance"] == 50.0
        assert result["status"] == "FAIL"

    def test_negative_scores(self):
        """Test handling of negative scores."""
        from skill.eval.variance_analyzer import analyze_variance

        result = analyze_variance(-100, 100)
        assert result["variance"] == 200.0


class TestGetVariancePoints:
    """Test suite for get_variance_points."""

    def test_variance_under_10(self):
        """Test 40 points for variance < 10."""
        from skill.eval.variance_analyzer import get_variance_points

        assert get_variance_points(5) == 40

    def test_variance_under_20(self):
        """Test 30 points for variance < 20."""
        from skill.eval.variance_analyzer import get_variance_points

        assert get_variance_points(15) == 30

    def test_variance_under_30(self):
        """Test 15 points for variance < 30."""
        from skill.eval.variance_analyzer import get_variance_points

        assert get_variance_points(25) == 15

    def test_variance_above_30(self):
        """Test 0 points for variance >= 30."""
        from skill.eval.variance_analyzer import get_variance_points

        assert get_variance_points(50) == 0
