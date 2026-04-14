# Skill Registry Specification

> **Purpose**: Canonical format for skill identity, versioning, and shared distribution.
> **Load**: When §16 (INSTALL / SHARE) of `claude/skill-writer.md` is accessed.
> **Inspired by**: SkillClaw's skill registry with deterministic IDs and version history.
> **Enforcement**: `[CORE]` for ID generation and format; `[EXTENDED]` for remote sync.
> **v3.1.0**: Added `skill_tier` and `triggers` fields to registry entry; schema_version bumped to 1.1.

---

## §1  Concept

The Skill Registry provides:
1. **Deterministic identity** — each skill has a stable ID derived from its name
2. **Version history** — up to 20 recent versions tracked per skill
3. **Distribution metadata** — enables push/pull/sync across teams and backends
4. **Conflict resolution** — SHA-256 comparison + merge protocol for concurrent edits

The registry is the backbone of the SHARE mode (push/pull skills to cloud storage).

---

## §2  Skill ID Scheme

Every skill has a deterministic ID based on its canonical name:

```
skill_id = SHA-256(skill_name)[:12]   (lowercase hex)

Examples:
  "api-tester"    → SHA-256("api-tester")[:12]    = "a1b2c3d4e5f6"
  "code-reviewer" → SHA-256("code-reviewer")[:12] = "7f8a9b0c1d2e"
  "doc-generator" → SHA-256("doc-generator")[:12] = "3e4f5a6b7c8d"
```

**Properties**:
- Same name always produces the same ID — enables idempotent push/pull
- 12 hex characters = 48 bits — collision probability negligible for skill libraries < 10M skills
- Compatible with SkillClaw's registry format

### Adding `skill_id` to YAML frontmatter

When a skill is registered (on first SHARE push or explicit registration), add to frontmatter:

```yaml
skill_id: "a1b2c3d4e5f6"   # SHA-256(name)[:12]
```

**AI approximation** `[ENFORCED via convention]`: Since AI cannot compute SHA-256, use
this deterministic abbreviation: take the first 12 characters of
`base64(skill_name).replace(/[^a-z0-9]/g, '').toLowerCase()`. This is a stable
approximation sufficient for local tracking; true SHA-256 is computed server-side on push.

---

## §3  Registry File Format

The registry is stored as `registry.json` in the shared storage root:

```json
{
  "schema_version": "1.1",
  "registry_updated": "<ISO-8601>",
  "skills": [
    {
      "id": "a1b2c3d4e5f6",
      "name": "api-tester",
      "current_version": "1.2.0",
      "created_at": "2026-04-01",
      "updated_at": "2026-04-10",
      "certified_tier": "GOLD",
      "lean_score": 920,
      "skill_tier": "functional",
      "triggers": {
        "en": ["test api", "call endpoint", "check api response"],
        "zh": ["测试接口", "调用API"]
      },
      "usage_stats": {
        "total_invocations": 47,
        "successful_invocations": 44,
        "success_rate": 0.936,
        "trigger_phrase_counts": {
          "test api": 18,
          "call endpoint": 12,
          "check api response": 9,
          "verify api": 8
        },
        "last_invoked": "2026-04-13",
        "prm_distribution": { "good": 38, "ok": 6, "poor": 3 }
      },
      "platforms": ["claude", "opencode", "openclaw"],
      "tags": ["api", "testing", "http"],
      "history": [
        {
          "version": "1.2.0",
          "score": 920,
          "tier": "GOLD",
          "skill_tier": "functional",
          "date": "2026-04-10",
          "change_summary": "Added retry logic and ZH trigger support",
          "sha256": "<SHA-256 of skill file content>"
        },
        {
          "version": "1.1.0",
          "score": 895,
          "tier": "GOLD",
          "skill_tier": "functional",
          "date": "2026-04-05",
          "change_summary": "Improved error handling section",
          "sha256": "<SHA-256 of skill file content>"
        }
      ]
    }
  ]
}
```

**History limit**: Maximum 20 entries per skill. When the 21st version is added, drop the oldest entry.

---

## §4  Storage Layout

