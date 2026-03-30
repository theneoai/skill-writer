"""YAML Schema definitions for skill metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import yaml


class Mode(str, Enum):
    """Skill operation modes."""

    CREATE = "create"
    EVALUATE = "evaluate"
    RESTORE = "restore"
    SECURITY = "security"
    OPTIMIZE = "optimize"


class Tier(str, Enum):
    """Skill quality tiers."""

    PLATINUM = "platinum"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"


class SignoffType(str, Enum):
    """Skill signoff certification types."""

    HUMAN = "human"
    AUTOMATED = "automated"
    TEMP_CERT = "temp_cert"


class SkillType(str, Enum):
    """Skill type classifications."""

    MANAGER = "manager"
    WORKER = "worker"
    ORCHESTRATOR = "orchestrator"
    UTILITY = "utility"


@dataclass
class TriggerConfig:
    """Configuration for skill triggering mechanisms."""

    threshold: float = 0.8
    interval_seconds: int = 3600
    min_usage_count: int = 10


@dataclass
class EvolutionConfig:
    """Configuration for skill self-evolution."""

    enabled: bool = False
    f1_target: float = 0.90
    trigger: TriggerConfig = field(default_factory=TriggerConfig)


@dataclass
class SecurityConfig:
    """Configuration for security auditing."""

    cwe_enabled: bool = True
    scan_on_create: bool = True
    scan_on_update: bool = True


@dataclass
class ValidationConfig:
    """Configuration for skill validation."""

    require_description: bool = True
    min_description_length: int = 10
    require_tags: bool = False
    min_tags: int = 0


@dataclass
class LLMConfig:
    """Configuration for LLM deliberation settings."""

    enabled: bool = False
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 2048


@dataclass
class AuthorInfo:
    """Author information with optional email."""

    name: str
    email: str | None = None

    @classmethod
    def from_dict(cls, data: str | dict | None) -> AuthorInfo | None:
        """Parse author from various formats."""
        if data is None:
            return None
        if isinstance(data, str):
            return cls(name=data)
        if isinstance(data, dict):
            return cls(name=data.get("name", ""), email=data.get("email"))
        return None

    def to_dict(self) -> str | dict:
        """Convert to string or dict based on content."""
        if self.email:
            return {"name": self.name, "email": self.email}
        return self.name


@dataclass
class ExternalEvaluator:
    """External evaluation tool reference."""

    id: str
    name: str
    url: str
    metrics: list[str] = field(default_factory=list)


@dataclass
class InterfaceContract:
    """Universal interface contract for skill."""

    input: str = "user-natural-language"
    output: str = "structured-skill"
    modes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict | None) -> InterfaceContract:
        """Parse interface from dict."""
        if data is None:
            return cls()
        return cls(
            input=data.get("input", "user-natural-language"),
            output=data.get("output", "structured-skill"),
            modes=data.get("modes", []),
        )


@dataclass
class EvaluationExt:
    """Evaluation extension configuration."""

    metrics: list[str] = field(default_factory=lambda: ["f1", "mrr"])
    thresholds: dict[str, float] = field(default_factory=lambda: {"f1": 0.90, "mrr": 0.85})
    external: list[ExternalEvaluator] = field(default_factory=list)


@dataclass
class SecurityExt:
    """Security extension configuration."""

    standard: str = "CWE"
    scan_on_delivery: bool = True


@dataclass
class EvolutionExt:
    """Evolution extension configuration."""

    triggers: list[str] = field(default_factory=lambda: ["threshold", "time", "usage"])


@dataclass
class ExtendsConfig:
    """Implementation extensions (tool-specific)."""

    evaluation: EvaluationExt = field(default_factory=EvaluationExt)
    security: SecurityExt = field(default_factory=SecurityExt)
    evolution: EvolutionExt = field(default_factory=EvolutionExt)

    @classmethod
    def from_dict(cls, data: dict | None) -> ExtendsConfig:
        """Parse extends from dict."""
        if data is None:
            return cls()
        eval_data = data.get("evaluation")
        eval_ext = EvaluationExt(
            metrics=eval_data.get("metrics", ["f1", "mrr"]) if eval_data else ["f1", "mrr"],
            thresholds=eval_data.get("thresholds", {"f1": 0.90, "mrr": 0.85})
            if eval_data
            else {"f1": 0.90, "mrr": 0.85},
            external=[ExternalEvaluator(**e) for e in eval_data.get("external", []) if eval_data]
            if eval_data and eval_data.get("external")
            else [],
        )
        sec_data = data.get("security", {})
        sec_ext = SecurityExt(
            standard=sec_data.get("standard", "CWE") if sec_data else "CWE",
            scan_on_delivery=sec_data.get("scan_on_delivery", True) if sec_data else True,
        )
        evo_data = data.get("evolution", {})
        evo_ext = EvolutionExt(
            triggers=evo_data.get("triggers", ["threshold", "time", "usage"])
            if evo_data
            else ["threshold", "time", "usage"],
        )
        return cls(evaluation=eval_ext, security=sec_ext, evolution=evo_ext)


@dataclass
class SkillMetadata:
    """Complete metadata schema for skill definition (Universal + Implementation)."""

    name: str
    description: str | dict[str, str]
    version: str = "0.1.0"
    license: str = "MIT"
    author: str | dict[str, str] | None = None
    tags: list[str] = field(default_factory=list)
    type: SkillType = SkillType.WORKER
    modes: list[Mode] = field(default_factory=list)
    tier: Tier = Tier.BRONZE
    signoff: SignoffType = SignoffType.AUTOMATED
    created: str | None = None
    updated: str | None = None
    interface: InterfaceContract | None = None
    extends: ExtendsConfig | None = None
    evolution: EvolutionConfig = field(default_factory=EvolutionConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    llm_deliberation: LLMConfig = field(default_factory=LLMConfig)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> SkillMetadata:
        """Parse skill metadata from YAML string.

        Handles YAML frontmatter format with --- delimitators.
        """
        content = yaml_str.strip()
        if content.startswith("---"):
            content = content[3:]
            if content.startswith("\n"):
                content = content[1:]
            parts = content.split("---")
            if parts:
                content = parts[0].strip()
        if not content:
            return cls(name="", description="")
        data = yaml.safe_load(content)
        if data is None:
            data = {}
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SkillMetadata:
        """Create SkillMetadata from dictionary."""
        if "modes" in data and isinstance(data["modes"], list):
            data["modes"] = [Mode(m.lower()) if isinstance(m, str) else m for m in data["modes"]]
        if "type" in data and isinstance(data["type"], str):
            data["type"] = SkillType(data["type"].lower())
        if "tier" in data and isinstance(data["tier"], str):
            data["tier"] = Tier(data["tier"].lower())
        if "signoff" in data and isinstance(data["signoff"], str):
            data["signoff"] = SignoffType(data["signoff"].lower())
        if "interface" in data:
            data["interface"] = InterfaceContract.from_dict(data["interface"])
        if "extends" in data:
            data["extends"] = ExtendsConfig.from_dict(data["extends"])
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """Convert SkillMetadata to dictionary."""
        result: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "license": self.license,
            "author": self.author,
            "tags": self.tags,
            "type": self.type.value if isinstance(self.type, SkillType) else self.type,
            "modes": [m.value if isinstance(m, Mode) else m for m in self.modes],
            "tier": self.tier.value if isinstance(self.tier, Tier) else self.tier,
            "signoff": self.signoff.value
            if isinstance(self.signoff, SignoffType)
            else self.signoff,
        }
        if self.created:
            result["created"] = self.created
        if self.updated:
            result["updated"] = self.updated
        if self.interface:
            result["interface"] = {
                "input": self.interface.input,
                "output": self.interface.output,
                "modes": self.interface.modes,
            }
        if self.extends:
            result["extends"] = {
                "evaluation": {
                    "metrics": self.extends.evaluation.metrics,
                    "thresholds": self.extends.evaluation.thresholds,
                    "external": [
                        {"id": e.id, "name": e.name, "url": e.url, "metrics": e.metrics}
                        for e in self.extends.evaluation.external
                    ],
                },
                "security": {
                    "standard": self.extends.security.standard,
                    "scan_on_delivery": self.extends.security.scan_on_delivery,
                },
                "evolution": {
                    "triggers": self.extends.evolution.triggers,
                },
            }
        return result

    def validate(self) -> list[str]:
        """Validate the skill metadata and return list of errors."""
        errors = []

        if not self.name or not self.name.strip():
            errors.append("name is required and cannot be empty")

        if not self.description or not self.description.strip():
            errors.append("description is required and cannot be empty")
        elif isinstance(self.description, str) and len(self.description.strip()) < 10:
            errors.append("description must be at least 10 characters")

        if not self.version or not self.version.strip():
            errors.append("version is required and cannot be empty")

        if self.author is not None:
            if isinstance(self.author, str) and not self.author.strip():
                errors.append("author must be empty string or non-empty if provided")
            elif isinstance(self.author, dict) and not self.author.get("name", "").strip():
                errors.append("author.name is required if author is an object")

        return errors
