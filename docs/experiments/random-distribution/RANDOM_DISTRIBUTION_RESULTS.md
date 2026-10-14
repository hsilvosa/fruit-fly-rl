# Randomized distribution run (action R5): results

Run October 11, 2026 under [RANDOM_DISTRIBUTION_PROTOCOL.md](RANDOM_DISTRIBUTION_PROTOCOL.md), committed before training (`1d9a1b5`). Three seeds (601 to 603), 98,304 added transitions each, from the experiment 7 checkpoint, against the five variance-study runs as control. Training took 11 minutes in total. Evaluation took about 2 hours 50 minutes, against an estimate of about 85 minutes for evaluation. The driver also stopped silently at 10:03 for an unknown reason and was resumed at 10:47 without loss.

## Outcome by the frozen rule: negative

Successes out of 64 episodes, final checkpoints.

| Run | Random A, d=0.5 | Random A, d=0.9 | Random B development |
| --- | --- | --- | --- |
| R5 601 | 26 | 6 | 5 |
| R5 602 | 11 | 1 | 1 |
| R5 603 | 11 | 1 | 0 |
| R5 mean | 16.0 | 2.7 | 2.0 |
| Control 501 | 11 | 3 | 2 |
| Control 502 | 8 | 1 | 1 |
| Control 503 | 20 | 2 | 2 |
| Control 504 | 17 | 1 | 2 |
| Control 505 | 10 | 1 | 0 |
| Control mean | 13.2 | 1.6 | 1.4 |

The positive rule required a margin of at least 8 episodes of 64 on both d=0.9 and level B development. The margins are +1.1 and +0.6. No run of either group solves hard random maps: the best is 6 of 64 at d=0.9 and 5 of 64 on level B.

Fixed selection cells, 32 episodes (R5 runs only; control values are in [VARIANCE_STUDY_RESULTS.md](../variance-and-stability/VARIANCE_STUDY_RESULTS.md)):

| Run | Medium | Medium-b | Gate-two | Gate-long | Wide | Mid | Passages | Regression total of 128 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 601 | 21 | 24 | 32 | 32 | 32 | 19 | 7 | 97 |
| 602 | 25 | 28 | 32 | 32 | 18 | 3 | 0 | 109 |
| 603 | 27 | 27 | 32 | 32 | 23 | 7 | 0 | 112 |

All three pass the amended regression suite and keep gate-two at 28 or more. By the selection rule (highest sum on the two random A cells), run 601 is selected.

## Reading

1. **The adaptive difficulty barely moved.** The controller ended at 0.20 to 0.25 in all three runs, and the sampled maps had 1.1 to 1.4 partitions on average. With 98,304 transitions, the 20 random simulators finished too few episodes to fill the 64-episode window more than a few times, and success on the early maps stayed below the rise threshold. The training therefore saw mostly easy random maps. This run tests the recipe at a small budget, not the idea of a hard random distribution.
2. **Run 601 is an outlier again**, and not like the pilot: 32/32 on passages-wide (the best value measured), 19/32 on passages-mid and 7/32 on passages, with medium at 21 and 24. This is one run of three and it has not been confirmed on a fresh pool. The protocol does not let it count as a positive result, because the rule is about the mean.
3. The variance finding repeats. Among eight runs of two nearby recipes, one or two land far above the rest, and the means differ little.
4. No mix change has so far beaten the spread between seeds.

## Level C baseline of the start checkpoint

The experiment 7 checkpoint on the 21 architectural situations, 8 headings each (168 episodes, seed 900000): 71 successes (42%), 51 collisions and 46 timeouts. It took 22 minutes.

| Scene | Successes |
| --- | --- |
| courtyard | 24/24 |
| street-block | 12/40 |
| office-floor | 10/24 |
| warehouse | 10/32 |
| atrium | 8/24 |
| apartment | 7/24 |

Situations at 8/8: `over-the-desks`, `under-the-skybridge`, `bridge-crossing`, `gate-over-fountain`, `arcade-walk` and `courtyard-to-lobby`. Several of these are mostly open routes, so the 42% mixes open-space flights with real navigation. This is a baseline only. It was not used to choose anything.

## Consequences

- Result closed as negative under the frozen rule, with the controller's low difficulty as the main caveat.
- Run 601 is the selected R5 candidate. It is a development result, to be confirmed on a fresh 64-episode pool before any claim.
- The next experiment must make the random distribution actually hard. Options are a higher initial difficulty (for example 0.6), a smaller controller window, or a longer budget. Each is one change and needs a new protocol before training.
