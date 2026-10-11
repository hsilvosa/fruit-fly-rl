# Run 601 confirmation and stochastic check

October 11, 2026. Evaluation only, no training. Pool seeds 880000 to 880063 (the fresh pool of [VARIANCE_STUDY_RESULTS.md](VARIANCE_STUDY_RESULTS.md); run 601 was selected on other pools, so this is a fresh pool for it), 64 episodes per cell, Wilson 95% intervals. Scripts: `scripts/committee_evals.py`, `scripts/eval_cell.py` (new environment switch `STOCHASTIC=1`, which samples actions from the policy instead of taking the mode; `evaluate()` gained a `deterministic=True` argument and its default behavior is unchanged). The run took 14 minutes in the fast mode (4 processes), against 25 estimated.

## Run 601 on the fresh pool (deterministic)

| Cell | Successes | Interval | Collisions | Timeouts |
| --- | --- | --- | --- | --- |
| Medium | 59/64 (92%) | 83 to 97% | 2 | 3 |
| Passages-wide | 55/64 (86%) | 75 to 92% | 2 | 7 |
| Passages-mid | 35/64 (55%) | 43 to 66% | 13 | 16 |
| Passages | 9/64 (14%) | 8 to 25% | 34 | 21 |

Comparison on the same pool and seeds (from [VARIANCE_STUDY_RESULTS.md](VARIANCE_STUDY_RESULTS.md)):

| Checkpoint | Medium | Wide | Mid | Passages |
| --- | --- | --- | --- | --- |
| Run 601 | 59 | 55 | 35 | 9 |
| Pilot candidate | 57 | 14 | 37 | 17 |
| Seed 505 (best of variance study) | 55 | 41 | 17 | 2 |

Reading: run 601 is the first checkpoint that keeps medium, passages-wide and passages-mid together (92%, 86%, 55%). It gives up part of `passages` compared with the pilot (14% against 27%). The selection-pool values (wide 32/32, mid 19/32, passages 7/32) came down toward the fresh values for wide and passages, as expected after selection, and mid held. It is a development result from one training run selected among three. It is not a gate pass: `passages` is far from 81%, and the other families were not measured.

## Stochastic against deterministic evaluation

Same checkpoints, same pool, actions sampled from the policy. The rule in the committee plan: 8 or more extra successes of 64 means the deterministic policy sits in a fixed point.

| Checkpoint and cell | Deterministic | Stochastic | Change |
| --- | --- | --- | --- |
| Pilot, passages-wide | 14 (50 timeouts, 0 collisions) | 55 (6 timeouts, 3 collisions) | **+41** |
| Pilot, passages | 17 | 14 | -3 |
| Seed 505, passages-wide | 41 | 40 | -1 |
| Seed 505, passages | 2 | 5 | +3 |

Reading:

- For the pilot on `passages-wide`, the deterministic failure is a **hovering fixed point**. The deterministic policy times out in 50 of 64 episodes without colliding, and sampling the same policy solves 55. Its apparent trade-off between `passages-wide` and the harder profiles is largely an artifact of always taking the mode of the action distribution there.
- The effect is not general. Seed 505 does not change, and neither profile `passages` improves for either checkpoint. The hovering explanation applies to the pilot's wide failure, and does not explain the low scores on `passages` (there collisions dominate: 27 to 39 of 64).
- Consequence for method: comparing checkpoints under the deterministic rule only can hide or invent profile trade-offs. Any future comparison should report both modes. Sampled evaluation still uses only the learned policy, so it does not break the rule about planners. The mode must be declared in each protocol.

## Open

- The stochastic mode was not run for run 601, passages-mid or medium.
- The probe of the 256 pooled features is still not done (uses the GPU).
- Collisions dominate `passages` failures (run 601: 34 collisions of 64). The policy does reach the walls, which fits the exposure explanation of [LIGHT_AUDIT_RESULTS.md](LIGHT_AUDIT_RESULTS.md) better than a hovering one.
