# Reference-preserving transfer experiment 8: longer run, two seeds

Declared October 8, 2026 before any training.

## Why

Experiment 7 gave the best partitioned-map numbers with medium rooms preserved, but with one seed and a large dip (passages-wide 0 of 32 at one checkpoint). This experiment tests whether the gain continues with more budget, and measures seed variance with a second training seed.

## Design

- Initialization: `runs/training/reference-transfer-7/mix3e4/stage-2.zip` (the experiment 7 selected checkpoint). Lineage: 50/64 source, experiments 3, 4, 5, 6, 7, then this stage. Hash recorded at launch.
- Same mixed-batch assignment as experiment 7 (medium, medium, passages-mid x3, passages, passages-wide, gate-two), learning rate 0.0003, batch 8, gamma 0.995, coordinated dynamics, unchanged reward, no planner actions, no imitation.
- Single change relative to experiment 7: budget of 262,144 added transitions in four uninterrupted runs of 65,536, and two training seeds (442 and 443) run in parallel from the same start.

## Evaluation and selection (frozen before running)

- Cells and pools as in experiment 7: medium 100000, medium-b 840000, gate-two 830000, gate-long 830000, passages-wide 830000, passages-mid 850000, passages 810000, 32 episodes each.
- Evaluate after every 65,536 added transitions, for each seed.
- Accept only if medium is at least 21/32, medium-b at least 20/32, passages-wide at least 16/32 and gate-two at least 28/32. Among accepted checkpoints of both seeds, choose the highest passages-mid count, then passages, then the earlier checkpoint.
- Positive result: an accepted checkpoint with passages-mid at least 20/32 and passages at least 7/32, and the other seed also having an accepted checkpoint with passages-mid at least 15/32. This permits larger maps (large, maze) and an architectural stage. It is not a generalization claim.
- Report the spread between the two seeds at each evaluation.

## Limits

Two seeds share one starting checkpoint. They measure training-seed variance from that start, not variance of the whole lineage. Thirty-two episodes per cell. No reserved pool is used.
