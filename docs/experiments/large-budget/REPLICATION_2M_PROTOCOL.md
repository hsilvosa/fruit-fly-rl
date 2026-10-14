# Replication of the 2M recipe (B3): protocol

Declared October 12, 2026, before training. Follows [LARGE_BUDGET_2M_RESULTS.md](LARGE_BUDGET_2M_RESULTS.md): on one seed (801) the 2M recipe reached `passages` 38/64 with 6 collisions on pool 885000. The variance study found seed spreads of up to 11 episodes of 32 on one profile, and the 1.5M and 2M points of that run differ by 10 (48 and 38), so one seed cannot show that the effect belongs to the budget. Question: does it replicate on other seeds?

## Design

- Recipe: exactly the B2 recipe (start `runs/training/reference-transfer-7/mix3e4/stage-2.zip`, 61 stages of 32,768 = 1,998,848 added transitions, 32 simulators with 8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two`, clip 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, gamma 0.995, learning rate 3e-4 to 3e-5). Same code (`scripts/train_large_budget.py`).
- Seeds: 801 (existing B2 run, not retrained), 851 and 901 (new). The training seed also offsets the layout seeds of the simulators (seed plus simulator index, 32 values), so seeds are spaced by 50 to keep the three runs from sharing layout streams. Earlier consecutive seeds (701 to 703) did share shifted streams.
- Two new trainings, one at a time. Source hashes are checked after each.
- Baseline: the experiment 7 start checkpoint, evaluated on the same pool, `passages` and medium.

## Evaluation

- Fresh development pool 886000 to 886063 (64 episodes per cell). Unused before, selects nothing. Pool 885000 was inspected for seed 801 in B2, so seed 801 is re-evaluated on the new pool and the replication does not reuse numbers that were seen. The reserved level A report pool (940000 to 949999) stays unopened: the recipe was chosen after looking at B1 and B2, so this is still development.
- Checkpoints: stage 46 (1,507,328) and stage 61 (1,998,848) of every seed. Declared now because stage 46 scored higher than stage 61 in B2 (48 against 38, deterministic). **The decision uses stage 61 only**; stage 46 is reported and never substituted.
- Cells: `passages` and medium at both checkpoints; at stage 61 also `passages-mid`, `passages-wide` and `gate-two`. Both modes are run. **The decision mode is deterministic.**
- Fan-out through `scripts/resource_guard.py` (4 processes, 2 threads each).
- Level B and level C are not measured here. They are a separate step (B4) with their own protocol, decided after this verdict, because the cost of the level C evaluation is not yet measured.

## Decision rules (frozen)

Applied to stage 61 of the three seeds, deterministic, pool 886000:

- **Positive (replicates)**: mean `passages` of the three seeds at least 28/64, every seed at least 20/64, and medium at least 48/64 in every seed. Next step: B4, level B and C once, then the Phase 4 and 5 design for the remaining families.
- **Negative**: mean `passages` at most 20/64, or two or more seeds at most 16/64. The B2 result was a favorable seed. Close the scope with the bounded claim and run C1.
- **Inconclusive**: anything else. Report the three curves and decide with the user.

The thresholds are those of B2 (28 and 20), kept so the replication is judged against the rule that the first seed passed. They are arbitrary cut points set before the run. Also reported: collisions and timeouts (the gate allows 3 collisions per 64; B2 had 6), sampled numbers, the stage 46 values, the baseline, and the spread between seeds.

## Limits

- Three seeds give a mean and a spread, not a confidence interval that excludes seed luck for small effects. Seed 801 is not independent evidence because it motivated this test; the two new seeds are the real test, and the rule includes 801 only to fix the mean's reference.
- The pools are development pools. A positive result is on `passages` only, a family with partitions seen in training. It does not touch `large`, `maze` or the architectural family, and the gate (52 of 64 and at most 3 collisions per family) is not met by 38/64.
- The learning-rate schedule is tied to the total, so no earlier point is comparable to a separate shorter run.

## Estimate

Training 2 x about 77 min (65 to 81 s per stage in B2). Evaluation 46 cells at about 1.1 min each under the guard (B2: 26 cells in 29 min 30 s), about 52 min. Total about 3 h 25 min. CPU about 55% in training and 50 to 80% in evaluation, GPU 30 to 60%, one process during training.
