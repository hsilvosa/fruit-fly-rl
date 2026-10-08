# Reference-preserving transfer experiment 8: results

Completed October 8, 2026 under [REFERENCE_TRANSFER_PROTOCOL_8.md](REFERENCE_TRANSFER_PROTOCOL_8.md), committed before training (`6413312`). Start: the experiment 7 selected checkpoint. Mixed-batch training, learning rate 0.0003, 262,144 added transitions per seed, seeds 442 and 443 run in parallel. The starting checkpoint hash was unchanged. No reserved pool was used.

## Outcome

Negative. No checkpoint of either seed met the acceptance rule, and the positive result was not met. Continued training degraded the partitioned-map skills and, at several points, the medium-room regression too. The experiment 7 selected checkpoint (`runs/training/reference-transfer-7/mix3e4/stage-2.zip`) remains the best development candidate.

Cells, 32 episodes each. Columns: medium 100000, medium-b 840000, gate-two, gate-long, passages-wide, passages-mid, passages. A dash marks a failed acceptance condition.

| Seed | Added | Medium | Medium-b | Gate-two | Gate-long | Wide | Mid | Passages | Accepted |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| Start | 0 | 26 | 29 | 32 | 29 | 25 | 16 | 3 | not applicable |
| 442 | 65,536 | 19 | 23 | 31 | 30 | 1 | 0 | 0 | no (medium) |
| 442 | 131,072 | 22 | 24 | 25 | 29 | 17 | 4 | 0 | no (gate-two) |
| 442 | 196,608 | 18 | 15 | 31 | 27 | 5 | 2 | 2 | no (medium, medium-b, wide) |
| 442 | 262,144 | 24 | 28 | 31 | 32 | 5 | 4 | 0 | no (wide) |
| 443 | 65,536 | 24 | 28 | 30 | 30 | 5 | 5 | 1 | no (wide, gate-two) |
| 443 | 131,072 | 25 | 29 | 30 | 30 | 11 | 8 | 0 | no (wide, gate-two) |
| 443 | 196,608 | 16 | 28 | 27 | 21 | 2 | 3 | 0 | no (medium, wide, gate-two) |
| 443 | 262,144 | 18 | 26 | 31 | 32 | 10 | 6 | 0 | no (medium, wide) |

The baseline reads 16 on passages-mid here, and 15 in the same checkpoint's evaluation inside experiment 8's other seed. Experiment 7 measured 15. The evaluation is not exactly repeatable (GPU sparse operations and process timing), with a spread of about one episode.

## Reading

1. The gains seen in experiment 7 did not persist. Both seeds lose most of the partitioned-map performance within 65,536 transitions and do not recover in 262,144. Passages-wide falls from 25 to a range of 1 to 17 of 32.
2. The two seeds behave alike on average and differ at each point, so the swings come from the training process, not from one unlucky seed.
3. The experiment 7 numbers were selected from several noisy checkpoints on the same development pools used to report them. Selecting the best of several noisy checkpoints raises the apparent score. The experiment 7 result is therefore an upper estimate, and this experiment is the unbiased follow-up: from that start, the typical outcome of further PPO training is a loss of skill.
4. The training signal at these settings does not hold what it finds. Plain PPO with a constant learning rate on this policy oscillates. More budget does not fix that, and the earlier tests of a lower rate also did not learn.
5. The historical reference is intact. Medium rooms stay near their level at the evaluated points that passed, gates stay at 25 to 32 of 32, and the 50/64 source file and aliases are unchanged.

## Consequence

Further runs of the same family (more PPO steps on the same maps) have a low chance of progress. The next step needs a qualitative change, for example:

- Planner imitation of opening crossings on partitioned maps, with separate teacher-collection and imitation budgets, followed by planner-free evaluation. The completion plan lists this as an option that needs an agreed budget.
- Checkpoint handling that suits oscillation: a separate selection pool distinct from reporting pools, and a smaller trust region (smaller clip range, fewer epochs per update) to reduce the swings.
- A trainer change that does not restart the optimizer state, with the learning rate scheduled down over a run.

None of these is launched. See [TRANSFER_SUMMARY.md](TRANSFER_SUMMARY.md).
