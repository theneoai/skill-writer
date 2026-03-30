"""Tests for trigger-based intent detection."""

from __future__ import annotations

import pytest

from skill.lib.triggers import (
    detect_language,
    detect_intent,
    get_detected_mode,
    get_confidence,
    is_ambiguous,
    score_primary_keywords,
    score_secondary_keywords,
    check_negative_patterns,
    calculate_confidence,
)


class TestDetectLanguage:
    """Test suite for detect_language."""

    def test_detects_chinese_only(self):
        """Test detection of Chinese-only input."""
        assert detect_language("创建技能") == "ZH"

    def test_detects_english_only(self):
        """Test detection of English-only input."""
        assert detect_language("create skill") == "EN"

    def test_detects_mixed(self):
        """Test detection of mixed language input."""
        assert detect_language("创建 skill") == "MIXED"


class TestScorePrimaryKeywords:
    """Test suite for score_primary_keywords."""

    def test_create_mode_english_high_score(self):
        """Test high score for strong CREATE keywords."""
        score = score_primary_keywords("create a new skill for me", "EN", "CREATE")
        assert score == 3

    def test_create_mode_english_medium_score(self):
        """Test medium score for medium CREATE keywords."""
        score = score_primary_keywords("develop a new skill", "EN", "CREATE")
        assert score == 2

    def test_create_mode_chinese_high_score(self):
        """Test high score for Chinese CREATE keywords."""
        score = score_primary_keywords("创建新技能", "ZH", "CREATE")
        assert score == 3

    def test_evaluate_mode_english_high_score(self):
        """Test high score for strong EVALUATE keywords."""
        score = score_primary_keywords("evaluate this skill", "EN", "EVALUATE")
        assert score == 3

    def test_restore_mode_english_high_score(self):
        """Test high score for strong RESTORE keywords."""
        score = score_primary_keywords("restore the skill", "EN", "RESTORE")
        assert score == 3

    def test_security_mode_english_high_score(self):
        """Test high score for security keywords."""
        score = score_primary_keywords("security audit", "EN", "SECURITY")
        assert score == 3

    def test_optimize_mode_english_high_score(self):
        """Test high score for optimize keywords."""
        score = score_primary_keywords("optimize the skill", "EN", "OPTIMIZE")
        assert score == 3

    def test_no_match_returns_zero(self):
        """Test zero score when no keywords match."""
        score = score_primary_keywords("hello world", "EN", "CREATE")
        assert score == 0


class TestDetectIntent:
    """Test suite for detect_intent."""

    def test_create_intent_english(self):
        """Test CREATE intent detection in English."""
        result = detect_intent("create a new skill")
        mode = get_detected_mode(result)
        assert mode == "CREATE"

    def test_evaluate_intent_english(self):
        """Test EVALUATE intent detection in English."""
        result = detect_intent("evaluate this skill")
        mode = get_detected_mode(result)
        assert mode == "EVALUATE"

    def test_restore_intent_english(self):
        """Test RESTORE intent detection in English."""
        result = detect_intent("restore the broken skill")
        mode = get_detected_mode(result)
        assert mode == "RESTORE"

    def test_security_intent_english(self):
        """Test SECURITY intent detection."""
        result = detect_intent("security audit")
        mode = get_detected_mode(result)
        assert mode == "SECURITY"

    def test_optimize_intent_english(self):
        """Test OPTIMIZE intent detection."""
        result = detect_intent("optimize the skill performance")
        mode = get_detected_mode(result)
        assert mode == "OPTIMIZE"

    def test_empty_input_defaults_to_evaluate(self):
        """Test that empty input defaults to EVALUATE."""
        result = detect_intent("")
        mode = get_detected_mode(result)
        assert mode == "EVALUATE"

    def test_confidence_is_returned(self):
        """Test that confidence score is returned."""
        result = detect_intent("create a new skill")
        confidence = get_confidence(result)
        assert isinstance(confidence, str)
        confidence_val = float(confidence)
        assert confidence_val >= 0


class TestIsAmbiguous:
    """Test suite for is_ambiguous."""

    def test_ask_mode_is_ambiguous(self):
        """Test that ASK mode is flagged as ambiguous."""
        result = "ASK:CREATE:0.50"
        assert is_ambiguous(result) is True

    def test_normal_mode_is_not_ambiguous(self):
        """Test that normal modes are not flagged as ambiguous."""
        result = "CREATE:0.85"
        assert is_ambiguous(result) is False
