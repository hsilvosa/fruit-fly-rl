# Reference-preserving transfer experiment 3: graded gates

Declared October 8, 2026 before any training. The user delegated choices.

## Why

Edge ladder (frozen policies, 16 episodes, seeds 820000-820015, evaluation only, `scripts/profile_edge_ladder.py`):

| Profile | Description | 48/64 v3 policy (`3b9e8ba41305`) | 50/64 v2 policy (`0a1a6569549a`) |
| --- | --- | ---: | ---: |
| gate-near | 12 x 12 x 10, one wall, 4.5 m opening | 12/16 | 14/16 |
| gate-long | 24 x 12 x 10, one wall, 14 m separation | 5/16 | 11/16 |
| gate-two | 24 x 12 x 10, two walls | 0/16 | 5/16 |
| passages-wide | 32 x 32 x 12, 3 partitions, wide openings | 1/16 | 0/16 |

The 50/64 policy solves single gates and partly solves two gates. Experiments 1 and 2 jumped to `passages` and gave no success signal. This experiment trains where successes already occur, and mixes in medium rooms.

## Design

- Initialization: retained 50/64 checkpoint `0a1a6569549a` (v2 interface, warm-start lineage), copied, never modified. It is the best historical medium result and the best gate performer.
- One change relative to experiment 1: the partitioned training maps are the graded gates, not `passages`.
- Plan: 16 chunks of 8,192 transitions (131,072 added). Cycle of four chunks: gate-long, gate-two, medium, gate-two. Medium rooms are 25%. Original goals throughout. Unchanged reward. Training seed 42 plus chunk index. No planner actions, no imitation. Full MaleCNS v1.0 connectome.
- Batch 8, gamma 0.995, coordinated dynamics.

## Evaluation and selection (frozen before running)

- Evaluations at 0 (baseline), 65,536 and 131,072 added transitions.
- Medium regression: seeds 100000-100031, the pool where the source scored 23/32. Accept only 21/32 or more.
- Gate-two development: seeds 830000-830031. Gate-long: seeds 830000-830031. Passages-wide transfer probe: seeds 830000-830015.
- Among accepted checkpoints, choose the highest gate-two success count, then gate-long, then the earlier checkpoint.
- A positive result is an accepted checkpoint that beats the baseline on gate-two by at least 6 of 32 episodes. This needs a real gain, because 32 episodes give wide intervals. It permits the next stage (graded partitions toward `passages`). It is not a generalization claim.
- Lost medium successes are listed by seed.

## Limits

One training seed. Thirty-two episodes per cell. The medium pool was inspected before. Gate profiles are simple single and double walls, not architectural scenes.
