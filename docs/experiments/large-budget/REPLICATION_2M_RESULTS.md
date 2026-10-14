# Replication of the 2M recipe (B3): results

Protocol: [REPLICATION_2M_PROTOCOL.md](REPLICATION_2M_PROTOCOL.md), committed (`83c3ada`) before training. Seeds 801 (the B2 run, re-evaluated), 851 and 901 (new), 1,998,848 added transitions each, same recipe and code. Evaluation pool 886000 to 886063 (64 episodes per cell), unused before.

## Outcome by the frozen rule

**Positive (replicates).** Stage 61, deterministic, pool 886000:

- Mean `passages` of the three seeds: 39.0/64 (threshold 28).
- Every seed at least 20: 42, 36, 39.
- Medium at least 48 in every seed: 49, 54, 55.

The two new seeds, which are the independent test, score 36 and 39, both above the 28 threshold, against a start checkpoint that scores 5/64 on the same cell.

## Results (successes / collisions / timeouts, out of 64)

Stage 61 (1,998,848 transitions), the decision checkpoint:

| Seed | `passages` det. | `passages` sampled | Medium det. | Medium sampled | `passages-mid` det. | `passages-wide` det. | `gate-two` det. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 801 | 42 / 8 / 14 | 45 / 15 / 4 | 49 / 11 / 4 | 51 / 11 / 2 | 56 / 2 / 6 | 64 / 0 / 0 | 64 / 0 / 0 |
| 851 | 36 / 16 / 12 | 43 / 13 / 8 | 54 / 7 / 3 | 50 / 13 / 1 | 57 / 0 / 7 | 64 / 0 / 0 | 64 / 0 / 0 |
| 901 | 39 / 8 / 17 | 42 / 11 / 11 | 55 / 5 / 4 | 54 / 10 / 0 | 54 / 2 / 8 | 64 / 0 / 0 | 64 / 0 / 0 |
| Start checkpoint (baseline) | 5 / 27 / 32 | 7 / 37 / 20 | 51 / 7 / 6 | 54 / 8 / 2 | not run | not run | not run |

Stage 46 (1,507,328 transitions), reported and not used for the decision:

| Seed | `passages` det. | `passages` sampled | Medium det. | Medium sampled |
| --- | --- | --- | --- | --- |
| 801 | 40 / 15 / 9 | 43 / 16 / 5 | 45 / 13 / 6 | 54 / 9 / 1 |
| 851 | 33 / 15 / 16 | 41 / 13 / 10 | 53 / 8 / 3 | 54 / 8 / 2 |
| 901 | 33 / 7 / 24 | 40 / 13 / 11 | 53 / 7 / 4 | 56 / 7 / 1 |

Wilson 95% intervals for `passages`, stage 61, deterministic (percent): 42/64 is 53 to 76, 36/64 is 44 to 68, 39/64 is 49 to 72; the start checkpoint's 5/64 is 3 to 17.

## What the numbers show

- The effect replicates. Three seeds land at 36 to 42 on `passages` (spread of 6), against 5 for the start checkpoint and a 262k control mean of 12.3 on another pool. Sampled results agree (42 to 45).
- Seed 801 scores 42 here against 38 on pool 885000, and its stage 46 scores 40 here against 48 there. The 10-episode stage 46 versus 61 difference seen in B2 does not repeat on this pool: stage 61 is higher than or equal to stage 46 in deterministic mode for all three seeds (42 vs 40, 36 vs 33, 39 vs 33). That B2 gap was pool and seed noise, as the protocol allowed.
- `passages-mid` is 54 to 57 of 64 on all three seeds (84 to 89 percent). `passages-wide` and `gate-two` are 64/64 everywhere.
- Medium is the weak side. The start checkpoint scores 51 on this pool and the trained seeds 49, 54 and 55. Seed 801 sits one episode above the 48 line and its stage 46 (45) is under it. The release gate needs 52 and no more than 3 collisions in medium; collisions are 5 to 11 here. Medium does not improve with budget; it holds roughly where it was.
- Collisions on `passages` are 8, 16 and 8 at stage 61. The gate allows 3. They are lower than the 18 to 30 seen at 1M and below, and the start checkpoint has 27, but they have not reached the gate. Timeouts (12 to 17) are the larger part of the failures.

## Limits

- Three seeds from one start and one recipe on development pools. The new seeds are the replication; seed 801 motivated the test. A spread of 6 episodes among three seeds does not bound the spread across many seeds (the variance study found up to 11 of 32 on one profile for a smaller budget).
- `passages` is a partitioned-room family that appears in training. Nothing here measures levels B and C, `large`, `maze` or any family outside training. The release gate (at least 52 of 64 and at most 3 collisions in each of four families) is not met: `passages` is 36 to 42 with 8 to 16 collisions.
- The budget is not isolated from the schedule: the learning rate falls over the whole 2M, so no point of this run equals a shorter run. B1 (1M, one seed) and the three 2M seeds show that more budget helps in this recipe, and not that 2M is the best budget.
- The start checkpoint's 5/64 on `passages` is lower than the earlier 262k control (12.3 on pool 882000). Pools differ.

## What this supports

With the full connectome in the loop and no privileged input, a longer PPO run from the retained start raises `passages` from about 5 to 12 of 64 to 36 to 42 on three seeds, with `passages-mid` at 54 to 57. That is the first training change in this project that moves the partitioned-room family on every seed tried. It supports a claim of zero-shot navigation in new partitioned rooms of the trained family at about 60 percent, with collisions above the release gate. It does not support any claim about unseen families.

## Artifacts

Runs: `runs/training/large-budget-2m/seed801` (B2), `seed851` and `seed901`, each with stages 1 to 61, `experiment.json` and logs. Evaluation cells in `runs/training/large-budget-2m/b3-eval/` and `summary.json`. Stage 61 hashes (first 16 hex): seed 851 `fc1b2c69068ac72e`, seed 901 `29ac1bcf11652646`, seed 801 `3a4150b59b5fc894`. Source checkpoint unchanged in both new trainings (hash checked). Evidence copy in `private/replication-2m-evidence/`.

Timing from the clock: first stage of seed 851 saved at 09:32:11 on October 13; seed 851 finished at 10:52:40; seed 901 finished at 12:15:10; evaluation finished at 13:05:14 (50 min 4 s for 46 cells, 1.1 min per cell as estimated). Stage seconds sum to 81 min 40 s for seed 851 and 82 min 22 s for seed 901, against 77 min estimated from B2, so 6 percent slower than the estimate. Total from first stage to the end of evaluation: 3 h 33 min against 3 h 25 min estimated.
