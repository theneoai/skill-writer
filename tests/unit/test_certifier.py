"""Tests for certifier module."""

import pytest
from dataclasses import dataclass
from skill.eval.certifier import (
    CertificationResult,
    determine_tier,
    get_tier_points,
    get_tier_badge,
    certify,
    certify_from_json,
)


class TestDetermineTier:
    def test_platinum_tier(self):
        assert determine_tier(950, 330, 430, 9) == "PLATINUM"
        assert determine_tier(1000, 350, 450, 5) == "PLATINUM"

    def test_gold_tier(self):
        assert determine_tier(900, 315, 405, 14) == "GOLD"
        assert determine_tier(950, 320, 410, 10) == "GOLD"

    def test_silver_tier(self):
        assert determine_tier(800, 280, 360, 19) == "SILVER"
        assert determine_tier(850, 290, 370, 15) == "SILVER"

    def test_bronze_tier(self):
        assert determine_tier(700, 245, 315, 25) == "BRONZE"
        assert determine_tier(750, 250, 320, 20) == "BRONZE"

    def test_not_certified(self):
        assert determine_tier(600, 200, 300, 35) == "NOT_CERTIFIED"
        assert determine_tier(950, 300, 400, 35) == "NOT_CERTIFIED"

    def test_low_text_score_never_certified(self):
        assert determine_tier(1000, 200, 500, 5) == "NOT_CERTIFIED"


class TestGetTierPoints:
    def test_tier_points(self):
        assert get_tier_points("PLATINUM") == 30
        assert get_tier_points("GOLD") == 25
        assert get_tier_points("SILVER") == 20
        assert get_tier_points("BRONZE") == 15

    def test_unknown_tier_returns_zero(self):
        assert get_tier_points("NOT_CERTIFIED") == 0
        assert get_tier_points("UNKNOWN") == 0


class TestGetTierBadge:
    def test_badges(self):
        assert "PLATINUM" in get_tier_badge("PLATINUM")
        assert "GOLD" in get_tier_badge("GOLD")
        assert "SILVER" in get_tier_badge("SILVER")
        assert "BRONZE" in get_tier_badge("BRONZE")

    def test_not_certified_badge(self):
        assert "NOT CERTIFIED" in get_tier_badge("NOT_CERTIFIED")


class TestCertify:
    def test_certifies_with_valid_scores(self, tmp_path):
        skill_file = tmp_path / "test_skill.md"
        skill_file.write_text("# Test Skill\nContent here.")

        result = certify(str(skill_file), 280, 360, 15, 0.90, 0.85, 0.95, 300)
        assert result.certified in ["YES", "NO"]
        assert 0 <= result.certify_total <= 100

    def test_error_for_missing_file(self):
        result = certify("/nonexistent/file.md", 280, 360, 15, 0.90, 0.85, 0.95, 300)
        assert result.certify_total == 0

    def test_high_scores_certify(self, tmp_path):
        skill_file = tmp_path / "test_skill.md"
        skill_file.write_text("# Test Skill\nContent here.")

        result = certify(str(skill_file), 330, 430, 9, 0.92, 0.88, 0.95, 500)
        assert result.tier == "PLATINUM"
        assert result.certified == "YES"

    def test_p0_violation_blocks_certification(self, tmp_path):
        skill_file = tmp_path / "test_skill.md"
        skill_file.write_text("# Test Skill\nRun: eval ${USER_INPUT}")

        result = certify(
            str(skill_file), 330, 430, 9, 0.92, 0.88, 0.95, 500
        )
        assert result.certified == "NO"
        assert result.p0_violation == True

    def test_low_total_not_certified(self, tmp_path):
        skill_file = tmp_path / "test_skill.md"
        skill_file.write_text("# Test Skill\nContent here.")

        result = certify(str(skill_file), 200, 300, 35, 0.70, 0.70, 0.70, 100)
        assert result.certified == "NO"
        assert result.tier == "NOT_CERTIFIED"


class TestCertifyFromJson:
    def test_parses_json_results(self, tmp_path):
        skill_file = tmp_path / "test_skill.md"
        skill_file.write_text("# Test Skill\nContent here.")

        json_input = {
            "skill_file": str(skill_file),
            "text_score": 280,
            "runtime_score": 360,
            "variance": 15,
            "f1_score": 0.90,
            "mrr_score": 0.85,
            "trigger_accuracy": 0.95,
            "phase1_score": 300,
        }

        result = certify_from_json(json_input)
        assert result.certify_total > 0

    def test_handles_missing_fields(self):
        json_input = {"skill_file": "/some/file.md"}
        result = certify_from_json(json_input)
        assert result.certify_total >= 0
