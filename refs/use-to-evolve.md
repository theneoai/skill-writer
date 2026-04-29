# Use-to-Evolve (UTE) Specification

> **Purpose**: Protocol for injecting self-improvement capability into any skill.
> **Load**: When §15 (UTE Injection) of `claude/skill-writer.md` is accessed.
> **Main doc**: `claude/skill-writer.md §15`
> **v3.6.0**: Added §11 (R-Few anchor-calibrated evolution — prevents UTE drift with minimal
> annotation budget) and §12 (SoK skill taxonomy — scopes UTE micro-patches by skill type to
> prevent meta-skill contamination).

---

> ### Enforcement Level Summary
>
> | Component | Level | Reason |
> |-----------|-------|--------|
> | Feedback signal detection (correction / approval) | `[CORE]` | Observable within a single turn |
> | Trigger miss detection (user rephrasing) | `[CORE]` | Observable within session |
> | Micro-patch proposal & user confirmation | `[CORE]` | Single-session action |
> | LEAN score after micro-patch | `[CORE]` | Computed in same session |
> | `cumulative_invocations` counter | `[EXTENDED]` | Resets across LLM sessions |
> | Cadence checks (every 10/50/100 calls) | `[EXTENDED]` | Requires persistent counter |
> | `last_ute_check` / `pending_patches` fields | `[EXTENDED]` | Cross-session state |
> | Audit trail in `.skill-audit/` | `[EXTENDED]` | Requires external file system |
>
> **Workaround for `[EXTENDED]` items**: Treat each invocation as potentially the
> Nth invocation. Run a lightweight check every invocation if session context is fresh.
> For true cadence gating, connect an optional persistence backend (see §5).

---

## §1  Concept

**Use-to-Evolve** (UTE) makes a skill self-improving through actual use.
The AI, upon recognizing a `use_to_evolve:` block in a skill's YAML frontmatter,
follows this protocol to observe usage patterns and propose improvements.

```
User invokes skill
        │
        ▼
  Skill executes normally
        │
        ▼
  AI observes outcome
    ├─ Note feedback signal (correction / approval / none)
    ├─ Track trigger misses (user rephrased request)
    └─ Periodically assess skill health
              │
    ┌─────────┴──────────┐
    │ no action needed   │ improvement identified
    └─────────┬──────────┘       │
              │             ASSESS severity
              ▼                  │
          continue        ┌──────┴──────┐
                      MICRO  |     SUGGEST
                      PATCH  |     OPTIMIZE
                     (minor) |    (structural)
```

**Key constraint**: The skill never self-modifies mid-session.
Patches are proposed to the user; applied only on confirmation.

---

## §2  YAML Frontmatter Block

Every skill with UTE enabled **must** include a `use_to_evolve:` block in its YAML frontmatter with all 13 fields:

```yaml
use_to_evolve:
  enabled: true                          # (bool) UTE active
  injected_by: "skill-writer v3.4.0"    # (string) injector version
  injected_at: "2026-04-01"             # (ISO-8601) injection date
  check_cadence:                         # (dict) invocation thresholds
    lightweight: 10                      #   lightweight check every N invocations
    full_recompute: 50                   #   full metric recompute every N
    tier_drift: 100                      #   tier drift check every N
  micro_patch_enabled: true             # (bool) allow trigger keyword patches
  feedback_detection: true              # (bool) detect user feedback signals
  certified_lean_score: 390             # (int) baseline LEAN score for drift detection
  last_ute_check: null                  # (ISO-8601 | null) when last check ran
  pending_patches: 0                    # (int) staged but unapplied patches
  total_micro_patches_applied: 0        # (int) cumulative patches applied
  cumulative_invocations: 0             # (int) total invocations (cadence counter)
  generation_method: "human-authored"   # (string) auto-generated | human-authored | hybrid
  validation_status: "lean-only"        # (string) unvalidated | lean-only | full-eval | pragmatic-verified
```

> **Note**: Phase 4 certification checks that all 13 fields are present. Missing any field fails the UTE injection check (−60 points). The two v3.4.0 fields (`generation_method`, `validation_status`) affect Skill Summary heuristic ranking and SHARE gate behavior — see `refs/security-patterns.md §6` for supply chain trust integration.

