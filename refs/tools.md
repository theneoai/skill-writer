# Tools Reference

> **Purpose**: Complete tool documentation for skill management
> **Load**: When tool references are needed
> **Main doc**: SKILL.md (tool references throughout)

---

## User Scripts

### Quick CLI Reference

| Tool | Path | Purpose | Speed |
|------|------|---------|-------|
| **create-skill** | `scripts/create-skill.sh` | Create new skill from description | ~30s |
| **evaluate-skill** | `scripts/evaluate-skill.sh` | Full evaluation (fast/full) | ~2-10min |
| **lean-orchestrator** | `scripts/lean-orchestrator.sh` | Fast evaluation (~1s) | **~1s** |
| **optimize-skill** | `scripts/optimize-skill.sh` | 9-step self-optimization loop | ~5min |
| **security-audit** | `scripts/security-audit.sh` | OWASP AST10 security check | ~10s |
| **restore-skill** | `scripts/restore-skill.sh` | Fix broken skills | ~20s |
| **quick-score** | `scripts/quick-score.sh` | Fast text scoring (no LLM) | <1s |

### Usage Examples

```bash
# Fast path (~1 second)
./scripts/lean-orchestrator.sh ./SKILL.md BRONZE

# Full evaluation (~2 minutes)
./scripts/evaluate-skill.sh ./SKILL.md fast

# Create new skill
./scripts/create-skill.sh "Create a code review skill" ./code-review.md GOLD

# Optimize
./scripts/optimize-skill.sh ./code-review.md 20

# Security audit
./scripts/security-audit.sh ./code-review.md

# Restore broken skill
./scripts/restore-skill.sh ./broken-skill.md --snapshot <id>
```

---

## Engine Components

### Orchestrator

| Tool | Path | Purpose | LLM-Enhanced |
|------|------|---------|--------------|
| orchestrator | `tools/orchestrator.sh` | Main workflow coordinator | Yes |
| _workflow | `tools/orchestrator/_workflow.sh` | Workflow state machine | No |
| _actions | `tools/orchestrator/_actions.sh` | Decision logic | Yes |
| _state | `tools/orchestrator/_state.sh` | State management | No |
| _parallel | `tools/orchestrator/_parallel.sh` | Background tasks | No |

### Agents

| Tool | Path | Purpose | LLM-Enhanced |
|------|------|---------|--------------|
| creator | `tools/agents/creator.sh` | Section generator | Yes |
| evaluator | `tools/agents/evaluator.sh` | Skill evaluator | Yes |
| restorer | `tools/agents/restorer.sh` | Skill repair | Yes |
| security | `tools/agents/security.sh` | OWASP AST10 audit | Yes |
| base | `tools/agents/base.sh` | Agent infrastructure | No |

### Evolution

| Tool | Path | Purpose | LLM-Enhanced |
|------|------|---------|--------------|
| engine | `tools/evolution/engine.sh` | 9-step optimization loop | Yes |
| analyzer | `tools/evolution/analyzer.sh` | Log analysis | Yes |
| improver | `tools/evolution/improver.sh` | LLM improvement | Yes |
| summarizer | `tools/evolution/summarizer.sh` | Finding synthesis | Yes |
| rollback | `tools/evolution/rollback.sh` | Snapshot/rollback | No |
| usage_tracker | `tools/evolution/usage_tracker.sh` | Usage data collection | No |
| evolve_decider | `tools/evolution/evolve_decider.sh` | Evolution trigger decision | Yes |
| learner | `tools/evolution/learner.sh` | Pattern learning | Yes |

### Evaluation

| Tool | Path | Purpose |
|------|------|---------|
| main | `tools/eval/main.sh` | Eval entry point |
| parse_validate | `tools/eval/parse/parse_validate.sh` | Phase 1: Structure |
| text_scorer | `tools/eval/scorer/text_scorer.sh` | Phase 2: Text quality |
| runtime_tester | `tools/eval/scorer/runtime_tester.sh` | Phase 3: Runtime |
| runtime_agent_tester | `tools/eval/scorer/runtime_agent_tester.sh` | Phase 3: Agent-based |
| certifier | `tools/eval/certifier.sh` | Phase 4: Certification |
| agent_executor | `tools/eval/lib/agent_executor.sh` | Multi-LLM orchestration |

### Libraries

| Tool | Path | Purpose |
|------|------|---------|
| bootstrap | `tools/lib/bootstrap.sh` | Module loading |
| constants | `tools/lib/constants.sh` | Configuration |
| concurrency | `tools/lib/concurrency.sh` | Lock management |
| errors | `tools/lib/errors.sh` | Error handling |
| integration | `tools/lib/integration.sh` | Eval integration |

---

## Script Parameters

### create-skill.sh

```bash
./scripts/create-skill.sh <description> [output_path] [tier]

# Examples:
./scripts/create-skill.sh "Code review skill"
./scripts/create-skill.sh "API documentation generator" ./api-doc.md GOLD
```

### evaluate-skill.sh

```bash
./scripts/evaluate-skill.sh <skill_file> [mode]

# Modes: fast, full, lean
# Examples:
./scripts/evaluate-skill.sh ./SKILL.md lean
./scripts/evaluate-skill.sh ./SKILL.md full
```

### optimize-skill.sh

```bash
./scripts/optimize-skill.sh <skill_file> [rounds|auto] [force]

# Examples:
./scripts/optimize-skill.sh ./SKILL.md 20        # 20 rounds
./scripts/optimize-skill.sh ./SKILL.md auto      # Auto-evolve
./scripts/optimize-skill.sh ./SKILL.md auto force # Force even if not needed
```

### security-audit.sh

```bash
./scripts/security-audit.sh <skill_file> [--critical-only]

# Examples:
./scripts/security-audit.sh ./SKILL.md
./scripts/security-audit.sh ./SKILL.md --critical-only
```

### restore-skill.sh

```bash
./scripts/restore-skill.sh <skill_file> [--list|--snapshot <id>|auto]

# Examples:
./scripts/restore-skill.sh ./SKILL.md --list
./scripts/restore-skill.sh ./SKILL.md --snapshot 20260328_001
./scripts/restore-skill.sh ./SKILL.md auto
```

---

## Tool Integration

### Mode Routing

```
User Input → orchestrator.sh → Mode Selection
                              ↓
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
         CREATE           EVALUATE          OPTIMIZE
         creator          evaluator         engine
              ↓               ↓               ↓
         orchestrator    evaluator        evolution
```

### LLM Provider Selection

Automatic provider detection and selection:

```bash
# Provider Priority (strength):
# 1. anthropic: 100
# 2. openai: 90
# 3. kimi-code: 85
# 4. minimax: 80
# 5. kimi: 75

# Auto-selection: Top 2 providers for cross-validation
```

### Environment Variables

```bash
# Required for LLM calls
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
KIMI_API_KEY=sk-...
KIMI_CODE_API_KEY=sk-...  # Preferred
MINIMAX_API_KEY=sk-...
MINIMAX_GROUP_ID=...

# Optional endpoints
KIMI_CODE_ENDPOINT=https://api.kimi.com/coding/v1
```

---

## Usage

Referenced from SKILL.md footer for tool documentation.
Reference from: SKILL.md line 319
