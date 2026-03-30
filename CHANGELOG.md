# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.15.0] - 2026-03-30

### Added
- **Universal metadata format**: SKILL.md metadata updated to ISO 23026 industry standard with bilingual description support (EN/ZH)
- **External evaluators integration**: Comprehensive catalog of 12+ external evaluation tools (OpenAI Evals, LangSmith, Anthropic Claude Evaluation, Google Vertex AI, Microsoft Azure AI Studio, Arize Phoenix, W&B, Scale AI, LM Evaluation Harness, BIG-bench, HELM, MLflow, Fiddler AI, MMLU)
- **Schema synchronization**: Unified SkillMetadata dataclasses across schema.py, yaml_parser.py, md_generator.py
- **Cross-vendor compatibility**: SKILL.md format designed for maximum compatibility with MCP, Microsoft Copilot, and OpenAI agents

### Changed
- **CLI enhancements**: Fixed broken CLI caused by empty .pth file, improved error messages
- **pyproject.toml relocation**: Moved from skill/ subdirectory to project root for standard Python packaging
- **Test suite improvements**: Fixed test_invalid_field_type_string test case, verified all 634 tests pass

### Fixed
- **CLI import issues**: .pth file empty causing module import failures
- **pip installation issues**: Corrected venv installation problems from system Python pip

### Security
- **CWE-based security audit**: OWASP AST10 10-item security audit in SECURITY mode
- **Credential scanning**: Hardcoded credentials (CWE-798), SQL injection (CWE-89), XSS (CWE-79), code injection (CWE-94) detection

## [2.0.0] - 2026-03-28

### Added
- **RESTORE mode**: Skill restoration for broken/degraded skills
- **SECURITY mode**: OWASP AST10 10-item security audit
- **HUMAN_REVIEW step**: Manual review when score < 8.0 after 10 rounds
- **CURATION step**: Knowledge consolidation every 10 optimization rounds
- **Long-Context Handling**: New 10% weight dimension for chunking strategy
- **EdgeCase Agent**: Multi-LLM boundary condition testing
- **F1/MRR metrics**: Trigger accuracy and mean reciprocal rank tracking
- **Multi-LLM deliberation**: Cross-validation with Anthropic, OpenAI, Kimi
- **9-step optimization loop**: Complete self-evolution cycle

### Changed
- **SKILL.md**: Extended from 283 lines to 793 lines with complete tool documentation
- **engine/evolution/engine.sh**: Rewritten with 9-step loop and multi-LLM deliberation
- **eval/**: Separated into proper directory structure

### Security
- All security checks now use multi-LLM cross-validation
- P0 violations block deployment

## [1.0.0] - 2026-03-27

### Added
- Initial skill creation with orchestrator
- Creator and Evaluator agents
- Basic evaluation framework (4 phases)
- Evolution engine for self-optimization
- Snapshot and rollback mechanism
- Multi-provider LLM support (OpenAI, Anthropic, Kimi, MiniMax)

---

## Migration Guide

### v1.0 → v2.0

**Old workflow:**
```bash
engine/orchestrator.sh "prompt" output.md BRONZE
eval/main.sh --skill output.md --fast
```

**New workflow:**
```bash
skill create "prompt" output.md
skill evaluate output.md
skill security output.md
skill optimize output.md
skill restore broken.md
```

### v2.0 → v2.15

**Changes:**
- SKILL.md format is now universal (ISO 23026 standard)
- CLI commands unchanged, but `skill parse` and `skill validate` are new
- External evaluators can be referenced in SKILL.md extends.evaluation.external