---

## §3  Feedback Signal Detection

When the AI observes user responses after skill output, it classifies the feedback:

| Signal | What the AI Looks For | Classification |
|--------|----------------------|----------------|
| **correction** | "that's wrong", "不对", user provides alternative | `failure` |
| **rephrasing** | Same request rephrased without acceptance | `trigger_miss` |
| **approval** | "thanks", "perfect", "好的", user proceeds normally | `success` |
| **abandon** | Topic switches or session ends immediately | `ambiguous` |
| **none** | No follow-up signal | `neutral` |

**On correction**: Note that the skill produced incorrect output — indicates need for OPTIMIZE.
**On rephrasing**: Note the alternative phrasing as a trigger keyword candidate.
**On repeated pattern** (≥3 similar corrections): Propose a micro-patch or suggest OPTIMIZE.

---

## §4  Cadence-Gated Health Checks

The AI performs periodic assessments based on approximate invocation counts:

### Every ~10 invocations: Lightweight Check
- Review recent interactions: Are users getting what they need?
- Note recurring trigger misses or corrections
- If repeated failures detected → propose micro-patch or suggest OPTIMIZE

### Every ~50 invocations: Quality Assessment
- Estimate overall skill health: trigger accuracy, output quality, user satisfaction
- Compare against quality thresholds (F1 ≥ 0.90, MRR ≥ 0.85, trigger_accuracy ≥ 0.90)
- On any threshold concern → suggest running EVALUATE or OPTIMIZE

### Every ~100 invocations: Tier Drift Check
- Estimate whether skill quality has drifted from its certified baseline
- If significant drift detected (estimated score drop > 50 pts) → suggest full EVALUATE

---

## §5  Micro-Patch Protocol

Micro-patches are **atomic, minor changes** proposed for surface-level improvements.
They NEVER affect the skill's core logic — only trigger keywords or metadata.

### Eligible Changes (Micro-Patch)

| Change | Condition | Scope |
|--------|-----------|-------|
| Add trigger keyword | ≥3 users rephrased with same term | YAML + mode trigger list |
| Add ZH trigger | ZH input frequently unrecognized | Mode trigger list |
| Update `updated` date | Any patch applied | YAML frontmatter only |
| Bump patch version | Any patch applied | YAML `version` field |

### Ineligible Changes (Must OPTIMIZE)

- Structural section changes (add/remove phases)
- Output contract changes
- Security baseline changes
- Any change touching Red Lines

### Patch Application

1. **PROPOSE** — AI describes the patch and reason to the user
2. **CONFIRM** — User approves or rejects
3. **APPLY** — AI applies the change
4. **VERIFY** — Run LEAN eval on patched version; rollback if score drops > 10 pts

---

## §6  Safety Constraints

| Constraint | Rule |
|-----------|------|
| No mid-session modification | Propose patches; never apply during active task |
| User confirmation required | All patches require explicit user approval |
| Rollback always available | Pre-patch version can be restored |
| Structural changes blocked | Only trigger keywords and metadata eligible |
| Security scan required | Check for P0 patterns before applying any patch |
| Patch size limit | Max 5 micro-patches per skill per session |
| Edit guard integration | All UTE patches are MICRO class; structural changes escalate to OPTIMIZE (see `refs/edit-audit.md`) |

---

## §7  UTE 2.0 — Two-Tier Architecture

UTE operates at two tiers. Both tiers share the same feedback signals and micro-patch
protocol; they differ in *scope* (single-user vs. multi-user) and *persistence requirements*.

### L1: Single-User UTE (current)

- **Scope**: One user, one session, one skill
- **Enforcement**: `[CORE]` — runs fully within a single LLM session
- **Trigger source**: Feedback signals observed in the current conversation
- **Output**: Micro-patch proposals (keywords/metadata) or OPTIMIZE queue entries
- **State**: Session-local only; no cross-session persistence required

This is the complete implementation described in §1–§6 above.

