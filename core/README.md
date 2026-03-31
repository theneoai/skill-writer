# Skill Writer Core Engine

Platform-agnostic core engine for creating, evaluating, and optimizing AI skills.

## Overview

The core engine provides three main capabilities:

1. **CREATE** - Generate skills from templates with requirement elicitation
2. **EVALUATE** - 4-phase 1000-point quality assessment
3. **OPTIMIZE** - 7-dimension 9-step improvement loop

## Architecture

Each mode is self-contained with:
- `README.md` - Human-readable documentation
- `*.yaml` - Machine-executable structured data

## Directory Structure

```
core/
├── README.md                    # This file
├── create/                      # CREATE mode
│   ├── README.md               # Documentation
│   ├── workflow.yaml           # Step-by-step workflow
│   ├── elicitation.yaml        # 6 requirement questions
│   └── templates/              # Skill templates
│       ├── base.md
│       ├── api-integration.md
│       ├── data-pipeline.md
│       └── workflow-automation.md
├── evaluate/                    # EVALUATE mode
│   ├── README.md               # Documentation
│   ├── rubrics.yaml            # 1000-point scoring
│   ├── phases.yaml             # 4-phase pipeline
│   └── certification.yaml      # Certification tiers
├── optimize/                    # OPTIMIZE mode
│   ├── README.md               # Documentation
│   ├── dimensions.yaml         # 7-dimension analysis
│   ├── strategies.yaml         # Optimization strategies
│   └── convergence.yaml        # Convergence detection
└── shared/                      # Shared resources
    ├── security/
    │   └── cwe-patterns.yaml   # Security scanning
    └── utils/
        └── helpers.yaml        # Utility functions
```

## Usage

The core engine is embedded into platform-specific SKILL.md files by the builder tool.

See individual mode directories for detailed documentation.

## Modes

### CREATE
Generate new skills from typed templates.

**Input**: Natural language description  
**Output**: Complete SKILL.md file

Key features:
- Template selection (api-integration, data-pipeline, workflow-automation, base)
- 6-question requirement elicitation (Inversion pattern)
- Automatic placeholder filling
- Security scanning
- LEAN evaluation

### EVALUATE
4-phase 1000-point quality assessment.

**Phases**:
1. Parse & Validate (100 pts) - Structural checks
2. Text Quality (300 pts) - 6 sub-dimensions
3. Runtime Testing (400 pts) - Benchmark tests
4. Certification (200 pts) - Final gates

**Tiers**: PLATINUM (≥950), GOLD (≥900), SILVER (≥800), BRONZE (≥700)

### OPTIMIZE
7-dimension 9-step automated improvement.

**Dimensions**: System Design, Domain Knowledge, Workflow Definition, Error Handling, Examples, Metadata, Long-Context

**Loop**: READ → ANALYZE → CURATE → PLAN → IMPLEMENT → VERIFY → HUMAN_REVIEW → LOG → COMMIT

## Integration

The core engine is designed to be embedded by the builder tool:

1. Builder reads core/ content
2. Embeds into platform templates
3. Outputs platform-specific SKILL.md files

See `../builder/` for the build tool.

## Version

v1.0.0 - Initial release with CREATE, EVALUATE, OPTIMIZE modes
