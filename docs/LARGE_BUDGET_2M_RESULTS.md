# Two-million-transition test (B2): results

Protocol: [LARGE_BUDGET_2M_PROTOCOL.md](LARGE_BUDGET_2M_PROTOCOL.md), committed (`19f786e`) before training. One run, seed 801, 1,998,848 added transitions from the experiment 7 start. Evaluation pool 885000 to 885063 (64 episodes per cell), unused before. The B1 final checkpoint was evaluated on the same pool as the matched reference.

## Outcome by the frozen rule

**Positive.** Final checkpoint, deterministic mode, pool 885000: `passages` 38/64 (threshold 28), medium 54/64 (threshold 48), and `passages` is 11 episodes above the B1 final checkpoint on the same pool (27/64; required margin 4). This is one seed, so the rule's consequence is a replication and not a claim.

## Curve (successes / collisions / timeouts, out of 64)

| Added transitions | `passages`, deterministic | `passages`, sampled | Medium, deterministic | Medium, sampled |
| --- | --- | --- | --- | --- |
| 491,520 | 16 / 38 / 10 | 20 / 43 / 1 | 50 / 13 / 1 | 50 / 13 / 1 |
| 1,015,808 | 26 / 25 / 13 | 23 / 32 / 9 | 56 / 6 / 2 | 53 / 10 / 1 |
| 1,507,328 | 48 / 6 / 10 | 43 / 11 / 10 | 54 / 7 / 3 | 57 / 7 / 0 |
| 1,998,848 (final) | **38 / 6 / 20** | 45 / 8 / 11 | **54 / 7 / 3** | 55 / 6 / 3 |
| B1 final (1,015,808, other run), same pool | 27 / 20 / 17 | 30 / 20 / 14 | 51 / 10 / 3 | 55 / 9 / 0 |

Final checkpoint, other cells:

| Cell | Deterministic | Sampled |
| --- | --- | --- |
| `passages-mid` | 56 / 2 / 6 | 60 / 1 / 3 |
| `passages-wide` | 64 / 0 / 0 | 64 / 0 / 0 |
| `gate-two` | 63 / 0 / 1 | 64 / 0 / 0 |

Wilson 95% intervals (percent) for deterministic cells: `passages` 38/64 is 47 to 71, 48/64 is 63 to 84, 27/64 is 31 to 54; medium 54/64 is 74 to 91.

## What the numbers show

- Collisions on `passages` were 18 to 30 along the B1 curve, 20 for the B1 checkpoint on this pool, and 25 and 38 at this run's 1M and 491k points. They fall to 6 at 1.5M and at 2M. This is the first time collisions drop at all, but 6 is still twice the gate's limit of 3.
- The curve is not monotone in deterministic mode: 48 at 1.5M, 38 at 2M. The drop is timeouts (10 to 20), not collisions (6 to 6). In sampled mode the same two points are 43 and 45, so part of the 1.5M-to-2M deterministic loss is a hover tendency that sampling removes, as seen before in the pilot checkpoint. The protocol fixed the final checkpoint as the decision point, and the rule is applied to it. The 1.5M value is reported and is not used to pick a checkpoint.
- `passages-mid` is 56/64 (87%). Medium stays at 50 to 56, with the final at 54, above the 48 line but below the 52 of the release gate on most points.
- The B1 checkpoint scores 27 on this pool against 23 on pool 884000. The four-episode difference between pools is within pool noise, and it is why the comparison uses the same pool.
- The slope between 1M and 1.5M is large (26 to 48). A single seed with a learning-rate schedule tied to the total cannot say how much is budget and how much is seed.

## Limits

- One seed. The variance study found seed spreads of up to 11 episodes of 32 on one profile, and the final result sits between a 48 and a 38 on adjacent points of the same run.
- The 28 and 20 thresholds were arbitrary and set before the run. The result is far above 28, so the verdict does not depend on that choice, but the size of the effect on other seeds is unknown.
- The release gate (52 of 64 and at most 3 collisions per family) is not met: `passages` 38/64 with 6 collisions, and level B, level C, `large` and `maze` were not measured. This is a partitioned-room family; it is not evidence for unseen maps.
- Medium is lower than the best earlier figures (86 to 92 percent on fresh pools); 54/64 is 84 percent on this pool.

## What this supports

Budget is a real lever for `passages` in this recipe: two checkpoints of one run (1.5M and 2M) are well above every earlier checkpoint and above the 1M checkpoint on the same pool, with collisions down from 20 to 25 (the 1M checkpoints on this pool) to 6. This is the first change that moves `passages` and `passages-mid` together without any privileged input. It does not yet show that the effect holds across seeds, and it does not touch the four-family gate.

## Artifacts

Run: `runs/training/large-budget-2m/seed801/` (stage checkpoints 1 to 61, `experiment.json`, `summary.json`). Final checkpoint `stage-61.zip`, SHA-256 prefix `3a4150b59b5fc894`. Source checkpoint unchanged (hash checked after training). Evidence copy in `private/large-budget-2m-evidence/`.

Timing from the clock: training about 13:14 to 14:30:59 (stage seconds sum to 76 min 51 s, 65 to 81 s per stage), evaluation 14:30:59 to 15:00:29 (29 min 30 s for 26 cells). Estimates were 80 min and 28 min.
