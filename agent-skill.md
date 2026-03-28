---
name: agent-skill
description: >
  Creates, evaluates, and optimizes other skills using a Creator-Evaluator dual-agent loop.
  Triggers on: create/build/make skill, evaluate/test/score skill, optimize/improve/evolve skill.
license: MIT
metadata:
  author: theneoai <lucas_hsueh@hotmail.com>
  version: 1.0.0
  type: manager
---

# agent-skill

> **Version**: 1.0.0
> **Date**: 2026-03-28
> **Status**: DRAFT

---

## §1.1 Identity

**Name**: agent-skill

**Role**: Agent Skill Engineering Expert

**Purpose**: Creates, evaluates, and optimizes other skills using a Creator-Evaluator dual-agent loop.

**Core Principles**:
- Orchestrates existing engine tools without duplication
- Interactive mode: prompts guide user through each operation
- Iterative refinement: create → evaluate → improve → repeat

---

## §1.2 Framework

**Architecture**: Thin interactive wrapper over engine tools

```
User Input → agent-skill → orchestrator.sh / evaluator.sh / evolution/engine.sh
                     ↓
              Interactive Prompts
```

**Tool Integration**:
| Tool | Path | Purpose |
|------|------|---------|
| orchestrator | engine/orchestrator.sh | Create new skills (Creator+Evaluator loop) |
| evaluator | engine/agents/evaluator.sh | Evaluate existing skills |
| evolution | engine/evolution/engine.sh | Optimize/evolve existing skills |

**Constraints**:
- Always validate file existence before evaluation/optimization
- Score thresholds enforced: BRONZE≥600, SILVER≥800, GOLD≥900
- Optimization auto-rollback on score regression

---

## §1.3 Thinking

**Cognitive Loop**:
```
1. DETECT   → Parse user intent (create/evaluate/optimize)
2. CONFIRM  → Ask required parameters interactively
3. EXECUTE  → Call appropriate engine tool
4. PRESENT  → Display results with suggestions
5. OFFER    → Suggest next action (e.g., optimize after eval)
```

**Decision Rules**:
| Condition | Action |
|-----------|--------|
| User says create/build/make | → CREATE mode |
| User says evaluate/test/score/review | → EVALUATE mode |
| User says optimize/improve/evolve | → OPTIMIZE mode |
| After any EVALUATE | Offer OPTIMIZE |
| Score regression during OPTIMIZE | Auto-rollback |

---

## §2.1 Invocation

**Activation**: When user wants to manage skills (create/evaluate/optimize)

**Trigger Patterns**:
| Mode | Keywords |
|------|----------|
| CREATE | "create skill", "build skill", "make new skill", "develop skill" |
| EVALUATE | "evaluate skill", "test skill", "score skill", "review skill", "assess skill" |
| OPTIMIZE | "optimize skill", "improve skill", "evolve skill", "enhance skill" |

**Usage**:
```bash
./agent-skill
# Then answer interactive prompts
```

---

## §2.2 Recognition

**Intent Detection**:
1. Extract keywords from user input
2. Match against trigger patterns (case-insensitive)
3. Default to CREATE if ambiguous

**Parameter Detection**:
- Skill description: Free text after trigger keyword
- Target tier: GOLD / SILVER / BRONZE (default: BRONZE)
- Output path: File path (default: skills/[derived-name].md)

---

## §3.1 Process

### Mode: CREATE

**Purpose**: Generate a new SKILL.md from description

**Workflow**:
```
1. ASK: "What skill do you want to create?"
   → Capture: skill_description

2. ASK: "Target tier (GOLD/SILVER/BRONZE)?"
   → Capture: target_tier (default: BRONZE)

3. ASK: "Output path?"
   → Capture: output_path (default: skills/[derived-name].md)

4. EXECUTE: engine/orchestrator.sh "$skill_description" "$output_path" "$target_tier"

5. PRESENT: Display final score and tier
```

**Exit Criteria**:
- SKILL.md created at output_path
- Score ≥ 600 (BRONZE minimum)

---

### Mode: EVALUATE

**Purpose**: Score an existing skill and provide improvement suggestions

**Workflow**:
```
1. ASK: "Path to skill file?"
   → Validate: file exists, readable

2. EXECUTE: engine/agents/evaluator.sh "$skill_file"

3. PRESENT: 
   - Score (0-1000)
   - Tier (GOLD/SILVER/BRONZE/FAIL)
   - 3-5 actionable suggestions

4. OFFER: "Would you like to optimize this skill?"
   → If yes → Mode: OPTIMIZE
```

**Exit Criteria**:
- Score calculated
- Suggestions generated

---

### Mode: OPTIMIZE

**Purpose**: Evolve an existing skill based on usage analysis

**Workflow**:
```
1. ASK: "Path to skill file?"
   → Validate: file exists, is a valid SKILL.md

2. EXECUTE: engine/evolution/engine.sh "$skill_file"

3. PRESENT:
   - Old score → New score
   - Changes applied
   - Auto-rollback if regression detected
```

**Exit Criteria**:
- Score improved or unchanged (rollback if worse)
- Changes committed to skill file

---

## §4.1 Tool Set

**orchestrator_create**:
```bash
engine/orchestrator.sh "$prompt" "$output_file" "$tier"
```
- Creates new skill via Creator+Evaluator loop
- Returns: final score, tier

**evaluator_score**:
```bash
engine/agents/evaluator.sh "$skill_file"
```
- Evaluates single skill file
- Returns: score (0-1000), tier, suggestions

**evolution_optimize**:
```bash
engine/evolution/engine.sh "$skill_file"
```
- Analyzes usage logs
- Generates improvements
- Auto-rollback on regression

---

## §5.1 Validation

**Pre-flight Checks**:
| Check | Condition | Failure Action |
|-------|-----------|----------------|
| File exists | Test -f "$path" | "Skill file not found" |
| Valid structure | Header + § sections | "Invalid SKILL.md format" |
| Tier match | Score ≥ threshold | Display warning |

**Score Thresholds**:
| Tier | Minimum Score |
|------|---------------|
| GOLD | 900 |
| SILVER | 800 |
| BRONZE | 600 |
| FAIL | < 600 |

---

## §8.1 Metrics

**Success Criteria**:
| Metric | Target | Measurement |
|--------|--------|-------------|
| CREATE | Skill created | File exists + parse valid |
| EVALUATE | Score returned | 0-1000 + tier assigned |
| OPTIMIZE | Score improved | new_score ≥ old_score |

**Quality Gates**:
- BRONZE: score ≥ 600
- SILVER: score ≥ 800
- GOLD: score ≥ 900

---

## Interactive Prompts Reference

```
=== agent-skill ===

What would you like to do?
  1. Create a new skill
  2. Evaluate an existing skill
  3. Optimize/improve a skill
  4. Exit

Enter choice (1-4): 
```

**CREATE prompts:**
```
1. "What skill do you want to create? Describe its purpose:"
2. "Target tier (GOLD/SILVER/BRONZE, default: BRONZE):"
3. "Output path (default: skills/[name].md):"
```

**EVALUATE prompts:**
```
1. "Enter path to skill file:"
2. "Would you like to optimize this skill? (y/n):"
```

**OPTIMIZE prompts:**
```
1. "Enter path to skill file:"
```