---

## §7b  GitHub Gist Backend `[AVAILABLE — zero infrastructure]`

> **Why Gist?** UTE L2 cross-session tracking requires a persistent counter store,
> but most deployments don't have SQLite, Redis, or a custom API. GitHub Gist is
> free, requires only a personal access token (scope: `gist`), and stores structured
> JSON that any Claude session can read via the GitHub API.
>
> This upgrades `cumulative_invocations`, `cadence_events`, and artifact storage
> from `[EXTENDED]` (session-local) to near-`[CORE]` (persisted cross-session)
> with **zero server setup**.

### Setup (5 minutes)

```bash
# 1. Install (requests is optional; script falls back to urllib)
pip install requests   # optional — improves error messages

# 2. Set your GitHub token (scope: gist)
export GITHUB_TOKEN=ghp_your_token_here

# 3. Initialize a UTE state Gist for your skill
python3 scripts/ute_gist_backend.py init --skill my-skill --lean-score 380
#  ✓ Creates: https://gist.github.com/<your-gist-id>  (private)

# 4. Add the Gist ID to your skill's YAML frontmatter
#    use_to_evolve:
#      gist_id: "<returned-gist-id>"
```

### Daily Operations

```bash
# After each skill invocation (call from a PostToolUse hook or manually):
python3 scripts/ute_gist_backend.py record --skill my-skill
# Returns exit 2 when a cadence event fires (health check due)

# Check current state and pending events:
python3 scripts/ute_gist_backend.py status --skill my-skill

# After running COLLECT mode, store the session artifact:
python3 scripts/ute_gist_backend.py add-artifact --skill my-skill --artifact session.json

# When you have 2+ artifacts, export for AGGREGATE mode:
python3 scripts/ute_gist_backend.py export-artifacts --skill my-skill --out artifacts/
# Then: paste artifacts/my-skill-artifacts-all.json into AGGREGATE mode
```

### Enforcement status with Gist backend

| UTE Item | Without Gist | With Gist backend |
|----------|-------------|-------------------|
| `cumulative_invocations` persistence | `[EXTENDED]` — resets | `[CORE]` — Gist-persisted |
| Cadence checks (10/50/100) | `[EXTENDED]` — approximate | `[CORE]` — count-gated |
| Session artifact storage | `[EXTENDED]` — manual | `[CORE]` — API-persisted |
| Patch history log | `[EXTENDED]` — session-only | `[CORE]` — Gist-logged |
| Multi-user collective (L2) | `[EXTENDED]` — not supported | `[EXTENDED]` — share Gist URL with team |

### Limitations vs. full L2 backend

- **Gist rate limits**: GitHub's API rate limit is 5,000 requests/hr per token — adequate
  for cadence-gated recording (not real-time per-message tracking)
- **Concurrent writes**: If multiple agents run simultaneously, use `record --skill` sequentially.
  Gist does not have write locking — concurrent updates may lose counts.
- **Team sharing**: Share the Gist URL with teammates for read-only dashboards; each team
  member should have their own Gist for write access.
- **Max artifact storage**: Script caps at 50 stored artifacts per Gist to stay within
  GitHub's 1 MB Gist size limit.

> Full script: `scripts/ute_gist_backend.py`

---

## §8  Platform Hook Integration `[ENFORCED with hooks backend]`

> This section upgrades UTE's `[EXTENDED]` cross-session items to `[CORE]` by
> wiring them to the host platform's hook system. Currently documented for **Claude Code**
> (session hooks). The same pattern applies to any platform that exposes pre/post-session hooks.

### What Changes With Hooks

| UTE Item | Without Hooks | With Hooks |
|----------|--------------|-----------|
| `cumulative_invocations` counter | `[EXTENDED]` — resets per session | `[CORE]` — persisted to file |
| Cadence checks (every 10/50/100) | `[EXTENDED]` — approximate | `[CORE]` — precise count-gated |
| `last_ute_check` / `pending_patches` | `[EXTENDED]` — cross-session state lost | `[CORE]` — read/written via hook |
| Audit trail in `.skill-audit/` | `[EXTENDED]` — requires filesystem | `[CORE]` — hook writes on session end |

