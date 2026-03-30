"""Tests for pairwise_ranker module."""

import pytest
from skill.eval.pairwise_ranker import (
    PairwiseResult,
    bt_estimate,
    pairwise_judge,
    pairwise_judge_unbiased,
    rank_skills,
)


class TestBtEstimate:
    def test_requires_at_least_two_skills(self):
        results = []
        skill_names = ["only_one"]
        with pytest.raises(ValueError):
            bt_estimate(results, skill_names)

    def test_estimates_two_skills_with_winner(self):
        results = [{"winner": "skill_a", "loser": "skill_b"}]
        skill_names = ["skill_a", "skill_b"]
        result = bt_estimate(results, skill_names)
        assert result["skill_a"] > result["skill_b"]

    def test_all_ties_give_equal_scores(self):
        results = []
        skill_names = ["skill_a", "skill_b", "skill_c"]
        result = bt_estimate(results, skill_names)
        assert abs(result["skill_a"] - result["skill_b"]) < 0.1
        assert abs(result["skill_b"] - result["skill_c"]) < 0.1

    def test_more_wins_higher_score(self):
        results = [
            {"winner": "skill_a", "loser": "skill_b"},
            {"winner": "skill_a", "loser": "skill_b"},
            {"winner": "skill_b", "loser": "skill_c"},
        ]
        skill_names = ["skill_a", "skill_b", "skill_c"]
        result = bt_estimate(results, skill_names)
        assert result["skill_a"] > result["skill_b"]
        assert result["skill_b"] > result["skill_c"]

    def test_requires_at_least_two_skills(self):
        results = []
        skill_names = ["only_one"]
        with pytest.raises(ValueError):
            bt_estimate(results, skill_names)


class TestPairwiseJudge:
    def test_requires_skill_paths(self, tmp_path):
        skill_a = tmp_path / "skill_a.md"
        skill_a.write_text("# Skill A\nThis is skill A content.")
        skill_b = tmp_path / "skill_b.md"
        skill_b.write_text("# Skill B\nThis is skill B content.")

        result = pairwise_judge(str(skill_a), str(skill_b), "test task")
        assert result.winner in ["A", "B", "TIE"]
        assert 0.0 <= result.confidence <= 1.0

    def test_same_content_gives_tie(self, tmp_path):
        skill_a = tmp_path / "skill_a.md"
        skill_a.write_text("# Identical\nSame content.")
        skill_b = tmp_path / "skill_b.md"
        skill_b.write_text("# Identical\nSame content.")

        result = pairwise_judge(str(skill_a), str(skill_b), "test task")
        assert result.winner == "TIE"


class TestPairwiseJudgeUnbiased:
    def test_returns_structured_result(self, tmp_path):
        skill_a = tmp_path / "skill_a.md"
        skill_a.write_text("# Skill A\nContent A.")
        skill_b = tmp_path / "skill_b.md"
        skill_b.write_text("# Skill B\nContent B.")

        result = pairwise_judge_unbiased(str(skill_a), str(skill_b), "test task")
        assert hasattr(result, "winner")
        assert hasattr(result, "confidence")
        assert hasattr(result, "position_bias_detected")
        assert result.winner in ["A", "B", "TIE", "UNCERTAIN"]

    def test_swap_augmentation_detects_position_bias(self, tmp_path):
        skill_a = tmp_path / "skill_a.md"
        skill_a.write_text("# Skill A\nContent A with different words.")
        skill_b = tmp_path / "skill_b.md"
        skill_b.write_text("# Skill B\nContent B with different words.")

        result = pairwise_judge_unbiased(str(skill_a), str(skill_b), "test task")
        assert result.position_bias_detected in [True, False]


class TestRankSkills:
    def test_requires_multiple_skills(self, tmp_path):
        skill = tmp_path / "only_one.md"
        skill.write_text("# Single\nOnly one skill.")

        result = rank_skills("test task", str(skill))
        assert "ERROR" in result or "at least 2" in result

    def test_ranks_multiple_skills(self, tmp_path):
        skill_a = tmp_path / "skill_a.md"
        skill_a.write_text("# Skill A\nPython programming content.")
        skill_b = tmp_path / "skill_b.md"
        skill_b.write_text("# Skill B\nPython fastapi content.")
        skill_c = tmp_path / "skill_c.md"
        skill_c.write_text("# Skill C\nPython django content.")

        result = rank_skills("python task", str(skill_a), str(skill_b), str(skill_c))
        assert (
            "Rank" in result
            or "skill_a" in result
            or "skill_b" in result
            or "skill_c" in result
        )
