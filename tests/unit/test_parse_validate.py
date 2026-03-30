"""Tests for parse_validate module."""

from __future__ import annotations

import re
import pytest

from skill.eval.parse_validate import (
    ParseValidateResult,
    parse_validate,
    extract_yaml_frontmatter,
    check_yaml_frontmatter,
    check_sections,
    check_triggers,
    check_placeholders,
    check_security,
)


class TestExtractYamlFrontmatter:
    """Test suite for extract_yaml_frontmatter function."""

    def test_extracts_yaml_from_content(self):
        """Test extraction of YAML frontmatter from markdown content."""
        content = """---
name: test-skill
description: A test skill
license: MIT
---
# Content here
"""
        frontmatter = extract_yaml_frontmatter(content)
        assert frontmatter["name"] == "test-skill"
        assert frontmatter["description"] == "A test skill"
        assert frontmatter["license"] == "MIT"

    def test_returns_empty_dict_when_no_frontmatter(self):
        """Test empty dict returned when no frontmatter present."""
        content = "# Just content\n## Section"
        frontmatter = extract_yaml_frontmatter(content)
        assert frontmatter == {}


class TestCheckYamlFrontmatter:
    """Test suite for check_yaml_frontmatter function."""

    def test_scores_full_frontmatter(self):
        """Test scoring when all required fields present."""
        frontmatter = {
            "name": "test-skill",
            "description": "A test skill",
            "license": "MIT",
        }
        score, details = check_yaml_frontmatter(frontmatter)
        assert score == 30
        assert details["has_name"] is True
        assert details["has_description"] is True
        assert details["has_license"] is True

    def test_scores_partial_frontmatter(self):
        """Test scoring with partial frontmatter."""
        frontmatter = {
            "name": "test-skill",
        }
        score, details = check_yaml_frontmatter(frontmatter)
        assert score == 10
        assert details["has_name"] is True
        assert details["has_description"] is False
        assert details["has_license"] is False

    def test_empty_frontmatter_scores_zero(self):
        """Test zero score for empty frontmatter."""
        frontmatter = {}
        score, details = check_yaml_frontmatter(frontmatter)
        assert score == 0
        assert details["has_name"] is False


class TestCheckSections:
    """Test suite for check_sections function."""

    def test_finds_all_three_sections(self):
        """Test detection of §1.1, §1.2, §1.3 sections."""
        content = """
# §1.1 Identity
Some content
## §1.2 Framework
More content
### §1.3 Thinking
Final content
"""
        score, details = check_sections(content)
        assert score == 30
        assert details["has_1_1"] is True
        assert details["has_1_2"] is True
        assert details["has_1_3"] is True

    def test_partial_sections_score_proportionally(self):
        """Test partial section detection."""
        content = """
# §1.1 Identity
Some content
## §1.2 Framework
More content
"""
        score, details = check_sections(content)
        assert score == 20
        assert details["has_1_1"] is True
        assert details["has_1_2"] is True
        assert details["has_1_3"] is False


class TestCheckTriggers:
    """Test suite for check_triggers function."""

    def test_counts_trigger_words(self):
        """Test counting of CREATE, EVALUATE, RESTORE, TUNE."""
        content = """
CREATE a new skill
EVALUATE the quality
RESTORE the original
TUNE the parameters
CREATE another one
CREATE skill three
CREATE skill four
CREATE skill five
"""
        score, details = check_triggers(content)
        assert details["create_count"] == 5
        assert details["evaluate_count"] == 1
        assert details["restore_count"] == 1
        assert details["tune_count"] == 1
        assert score == 7

    def test_partial_trigger_score(self):
        """Test scoring when only some triggers meet threshold."""
        content = """
CREATE skill one
CREATE skill two
CREATE skill three
CREATE skill four
"""
        score, details = check_triggers(content)
        assert details["create_count"] == 4
        assert details["evaluate_count"] == 0
        assert details["restore_count"] == 0
        assert details["tune_count"] == 0
        assert score == 0


class TestCheckPlaceholders:
    """Test suite for check_placeholders function."""

    def test_no_placeholders_max_score(self):
        """Test full score when no placeholders found."""
        content = "This is a well-written skill document."
        score, details = check_placeholders(content)
        assert score == 15
        assert details["placeholder_count"] == 0

    def test_some_placeholders_reduced_score(self):
        """Test reduced score with some placeholders."""
        content = "This has [TODO] and TBD placeholders."
        score, details = check_placeholders(content)
        assert details["placeholder_count"] == 2
        assert score == 10


class TestCheckSecurity:
    """Test suite for check_security function."""

    def test_detects_api_key_pattern(self):
        """Test detection of hardcoded API keys."""
        content = "api_key = sk-1234567890abcdefghij"
        is_violation, details = check_security(content)
        assert is_violation is True
        assert details["has_hardcoded_secret"] is True

    def test_detects_path_traversal(self):
        """Test detection of path traversal patterns."""
        content = "Path: ../../../etc/passwd"
        is_violation, details = check_security(content)
        assert is_violation is True
        assert details["has_path_traversal"] is True

    def test_clean_content_passes(self):
        """Test that clean content passes security check."""
        content = "This is a normal skill document."
        is_violation, details = check_security(content)
        assert is_violation is False


class TestParseValidate:
    """Test suite for parse_validate main function."""

    def test_file_not_found(self):
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError):
            parse_validate("/nonexistent/path/SKILL.md")

    def test_full_validation_with_good_skill(self, tmp_path):
        """Test complete validation of a well-formed skill."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: good-skill
description: A well-formed skill
license: MIT
---
# §1.1 Identity
Create new skills

# §1.2 Framework
Use the framework

# §1.3 Thinking
Think carefully

CREATE skills properly
CREATE another one
CREATE more skills
CREATE even more
CREATE final one
EVALUATE them well
EVALUATE quality
EVALUATE performance
EVALUATE security
EVALUATE reliability
RESTORE when needed
RESTORE lost work
RESTORE settings
RESTORE defaults
RESTORE backup
TUNE for performance
TUNE for speed
TUNE for accuracy
TUNE for reliability
TUNE for security
""")
        result = parse_validate(skill_file)
        assert result.total_score > 80
        assert result.security_pass is True

    def test_result_dataclass_fields(self, tmp_path):
        """Test ParseValidateResult contains all expected fields."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: test
description: Test skill
---
# §1.1 Identity
# §1.2 Framework
# §1.3 Thinking
""")
        result = parse_validate(skill_file)
        assert hasattr(result, "yaml_score")
        assert hasattr(result, "sections_score")
        assert hasattr(result, "trigger_score")
        assert hasattr(result, "placeholder_score")
        assert hasattr(result, "security_pass")
        assert hasattr(result, "total_score")