### Claude Code Hook Setup

#### 1. Create the UTE state file

For each UTE-enabled skill, create a JSON state file alongside the skill:

```bash
# Example: for a skill at ~/.claude/skills/my-skill.md
touch ~/.claude/skills/.ute-state/my-skill.json
```

Initial state file contents:
```json
{
  "skill_name": "my-skill",
  "skill_path": "~/.claude/skills/my-skill.md",
  "cumulative_invocations": 0,
  "last_ute_check": null,
  "pending_patches": 0,
  "total_micro_patches_applied": 0,
  "certified_lean_score": 390,
  "session_log": []
}
```

#### 2. Register a Claude Code PostToolUse hook

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "node ~/.claude/hooks/ute-tracker.js post-use \"$CLAUDE_SKILL_NAME\""
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node ~/.claude/hooks/ute-tracker.js session-end"
          }
        ]
      }
    ]
  }
}
```

#### 3. ute-tracker.js — Minimal hook script

Create `~/.claude/hooks/ute-tracker.js`:

```javascript
#!/usr/bin/env node
// UTE state persistence hook for Claude Code
// Upgrades [EXTENDED] cross-session tracking to [CORE]

const fs = require('fs');
const path = require('path');

const STATE_DIR = path.join(process.env.HOME, '.claude', 'skills', '.ute-state');
const cmd = process.argv[2];       // 'post-use' | 'session-end'
const skillName = process.argv[3]; // skill identifier from env

