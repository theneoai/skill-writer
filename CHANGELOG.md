# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 2026-04-17 — skill-creator design review (`claude/review-skill-creator-design-8ZK8R`)

Full punch list from a head-to-head comparison with Anthropic's `skill-creator`.
Seven P-priority items addressed; no breaking changes to installed skills.

#### Real trigger-accuracy evaluation (breaks generator bias)
- `scripts/run_trigger_eval.py` — classifies each query against the skill's
  `(name, description)` via the Anthropic API, majority-votes over N runs,
  reports precision / recall / f1 / accuracy. Handles the Cursor MDC dual
  frontmatter case.
- `scripts/optimize_description.py` — iterative description tuner with 60/40
  train/test split; selects the best candidate by test-f1 to prevent rubric
  overfit. Matches the pattern in Anthropic skill-creator's `run_loop.py`.
- `scripts/aggregate_benchmark.py` — aggregates grader outputs to
  `benchmark.json` + `benchmark.md`.
- `agents/grader.md` — independent grader prompt (fresh context, strict JSON
  output contract). The only mechanism in the repo that actually isolates
  evaluation from generation.
- `eval/trigger-eval.example.json` — 20-query starter set (10 should-trigger,
  10 should-not-trigger, bilingual).
- CREATE mode gains a **test-first sub-phase** between PLAN and GENERATE.
  Skills delivered without a real trigger eval are flagged
  `validation_status: lean-only` and SHARE mode blocks them until `/eval` runs.

#### Canonical skill slimmed (2541 → 499 lines)
- Extracted §3 and §6–§20 from `claude/skill-writer.md` into
  `refs/mode-router.md` + `refs/modes/{create,lean,elicit,evaluate,optimize,
  self-evolution,security,audit,ute,install,memory,collect,graph}.md`.
- Main file keeps stub sections with pointers — progressive-disclosure
  pattern. All 8 platform mirrors rebuilt via `build-platforms.py`; sync
  verified.

#### Spec-pure frontmatter emission
- `scripts/emit_spec_pure.py` — migrates flat frontmatter to the agentskills.io
  v1.0 layout: top-level keys limited to `{name, description, version, license,
  author, spec_version, tags}`; everything else under the `x-skill-writer:`
  namespace; runtime state (`cumulative_invocations`, `pending_patches`,
  `last_ute_check`, `total_micro_patches_applied`, `certified_lean_score`)
  stripped to sidecar JSON.
- `templates/base.md` now demonstrates the nested layout.

#### Roadmap skeletons relocated
- `mcp/` → `experimental/mcp/`
- `scripts/gepa-optimize.py` → `experimental/gepa-optimize.py`
- `docs/mcp-integration.md` → `experimental/mcp-integration.md`
- `experimental/README.md` explicitly labels them as non-operational.
- All doc cross-references (install.md, strategies.md, skill-framework*,
  CI workflows, examples) updated to the new paths.

#### Honest research citations
- `scripts/sanitize_refs.py` — one-shot cleanup script replacing fake arxiv
  IDs and vendor-branded names (`SkillRouter`, `SkillRL`, `SkillClaw`,
  `SkillForge`, `EvoSkills`, `SkillNet`, `SkillProbe`, `SkillX`, `ToxicSkills`,
  `ClawHavoc`) with honest heuristic labels (e.g. `Skill Summary heuristic`,
  `Failure-Driven CREATE heuristic`). 486 replacements across 32 files, plus
  a follow-up pass for CJK-punctuation-adjacent occurrences on 8 platform
  files.
- `91.7% cross-encoder accuracy` → `high cross-encoder agreement (empirical,
  unpublished)` — the number has no citable source.

#### Makefile + discoverability
- New targets: `eval-trigger`, `optimize-description`, `emit-spec-pure`.
- Removed: `mcp-selftest`.
- PATH CONVENTION block in `claude/skill-writer.md` now lists `scripts/` and
  `agents/` so the in-session LLM knows these exist.

### Migration notes
- No installed skill changes shape. The real-eval pipeline is opt-in — if you
  never run `scripts/run_trigger_eval.py`, the rubric pipeline still works.
