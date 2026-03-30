"""Tests for convert_corpus module."""

from __future__ import annotations

import json

import pytest


class TestConvertCorpus:
    """Test suite for convert_corpus."""

    def test_converts_basic_format(self, tmp_path):
        """Test basic corpus conversion."""
        from skill.eval.convert_corpus import convert_corpus

        input_data = {
            "test_cases": [
                {
                    "id": "test1",
                    "expected_mode": "CREATE",
                    "mode": "CREATE",
                    "should_trigger": True,
                }
            ]
        }
        input_file = tmp_path / "input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        result = convert_corpus(str(input_file))
        result_data = json.loads(result)

        assert len(result_data) == 1
        assert result_data[0]["expected_trigger"] == "CREATE"
        assert result_data[0]["predicted_triggers"] == ["CREATE"]

    def test_converts_multiple_cases(self, tmp_path):
        """Test conversion of multiple test cases."""
        from skill.eval.convert_corpus import convert_corpus

        input_data = {
            "test_cases": [
                {
                    "id": "test1",
                    "expected_mode": "CREATE",
                    "mode": "CREATE",
                    "should_trigger": True,
                },
                {
                    "id": "test2",
                    "expected_mode": "EVALUATE",
                    "mode": "EVALUATE",
                    "should_trigger": True,
                },
                {
                    "id": "test3",
                    "expected_mode": "RESTORE",
                    "mode": "RESTORE",
                    "should_trigger": True,
                },
            ]
        }
        input_file = tmp_path / "input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        result = convert_corpus(str(input_file))
        result_data = json.loads(result)

        assert len(result_data) == 3
        assert result_data[0]["expected_trigger"] == "CREATE"
        assert result_data[2]["expected_trigger"] == "RESTORE"

    def test_rank_is_1_when_match(self, tmp_path):
        """Test that rank is 1 when predicted matches expected."""
        from skill.eval.convert_corpus import convert_corpus

        input_data = {
            "test_cases": [
                {
                    "id": "test1",
                    "expected_mode": "CREATE",
                    "mode": "CREATE",
                    "should_trigger": True,
                }
            ]
        }
        input_file = tmp_path / "input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        result = convert_corpus(str(input_file))
        result_data = json.loads(result)

        assert result_data[0]["rank"] == 1

    def test_rank_is_0_when_no_match(self, tmp_path):
        """Test that rank is 0 when predicted doesn't match expected."""
        from skill.eval.convert_corpus import convert_corpus

        input_data = {
            "test_cases": [
                {
                    "id": "test1",
                    "expected_mode": "CREATE",
                    "mode": "EVALUATE",
                    "should_trigger": True,
                }
            ]
        }
        input_file = tmp_path / "input.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        result = convert_corpus(str(input_file))
        result_data = json.loads(result)

        assert result_data[0]["rank"] == 0

    def test_writes_to_output_file(self, tmp_path):
        """Test writing to output file."""
        from skill.eval.convert_corpus import convert_corpus

        input_data = {
            "test_cases": [
                {
                    "id": "test1",
                    "expected_mode": "CREATE",
                    "mode": "CREATE",
                    "should_trigger": True,
                }
            ]
        }
        input_file = tmp_path / "input.json"
        output_file = tmp_path / "output.json"
        with open(input_file, "w") as f:
            json.dump(input_data, f)

        convert_corpus(str(input_file), str(output_file))

        assert output_file.exists()
        with open(output_file) as f:
            result_data = json.load(f)

        assert len(result_data) == 1
