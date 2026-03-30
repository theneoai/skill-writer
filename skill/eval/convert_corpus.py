"""Convert corpus - Convert corpus format to trigger_analyzer expected format.

Input: corpus JSON with test_cases array
Output: JSON array with expected_trigger, predicted_triggers, rank fields
"""

from __future__ import annotations

import json
from typing import Optional


def convert_corpus(input_file: str, output_file: Optional[str] = None) -> str:
    """Convert corpus format to trigger_analyzer expected format.

    Args:
        input_file: Path to input corpus JSON file
        output_file: Optional path to output file. If None, returns JSON string.

    Returns:
        JSON string with converted data, or empty string on error
    """
    try:
        with open(input_file) as f:
            input_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return "[]"

    test_cases = input_data.get("test_cases", [])

    if not test_cases:
        return "[]"

    converted = []
    for case in test_cases:
        expected_mode = case.get("expected_mode")
        mode = case.get("mode")

        rank = 1 if mode == expected_mode else 0

        converted_case = {
            "expected_trigger": expected_mode,
            "predicted_triggers": [mode] if mode else [],
            "rank": rank,
            "should_trigger": case.get("should_trigger", True),
            "id": case.get("id"),
        }
        converted.append(converted_case)

    result = json.dumps(converted)

    if output_file:
        try:
            with open(output_file, "w") as f:
                f.write(result)
        except OSError:
            pass

    return result


def convert_corpus_from_json(json_str: str) -> str:
    """Convert corpus from JSON string.

    Args:
        json_str: JSON string with corpus data

    Returns:
        JSON string with converted data
    """
    try:
        input_data = json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return "[]"

    test_cases = input_data.get("test_cases", [])

    if not test_cases:
        return "[]"

    converted = []
    for case in test_cases:
        expected_mode = case.get("expected_mode")
        mode = case.get("mode")

        rank = 1 if mode == expected_mode else 0

        converted_case = {
            "expected_trigger": expected_mode,
            "predicted_triggers": [mode] if mode else [],
            "rank": rank,
            "should_trigger": case.get("should_trigger", True),
            "id": case.get("id"),
        }
        converted.append(converted_case)

    return json.dumps(converted)
