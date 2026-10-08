# Reference-preserving transfer experiment 2

Declared October 8, 2026 before any training, after the failure classification in [PASSAGES_FAILURE_CLASSIFICATION.md](PASSAGES_FAILURE_CLASSIFICATION.md). The user delegated budget and protocol choices.

Both arms start from the retained 48/64 checkpoint `3b9e8ba41305` (copied, never modified), with the v3 interface, `random-pool-256-v1` readout, full MaleCNS v1.0 connectome, coordinated dynamics, batch 8, gamma 0.995, no planner actions and no imitation. Chunk plan and seeds are those of experiment 1, repeated for the longer arm. Chunks alternate between `passages` and original medium rooms (25% medium).

| Arm | Single change relative to experiment 1 (retained arm) |
| --- | --- |
| route65 | Training reward on `passages` chunks uses `certified-route-progress-v1`. Same 65,536 transitions. |
| budget262 | Same unchanged reward, 262,144 transitions (the experiment 1 plan, four times). |

`certified-route-progress-v1` replaces the Euclidean progress term with progress along a certified feasible route, computed from privileged training geometry. Observations are unchanged. The reward is used only during training chunks on `passages`. Evaluation reward and policy inputs are unchanged. The planner never chooses actions. Medium chunks use the original reward. Training layouts are seeds 900000-900255, disjoint from every evaluation pool.

## Evaluation and selection (frozen before running)

- route65 evaluates after 32,768 and 65,536 added transitions. budget262 evaluates after 131,072 and 262,144.
- Medium regression: seeds 240000-240031. Passages development: seeds 810000-810031. Same pools as experiment 1.
- Accept a checkpoint only with medium regression of at least 25/32. Among accepted checkpoints, choose the highest passages count. Ties go to the earlier checkpoint.
- A positive result needs passages successes above zero in an accepted checkpoint. It permits larger work. It is not a claim about generalization.
- Lost reference successes are listed by seed.

## Limits

One training seed per arm. Thirty-two episodes per cell. The route reward uses privileged geometry in training only. If it succeeds, the learned policy still must be shown to work without it, which the evaluation does, because evaluation uses no route.
