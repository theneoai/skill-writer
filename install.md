# Skill Writer — Agent Install Guide

> **For AI agents**: This file contains executable installation instructions.
> When a user asks you to "read this file and install", follow the steps below exactly.
> No user interaction is needed unless the platform cannot be detected automatically.

---

## §1  What Gets Installed

| Item | Source (repo-relative) | Purpose |
|------|----------------------|---------|
| Main skill file | `skill-framework.md` | Core skill-writer logic |
| Reference docs | `refs/*.md` | Evolution, deliberation, convergence specs (Claude only) |
| Templates | `templates/*.md` | Skill creation templates (Claude only) |
| Eval rubrics | `eval/*.md` | Evaluation rubrics (Claude only) |
| Optimize guides | `optimize/*.md` | Optimization strategies (Claude only) |

---

## §2  Platform → Destination Map

| Platform | Skills directory | Extra companion files |
|----------|----------------|-----------------------|
| **claude** | `~/.claude/skills/` | Yes — refs, templates, eval, optimize (see §4) |
| **opencode** | `~/.config/opencode/skills/` | No |
| **openclaw** | `~/.openclaw/skills/` | No |
| **cursor** | `~/.cursor/skills/` | No |
| **gemini** | `~/.gemini/skills/` | No |
| **openai** | N/A | Manual — see §5 |

Installed filename on all platforms: `skill-writer.md`

---

## §3  Installation Steps (Agent: execute these)

### Step 1 — Locate source files

The directory containing this file (`install.md`) is the repo root.
`skill-framework.md` is in the same directory.

```
REPO_ROOT = directory of this file
SOURCE    = REPO_ROOT/skill-framework.md
```

Verify: `SOURCE` must exist and contain the line `name: skill-writer`.
If missing, abort and tell the user.

### Step 2 — Determine target platform(s)

**Auto-detect** from the user's request:
- "install" or "install to all" → all platforms except openai
- "install to claude" → claude only
- "install to opencode" → opencode only
- "install to openclaw" → openclaw only
- "install to cursor" → cursor only
- "install to gemini" → gemini only
- "安装" / "安装到所有平台" → all platforms except openai
- "安装到 <平台名>" → that platform only

If ambiguous, ask: "Which platform would you like to install to? (claude / opencode / openclaw / cursor / gemini / all)"

### Step 3 — Install for each target platform

For every target platform, do:

```
1. Create destination directory if it does not exist
2. Copy SOURCE → <skills_dir>/skill-writer.md
3. If platform is "claude", also run Step 4
4. Report: ✓ [<platform>] <full destination path>
```

### Step 4 — Claude companion files (claude only)

Copy each subdirectory from the repo into `~/.claude/`:

| Source | Destination |
|--------|-------------|
| `REPO_ROOT/refs/*.md` | `~/.claude/refs/` |
| `REPO_ROOT/templates/*.md` | `~/.claude/templates/` |
| `REPO_ROOT/eval/*.md` | `~/.claude/eval/` |
| `REPO_ROOT/optimize/*.md` | `~/.claude/optimize/` |

Create each destination directory if it does not exist.
Skip silently if a source directory is empty.

### Step 5 — Report results

Print a summary like:

```
✓ [claude]   ~/.claude/skills/skill-writer.md
✓ [claude]   companion files → ~/.claude/{refs,templates,eval,optimize}/
✓ [opencode] ~/.config/opencode/skills/skill-writer.md
...

Installed to N platform(s). Restart each platform to activate skill-writer.
```

---

## §4  Companion Files Detail (Claude)

These files extend skill-writer's capabilities on Claude:

| File | Purpose |
|------|---------|
| `refs/use-to-evolve.md` | UTE self-evolution protocol |
| `refs/evolution.md` | Evolution trigger rules |
| `refs/deliberation.md` | Multi-LLM deliberation spec |
| `refs/convergence.md` | Convergence detection rules |
| `refs/security-patterns.md` | CWE security pattern library |
| `templates/base.md` | Base skill template |
| `templates/api-integration.md` | API integration template |
| `templates/data-pipeline.md` | Data pipeline template |
| `templates/workflow-automation.md` | Workflow automation template |
| `templates/use-to-evolve-snippet.md` | UTE YAML snippet |
| `eval/rubrics.md` | Evaluation scoring rubrics |
| `eval/benchmarks.md` | Benchmark reference data |
| `eval/pairwise.md` | Pairwise comparison guide |
| `optimize/strategies.md` | Optimization strategy guide |
| `optimize/anti-patterns.md` | Anti-pattern reference |

---

## §5  OpenAI — Manual Installation

OpenAI does not use a local skills directory.
Tell the user:

> OpenAI platform requires manual installation:
> upload `skill-framework.md` as a custom instruction or system prompt
> in your OpenAI project or assistant settings.

---

## §6  Quick Reference for Users

Paste one of these into your AI agent:

```
# Install to all platforms (recommended)
read install.md and install

# Install to a specific platform
read install.md and install to claude
read install.md and install to opencode
read install.md and install to cursor

# Chinese
读取 install.md 并安装
读取 install.md 并安装到 claude
```

---

## §7  Verification

After installation, verify by asking your AI agent:

```
"Are you skill-writer? What version are you?"
```

Expected response: agent acknowledges skill-writer v2.0.0 and offers CREATE / LEAN / EVALUATE / OPTIMIZE / INSTALL modes.
