# Reference-preserving transfer experiment 4: recover medium rooms, keep the gate gains

Declared October 8, 2026 before any training.

## Design

- Initialization: the final checkpoint of experiment 3 (`runs/training/reference-transfer-3/gates/chunk-16.zip`, 131,072 added transitions over the 50/64 source). This is a continued policy in a declared lineage: 50/64 source, then experiment 3, then this stage. Its hash is recorded at launch.
- One change relative to experiment 3: the medium share rises from 25% to 50%, and passages-wide enters the training mix.
- Plan: eight chunks of 8,192 (65,536 added). Cycle of four: medium, passages-wide, medium, gate-two. Twice. Unchanged reward, original goals, batch 8, gamma 0.995, coordinated dynamics, seeds 42 plus 100 plus chunk index. No planner actions, no imitation.

## Evaluation and selection (frozen before running)

- Cells: medium seeds 100000-100031 (regression pool), medium-b seeds 840000-840031 (a new development pool, to check pool-specific effects), gate-two 830000-830031, gate-long 830000-830031, passages-wide 830000-830031 (32 episodes here).
- Baselines: the experiment 3 final checkpoint on all cells, and the 50/64 source on medium-b.
- Evaluate after 32,768 and 65,536 added transitions.
- Accept a checkpoint only if medium is at least 21/32 and medium-b is not more than three episodes below the source on medium-b. Among accepted checkpoints, choose the highest passages-wide count, then gate-two, then the earlier checkpoint.
- Positive result: an accepted checkpoint whose passages-wide count is at least the experiment 3 baseline and whose gate-two count is not lower than 26/32. This permits the next stage (the `passages` profile in the mix). It is not a generalization claim.

## Limits

One seed. Wide intervals at 32 episodes. Medium pools were inspected before; medium-b is new but also a development pool.
