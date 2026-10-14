# No-connectome control, stage C1.2: results

Protocol: [CONNECTOME_CONTROL_PROTOCOL_C12.md](CONNECTOME_CONTROL_PROTOCOL_C12.md), committed (`3c0bb81`) before training. The four C1.1 control runs (real and edge-shuffled, seeds 1001 and 1051) were trained 61 more stages (1,998,848 transitions) with the B2 recipe and a layout offset of 100, reaching 4,882,432 transitions each. Final checkpoints evaluated on the new pool 888000 to 888063 (64 episodes per cell) together with the three retained checkpoints (B3 stage 61), level B (950000) and level C (deterministic only, seed 900000). The decision mode is deterministic.

## Outcome by the frozen rules

**The chain check fails, by half an episode.** The rule required the mean of the two `real` seeds on `passages` to be at least 28/64. It is 27.5 (21 and 34). The rule is not adjusted after the fact. Per the protocol, a failed check means the result is "budget does not close the gap" and the comparison between arms stays a weaker-regime result.

For the record, the comparison rule applied anyway gives **inconclusive**: S (shuffled mean) is 21.0 (13 and 29), which is neither at least R minus 5 (22.5) nor at most R minus 10 (17.5), and the seed ranges overlap (shuffled 13 to 29, real 21 to 34).

## Results (final checkpoints, successes out of 64 unless noted; deterministic / sampled)

| Cell | Real 1001 | Real 1051 | Real mean | Shuffled 1001 | Shuffled 1051 | Shuffled mean | Retained mean (801, 851, 901) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `passages` | 21 / 25 | 34 / 37 | 27.5 / 31.0 | 13 / 27 | 29 / 35 | 21.0 / 31.0 | 38.0 / 38.7 |
| `passages-mid` | 48 / 55 | 54 / 57 | 51.0 / 56.0 | 40 / 51 | 54 / 58 | 47.0 / 54.5 | 52.3 / 55.3 |
| `passages-wide` | 62 / 63 | 64 / 64 | 63.0 / 63.5 | 64 / 64 | 64 / 64 | 64.0 / 64.0 | 64.0 / 63.7 |
| Medium | 58 / 59 | 54 / 59 | 56.0 / 59.0 | 54 / 55 | 53 / 57 | 53.5 / 56.0 | 55.3 / 55.7 |
| Level B (64) | 7 / 7 | 12 / 20 | 9.5 / 13.5 | 11 / 12 | 13 / 17 | 12.0 / 14.5 | 18.3 (B4) |
| Level C (168), deterministic | 91 | 105 | 98.0 | 111 | 100 | 105.5 | 103.7 (B4) |

`passages`, deterministic, successes / collisions / timeouts: real 1001 21 / 13 / 30; real 1051 34 / 9 / 21; shuffled 1001 13 / 7 / 44; shuffled 1051 29 / 11 / 24; retained 41 / 7 / 16, 35 / 10 / 19 and 38 / 8 / 18.

## Secondary comparisons (the C1.1 cuts, informational because the chain check failed)

- `passages-mid`: R 51.0, S 47.0. S is within 5 of R: no evidence of a wiring effect.
- Level B: R 9.5, S 12.0. No evidence.
- Level C (cuts 13 and 26 of 168): R 98.0, S 105.5. No evidence.

## Change from C1.1 to C1.2 (2.88M to 4.88M transitions; `passages`, deterministic, different pools: 886000 then 888000)

| Run | C1.1 | C1.2 |
| --- | --- | --- |
| Real 1001 | 13 | 21 |
| Real 1051 | 19 | 34 |
| Shuffled 1001 | 25 | 13 (sampled 27: 44 timeouts, a hover fixed point in deterministic mode) |
| Shuffled 1051 | 26 | 29 |

## What the numbers show

- More budget helps the real arm: it moves from 16.0 to 27.5 on `passages` and its seed 1051 (34) reaches the lower part of the retained range (35 to 41). The fresh chain at 4.88M still has the retained lineage (38.0) ahead by about 10 episodes on the mean.
- The direction between arms reverses relative to C1.1: shuffled was above real (25.5 against 16.0) and is now below (21.0 against 27.5). Each of the two comparisons stays inside seed spread, which is the finding: within each arm the two seeds differ by 13 (real) and 16 (shuffled) episodes deterministic in C1.2, as much as the differences between arms. In sampled mode both arms have the same mean (31.0), and shuffled 1001 shows that deterministic action selection can hide a hover fixed point (13 deterministic, 27 sampled).
- On the other cells there is no sign of an advantage of the real connectome: `passages-mid` 51 against 47, level B 9.5 against 12, level C 98 against 105.5, medium 56 against 53.5. The fresh arms at 4.88M reach the retained level on level C (98 and 105.5 against 103.7) and in medium and `passages-wide`, and stay under it on `passages` and level B.
- Collisions on `passages` are 7 to 13 in the control runs, against 7 to 10 in the retained runs, and all remain above the 3 allowed by the gate.

## Limits

- Two seeds per arm and one shuffled graph. From the spread seen here and in C1.1 (single-run standard deviation of about 7 episodes on `passages`), detecting a difference of 10 episodes with 80 percent power would take about 8 seeds per arm. That is 16 runs of about 4.9M transitions, out of reach for this project. A second graph would add a second source of variation and be limited in the same way.
- The result at the chain check is within half an episode of the threshold; reading it as pass or fail changes the wording but not the evidence.
- The extra budget includes a second learning-rate cycle. The pool changed between C1.1 and C1.2, so the C1.1 to C1.2 column is indicative.
- The matched comparison is still not at the retained level on `passages` (27.5 and 21.0 against 38.0), so a connectome effect at the retained level is neither shown nor excluded.

## What this supports

The bound stays as in C1.1: the biological connectome is not shown to improve or to be necessary for navigation in this project. After doubling the budget, the real and the edge-shuffled arms are indistinguishable within the measured uncertainty on every cell, and both approach the retained policy on medium, `passages-wide`, `passages-mid` and level C. A stronger statement in either direction would need many more seeds than this project can afford.

## Artifacts

Runs: `runs/training/connectome-control/phase3-{real,shuffled}{1001,1051}` (stages 1 to 61, `experiment.json`, sources unchanged). Cells in `c12-eval/` and `summary.json`; logs `c12-driver.log`, `c12-resources.log`. Evidence copy in `private/connectome-control-c12-evidence/`. Final checkpoint hashes (first 16 hex): real 1001 `89afcdc35f385c56`, real 1051 `a7e549d4c9bf8d93`, shuffled 1001 `b85f2e42c67fea4a`, shuffled 1051 `9ca7652aa583a5e1`.

Timing from the clock: launch 10:32:14 on October 14; pair A finished 11:50:05 (78 min), pair B 13:11:25 (81 min); evaluation 13:11:25 to 14:38:16 (86 min 51 s); 4 h 06 in all against 4 h 10 estimated. Evaluation was inside the estimated range of 60 to 100 min. Resources: CPU mean 70 to 75 percent, peak 94 percent, memory peak 64 percent, no fallback needed.
