# Level B and level C measurement (B4): protocol

Declared October 13, 2026, before any evaluation. Follows [REPLICATION_2M_RESULTS.md](REPLICATION_2M_RESULTS.md): the 2M recipe lifts `passages` to 36 to 42 of 64 on three seeds. Question: does any of that carry to the held-out parameter region (level B) or to a family that never entered training (level C)? This is a measurement of three frozen checkpoints. Nothing is trained or selected.

## What is measured

- Checkpoints: stage 61 (1,998,848 added transitions) of seeds 801, 851 and 901 (the same final checkpoints as B3, no choice among them), and the experiment 7 start checkpoint as baseline. SHA-256 of each is recorded in the results.
- **Level B**: held-out sampler (opening width below 3.8 m with at least four partitions), difficulty 0.8, seeds 950000 to 950063, 64 episodes, `scripts/eval_random_cell.py`. This is the development pool used for every earlier level B number (1 to 6 of 64 for all earlier runs), so the numbers are directly comparable. It is inspected and selects nothing. The final region (960000 to 969999) stays sealed.
- **Level C**: the 21 architectural situations, 8 headings each, seed 900000 (168 episodes), `scripts/eval_architecture.py`. This is the development headings set used for the start checkpoint baseline (71 of 168, 42 percent, deterministic, 22 minutes). That baseline is not repeated. The final headings (970000 to 979999) stay sealed.
- Both action modes for every checkpoint and level. **The decision mode is deterministic.** The start checkpoint in sampled mode is run; its deterministic level C number is the recorded 71 of 168.
- Both eval scripts gained an optional `sampled` argument; the default is unchanged (deterministic) and the output files only add an `actions` field.

## Exception to the held-out rule, recorded

[HELD_OUT_SPEC.md](../../methods/HELD_OUT_SPEC.md) allows one measurement of a starting checkpoint on level C before Phase 5, and says every other use is logged with its reason. This protocol uses the level C development headings on three trained checkpoints. Reason: the user asked for level B and C to be measured once after the replication, to learn whether the effect leaves the trained family. Safeguards: the three checkpoints were fixed before this measurement (B3); no checkpoint, setting or recipe is chosen from these numbers; all three seeds are reported; level C results may inform which family to work on next but not any hyperparameter or checkpoint; the final headings and the final level B region stay sealed. The scene geometry is fixed and not hidden (see the limits section of the spec), so these numbers show behavior in an unseen family and are not a final assessment.

## Decision rules (frozen)

Level B, deterministic, three seeds:

- **Positive**: mean at least 20/64 (half the `passages` rate of B3) and every seed at least 12/64. First evidence of transfer to the held-out region.
- **Negative**: mean at most 8/64 (earlier runs ranged from 1 to 6). No transfer.
- **Inconclusive**: anything else.

Level C, deterministic, three seeds:

- **Positive**: mean success rate at least 10 points above the start checkpoint's 42 percent (71 of 168), that is at least 88 of 168 on average, and no seed below the start's 71.
- **Negative**: mean within 5 points of the start or below (at most 79 of 168 on average).
- **Inconclusive**: anything else.

Per-scene results are reported but the rule uses the 168-episode total. The 10-point margin is about 1.8 standard deviations of the difference between two proportions at this sample size (5.5 points), and the 20/64 and 8/64 thresholds are arbitrary cut points. Also reported: collisions, timeouts, sampled numbers, per-scene tables, Wilson intervals.

## Consequences (declared)

- Both positive: design Phase 4 and 5 for the remaining gap (collisions and the families `large` and `maze`).
- Level B negative, level C anything: the effect is specific to the trained partition family. The bounded claim stands (zero-shot in new rooms of trained families), and the next step is one of the costly alternatives in [ROADMAP.md](../../../ROADMAP.md) or C1 and the release with limitations.
- Level C positive, level B negative: report the split, since the scenes have open routes that may inflate the rate.

## Limits

- Level C is 21 situations with eight initial headings each. The headings are not independent samples of buildings, and the 168 episodes are strongly clustered. Treat the rate as a descriptive number.
- Three checkpoints from one start and recipe; level B has 64 episodes per cell.
- Level B has 64 episodes at one difficulty; level B maps are the hardest ones the sampler produces and every earlier policy scored 1 to 6, so a flat result is the expected null.
- The release gate (52 of 64 and at most 3 collisions per family) is not tested by this protocol. Real buildings stay out of scope.

## Estimate

Level C: 22 minutes for 168 episodes in a single process (R5 measurement), 7 runs (three seeds in two modes and the start in sampled mode), 154 process-minutes. Level B: 8 cells of 64 episodes; no timing for this cell is recorded, and R5 evaluation took 2 h 50 against an estimate of 85 minutes, so estimates for these cells carry a large error. Under the guard with 4 processes of 2 threads each: about 1 h 30, plausibly up to 2 h 30. CPU 50 to 80 percent during evaluation, GPU light, no training.
