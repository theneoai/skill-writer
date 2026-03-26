# 7-Step Optimization Loop

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        AUTONOMOUS OPTIMIZATION LOOP                          │
└──────────────────────────────────────────────────────────────────────────────┘

     ┌─────────┐
     │  START  │
     └────┬────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. EVALUATE    │────▶│  2. ANALYZE     │────▶│  3. GENERATE    │
│  - Run tests    │     │  - Identify     │     │  - Create       │
│  - Measure      │     │    gaps         │     │    candidates  │
│    metrics      │     │  - Score        │     │  - Propose     │
└─────────────────┘     │    dimensions   │     │    changes     │
                        └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  7. ITERATE     │◀────│  6. VALIDATE    │◀────│  4. SELECT      │
│  - Check        │     │  - Dual-track   │     │  - Rank         │
│    convergence  │     │    testing      │     │  - Filter       │
│  - Loop or end  │     │  - Consensus    │     │  - Choose best  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  5. IMPLEMENT   │
                                                │  - Apply change │
                                                │  - Monitor      │
                                                └─────────────────┘
```