```
storage-root/
├── registry.json              # Master skill registry
├── skills/                    # Published skill files
│   ├── a1b2c3d4e5f6/          # One directory per skill_id
│   │   ├── current.md         # Latest version (symlink or copy)
│   │   ├── v1.2.0.md          # Pinned versions
│   │   ├── v1.1.0.md
│   │   └── v1.0.0.md
│   └── 7f8a9b0c1d2e/
│       ├── current.md
│       └── v2.0.0.md
└── sessions/                  # COLLECT mode session artifacts (see refs/session-artifact.md)
    └── 2026-04-11-a3f9c2.json
```

**Supported backends** `[EXTENDED]`:
- `local://`  — local filesystem (default; zero config)
- `s3://`     — AWS S3 or any S3-compatible store
- `oss://`    — Alibaba Cloud OSS
- `http://`   — custom REST API implementing the SHARE protocol

---

## §5  SHARE Protocol — CLI Commands

The SHARE mode extends INSTALL with remote synchronization:

```
# Push local skill to shared storage
skillclaw push <skill-file.md> --storage <backend-url>

# Pull skill from shared storage by name or ID
skillclaw pull <skill-name-or-id> --storage <backend-url>

# Two-way sync: push updated skills, pull newer versions
skillclaw sync --storage <backend-url>

# Browse available skills in shared registry
skillclaw list --storage <backend-url> [--tag <tag>] [--tier <tier>]
```

### Push workflow

```
1. READ   — load local skill file and extract frontmatter
2. ENSURE — generate or verify skill_id (§2)
3. SCORE  — run LEAN eval; include score in registry entry
4. COMPARE — fetch registry.json from backend
   IF skill_id exists in registry:
     COMPARE sha256 of current.md vs local file
     IF different → conflict detected → §6 conflict resolution
     IF same → "already up to date"
   ELSE:
     INSERT new entry into registry
5. UPLOAD — write skill file to skills/<skill_id>/v<version>.md
6. UPDATE — update registry.json with new version entry
7. REPORT — show "pushed <name> v<version> → <backend>"
```

### Pull workflow

```
1. LOOKUP — search registry.json by name or id
2. SELECT — choose version (default: current)
3. DOWNLOAD — fetch skills/<skill_id>/v<version>.md
4. INSTALL — write to local platform skills directory (§16 INSTALL mode)
5. REPORT — show "pulled <name> v<version> from <backend>"
```

---

## §6  Conflict Resolution Protocol

When two users push different versions of the same skill concurrently:

```
CONFLICT DETECTED
  Local  SHA-256: <hash_a>
  Remote SHA-256: <hash_b>
  Skill: <name> v<version>

Resolution strategy:
  1. DIFF — show structural diff: which §-sections changed in each version
  2. ASSESS — AI assesses which changes are complementary vs. conflicting:
       Complementary: version A adds Error Handling; version B adds ZH triggers
       Conflicting:   both versions rewrote the Workflow section differently

  3a. IF complementary → AUTO-MERGE:
       Merge additive changes; use higher-scoring version's core content
       Run LEAN eval on merged result; if score ≥ min(A_score, B_score) → accept

  3b. IF conflicting → HUMAN-MERGE:
       Present both versions to user
       User selects which sections to keep from each
       AI applies selections and runs LEAN eval

  4. PUSH merged version as next patch version (e.g., v1.2.1)
  5. LOG conflict event in registry entry
```

---

## §7  Version Compatibility with Existing YAML

Skills already using the skill-writer format add `skill_id` as an optional field.
No breaking changes to existing skills.

```yaml
# Existing fields (required)
name: api-tester
version: "1.2.0"

# Registry field (added on first registry push)
skill_id: "a1b2c3d4e5f6"

# v3.1.0: new classification fields (added on first push for new skills;
#          added to existing skills on next OPTIMIZE cycle or explicit re-register)
skill_tier: "functional"          # planning | functional | atomic (SkillX tier)
triggers:
  en: ["test api", "call endpoint", "check api response"]
  zh: ["测试接口", "调用API"]
```

**Migration**: Run `skillclaw register` on existing skills to compute and inject `skill_id`.
For `skill_tier` and `triggers`: populated automatically from YAML frontmatter on push.
Existing skills without these fields receive an advisory warning; they are not rejected.

**Schema version history**:
- `1.0`: Original — id, name, version, tier, score, platforms, tags, history
- `1.1` (v3.1.0): Added `skill_tier`, `triggers` at registry entry level; added `skill_tier` to history entries
- `2.0` (v3.2.0): Added top-level `graph` object with `edges[]` and `bundles[]` arrays (Graph of Skills)

