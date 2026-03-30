"""Tests for swap augmentation module."""

from __future__ import annotations

import pytest


class TestSwapAugmentationResult:
    """Test suite for swap_augmented_eval result parsing."""

    def test_swap_eval_returns_confidence(self):
        """Test that swap_augmented_eval returns confidence field."""
        from skill.lib.swap_augmentation import get_confidence

        result = '{"verdict": "pass", "confidence": "CONFIDENT", "agreement": true}'
        confidence = get_confidence(result)
        assert confidence == "CONFIDENT"

    def test_swap_eval_returns_verdict(self):
        """Test that swap_augmented_eval returns verdict field."""
        from skill.lib.swap_augmentation import get_verdict

        result = '{"verdict": "pass", "confidence": "CONFIDENT", "agreement": true}'
        verdict = get_verdict(result)
        assert verdict == "pass"

    def test_uncertain_when_verdicts_differ(self):
        """Test that disagreement leads to UNCERTAIN confidence."""
        from skill.lib.swap_augmentation import parse_swap_result

        round1 = '{"verdict": "pass"}'
        round2 = '{"verdict": "fail"}'

        result = parse_swap_result(round1, round2)
        assert result["confidence"] == "UNCERTAIN"
        assert result["agreement"] is False

    def test_confident_when_verdicts_match(self):
        """Test that agreement leads to CONFIDENT confidence."""
        from skill.lib.swap_augmentation import parse_swap_result

        round1 = '{"verdict": "pass"}'
        round2 = '{"verdict": "pass"}'

        result = parse_swap_result(round1, round2)
        assert result["confidence"] == "CONFIDENT"
        assert result["agreement"] is True


class TestIsUncertain:
    """Test suite for is_uncertain function."""

    def test_uncertain_returns_true(self):
        """Test that UNCERTAIN results return True."""
        from skill.lib.swap_augmentation import is_uncertain

        assert is_uncertain("UNCERTAIN") is True

    def test_confident_returns_false(self):
        """Test that CONFIDENT results return False."""
        from skill.lib.swap_augmentation import is_uncertain

        assert is_uncertain("CONFIDENT") is False