function readState(name) {
  const file = path.join(STATE_DIR, `${name}.json`);
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writeState(name, state) {
  fs.mkdirSync(STATE_DIR, { recursive: true });
  const file = path.join(STATE_DIR, `${name}.json`);
  fs.writeFileSync(file, JSON.stringify(state, null, 2));
}

if (cmd === 'post-use' && skillName) {
  const state = readState(skillName) || { cumulative_invocations: 0, session_log: [] };
  state.cumulative_invocations += 1;

  // Cadence gate: log when thresholds hit
  const inv = state.cumulative_invocations;
  if (inv % 10 === 0)  state.session_log.push({ at: new Date().toISOString(), event: 'lightweight_check_due', inv });
  if (inv % 50 === 0)  state.session_log.push({ at: new Date().toISOString(), event: 'quality_assessment_due', inv });
  if (inv % 100 === 0) state.session_log.push({ at: new Date().toISOString(), event: 'tier_drift_check_due', inv });

  writeState(skillName, state);
}

if (cmd === 'session-end') {
  // Write session summary to audit trail
  const auditDir = path.join(process.env.HOME, '.claude', '.skill-audit');
  fs.mkdirSync(auditDir, { recursive: true });
  const entry = { session_end: new Date().toISOString(), skills_active: skillName || 'unknown' };
  const auditFile = path.join(auditDir, 'sessions.jsonl');
  fs.appendFileSync(auditFile, JSON.stringify(entry) + '\n');
}
```

#### 4. How Claude reads UTE state at session start

In your system prompt or session-start hook, inject the current state:

```bash
# Add to ~/.claude/hooks/session-start.sh
SKILL_STATE=$(cat ~/.claude/skills/.ute-state/my-skill.json 2>/dev/null || echo '{}')
echo "UTE_STATE: $SKILL_STATE" >> /tmp/claude-session-context.txt
```

Then reference in `~/.claude/CLAUDE.md`:
```markdown
At session start, read /tmp/claude-session-context.txt.
If UTE_STATE contains `session_log` entries with `_due` events,
notify the user and offer to run the corresponding UTE health check.
```

### Enforcement Status After Hook Integration

With the above setup, these items upgrade from `[EXTENDED]` to `[CORE]`:

| Item | New Status |
|------|-----------|
| `cumulative_invocations` persistence | `[CORE]` — written by PostToolUse hook |
| Cadence check notifications | `[CORE]` — session_log entries trigger next-session prompt |
| `last_ute_check` update | `[CORE]` — written by session-end hook |
| Audit trail | `[CORE]` — sessions.jsonl append on Stop |

**Remaining `[EXTENDED]` items** (require L2 collective infrastructure):
- Multi-user artifact aggregation (collective-evolution design / reinforcement-style evolution design collective pipeline)
- Cross-skill tier drift monitoring (requires shared registry backend)

---

### L2: Collective UTE `[EXTENDED]`

> **`[EXTENDED]`**: L2 requires external storage and the COLLECT + AGGREGATE pipeline.
> See `refs/session-artifact.md` and `skill-framework.md §17` for full spec.

- **Scope**: Multiple users, multiple sessions, one skill (or skill cluster)
- **Enforcement**: `[EXTENDED]` — requires Session Artifact storage and AGGREGATE pipeline
- **Trigger source**: Aggregated patterns from N session artifacts
- **Output**: Evidence-backed evolution proposals (stronger signal than single-session L1)
- **State**: Persistent storage (`sessions/` directory in shared storage backend)

**Key insight** (from collective-evolution design research): L2 collective evolution produces measurably better
skills than L1 single-user optimization — not because of bigger models, but because broader
usage data reveals blind spots that single-user testing misses.

### Relationship between tiers

```
Single user interacts with skill
         │
         ▼
L1 UTE fires (every session)
   ├─ Detect feedback signals
   ├─ Propose micro-patches
   └─ Generate Session Artifact (if COLLECT mode active)
         │
         ▼ (optional, requires backend)
L2 Collective pipeline
   ├─ Session Artifact → sessions/ queue
   ├─ AGGREGATE (Summarize → Aggregate → Execute)
   └─ Cross-user evolution proposals → stronger OPTIMIZE suggestions
```

### L2 Minimum Viable Flow (no backend required)

Even without an external backend, L2 benefits are accessible manually:

1. User runs COLLECT mode after each session → downloads Session Artifact JSON
2. After N sessions (or across multiple users sharing artifacts): paste artifacts into AGGREGATE mode
3. AGGREGATE synthesizes cross-session patterns into ranked improvement list
4. Apply improvements via standard OPTIMIZE mode

This manual flow degrades gracefully to near-L2 quality with zero infrastructure cost.

---

## §11  R-Few Anchor-Calibrated Evolution (v3.6.0) `[CORE]`

> **Research basis**: Wu et al. 2025, *"Guided Self-Evolving Alignment Without Explicit
> Human Annotation"* (arXiv:2512.02472, December 2025). R-Few uses 1–5% "anchor"
> human-annotated data to guide self-play evolution loops, achieving near-RLHF performance
> with near-zero annotation budget. The anchor set acts as a calibration ground truth —
> preventing self-evolution from drifting into local optima that feel correct to the model
> but fail real user needs.

### §11.1  Anchor Set Concept

An **anchor set** is a small, curated collection of ground-truth skill invocations:
```
Anchor: {input, expected_output, quality_rating: 1–5}
Minimum: 3 anchors  (viable floor)
Target:  5–10 anchors (1–5% of expected total invocations)
Source:  manually curated by the skill author or power users
```

**Why anchors matter for UTE**: Without anchors, UTE L1 micro-patches may optimize for
the feedback signals of a single power user — drifting away from the skill's documented
purpose. Anchors act as a fixed evaluation point that each patch must satisfy.

### §11.2  Anchor-Calibrated Micro-Patch Protocol

Replace standard §5 Micro-Patch Protocol with the calibrated version when
anchors are available:

```
ANCHOR-CALIBRATED PATCH (replaces standard §5 when anchor_set is present):

1. PROPOSE    — AI describes the patch and reason (same as standard §5)
2. PRE-CHECK  — Score patch against anchor set BEFORE user confirmation:
                For each anchor {input, expected_output}:
                  Predict: would the patched skill produce output ≥ expected_quality?
                  Score: anchor_pass_rate = passing_anchors / total_anchors
3. GATE       — If anchor_pass_rate < 0.67 (< 2/3 anchors pass):
                → Reject the patch automatically
                → Report: "Patch rejected: fails {N} of {M} anchor cases.
                           Failing anchors: [list]"
                → Propose alternative patch or escalate to OPTIMIZE
4. CONFIRM    — (only if anchor_pass_rate ≥ 0.67) Present to user for approval
5. APPLY      — Apply with user confirmation (same as standard §5)
6. POST-CHECK — Run LEAN eval + anchor re-score on patched version
                If LEAN drops > 10 pts OR anchor_pass_rate drops: rollback
```

### §11.3  Anchor Set Storage

```yaml
# Add to skill YAML frontmatter when anchors are established
ute_anchors:
  established_at: "2026-04-28"
  count: 5
  source: "author-curated"        # author-curated | user-contributed | mixed
  anchor_file: ".skill-anchors.json"  # companion file; same dir as skill
  min_pass_rate: 0.67             # minimum anchor pass rate for any patch
```

Anchor file format (`.skill-anchors.json`):
```json
{
  "skill": "<name>",
  "version": "<semver>",
  "anchors": [
    {
      "id": "anchor-001",
      "input": "create a skill that summarizes git diffs",
      "expected_output_contains": ["skill_tier", "triggers", "## §1"],
      "quality_rating": 5,
      "added_by": "author",
      "added_at": "2026-04-28"
    }
  ]
}
```

### §11.4  When to Use Anchor-Calibrated Evolution

| Situation | Action |
|-----------|--------|
| Skill has 0 anchors | Use standard §5 protocol; gather anchors over time |
| Skill has 3–4 anchors | Use anchor-calibrated protocol (viable but limited) |
| Skill has 5+ anchors | Full R-Few anchor calibration — highest confidence |
| UTE has > 5 patches without anchors | Create anchors before applying more patches (anti-pattern L1) |
| Meta-skill or planning tier | Create anchors; disable micro_patch_enabled (anti-pattern L3) |

---

## §12  SoK Skill Taxonomy for UTE Scoping (v3.6.0)

> **Research basis**: SoK: Agentic Skills (arXiv:2602.20867, February 2026). Systematization
> of 60+ agentic skill systems. Establishes formal taxonomy: Atomic → Composite → Adaptive → Meta.
> Key finding: skill evolution strategies must match the skill type — evolving a Meta-Skill
> the same way as an Atomic Skill causes cascading failures.

### §12.1  Taxonomy Mapping to UTE Configuration

| SoK Type | skill_tier Equivalent | UTE Micro-Patch Scope | Full OPTIMIZE Trigger |
|----------|----------------------|----------------------|----------------------|
| **Atomic** (single API call) | `atomic` | Constraint wording, rejection examples | New mode or workflow phase |
| **Composite** (multi-step) | `functional` | Trigger keywords, output schema | Structural section changes |
| **Adaptive** (context-dependent) | `functional` with context flags | Trigger coverage per context | Core routing logic changes |
| **Meta** (creates/manages skills) | `planning` | NONE — micro-patches disabled | Requires HUMAN_REVIEW |

### §12.2  Skill Type Detection Heuristics

If `skill_tier` is set, use it. Otherwise, use these heuristics to infer SoK type:

```
Heuristic detection:
  IF skill body has 1 mode + no sub-skill delegation → Atomic
  IF skill body has 2+ modes + no sub-skill delegation → Composite/Functional
  IF skill body has conditional routing based on context → Adaptive
  IF skill body contains "create skill", "invoke [skill-name]", "delegate to" → Meta
```

### §12.3  UTE Configuration by Taxonomy

Add to `use_to_evolve:` block:
```yaml
use_to_evolve:
  enabled: true
  skill_type: "composite"   # atomic | composite | adaptive | meta
  # For meta-type: micro_patch_enabled MUST be false
  # For adaptive: set context_aware_triggers: true
  micro_patch_enabled: true   # false for meta-type
  feedback_detection: true
  anchor_calibration: false   # true when ute_anchors: block is present
```

**Validation rule**: If `skill_type: meta` AND `micro_patch_enabled: true` → EVALUATE
Phase 4 emits ERROR (anti-pattern L3). Fix: set `micro_patch_enabled: false`.
