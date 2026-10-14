# Level B and level C measurement (B4): results

Protocol: [LEVEL_BC_PROTOCOL.md](LEVEL_BC_PROTOCOL.md), committed (`bd70470`) before any evaluation. Stage 61 (1,998,848 added transitions) of seeds 801, 851 and 901, plus the experiment 7 start checkpoint. Nothing was trained or selected. Level B: held-out sampler, difficulty 0.8, seeds 950000 to 950063, 64 episodes (the development pool of every earlier level B number). Level C: 21 architectural situations x 8 headings, seed 900000, 168 episodes. The recorded start baseline on level C (deterministic) is 71 of 168 from R5 and was not repeated.

## Outcome by the frozen rules

| Level | Rule outcome | Basis |
| --- | --- | --- |
| B | **Inconclusive** | Mean 18.3/64 (positive needed 20, negative was 8 or less). Every seed at least 12: 26, 17, 12 |
| C | **Positive** | Mean 103.7/168 (positive needed 88), no seed below the start's 71: 95, 108, 108 |

Level B misses the positive threshold by 1.7 episodes of mean. The rule is not adjusted after the fact.

## Level B (successes / collisions / timeouts, out of 64)

| Checkpoint | Deterministic | Sampled |
| --- | --- | --- |
| Seed 801 | 26 / 10 / 28 | 23 / 16 / 25 |
| Seed 851 | 17 / 14 / 33 | 16 / 24 / 24 |
| Seed 901 | 12 / 17 / 35 | 20 / 19 / 25 |
| Start checkpoint | 1 / 28 / 35 | 1 / 30 / 33 |

Wilson 95% intervals, deterministic (percent): seed 801 is 29 to 53, seed 851 is 17 to 38, seed 901 is 11 to 30. Earlier runs on this same pool scored 1 to 6 of 64, so all three seeds are above anything before. The spread between seeds (12 to 26) is as large as the gain over the start.

## Level C (successes / collisions / timeouts, out of 168)

| Checkpoint | Deterministic | Sampled |
| --- | --- | --- |
| Seed 801 | 95 / 52 / 21 | 113 / 53 / 2 |
| Seed 851 | 108 / 45 / 15 | 108 / 52 / 8 |
| Seed 901 | 108 / 54 / 6 | 105 / 62 / 1 |
| Start checkpoint | 71 / 51 / 46 (recorded in R5) | 93 / 64 / 11 |

Per scene, deterministic successes (episodes: office-floor 24, apartment 24, street-block 40, atrium 24, warehouse 32, courtyard 24):

| Scene | Start | Seed 801 | Seed 851 | Seed 901 |
| --- | --- | --- | --- | --- |
| office-floor | 10 | 16 | 16 | 16 |
| apartment | 7 | 8 | 8 | 8 |
| street-block | 12 | 32 | 36 | 40 |
| atrium | 8 | 8 | 8 | 9 |
| warehouse | 10 | 24 | 17 | 18 |
| courtyard | 24 | 7 | 23 | 17 |

Wilson 95% intervals, deterministic totals: start 35 to 50 percent (71/168), seed 801 49 to 64, seed 851 and seed 901 57 to 71.

## What the numbers show

- The partition-family effect partly leaves the trained family. All three seeds clear every earlier level B figure, and the level C rule passes. Level C is positive by the rule. It is also uneven, as below.
- Level C gains come from three scenes: `street-block` (12 to 32-40 of 40), `warehouse` (10 to 17-24 of 32) and `office-floor` (10 to 16 of 24, the same on all three seeds). `apartment` (7 to 8 of 24) and `atrium` (8 to 9 of 24) do not move. These two are 28 to 38 percent after 2M transitions.
- `courtyard` regressed. The start scored 24/24 and the trained seeds score 7, 23 and 17. The rule counts the 168-episode total, so this loss is inside the positive result. Seed 801's courtyard loss is 17 episodes, which largely explains why its total is 13 lower than the other two seeds.
- The start's sampled level C score (93) is 22 above its deterministic one (71), because `street-block` and `warehouse` rise while `courtyard` falls to 17. Against the sampled start, the trained seeds gain 12 to 20 episodes (105 to 113, mean 108.7, against 93), about 7 to 12 points, and not the 31 episodes of the deterministic comparison. The rule uses the deterministic mode, declared before the run. The sampled comparison is the fairer measure of the gain, and the deterministic start is lowered by the same hover tendency seen in earlier experiments.
- Level B failures are mostly timeouts (24 to 35 of 64), then collisions (10 to 24). The held-out region has narrow openings under 3.8 m, and the policy does not commit through them. This is the pattern of `passages` before the large budget.
- Level C collisions (45 to 62 of 168, 27 to 37 percent) are not lower than the start's 51. The gate allows 3 per 64.

## Limits

- Level C is 21 situations with fixed geometry and eight initial headings each. The headings are not independent samples of buildings and the successes cluster by scene. The rate is descriptive.
- Level B has 64 episodes per cell and seeds that differ by 14. The mean of 18.3 rests on three values (26, 17, 12) and sits one episode under its threshold.
- The 2M recipe was chosen without looking at these cells, but the level C development headings and the level B development pool are inspected and not independent of future decisions. The sealed final pools were not opened.
- The release gate (52 of 64, at most 3 collisions, in each of four families) is not met on level B (12 to 26 of 64 with 10 to 17 collisions), level C or any family measured. `large` and `maze` were not measured.

## What this supports

With the connectome in the loop and no privileged input, a 2M-transition run from the retained start raises success from 1 of 64 to 12 to 26 of 64 in the held-out parameter region, and from 42 percent (deterministic) or 55 percent (sampled) to 57 to 67 percent on a family of synthetic architectural scenes that never entered training. This is partial transfer, not a result that meets the gate. It comes with a loss in one scene that the start flew perfectly and with no gain in two others.

## Artifacts

Cells in `runs/training/large-budget-2m/b4-eval/` (`summary.json` and one file per cell, level C files include per-situation outcomes). Evidence copy in `private/level-bc-evidence/`. Checkpoints are the B3 stage 61 files (hashes in [REPLICATION_2M_RESULTS.md](REPLICATION_2M_RESULTS.md)).

Timing from the clock: driver log created 14:19:55 on October 13, evaluation finished 15:12:52 (52 min 57 s), against an estimate of 1 h 30 with a range up to 2 h 30. Level C runs took 703 to 1,013 s each (12 to 17 min, faster than the 22 min recorded in R5, which ran alone); level B cells were not timed separately.
