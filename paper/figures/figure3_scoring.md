# Dual-Track Validation Flow

```
                           ┌─────────────────────────┐
                           │     Candidate Skill     │
                           └─────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌───────────────────────┐       ┌───────────────────────┐
        │    TRACK A:           │       │    TRACK B:           │
        │    Automated Bench   │       │    Human Expert       │
        │    (Quantitative)    │       │    (Qualitative)      │
        └───────────────────────┘       └───────────────────────┘
                    │                               │
                    │  ┌─────────────────────┐     │
                    │  │ • Complexity score  │     │
                    │  │ • Coverage rate     │     │
                    └──│ • Consistency check │─────┤
                       │ • Performance test  │     │
                       └─────────────────────┘     │
                                                    │
                                                    ▼
                                        ┌─────────────────────┐
                                        │   SCORE MATRIX     │
                                        ├─────────────────────┤
                                        │ Automated: 0.85    │
                                        │ Human: 0.78        │
                                        │ Combined: 0.82     │
                                        └─────────────────────┘
                                                    │
                                                    ▼
                                        ┌─────────────────────┐
                                        │   AGGREGATOR        │
                                        │   (Weighted Consen.)│
                                        └─────────────────────┘
                                                    │
                                                    ▼
                                        ┌─────────────────────┐
                                        │   PASS/FAIL        │
                                        │   THRESHOLD ≥ 0.75 │
                                        └─────────────────────┘
```
