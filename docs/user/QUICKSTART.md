# Quick Start Guide

**Goal**: 5 minutes to evaluate your first skill, 30 minutes to master the system

---

## Prerequisites

- [ ] Bash 3.2+ (macOS/Linux)
- [ ] Git
- [ ] jq (for JSON processing)
- [ ] 至少一个 LLM API key (optional, for full eval)

### Install

```bash
git clone <repo-url>
cd skill-system
```

### Verify Installation

```bash
bash scripts/lean-orchestrator.sh SKILL.md
```

Expected output:
```
[LEAN 21:54:22] START: Lean orchestration for SKILL.md
[LEAN 21:54:22] PHASE 1: Fast Parse
[LEAN 21:54:22] Parse score: 100/100
[LEAN 21:54:22] PHASE 2: Text Score (Heuristic)
[LEAN 21:54:22] Text score: 325/350
[LEAN 21:54:22] PHASE 3: Runtime Test
[LEAN 21:54:22] Runtime score: 50/50
{"status":"PASS","tier":"GOLD","total":475}
```

---

## 5-Minute Tutorial

### Step 1: Evaluate a Skill (~10 seconds)

```bash
# Lean evaluation (no LLM, instant)
./scripts/lean-orchestrator.sh SKILL.md SILVER
```

**What happens**:
1. Fast parse (YAML, sections, triggers)
2. Heuristic text scoring (keywords, patterns)
3. Runtime pattern detection
4. Certificate tier output

### Step 2: Create a New Skill (~1 minute)

```bash
./scripts/create-skill.sh "Code Review Skill"
```

**What happens**:
1. Creates `code-review-skill.md`
2. Populates §1.1 Identity
3. Populates §1.2 Framework
4. Populates §1.3 Thinking

### Step 3: Evaluate Your New Skill (~10 seconds)

```bash
./scripts/lean-orchestrator.sh code-review-skill.md SILVER
```

### Step 4: Optimize if Needed (~5 minutes)

```bash
# With auto-evolution (uses usage data)
./scripts/optimize-skill.sh code-review-skill.md auto
```

---

## 30-Minute Mastery Path

### Minute 1-5: Basics
```bash
# Learn the CLI interface
./scripts/lean-orchestrator.sh --help
./scripts/quick-score.sh --help
```

### Minute 6-10: Create
```bash
# Interactive creation
./scripts/create-skill.sh --interactive
```

### Minute 11-15: Evaluate
```bash
# Full evaluation (with LLM)
./scripts/evaluate-skill.sh code-review-skill.md
```

### Minute 16-20: Optimize
```bash
# Manual optimization (3 rounds)
./scripts/optimize-skill.sh code-review-skill.md 3
```

### Minute 21-25: Auto-Evolve
```bash
# Enable auto-evolution
./scripts/optimize-skill.sh code-review-skill.md auto

# Track usage
source engine/evolution/usage_tracker.sh
track_trigger "code-review-skill" "CREATE" "CREATE"
track_task "code-review-skill" "code_review" "true" 5
```

### Minute 26-30: Security
```bash
# Run security audit
./scripts/security-audit.sh code-review-skill.md
```

---

## Common Workflows

### Workflow 1: CI/CD Integration

```bash
# In your CI pipeline
if ./scripts/lean-orchestrator.sh SKILL.md | grep -q "GOLD"; then
    echo "Skill certified, proceeding..."
else
    echo "Skill needs improvement"
    exit 1
fi
```

### Workflow 2: Development Loop

```bash
# Edit skill
vim SKILL.md

# Quick check (in loop)
./scripts/quick-score.sh SKILL.md

# Full eval before commit
./scripts/evaluate-skill.sh SKILL.md
```

### Workflow 3: Auto-Evolution Setup

```bash
# Add to crontab (daily at 2am)
0 2 * * * cd /path/to/skill-system && ./scripts/optimize-skill.sh SKILL.md auto

# Or run manually
./scripts/optimize-skill.sh SKILL.md auto force
```

---

## FAQ

### Q: Lean vs Full Evaluation - Which to Use?

| Scenario | Recommended |
|----------|-------------|
| During development | Lean (~0s) |
| CI/CD pipeline | Lean |
| Pre-commit check | Lean |
| Production certification | Full (~2min) |
| Final quality gate | Full |

### Q: How Often Should I Optimize?

- **Daily**: If score < GOLD (475)
- **Weekly**: If score >= GOLD but < PLATINUM (950)
- **Monthly**: If score >= PLATINUM

### Q: What Triggers Auto-Evolution?

1. **Threshold**: Score drops below 475
2. **Scheduled**: 24 hours since last check
3. **Usage**: Trigger F1 < 0.85 or Task Rate < 0.80

---

## Next Steps

- [Complete Tutorial](TUTORIAL.md)
- [Workflow: Create](workflows/CREATE.md)
- [Workflow: Evaluate](workflows/EVALUATE.md)
- [Workflow: Optimize](workflows/OPTIMIZE.md)

---

**Related Documents**:
- [Tutorial](TUTORIAL.md)
- [Architecture](../technical/ARCHITECTURE.md)
