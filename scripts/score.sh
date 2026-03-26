
# ── Dimension 8: Completeness (5%) ─────────────────────────────────────────
CM_SCORE=5
CM_NOTES=""
HAS_SKILL_MD=$(grep -c "SKILL.md" "$SKILL_FILE" || true)
HAS_EVALS=$(grep -ci "evals\|eval.sh\|evaluation" "$SKILL_FILE" || true)
HAS_SCRIPTS=$(grep -ci "scripts\|script" "$SKILL_FILE" || true)
HAS_REFS=$(grep -ci "references\|ref" "$SKILL_FILE" || true)
HAS_TRIGGERS=$(grep -ci "trigger\|when.*require\|when.*ask" "$SKILL_FILE" || true)

[[ $HAS_SKILL_MD -gt 0 ]] && CM_SCORE=$((CM_SCORE+1)) && CM_NOTES+="self-referential "
[[ $HAS_EVALS -gt 0 ]] && CM_SCORE=$((CM_SCORE+2)) && CM_NOTES+="eval-defined "
[[ $HAS_SCRIPTS -gt 0 ]] && CM_SCORE=$((CM_SCORE+1)) && CM_NOTES+="scripts-defined "
[[ $HAS_REFS -gt 0 ]] && CM_SCORE=$((CM_SCORE+1)) && CM_NOTES+="references-defined "
[[ $HAS_TRIGGERS -gt 0 ]] && CM_SCORE=$((CM_SCORE+1)) && CM_NOTES+="triggers-defined "
[[ $CM_SCORE -gt 10 ]] && CM_SCORE=10
dim_score "Completeness" 5 "$CM_SCORE" "$CM_NOTES"