---

## §8  Semantic Versioning — Breaking Change Matrix

> **Research basis**: Community data shows 60% of production agent failures are caused by
> unversioned tool / skill changes. This matrix defines what constitutes a MAJOR (breaking)
> vs. MINOR vs. PATCH change in a skill, so consumers can safely pin versions.

### Version Bump Rules

```
MAJOR.MINOR.PATCH
```

| Change Type | Version Bump | Breaking? | Rationale |
|-------------|-------------|-----------|-----------|
| **Trigger keyword removed** | MAJOR | ✅ Yes | Consumers relying on that phrase will fail to route |
| **Trigger keyword renamed** | MAJOR | ✅ Yes | Effectively: remove old + add new |
| **Output format changed** (new fields, removed fields, type change) | MAJOR | ✅ Yes | Downstream consumers depend on output schema |
| **Mode removed** | MAJOR | ✅ Yes | Workflows invoking that mode will fail |
| **Red Line added** (stricter constraint) | MAJOR | ✅ Yes | Existing callers may now be blocked |
| **Interface.modes changed** | MAJOR | ✅ Yes | Mode routing contract is broken |
| **New trigger keyword added** | MINOR | No | Extends coverage; backward compatible |
| **New optional mode added** | MINOR | No | Existing modes unchanged |
| **New output field added** (additive) | MINOR | No | Existing consumers can ignore new fields |
| **Security baseline tightened** (advisory → P1) | MINOR | No | More conservative; safe for consumers |
| **Workflow step added within a mode** | MINOR | No | Output contract unchanged |
| **Example updated** | PATCH | No | Documentation only |
| **Trigger keyword added (ZH equivalent)** | PATCH | No | Extends coverage, no removals |
| **Metadata fields updated** (description, author, dates) | PATCH | No | No behavioral change |
| **Bug fix** (incorrect output corrected) | PATCH | No | Improves correctness |
| **UTE cadence thresholds adjusted** | PATCH | No | Internal optimization behavior |

### MAJOR Version Announcement Protocol

When a MAJOR version is published:

1. **Changelog entry** — document every breaking change with old behavior vs. new behavior
2. **Migration guide** — provide exact changes consumers must make to stay compatible
3. **Deprecation period** — keep the previous MAJOR version in the registry for ≥ 30 days
4. **Consumers pinned to old version** — do NOT receive automatic updates; must opt in

```yaml
# Registry entry for a breaking change
{
  "version": "2.0.0",
  "change_summary": "BREAKING: Removed SCAN mode; merged into REVIEW mode. Update callers to use mode=REVIEW with scan=true parameter.",
  "breaking_changes": [
    "mode SCAN removed — use REVIEW with {scan: true}",
    "output field 'scan_result' renamed to 'security_findings'"
  ],
  "migration_guide": "https://github.com/.../MIGRATION-v2.md"
}
```

### Skill Tier Change Rules

`skill_tier` changes require special handling:

| Tier Change | Version Bump | Note |
|-------------|-------------|------|
| `atomic` → `functional` | MINOR | Skill gained new capabilities; backward compatible |
| `functional` → `planning` | MINOR | Higher-level orchestration added |
| `planning` → `functional` | MAJOR | Scope reduction — may remove orchestration capabilities |
| `functional` → `atomic` | MAJOR | Scope reduction — callers expecting rich workflow may fail |

---

## §10  Graph of Skills — Schema v2.0

> **v3.2.0 addition**. Research basis: SkillNet (arxiv:2603.04448), GoS bundle retrieval,
> SkillX tier hierarchy (arxiv:2604.04804).
> **Backward compatible**: existing v1.x registries work unchanged; `graph` key is optional.
> Full specification: `claude/refs/skill-graph.md`

### §10.1  Registry v2.0 Format Extension

Schema v2.0 adds a top-level `graph` object alongside `skills[]`:

