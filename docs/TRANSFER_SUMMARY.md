# Transfer experiments 1 to 8: summary

October 8, 2026. Eight bounded experiments continued the recovered historical reference toward partitioned maps. Every experiment had its protocol committed before training. No reserved pool was used. The 50/64 and 48/64 checkpoints, the aliases and the original runs were never modified.

| Experiment | Change | Best partitioned-map result | Medium rooms | Outcome |
| --- | --- | --- | --- | --- |
| 1 | Retained 48/64 policy and a fresh control trained on `passages`, 65,536 transitions | passages 0/32 | 24/32 retained, 11/32 fresh | No candidate |
| 2 | Route-progress reward, and separately 262,144 transitions | passages 0/32 | fell to 17/32 | No candidate |
| 3 | Graded single and double gates from the 50/64 policy | gate-long 32/32, gate-two 28/32, passages-wide 4/16 | 19/32 | Rejected (medium) |
| 4 | Medium share 50%, passages-wide in the mix | passages-wide 6/32 | 24/32 | Positive |
| 5 | `passages` in the mix | passages-wide 26/32, passages 2/32 | 22 to 23/32 | Not positive |
| 6 | Intermediate profile `passages-mid` | passages-mid 12/32 | 23 to 26/32 | Not positive, unstable |
| 7 | Profiles mixed inside every update | passages-mid 15/32, passages 4/32 | 26/32 | One episode short of positive |
| 8 | 262,144 transitions, two seeds | no gain | 16 to 25/32 | Negative |

## What is established

- The historical winners are recovered, hash-verified and replay exactly (see [HISTORICAL_REFERENCE.md](HISTORICAL_REFERENCE.md)).
- The reference solves medium rooms and single gates and fails on rooms with several partitions. Training only on the hard maps (experiments 1 and 2) gave no signal. Grading the maps gave the first signal (experiment 3) and mixing in medium rooms kept the reference skills (experiments 4 to 7).
- Plain PPO at a constant learning rate oscillates on this policy. Performance on a profile moved by 20 episodes or more between checkpoints 65,536 transitions apart, and experiment 8 lost the experiment 7 gains.

## What is not established

- No candidate meets the proposed release gate (at least 52 of 64 on each of four families). The best development numbers are passages-wide about 25/32, passages-mid about 15/32 and passages about 4/32, with one seed and development pools. Large rooms, mazes and architectural scenes were not trained in these experiments.
- No claim holds about robustness across seeds, about the connectome's contribution, or about generalization to unseen layouts.
- Experiment 7 selected its checkpoint from several noisy evaluations on pools it also reports, so its numbers are optimistic.

## Open decision

The next step needs a qualitative change and an agreed budget: planner imitation for opening crossings (separate teacher and imitation budgets), or a trainer change that reduces oscillation (trust-region and learning-rate schedule with separate selection pools). The earlier plan in [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) calls for the user to agree the budget before a substantial new experiment.
