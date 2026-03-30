"""Tests for YAML parser and validator."""

from __future__ import annotations

import pytest

from skill.yaml_parser import (
    SkillMetadata,
    SkillValidationError,
    ValidationResult,
    extract_frontmatter,
    parse_skill_file,
    validate_metadata,
)


class TestExtractFrontmatter:
    """Test suite for extract_frontmatter function."""

    def test_extracts_valid_frontmatter(self):
        """Test extraction of valid YAML frontmatter."""
        content = """---
name: test-skill
description: A test skill
---
# Content here
"""
        data, remaining = extract_frontmatter(content)
        assert data == {"name": "test-skill", "description": "A test skill"}
        assert remaining == "# Content here\n"

    def test_handles_multiline_description(self):
        """Test extraction with multiline description."""
        content = """---
name: test
description: >
  Multi line
  description
---
"""
        data, _ = extract_frontmatter(content)
        assert "description" in data

    def test_missing_frontmatter(self):
        """Test handling of missing frontmatter."""
        content = "# Just content\n## Section"
        data, remaining = extract_frontmatter(content)
        assert data == {}
        assert remaining == content

    def test_malformed_yaml(self):
        """Test handling of malformed YAML."""
        content = """---
name: test
  invalid: indentation
---
"""
        with pytest.raises(ValueError, match="Malformed YAML"):
            extract_frontmatter(content)

    def test_empty_frontmatter(self):
        """Test handling of empty frontmatter."""
        content = "---\n\n---\n\n# Content"
        data, remaining = extract_frontmatter(content)
        assert data == {}
        assert remaining == "# Content"


class TestValidateMetadata:
    """Test suite for validate_metadata function."""

    def test_valid_metadata(self):
        """Test validation of valid metadata."""
        data = {
            "name": "test-skill",
            "description": "A test skill",
            "version": "1.0.0",
            "tags": ["test", "example"],
        }
        result = validate_metadata(data)
        assert result.is_valid
        assert result.errors == []

    def test_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        data = {"version": "1.0.0"}
        result = validate_metadata(data)
        assert not result.is_valid
        assert any("name" in err for err in result.errors)

    def test_invalid_field_type_string(self):
        """Test validation fails for non-string non-dict string field."""
        data = {"name": "test", "description": 123}
        result = validate_metadata(data)
        assert not result.is_valid
        assert any("'description' must be a string or dict" in err for err in result.errors)

    def test_invalid_field_type_list(self):
        """Test validation fails for non-list list field."""
        data = {"name": "test", "description": "desc", "tags": "not-a-list"}
        result = validate_metadata(data)
        assert not result.is_valid
        assert any("'tags' must be a list" in err for err in result.errors)

    def test_non_dict_input(self):
        """Test validation fails for non-dict input."""
        result = validate_metadata("not a dict")
        assert not result.is_valid
        assert "YAML dictionary" in result.errors[0]

    def test_warning_for_non_semver_version(self):
        """Test warning for non-semver version string."""
        data = {"name": "test", "description": "desc", "version": "latest"}
        result = validate_metadata(data)
        assert result.is_valid
        assert any("semver" in warn for warn in result.warnings)


class TestParseSkillFile:
    """Test suite for parse_skill_file function."""

    def test_parses_valid_file(self, tmp_path):
        """Test parsing a valid SKILL.md file."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill
license: MIT
---
# Content
""")
        metadata = parse_skill_file(skill_file)
        assert metadata.name == "test-skill"
        assert metadata.description == "A test skill"
        assert metadata.license == "MIT"

    def test_raises_error_for_missing_file(self):
        """Test error raised for non-existent file."""
        from pathlib import Path

        with pytest.raises(SkillValidationError, match="Cannot read file"):
            parse_skill_file(Path("/nonexistent/SKILL.md"))

    def test_raises_error_for_invalid_metadata(self, tmp_path):
        """Test error raised for invalid metadata."""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("""---
version: 1.0.0
---
# Missing name and description
""")
        with pytest.raises(SkillValidationError, match="Missing required fields"):
            parse_skill_file(skill_file)
