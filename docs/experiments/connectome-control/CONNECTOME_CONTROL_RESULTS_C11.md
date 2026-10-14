# No-connectome control, stage C1.1: results

Protocol: [CONNECTOME_CONTROL_PROTOCOL_C11.md](CONNECTOME_CONTROL_PROTOCOL_C11.md), committed (`38d5dad`) before training. Two arms from random weights, `real` (full connectome) and `shuffled` (edge targets permuted, shuffle seed 1), seeds 1001 and 1051, phase 1 of 884,736 transitions on medium rooms and phase 2 of 1,998,848 transitions with the B2 mix: 2,883,584 transitions per run, the same as the retained lineage. Final checkpoint (stage 61) of each of the four runs, deterministic mode decides.

## Outcome by the frozen rules

**The chain check fails.** The rule required the mean of the `real` arm on `passages` to be at least 28/64 so that the fresh chain reproduces the retained effect. It is 16.0 (13 and 19). The fresh chain with the same number of transitions does not reach the retained policy (36 to 42 on three seeds), so the arm comparison is reported but it cannot be used to speak about the retained lineage.

**Primary comparison on `passages`, as a fresh-chain result only:** R (real mean) = 16.0, S (shuffled mean) = 25.5. S is above R, so the rule gives **no evidence that the wiring matters** (S at least R minus 5). The direction is the opposite of a connectome advantage: both shuffled seeds (25, 26) are above both real seeds (13, 19). The gap of 9.5 is just under the 10-episode cut that would have counted as a difference, and with two seeds per arm it is not distinguishable from seed spread (the probability that two seeds of one arm both exceed the other arm's two seeds by chance is 1 in 6 each way).

## Results (final checkpoints, deterministic / sampled, successes out of 64 unless noted)

| Cell | Real 1001 | Real 1051 | Real mean | Shuffled 1001 | Shuffled 1051 | Shuffled mean | Retained mean (B3, B4) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `passages` | 13 / 18 | 19 / 20 | 16.0 | 25 / 26 | 26 / 32 | 25.5 | 39.0 |
| `passages-mid` | 38 / 42 | 45 / 54 | 41.5 | 54 / 55 | 48 / 52 | 51.0 | 55.7 |
| `passages-wide` | 56 / 56 | 63 / 64 | 59.5 | 64 / 64 | 64 / 64 | 64.0 | 64.0 |
| Medium | 57 / 55 | 61 / 59 | 59.0 | 52 / 57 | 55 / 55 | 53.5 | 52.7 |
| Level B (64) | 5 / 8 | 6 / 11 | 5.5 | 10 / 13 | 3 / 10 | 6.5 | 18.3 |
| Level C (168) | 77 / 83 | 81 / 93 | 79.0 | 75 / 96 | 97 / 94 | 86.0 | 103.7 |

Collisions and timeouts, deterministic: `passages` collisions 14 and 14 (real), 12 and 13 (shuffled), against 8 to 16 for the retained seeds; timeouts 37 and 31 (real), 27 and 25 (shuffled). Level B collisions 12 to 23 and timeouts 35 to 46 in all four runs.

## Secondary comparisons (same cuts as the protocol)

- `passages-mid`: R 41.5, S 51.0. S above R, no evidence of a wiring effect (the shuffled arm is 9.5 higher, under the 10 cut).
- Level B: R 5.5, S 6.5. No evidence (both arms near the 1 to 6 of every earlier run).
- Level C (168 episodes, cuts 13 and 26): R 79.0, S 86.0. No evidence.
- Medium: R 59.0, S 53.5. The only cell where the real arm is higher (5.5), inside the cut.

## What the numbers show

- The edge-shuffled reservoir does at least as well as the real connectome under this chain. In no cell is the real arm 10 or more episodes above the shuffled one, and on `passages` and `passages-mid` it is the other way round by 9.5 each. With two seeds this is a nominal tendency and not an effect.
- The fresh chain is much weaker than the retained lineage on the hard cells even with the same number of transitions: `passages` 16 and 25.5 against 39, level B 5.5 and 6.5 against 18.3, level C 79 and 86 against 103.7. Both fresh arms are below every retained seed on `passages` (36 to 42) and on level B (12 to 26). Medium and `passages-wide` are matched.
- So the retained advantage does not come from the connectome (the shuffled control also lacks it) and does not come from the count of transitions alone. A likely cause is the history of the retained start: its 884,736 transitions came from a chain of transfer experiments that included partitioned rooms and gate training, whereas the fresh phase 1 saw medium rooms only. This was not tested. It is a hypothesis.
- Fresh real seeds differ by 6 episodes on `passages` (13 and 19) and shuffled seeds by 1, so this stage cannot rank the arms.

## Limits

- Two seeds per arm and one shuffled graph realization. Seed spreads of 6 and more mean that differences below about 10 episodes cannot be read as effects.
- The matched comparison is made where the policies reach 16 to 26 of 64 on `passages`, not at the retained level of 36 to 42. A connectome advantage at the retained level is neither shown nor excluded.
- The shuffle keeps degrees, weights and signs. It removes the specific wiring, not those properties.
- The retained numbers come from three seeds trained along a different chain and evaluated on the same pools (886000, 950000 and 900000).
- Level C is clustered by scene and inspected; it is descriptive.

## What this supports

For this project, the claim that the biological connectome improves or is necessary for navigation is **not supported**. The learned policy works with the full connectome in the loop, and a degree-preserving shuffled reservoir learns medium rooms, partitioned rooms and the held-out cells at least as well in a matched fresh chain, within the measured uncertainty. This is the bound that the release must state (PROJECT_COMPLETION rule). It is not evidence that the connectome is useless: a second shuffled graph, more seeds, and a matched chain that reaches the retained level could change the reading.

## Artifacts

Runs: `runs/training/connectome-control/phase2-{real,shuffled}{1001,1051}` (stages 1 to 61, `experiment.json`; source hashes unchanged in all four). Cells in `c11-eval/` with `summary.json`; logs `c11-driver.log`, `c11-eval-driver.log`, `c11-resources.log`. Evidence copy in `private/connectome-control-c11-evidence/`. Final checkpoint hashes (first 16 hex): real 1001 `d1cf2ca4e3c3c535`, real 1051 `b2e6a0f459ce41b8`, shuffled 1001 `47ab8dc1c288566f`, shuffled 1051 `918cbc6fbf0c3464`.

Timing from the clock: launch about 20:29 on October 13; pair A finished 21:52:37 (about 83 min), pair B 22:32:58 (about 40 min), pair C 23:57 (about 84 min), then a pause at the user's request before evaluation; evaluation 08:37:00 to 10:02:12 on October 14 (85 min 12 s). Estimates were 86, 38 and 86 min for training and 45 min for evaluation: training matched, evaluation took almost twice the estimate (eight level C passes at about 15 min each with six processes sharing the CPU). Active time 3 h 28 of training and 1 h 25 of evaluation, 4 h 53 in total against 4 h 15 estimated. Resources: CPU mean about 66 to 76 percent with two trainings, peak 90 percent, memory peak 70 percent.
