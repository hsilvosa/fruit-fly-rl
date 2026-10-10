# Phase 3 replication (experiment 12): long memory window, seed 443

Declared October 10, 2026 before any training. It replicates the one window that was promising in [PHASE3_SCREENING_RESULTS.md](PHASE3_SCREENING_RESULTS.md).

## Design

Identical to the screening for the long window (16 frames, stride 32, 25.6 s): same start, stabilization bundle, profile mix, budget (131,072 added transitions in four stages) and pools, with training seed 443. Nothing else changes. The report pools stay unopened. Resources: one training process, then evaluation through the resource guard, no Telegram.

Control for seed 443: the Phase 1 run with seed 443 and no memory ([PHASE1_RUN_RESULTS.md](PHASE1_RUN_RESULTS.md)), same start and mix.

Control values at stage 4 (131,072 added), order medium, medium-b, gate-two, gate-long, passages-wide, passages-mid, passages:

- Selection pools: [28, 27, 32, 32, 6, 10, 0].
- Old pools: [27, 30, 32, 32, 3, 11, 2].

Seed 442 control at stage 4: selection [25, 26, 31, 32, 22, 6, 2], old [21, 27, 32, 32, 22, 12, 2]. The seed 442 long-window result: selection [25, 28, 32, 32, 28, 15, 6], old [24, 30, 32, 32, 29, 23, 6].

## Decision rule (frozen before running)

- A seed shows a memory gain if, on the selection pools at stage 4, at least one of passages-wide, passages-mid and passages is at least 6 episodes above its seed's control, while medium is at least 21/32, medium-b at least 20/32 and gate-two at least 28/32.
- Seed 442 meets this (passages-wide +6, passages-mid +9, passages +4).
- The Phase 3 exit criterion is met if seed 443 also shows a memory gain. The same rule on the old pools is reported as a consistency check.
- If seed 443 does not show a gain, the result is recorded as not replicated, and the seed 442 result is treated as a high draw.
- All four stages are evaluated and reported, including the stability across stages.

## Limits

Two seeds from one start. Thirty-two episodes per cell. A gain here does not show generalization to unseen maps. It shows that a longer memory helps on the profiles in the training mix. The held-out parameters and family of Phase 2 are the test of generalization.