- `mcp/` path consumers: update imports/references to `experimental/mcp/`.
- `validation_status: lean-only` skills are not broken, but SHARE mode will
  now prompt for a real eval before publication.

---

## [3.5.0-dev] - 2026-04-17 (in progress on `claude/research-architecture-review-pEXSL`)

### Added — Spec compatibility, supply-chain hardening, MCP, CLEAR, GEPA roadmap

#### agentskills.io v1.0 compatibility (`spec/agent-skills-compat.md`, `scripts/check-spec-compat.py`)
- New **compatibility spec** documents how skill-writer's schema maps to
  agentskills.io v1.0 (name/description/version/license/author/homepage/keywords)
  and declares `x-skill-writer:` as the reserved extension namespace.
- Three emission modes defined: native (current), spec (minimal v1.0), spec+ext
  (v1.0 fields + `x-skill-writer` extensions).
- **`scripts/check-spec-compat.py`** — stdlib-only validator that reads
  frontmatter across the 8 platforms + templates + examples. Handles the Cursor
  MDC dual-frontmatter case. Emits `SPEC-W###` warnings instead of hard failing
  to keep migration non-blocking. Status: 0 errors, body-length warnings only.
- `spec_version: "1.0"` added to all templates (base / api-integration /
  data-pipeline / workflow-automation) and new example skills.

#### Supply-chain: Ed25519 signing + trust tiers (`scripts/sign-release.sh`, `scripts/verify-signature.sh`, `docs/supply-chain-security.md`)
- **Dual-layer signing pipeline** — author signature + (future) registry
  counter-signature. Python `cryptography` primary path, OpenSSL fallback.
- Emits `.sig`, `.pubkey`, and `.provenance` JSON sidecars per release artifact.
- `verify-signature.sh` supports TOFU (first-use pinning) and a repo-level trust
  store.
- **Trust tiers** (TRUSTED / VERIFIED / LOW_TRUST / UNTRUSTED) documented,
  referencing the 2026 OpenClaw incident (1,184 malicious packages).

#### Sandboxing handbook (`docs/sandboxing.md`)
- Threat-model tiers T0–T4, Docker reference config (network-none, read-only,
  cap-drop=ALL, no-new-privileges, pids/memory/cpu caps), Firejail (Linux T1)
  and macOS seatbelt (T1) equivalents, verification tests, CI recipe.
- Recommendation: **T2 container is the production default** for third-party
  skills; T1 for local dev.

#### Single-source platform build (`platforms.yaml`, `scripts/build-platforms.py`)
- **`platforms.yaml`** — narrow-YAML manifest declaring per-platform
  transforms (prepend / replace / footer_append / frontmatter_append) so the 8
  platform files can regenerate from one canonical source.
- **`scripts/build-platforms.py`** — stdlib-only parser + transform engine.
  `--check` (strict) and `--check-warn` (migration mode, non-blocking)
  available; `--only PLATFORM` for single-target builds. Ships in v3.5.0 as
  migration mode — full sync flip is `[ROADMAP v3.6.0]`.

#### MCP-native integration (`experimental/mcp/server.py`, `experimental/mcp/README.md`, `experimental/mcp-integration.md`) — since relocated to `experimental/`
- **Zero-LLM MCP server** — exposes 7 tools
  (`lean` / `evaluate` / `optimize` / `check_spec` / `build_platforms` /
  `verify_sig` / `list_skills`) that return structured *plans* for the host's
  LLM to execute. Stateless; no bundled model/provider.
- Detects the official MCP Python SDK; falls back to a stdlib stdio JSON-RPC
  loop (keeps zero-build promise).
- Install configs for Claude Desktop, Cursor, VS Code Copilot + MCP.
- `python3 experimental/mcp/server.py --selftest` validates the 7-tool handler table.

#### CLEAR production dimensions (`eval/rubrics.md §9a`)
- Opt-in (`/eval --clear`) D9 Cost (50 pts) + D10 Latency (50 pts) dimensions
  implementing the CLEAR framework (arXiv 2511.14136). Total ceiling rises to
  1100 when enabled; tier thresholds scale by 1.10.
- Production envelope fields added under `extends.production:` —
  `cost_budget_usd`, `est_tokens_p50/p95`, `latency_budget_ms`, `est_p95_ms`.

