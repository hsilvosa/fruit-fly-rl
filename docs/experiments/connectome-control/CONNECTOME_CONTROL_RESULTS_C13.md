# No-connectome control, stage C1.3: results

Protocol: [CONNECTOME_CONTROL_PROTOCOL_C13.md](CONNECTOME_CONTROL_PROTOCOL_C13.md), committed (`66ef9b9`) before training. Two more seeds (1101 and 1151) of the fresh chain were trained for both arms (`real` and edge-shuffled), through the three phases (27, 61 and 61 stages, 4,882,432 transitions each), with the recipe of C1.2. The final checkpoints were evaluated on the C1.2 cells and pool 888000 to 888063 (64 episodes per cell), level B (950000) and level C (deterministic, seed 900000). All four seeds of an arm therefore saw the same maps. The decision mode is deterministic. The frozen analysis is `scripts/connectome_control_stats.py` (Welch interval of real minus shuffled, four seeds per arm, seeds 1001 and 1051 taken unchanged from C1.2).

## Outcome by the frozen rules

**Primary cell (`passages`): inconclusive.** Real 21, 34, 21, 28 (mean 26.0); shuffled 13, 29, 22, 25 (mean 22.25). `D = +3.75`, standard error 4.63, 95 percent interval [-7.6, +15.1], 90 percent interval [-5.2, +12.7]. The interval does not lie above 0 (not "wiring matters"), does not lie below 0 (not "shuffled better"), and the 90 percent interval is not inside (-10, +10) because its upper end is 12.7 (not "equivalent within 10"). The rule is applied as declared.

**Chain check fails again.** The real mean on `passages` is 26.0, below the 28 required. The fresh chain at 4.88M transitions stays below the retained lineage (38.0 in C1.2, not rerun) whatever the wiring.

**Secondary cells** (same rules, informational; they never override the primary one):

| Cell | Real mean | Shuffled mean | D | 95 percent interval | Verdict |
| --- | --- | --- | --- | --- | --- |
| `passages-mid` | 50.0 | 48.0 | +2.0 | [-6.7, +10.7] | equivalent |
| `passages-wide` | 63.5 | 62.75 | +0.75 | [-3.0, +4.5] | equivalent (near ceiling) |
| Medium | 53.5 | 54.5 | -1.0 | [-6.6, +4.6] | equivalent (near ceiling) |
| Level B (64) | 8.5 | 12.0 | -3.5 | [-11.2, +4.2] | equivalent |
| Level C (168, margin 26) | 100.0 | 103.75 | -3.75 | [-16.9, +9.4] | equivalent |

No cell favors the real connectome. `passages-wide` and medium sit near the ceiling for every run, so their verdict says little.

## Results by seed (successes out of 64 unless noted; deterministic, sampled in parentheses)

| Cell | Real 1001, 1051, 1101, 1151 | Shuffled 1001, 1051, 1101, 1151 |
| --- | --- | --- |
| `passages` | 21, 34, 21, 28 (25, 37, 26, 29) | 13, 29, 22, 25 (27, 35, 31, 36) |
| `passages-mid` | 48, 54, 49, 49 (55, 57, 51, 53) | 40, 54, 49, 49 (51, 58, 53, 55) |
| `passages-wide` | 62, 64, 64, 64 (63, 64, 64, 62) | 64, 64, 59, 64 (64, 64, 64, 64) |
| Medium | 58, 54, 53, 49 (59, 59, 55, 49) | 54, 53, 55, 56 (55, 57, 54, 55) |
| Level B | 7, 12, 11, 4 (7, 20, 13, 7) | 11, 13, 6, 18 (12, 17, 11, 19) |
| Level C (168), det. only | 91, 105, 109, 95 | 111, 100, 97, 107 |

Sampled means: `passages` real 29.25 against shuffled 32.25; `passages-mid` 54.0 against 54.25; medium 55.5 against 55.25; level B 11.75 against 14.75. Sampled actions do not change the reading.