```json
{
  "schema_version": "2.0",
  "registry_updated": "<ISO-8601>",
  "skills": [ /* ... same as v1.1 ... */ ],

  "graph": {
    "edges": [
      {
        "from":          "a1b2c3d4e5f6",
        "to":            "7f8a9b0c1d2e",
        "type":          "depends_on",
        "weight":        1.0,
        "required":      true,
        "auto_inferred": false,
        "confidence":    1.0,
        "added_at":      "<ISO-8601>",
        "added_by":      "skill-writer-v3.2.0 | aggregate | user"
      }
    ],
    "bundles": [
      {
        "bundle_id":    "bnd-api-testing",
        "name":         "API Testing Suite",
        "description":  "End-to-end API testing: schema validation → execution → reporting",
        "skills":       ["a1b2c3d4e5f6", "7f8a9b0c1d2e", "3e4f5a6b7c8d"],
        "entry_point":  "a1b2c3d4e5f6",
        "created_at":   "<ISO-8601>",
        "auto_composed": false
      }
    ]
  }
}
```

### §10.2  Edge Types (canonical — from `builder/src/config.js GRAPH_EDGE_TYPES`)

| Type | Direction | Meaning | Which Tier Uses It |
|------|-----------|---------|-------------------|
| `depends_on` | A → B | A requires B to be available before execution | functional, planning |
| `composes` | A → [B,C,D] | A orchestrates B, C, D as sub-skills | planning only |
| `similar_to` | A ↔ B | A and B are functionally similar; may substitute | any |
| `uses_resource` | A → R | A reads a companion resource file | any |
| `provides` | A → type | A outputs a named data type | any |
| `consumes` | A → type | A requires a named input data type | any |

### §10.3  Auto-Inference from COLLECT Artifacts

The AGGREGATE pipeline (`/collect` → `aggregate skill feedback`) reads `bundle_context`
fields in Session Artifacts and infers graph edges:

```
Rule 1 — Co-invocation:
  IF ≥ 80% of artifacts show skill A and B invoked in same session
  → Propose edge: A depends_on B  (confidence = co_invocation_rate)
  → Mark: auto_inferred: true

Rule 2 — Data Flow:
  IF ≥ 60% of artifacts show A.provides → B.consumes match
  → Propose edge: A provides type; B consumes type
  → Create directed edge: A → B (type: depends_on, weight: flow_rate)

Rule 3 — Merge Advisory:
  IF similar_to similarity > 0.95
  → GRAPH-004 warning; DO NOT auto-merge; present to user for confirmation
```

### §10.4  Bundle Lifecycle

```
/graph plan [task description]
     ↓
Resolve bundle via builder/src/core/graph.js resolveBundle()
     ↓
Bundle entry saved to registry graph.bundles[]
     ↓
/install --bundle bnd-xxx  → installs all bundle skills in topological order
     ↓
Bundle usage tracked in Session Artifact bundle_context.bundle_id
```

### §10.5  Migration: v1.x → v2.0

No breaking changes. To upgrade an existing registry:

```bash
# Add empty graph section to registry.json
node -e "
const fs = require('fs');
const r = JSON.parse(fs.readFileSync('registry.json'));
if (!r.graph) r.graph = { edges: [], bundles: [] };
r.schema_version = '2.0';
fs.writeFileSync('registry.json', JSON.stringify(r, null, 2));
"
```

Skills that have `graph:` blocks in their YAML frontmatter will have their edges
populated automatically on the next `skillclaw push` or `/install` command.

---

## §9  Integration with SkillClaw

Skills published via the SHARE registry are directly consumable by a SkillClaw
deployment. The `skills/` directory layout and `registry.json` format are intentionally
compatible with SkillClaw's storage spec.

| SkillClaw concept | skill-writer registry equivalent |
|-------------------|----------------------------------|
| `skills/` directory | `skills/<skill_id>/` |
| Deterministic skill ID | `SHA-256(name)[:12]` |
| Version history | `history[]` array (20-entry limit) |
| SHA-256 conflict detection | `sha256` field per version entry |
| LLM-based merge | Conflict Resolution Protocol (§6) |

---

## §11  SkillRouter — Weighted Ranking & Quality Gate (v3.3.0)

> **Research basis**: 得物 AI Coding component reuse practice (2026) — multi-factor weighted
> ranking with quality threshold gate prevents AI from "going with wrong result" (将错就错).
> Extends the existing SkillRouter (91.7% cross-encoder accuracy) with usage-signal weighting.

### §11.1  Ranking Formula

When multiple skills match a user query, rank candidates by:

