# Reference-preserving transfer experiment 1

Declared October 8, 2026, before any training. The user delegated the choice of budget and protocol. This experiment changes one factor relative to the historical reference: it adds partitioned-room (`passages`) training to a retained policy.

## Arms

| Arm | Initialization | Class |
| --- | --- | --- |
| retained | Checkpoint `3b9e8ba41305` (48/64, v3, `ray-risk-v1`), copied, not modified | Retained policy |
| fresh | Newly initialized v3 policy | Declared control |

Both arms use the same sensor contract (v3), readout (`random-pool-256-v1`), coordinated dynamics, batch 8, gamma 0.995, seeds, chunk plan and evaluations. The full MaleCNS v1.0 connectome is used in both arms. No planner or imitation teacher is used. Actions come from the learned policy.

## Budget

65,536 added transitions per arm, in eight chunks of 8,192. Plan: passages, passages, medium, passages, passages, passages, medium, passages. Medium rooms are 25% of the budget to measure forgetting. Original goals are used in every chunk. Each chunk uses training seed 42 plus the chunk index.

## Evaluation and selection (frozen before running)

- Evaluations after chunks 4 and 8 (32,768 and 65,536 transitions), no training.
- Medium regression: seeds 240000-240031, the pool the source scored 27/32 on. This is an already inspected validation pool, used as a regression check.
- Passages development: seeds 810000-810031, `passages` profile, created for this experiment. The source scored 0/16 on `passages` in the earlier ladder. This is a development pool, not a test.
- A checkpoint is accepted only if its medium regression is at least 25/32 (at most two lost successes against 27/32). Among accepted checkpoints, choose the highest passages success count. Ties go to the earlier checkpoint.
- If no checkpoint is accepted, the result is a regression, and no candidate is promoted.
- Lost reference successes are listed by seed.

## Limits

One training seed per arm. A single seed cannot support a claim about the method. Thirty-two episodes per cell give wide intervals. Passed development gates permit further work. They are not a generalization claim. Aliases and original runs are not modified; the source hash is re-checked after every chunk.
