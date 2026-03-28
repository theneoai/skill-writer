# SKILL.md Format Specification

> This document describes the required structure and content of a SKILL.md file

---

## Overview

SKILL.md is a self-describing manifest for AI agent skills. It uses a structured markdown format with YAML frontmatter and numbered sections (§X.X).

---

## File Structure

```
---
name: <skill-name>
description: >
  <one-line description>
  <multi-line description>
license: <license>
metadata:
  author: <author>
  version: <semver>
  type: <skill-type>
  tags: [<tags>]
---

# <Skill Name>

> **Version**: X.X.X
> **Date**: YYYY-MM-DD
> **Status**: ACTIVE|DRAFT|DEPRECATED
> **Capabilities**: CREATE, EVALUATE, OPTIMIZE, RESTORE, SECURITY

---

## §1.1 Identity

**Name**: <name>
**Role**: <role>
**Purpose**: <purpose statement>

**Core Principles**:
- <principle 1>
- <principle 2>

**Red Lines (严禁)**:
- <forbidden action 1>
- <forbidden action 2>

---

## §1.2 Framework

**Architecture**: <architecture description>

```
<architecture diagram>
```

**Tool Integration**:
| Tool | Path | Purpose | LLM-Enhanced |
|------|------|---------|--------------|
| <tool1> | <path> | <purpose> | Yes/No |

**Constraints**:
- <constraint 1>
- <constraint 2>

---

## §1.3 Thinking

**Cognitive Loop**:
```
1. <step> → <action>
2. <step> → <action>
3. <step> → <action>
```

---

## §2 Invocation

### Trigger Detection

| Pattern | Mode |
|---------|------|
| <pattern1> | CREATE |
| <pattern2> | EVALUATE |

### Mode Routing

| Mode | When |
|------|------|
| CREATE | <condition> |
| EVALUATE | <condition> |

---

## §3 Workflow

### §3.1 Process

**Phase 1**: <name>
- <step>
- <step>

**Phase 2**: <name>
- <step>

### §3.2 Done Criteria

- <criterion 1>
- <criterion 2>

### §3.3 Fail Criteria

- <criterion 1>
- <criterion 2>

---

## §4 Examples

### Example 1: <title>

**Input**:
```
<user input>
```

**Output**:
```
<expected output>
```

---

## §5 Validation

### Pre-flight Checks

| Check | Condition | Failure Action |
|-------|-----------|----------------|
| <check1> | <condition> | <action> |

### Score Thresholds

| Tier | Minimum Score |
|------|---------------|
| GOLD | <score> |
| SILVER | <score> |
| BRONZE | <score> |

---

## §6 Self-Evolution (Optional)

### Trigger Mechanisms

| Trigger | Condition | Priority |
|---------|-----------|----------|
| Threshold | <condition> | High |

---

## Appendix A: YAML Frontmatter

| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Unique skill identifier (kebab-case) |
| description | Yes | Brief description (< 200 chars) |
| license | Yes | License (MIT, Apache, etc) |
| metadata.author | Yes | Author email or name |
| metadata.version | Yes | Semantic version (X.Y.Z) |
| metadata.type | Yes | Skill category |
| metadata.tags | No | Array of tags |

## Appendix B: Section Numbers

| Section | Purpose |
|---------|---------|
| §1.1 | Identity - Who this skill is |
| §1.2 | Framework - How it works |
| §1.3 | Thinking - Cognitive process |
| §2 | Invocation - How to trigger |
| §3 | Workflow - Steps and criteria |
| §4 | Examples - Usage examples |
| §5 | Validation - Quality checks |
| §6 | Self-Evolution - Auto-optimization |

## Appendix C: Style Guide

- **Line length**: < 120 characters
- **Section length**: < 100 lines each
- **Total length**: < 400 lines (details to external docs)
- **Emphasis**: Use **bold** for critical info
- **Lists**: Use - for bullets, | for tables

---

## Example: Minimal SKILL.md

```markdown
---
name: my-skill
description: >
  A brief description of what this skill does.
license: MIT
metadata:
  author: author@example.com
  version: 1.0.0
  type: utility
---

# My Skill

> **Version**: 1.0.0
> **Status**: ACTIVE
> **Capabilities**: CREATE, EVALUATE

## §1.1 Identity

**Name**: my-skill
**Role**: Example Skill
**Purpose**: Demonstrates SKILL.md format

## §1.2 Framework

**Architecture**: Simple single-purpose skill

## §1.3 Thinking

1. Parse input
2. Process task
3. Return result

## §2 Invocation

| Pattern | Mode |
|---------|------|
| my-skill | CREATE |

## §3 Workflow

### §3.1 Process

**Phase 1**: Execute
- Receive input
- Process task

### §3.2 Done Criteria

- Task completed

## §5 Validation

| Check | Condition |
|-------|-----------|
| Valid input | Non-empty |
```

---

**Related Documents**:
- [SKILL.md (root)](../../SKILL.md) - Example skill implementation
- [METRICS.md](METRICS.md) - Quality metrics definitions
- [THRESHOLDS.md](THRESHOLDS.md) - Certification thresholds
