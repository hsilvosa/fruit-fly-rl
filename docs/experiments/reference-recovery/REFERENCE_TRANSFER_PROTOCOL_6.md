# Reference-preserving transfer experiment 6: an intermediate partition profile

Declared October 8, 2026 before any training.

## Why

Experiment 5 raised passages-wide to 20 to 26 of 32 but left `passages` at 1 to 2 of 32. The two profiles share the room size and the three partitions. They differ in aperture (8 by 4.8 m against 4 by 4 m) and obstacle count (12 against 64). Gates to passages-wide worked by grading. This experiment adds one more grade.

## Design

- Initialization: `runs/training/reference-transfer-5/passages/chunk-8.zip` (the experiment 5 selected checkpoint, 65,536 added in that stage). Lineage: 50/64 source, experiments 3, 4, 5, then this stage. Hash recorded at launch.
- New profile `passages-mid` (`scripts/profiles/passages-mid.json`): 32 by 32 by 12 m, 36 obstacles, three partitions, aperture 6.0 by 4.4 m. It sits between passages-wide and passages. It uses the existing generator and the existing profile version.
- One change relative to experiment 5: `passages-mid` enters the mix, and `passages` keeps a smaller share.
- Plan: sixteen chunks of 8,192 (131,072 added). Cycle of eight, twice: medium, passages-mid, medium, passages-mid, passages, passages-mid, gate-two, passages-wide. Medium is 25%, passages-mid 37.5%, passages 12.5%. Unchanged reward, original goals, batch 8, gamma 0.995, coordinated dynamics, training seeds 342 plus chunk index. No planner actions, no imitation. Parallel evaluation cells.

## Evaluation and selection (frozen before running)

- Cells: medium 100000, medium-b 840000, gate-two 830000, gate-long 830000, passages-wide 830000, passages-mid 850000, passages 810000 (32 episodes each).
- Baseline: the starting checkpoint on all cells.
- Evaluate after 65,536 and 131,072 added transitions.
- Accept only if medium is at least 21/32, medium-b at least 20/32 and passages-wide at least 16/32. Among accepted checkpoints, choose the highest passages-mid count, then passages, then the earlier checkpoint.
- Positive result: an accepted checkpoint with passages-mid at least 16/32 and passages at least three above the baseline. This permits the next stage (full-size `passages` weight, then `large` and maze). It is not a generalization claim.

## Limits

One seed. The passages-mid profile is a new development profile. No reserved pool is used. Passages pool 810000 has been inspected.