```
rank(skill) =
    trigger_match_score  × 0.40   // exact/fuzzy match against triggers.en/zh
  + lean_score_normalized × 0.30  // lean_score / 520 (max LEAN+D8 score)
  + usage_frequency_score × 0.20  // log(total_invocations + 1) / log(MAX_INVOCATIONS + 1)
  + source_quality_score  × 0.10  // see §11.2

where:
  trigger_match_score:
    1.0  = exact phrase match (e.g. "test api" matches trigger "test api")
    0.8  = token overlap ≥ 80%
    0.6  = acronym expansion match (e.g. "dlp" → "DateLinkPicker")
    0.4  = semantic match via cross-encoder (existing SkillRouter behavior)
    0.0  = no match

  lean_score_normalized: lean_score / 520.0  (clamp to [0.0, 1.0])

  usage_frequency_score: log(usage_stats.total_invocations + 1) / log(MAX_INVOCATIONS + 1)
    MAX_INVOCATIONS = 500  (normalizes across typical skill library sizes)
    Falls back to 0.0 if usage_stats is absent (new or untracked skills)

  source_quality_score: see §11.2
```

### §11.2  Source Quality Weights

| Source | Score | Rationale |
|--------|-------|-----------|
| User-authored, GOLD/PLATINUM certified | 1.0 | Highest trust — human-verified |
| User-authored, SILVER certified | 0.8 | High quality, minor gaps possible |
| User-authored, BRONZE certified | 0.6 | Usable, may need optimization |
| Registry-pulled, stable tag | 0.9 | Team-vetted, stable |
| Registry-pulled, beta tag | 0.7 | Community-reviewed |
| Registry-pulled, experimental tag | 0.4 | Low trust — evaluate before relying on |
| Auto-generated (CREATE without LEAN) | 0.2 | Unvalidated — treat as draft |

### §11.3  Quality Threshold Gate

**Purpose**: Prevent the AI from "going with wrong result" — if no candidate scores
above the minimum threshold, return `noMatch` rather than the best low-quality hit.

```
QUALITY_THRESHOLD = 0.35  (configurable per team via registry.config.router_threshold)

IF max(rank) < QUALITY_THRESHOLD:
  → Return: { status: "noMatch", reason: "best_match_score_below_threshold",
              best_score: <score>, best_candidate: <name> }
  → AI MUST NOT use the low-ranked skill; escalate to user or CREATE new skill

IF max(rank) ≥ QUALITY_THRESHOLD:
  → Return top candidate; include rank score in response metadata

IF rank_1 - rank_2 < 0.05  (top two candidates too close):
  → Show disambiguation: "Found 2 similar skills — which did you mean?"
    (a) <skill_1_name>  [score: X, tier: Y]
    (b) <skill_2_name>  [score: X, tier: Y]
```

### §11.4  Trigger Phrase Discovery via Session Artifacts

The AGGREGATE pipeline feeds observed user phrases back into `trigger_phrase_counts`
and proposes new canonical triggers (see `refs/session-artifact.md §8 Rule 4`).

When a phrase appears in `trigger_phrase_counts` but NOT in `triggers.en`:
```
IF trigger_phrase_counts[phrase] ≥ 5 AND
   phrase_match_score_without_trigger < 0.60:
  → Propose: add "<phrase>" to triggers.en
  → Present to user for confirmation before updating registry
```

This closes the feedback loop: usage patterns → trigger discovery → routing quality improvement.

### §11.5  `usage_stats` Field Spec

Added to each skill entry in `registry.json` (schema v1.1+):

```json
"usage_stats": {
  "total_invocations":     <int>,    // cumulative invocation count
  "successful_invocations":<int>,    // outcome == "success" count
  "success_rate":          <float>,  // successful / total (0.0–1.0)
  "trigger_phrase_counts": {         // observed user phrasing → count
    "<phrase>": <int>
  },
  "last_invoked": "<ISO-8601-date>",
  "prm_distribution": {             // from session artifacts prm_signal
    "good": <int>,
    "ok":   <int>,
    "poor": <int>
  }
}
```

**Update rules** `[EXTENDED — requires AGGREGATE pipeline]`:
- `total_invocations`: incremented by 1 per session artifact processed
- `trigger_phrase_counts[trigger_used]`: incremented by 1 per artifact
- `success_rate`: recomputed on each AGGREGATE run
- `last_invoked`: set to artifact `recorded_at` date
- `prm_distribution`: tallied from artifact `prm_signal` field

**Fallback** `[CORE]`: When no AGGREGATE backend is available, the AI MAY manually
update `usage_stats` at session end if the user runs `/collect` and confirms the update.
