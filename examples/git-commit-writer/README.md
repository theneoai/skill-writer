# Example: git-commit-writer

**Tier**: 🏆 PLATINUM · **Score**: 1007/1020 · **Type**: Base (text assistant)

This example demonstrates the full skill-writer lifecycle:
CREATE (9-phase) → LEAN eval → OPTIMIZE (1 round) → full EVALUATE → PLATINUM certification.

## What this skill does

Generates [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)-compliant
commit messages from a git diff or plain-text description. Supports two modes:

- **GENERATE**: diff or description → structured `<type>(<scope>): <description>` message
- **VALIDATE**: check an existing message for spec compliance

## Install

```
"read https://github.com/theneoai/skill-writer/raw/main/examples/git-commit-writer/skill.md and install to claude"
```

## Usage

```
"write commit message for this diff: + export function parseDate(s) {...}"
→ feat: add parseDate utility function

"检查提交消息: 'updated the login page and fixed styles'"
→ VALIDATE: FAIL — missing type prefix; multiple concerns; past tense
   Suggested: fix(auth): resolve login page styling issue
```

## OPTIMIZE Trace

| Version | LEAN | Tier Proxy | Key Change |
|---------|------|-----------|------------|
| v1.0.0 | 448/500 | SILVER | CREATE output — missing HUMAN_REVIEW escalation |
| v1.1.0 | 493/500 | **PLATINUM** | +HUMAN_REVIEW matrix, +type/scope tables |

**One optimization round, +45 LEAN pts, SILVER → PLATINUM.**

## Files

| File | Description |
|------|-------------|
| `skill.md` | The certified skill (v1.1.0, PLATINUM) |
| `eval-report.md` | Full 4-phase EVALUATE report with Behavioral Verifier results |
| `README.md` | This file |
