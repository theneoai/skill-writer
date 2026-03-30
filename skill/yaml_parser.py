"""YAML parser and validator for Skill metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from skill.schema import SkillMetadata as BaseSkillMetadata


@dataclass
class ValidationResult:
    """Result of metadata validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class SkillValidationError(Exception):
    """Raised when skill metadata validation fails."""

    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


@dataclass
class SkillMetadata(BaseSkillMetadata):
    """Parsed skill metadata from SKILL.md frontmatter."""

    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SkillMetadata:
        """Create SkillMetadata from dictionary."""
        base = super().from_dict(data)
        return cls(
            name=base.name,
            description=base.description,
            version=base.version,
            license=base.license,
            author=base.author,
            tags=base.tags,
            type=base.type,
            modes=base.modes,
            tier=base.tier,
            signoff=base.signoff,
            created=base.created,
            updated=base.updated,
            interface=base.interface,
            extends=base.extends,
            raw_data=data,
        )


REQUIRED_FIELDS = {"name", "description"}
STRING_FIELDS = {"license", "version", "type"}
DICT_OR_STRING_FIELDS = {"description", "author"}
LIST_FIELDS = {"tags"}


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Full markdown content including frontmatter.

    Returns:
        Tuple of (frontmatter dict, remaining content after frontmatter).

    Raises:
        ValueError: If frontmatter is malformed.
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    yaml_content = match.group(1)
    remaining = content[match.end() :]

    try:
        data = yaml.safe_load(yaml_content) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Malformed YAML frontmatter: {e}") from e

    return data, remaining


def validate_metadata(data: dict) -> ValidationResult:
    """Validate metadata against schema.

    Args:
        data: Parsed YAML frontmatter data.

    Returns:
        ValidationResult with is_valid, errors, and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        errors.append("Frontmatter must be a YAML dictionary")
        return ValidationResult(is_valid=False, errors=errors)

    missing_fields = REQUIRED_FIELDS - set(data.keys())
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(sorted(missing_fields))}")

    for field_name, value in data.items():
        if field_name in STRING_FIELDS and value is not None:
            if not isinstance(value, str):
                errors.append(f"Field '{field_name}' must be a string")

        if field_name in DICT_OR_STRING_FIELDS and value is not None:
            if not isinstance(value, (str, dict)):
                errors.append(f"Field '{field_name}' must be a string or dict")

        if field_name in LIST_FIELDS:
            if not isinstance(value, list):
                errors.append(f"Field '{field_name}' must be a list")
            elif not all(isinstance(item, str) for item in value):
                errors.append(f"Field '{field_name}' must contain only strings")

    if "version" in data and data["version"] is not None:
        if not re.match(r"^\d+\.\d+(\.\d+)?$", str(data["version"])):
            warnings.append(f"Version '{data['version']}' does not follow semver format")

    return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)


def parse_skill_file(path: Path) -> SkillMetadata:
    """Parse entire SKILL.md file.

    Args:
        path: Path to SKILL.md file.

    Returns:
        SkillMetadata instance.

    Raises:
        SkillValidationError: If file cannot be parsed or validation fails.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        raise SkillValidationError(f"Cannot read file: {path}") from e

    try:
        frontmatter, _ = extract_frontmatter(content)
    except ValueError as e:
        raise SkillValidationError(str(e)) from e

    result = validate_metadata(frontmatter)
    if not result.is_valid:
        raise SkillValidationError(f"Validation failed: {', '.join(result.errors)}", result.errors)

    return SkillMetadata.from_dict(frontmatter)