`passages`, deterministic, successes / collisions / timeouts: real 1101 21 / 21 / 22, real 1151 28 / 14 / 22 (seeds 1001 and 1051: 21 / 13 / 30 and 34 / 9 / 21); shuffled 1101 22 / 7 / 35, shuffled 1151 25 / 13 / 26 (seeds 1001 and 1051: 13 / 7 / 44 and 29 / 11 / 24). Mean collisions are 14.25 (real) and 9.5 (shuffled); the retained seeds had 7 to 10. Every run stays above the 3 collisions the gate allows. The collision difference between arms is inside the seed spread and was not a frozen test.

## What four seeds changed

- The spread inside an arm is smaller than the two-seed estimate suggested: sample standard deviations of 6.3 (real) and 6.8 (shuffled) on `passages`, against the 9 and 11 assumed in the protocol. The standard error of D is 4.6 instead of the expected 7, and the 95 percent interval half-width is about 11 instead of 17.
- The shuffled `passages` runs of C1.2 (13 and 29) were the extremes of that arm; the two new seeds (22 and 25) sit between them. Seed 1001 shuffled (13) is the hover fixed point already noted in C1.2 (44 timeouts deterministic, 27 successes sampled).
- The sign of the difference changed between C1.1 (shuffled ahead, two seeds) and C1.2 (real ahead, two seeds) and the four-seed estimate is small and positive, which is what an interval around zero looks like.

## Limits

- Four seeds per arm and one shuffled graph (shuffle seed 1); development pools; one recipe and one start (random weights).
- Inputs and outputs are placed at random in both arms, so this tests the wiring inside the reservoir, not the anatomical sensorimotor organization.
- The fresh chain does not reach the retained level on `passages` (26.0 and 22.25 against 38.0), so an effect at the retained level is neither shown nor excluded.
- The statement "no advantage larger than 15 episodes of 64" is what the 95 percent interval supports on `passages` (upper end +15.1). A "no advantage larger than 10" verdict is not reached.
- Rough sample-size estimate, normal approximation with a spread of 6.5: if the true difference is near the observed +3.75, about seven seeds per arm would put the 90 percent interval inside (-10, +10); if the true difference is zero, fewer would. This is an estimate, not a protocol. A second shuffle realization would add a variance source of its own.

## What this supports

The biological connectome is not shown to improve or to be necessary for navigation in this project, and with four seeds per arm its effect on `passages` is bounded to between -7.6 and +15.1 episodes of 64 (95 percent), without reaching the declared equivalence margin. On every other cell the arms are equivalent within the margin, and none favors the real wiring. This is the wording the release uses.

## Artifacts

Runs: `runs/training/connectome-control/phase3-{real,shuffled}{1101,1151}` (stage 61 final; phases 1 and 2 in `phase1-*` and `phase2-*`). Cells, `summary.json` and `analysis.json` in `c13-eval/` (analysis SHA-256 `8ea35b5fbc74bb2e`); logs `c13-driver.log`, `c13-resources.log`. Evidence copy in `private/connectome-control-c13-evidence/`. Final checkpoint hashes (first 16 hex): real 1101 `26607282e83b85bb`, real 1151 `177f3fccc7fcf628`, shuffled 1101 `807ce3127a0fb324`, shuffled 1151 `d412c31c69e8ef1a`.

Timing from the clock: launch 09:04, seed 1101 phase 1 done 09:47:03, phase 2 11:10:04, phase 3 12:33:34; seed 1151 phase 1 13:16:04, phase 2 14:39:35, phase 3 16:04:06; evaluation 16:04:06 to 17:10:17 (66 min); 8 h 06 in all against 7 h 50 estimated. Training took about 6 h 59 against 6 h 46 estimated (phase 1 took 42 to 43 min against 40 estimated, phases 2 and 3 83 to 85 min against 78 to 84); evaluation fell inside the estimated 60 to 70 min. Resources: no fallback to serial was needed (mean CPU over the first two minutes of overlap was 91 percent for the first pair, below the 93 percent trigger). Over 2,415 ten-second samples CPU averaged 74 percent and memory peaked at 65 percent; CPU touched 99 percent in one sample during the first overlap, above the 95 percent ceiling the user set.