#### GEPA reflective optimization (`optimize/strategies.md §4a`, `experimental/gepa-optimize.py`) — since relocated to `experimental/`
- **S15 — Reflective Prompt Evolution** strategy added (arXiv 2507.19457):
  100–500 rollouts vs 10K+ RL; reflect-and-crossover loop on a Pareto frontier.
- `experimental/gepa-optimize.py` skeleton with stage stubs (seed/evaluate/
  reflect/crossover/select/verify). `--dry-run` prints the plan; real
  execution raises `NotImplementedError` until v3.6.0. Labelled
  `[experimental]` and excluded from default build/install targets.

#### Framework-index for 2772-line spec (`skill-framework-index.md`)
- Section-by-section TOC with line ranges, load triggers, and external cross-refs
  for `skill-framework.md`. Documents the v3.6.0 split plan (framework-core /
  framework-modes / framework-evolution).

#### Windows-native install (`scripts/merge-routing.ps1`)
- PowerShell idempotent marker-based routing-file merger — Windows users no
  longer need WSL2/Python to update `CLAUDE.md` / `GEMINI.md` / `AGENTS.md`.
  Parameters match the Python merger in `install.sh`.

#### New reference examples (`examples/data-pipeline-demo/`, `examples/mcp-bridge/`)
- **`data-pipeline-demo/`** — functional-tier `csv-to-json-validator` with
  schema-first validation, three-mode router, OWASP (ASI02/ASI07 + CWE-22)
  security baseline, and full CLEAR production fields.
- **`mcp-bridge/`** — atomic-tier `mcp-github-bridge` showing the
  thin-skill/delegation pattern: route intent to an MCP tool, render response
  in a blockquote, refuse write intents.

#### Cursor & roadmap polish
- README Cursor section: added explicit `.mdc` vs `.md` translation table and
  loader expectation warning.
- `refs/skill-graph.md`: three `builder/src/core/graph.js` references tagged
  `[ROADMAP v4.0+]` so readers don't expect a runtime that doesn't ship yet.
- README top-level feature table now uses a **CORE / EXTENDED / ROADMAP**
  legend so availability is unambiguous.

### Changed
- Templates: added `spec_version: "1.0"` to frontmatter across
  `templates/base.md`, `templates/api-integration.md`,
  `templates/data-pipeline.md`, `templates/workflow-automation.md`.
- `eval/rubrics.md` total-score math updated to reflect opt-in CLEAR (1100 max
  when `--clear`; default remains 1020 with Behavioral Verifier).
- `optimize/strategies.md` table of strategies now includes S15 (GEPA).

### Migration notes
- **No breaking changes**. CLEAR and GEPA are opt-in (`/eval --clear`,
  `/optimize --gepa`). Platform-build is migration-mode (`--check-warn`);
  existing platform files are untouched until v3.6.0.
- Recommend running `python3 scripts/check-spec-compat.py` once to see which
  skills are already agentskills.io-clean.


---

## Historical releases

Entries for versions `1.0.0` through `3.4.0` have been removed from this file to keep
it focused on the current development cycle and upcoming work.

The full history remains accessible through git:

```bash
git log --oneline --grep='^[Rr]elease\|CHANGELOG\|^v[0-9]' -- CHANGELOG.md
git log -- CHANGELOG.md
```

Or browse the pre-trim revision directly on GitHub — the prior CHANGELOG covered:

- `3.4.0` — Honest Skill Labeling, Behavioral Verifier, Pragmatic Test, GoS MVR
- `3.3.0` — Three-layer routing (AGENTS.md + Hook + triggers), Layer -1 injection
- `3.2.0` — Graph of Skills (GoS), GRAPH mode, D8 Composability scoring
- `3.1.0` — OWASP Agentic Skills Top 10 (ASI01–ASI10), Co-evolutionary VERIFY
- `3.0.0` — COLLECT + AGGREGATE (UTE 2.0 L2), Session Artifact, 5 new platforms
- `2.x`   — LEAN fast mode, UTE self-evolution, variance-gated certification
- `1.0.0` — Initial 1000-point rubric, multi-LLM review, 3 example skills

These releases are part of the project's past; they are not the current state.
