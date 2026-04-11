
## §9 Self-Review Protocol

| Role | Responsibility |
|------|----------------|
| Pass 1 — Generate | Produce initial draft / score / fix proposal |
| Pass 2 — Review | Security + quality audit; severity-tagged issue list (ERROR/WARNING/INFO) |
| Pass 3 — Reconcile | Address all ERRORs, reconcile scores, produce final artifact |

Timeouts: 30 s per pass, 60 s per phase, 180 s total (6 turns max).
Consensus: CLEAR → proceed; REVISED → proceed with notes;
UNRESOLVED → HUMAN_REVIEW.
