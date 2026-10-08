# Reference-preserving transfer experiment 7: profiles mixed inside every update

Declared October 8, 2026 before any training.

## Why

Experiment 6 showed large swings between checkpoints (passages-wide 26, 5, 20 of 32). Chunks of 8,192 transitions each came from one profile, so the policy may follow the latest profile. This experiment trains all profiles at once: the eight parallel simulators of every PPO rollout run different profiles, and the run is continuous.

## Design

- Initialization: `runs/training/reference-transfer-6/mid/chunk-16.zip` (the experiment 6 selected checkpoint). Lineage: 50/64 source, experiments 3, 4, 5, 6, then this stage. Hash recorded at launch.
- Simulator assignment for the eight parallel environments (fixed for the whole run): medium, medium, passages-mid, passages-mid, passages-mid, passages, passages-wide, gate-two. Medium is 25%, passages-mid 37.5%, passages 12.5%, passages-wide 12.5%, gate-two 12.5%. Episodes restart in their own profile.
- Budget: 131,072 added transitions in two uninterrupted runs of 65,536 (no environment restart between them). Unchanged reward, original goals, batch 8, gamma 0.995, coordinated dynamics, training seed 442. No planner actions, no imitation.
- Two arms run in parallel, each with its own output directory:

| Arm | Learning rate | Single change |
| --- | --- | --- |
| mix3e4 | 0.0003 (unchanged) | Profiles mixed inside every update |
| mix1e4 | 0.0001 | Same, with a lower learning rate |

The learning rate is set after loading, and only the arm named above changes it.

## Evaluation and selection (frozen before running)

- Cells: medium 100000, medium-b 840000, gate-two 830000, gate-long 830000, passages-wide 830000, passages-mid 850000, passages 810000 (32 episodes each).
- Baseline: the starting checkpoint on all cells.
- Evaluate after 65,536 and 131,072 added transitions, per arm.
- Accept only if medium is at least 21/32, medium-b at least 20/32 and passages-wide at least 16/32. Among accepted checkpoints of both arms, choose the highest passages-mid count, then passages, then the earlier checkpoint.
- Positive result: an accepted checkpoint with passages-mid at least 16/32 and passages at least three above the baseline.
- Stability is also reported: for each arm, the spread of passages-wide and passages-mid across its two evaluations.

## Limits

One seed per arm. Thirty-two episodes per cell. Two arms with a shared start do not measure seed variance. No reserved pool is used.
