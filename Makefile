# Makefile — skill-writer development helpers
#
# Targets:
#   make help              Show this help
#   make lint              Run shellcheck on all install scripts
#   make validate          Dry-run all platform installers
#   make check-version     Verify version consistency across all platform files
#   make check-spec-compat Validate frontmatter against agentskills.io v1.0 spec
#   make build-platforms       Regenerate 8 platform files from platforms.yaml (strict)
#   make build-platforms-check Drift-check platform files vs platforms.yaml (migration mode)
#   make sign ARTIFACT=path    Ed25519-sign a release artifact (+ .sig/.pubkey/.provenance)
#   make verify ARTIFACT=path  Verify Ed25519 signature on a release artifact
#   make eval-trigger ARGS="--skill ... --eval-set ..."   Run real trigger-accuracy eval
#   make optimize-description ARGS="--skill ... --eval-set ..." Iterative description optimizer
#   make install           Auto-detect and install to local platforms
#   make install-all       Install to all 8 platforms
#   make ci                Run lint + validate + check-version + check-spec-compat
#                          + build-platforms-check + check-platform-sync

.PHONY: help lint validate check-version check-spec-compat \
        build-platforms build-platforms-check sign verify \
        eval-trigger optimize-description emit-spec-pure \
        check-platform-sync install install-all ci

VERSION := $(shell cat VERSION)
PLATFORMS := claude openclaw opencode cursor gemini openai kimi hermes

# ── Default target ────────────────────────────────────────────────────────────

help:
	@echo "skill-writer $(VERSION) — development helpers"
	@echo ""
	@echo "  lint                     Run shellcheck on all install scripts"
	@echo "  validate                 Dry-run every platform installer (smoke test)"
	@echo "  check-version            Verify version $(VERSION) is consistent across all platform files"
	@echo "  check-spec-compat        Validate frontmatter against agentskills.io v1.0 spec"
	@echo "  build-platforms          Regenerate 8 platform files from platforms.yaml (strict)"
	@echo "  build-platforms-check    Drift-check platform files vs platforms.yaml (migration mode)"
	@echo "  sign ARTIFACT=<path>     Ed25519-sign a release artifact"
	@echo "  verify ARTIFACT=<path>   Verify Ed25519 signature"
	@echo "  eval-trigger             Real trigger-accuracy eval (needs ANTHROPIC_API_KEY)"
	@echo "  optimize-description     Iterative description optimizer (needs ANTHROPIC_API_KEY)"
	@echo "  emit-spec-pure           Emit skill to agentskills.io v1.0 spec-pure layout"
	@echo "  check-platform-sync      Diff all platform skill files against claude/skill-writer.md"
	@echo "  install                  Auto-detect installed platforms and install"
	@echo "  install-all              Install to all 8 platforms"
	@echo "  ci                       Full local CI (lint + validate + version + spec-compat + build-check + platform-sync)"

# ── Lint ──────────────────────────────────────────────────────────────────────

lint:
	@echo "==> shellcheck"
	@bash scripts/lint.sh

# ── Validate (dry-run all installers) ────────────────────────────────────────

validate:
	@echo "==> dry-run validation"
	@bash scripts/validate.sh

# ── Version consistency check ─────────────────────────────────────────────────

check-version:
	@echo "==> version consistency check (expected: $(VERSION))"
	@python3 scripts/check-version.py "$(VERSION)"

# ── Platform sync check ──────────────────────────────────────────────────────
# Compares each platform's skill-writer.md against the canonical claude/skill-writer.md.
# Ignores platform-specific blocks (metadata.openclaw, Triggers: footer, MDC header, AGENTS.md refs).
# Exits non-zero if any platform has diverged beyond platform-specific sections.

check-platform-sync:
	@echo "==> platform sync check (canonical: claude/skill-writer.md)"
	@python3 scripts/build-platforms.py --check

# ── agentskills.io spec compatibility (v3.5.0+) ───────────────────────────────

check-spec-compat:
	@echo "==> agentskills.io v1.0 frontmatter validation"
	@python3 scripts/check-spec-compat.py

# ── Single-source platform build (v3.5.0+) ────────────────────────────────────
# Strict mode regenerates files from platforms.yaml; migration mode only warns
# on drift. v3.5.0 ships in migration mode; v3.6.0 flips to strict.

build-platforms:
	@echo "==> build all platform files from platforms.yaml (strict)"
	@python3 scripts/build-platforms.py

build-platforms-check:
	@echo "==> drift-check platform files vs platforms.yaml (migration mode)"
	@python3 scripts/build-platforms.py --check-warn

# ── Ed25519 release signing (v3.5.0+) ─────────────────────────────────────────

sign:
	@if [ -z "$(ARTIFACT)" ]; then \
		echo "usage: make sign ARTIFACT=<path>"; exit 1; \
	fi
	@bash scripts/sign-release.sh "$(ARTIFACT)"

verify:
	@if [ -z "$(ARTIFACT)" ]; then \
		echo "usage: make verify ARTIFACT=<path>"; exit 1; \
	fi
	@bash scripts/verify-signature.sh "$(ARTIFACT)"

# ── Real eval pipeline (matches Anthropic skill-creator design) ──────────────

eval-trigger:
	@echo "==> real trigger-accuracy eval"
	@python3 scripts/run_trigger_eval.py $(ARGS)

optimize-description:
	@echo "==> iterative description optimizer"
	@python3 scripts/optimize_description.py $(ARGS)

# ── Spec-pure emission (agentskills.io v1.0 conformance) ──────────────────────

emit-spec-pure:
	@if [ -z "$(SKILL)" ]; then \
		echo "usage: make emit-spec-pure SKILL=<path> OUT=<path> [STATE=<path>]"; exit 1; \
	fi
	@python3 scripts/emit_spec_pure.py "$(SKILL)" --out "$(OUT)" $(if $(STATE),--state-out "$(STATE)",)

# ── Install ───────────────────────────────────────────────────────────────────

install:
	@bash install.sh

install-all:
	@bash install.sh --all

# ── Full local CI ─────────────────────────────────────────────────────────────

ci: lint validate check-version check-spec-compat build-platforms-check check-platform-sync
	@echo ""
	@echo "  ✓ all CI checks passed"
