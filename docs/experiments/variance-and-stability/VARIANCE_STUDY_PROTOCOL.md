# Variance study (action R1)

Declared October 10, 2026 before any training. Part of [ROADMAP.md](../../../ROADMAP.md).

## Question

How much do final results vary between training runs of one fixed recipe? Phase 1 showed differences of up to 18 episodes between two seeds, and a rerun with a different decay horizon reversed an outcome. A direct measurement sets the effect size that later comparisons must exceed, and it gives a legitimate best-of-N candidate.

## Design

- Recipe: exactly the Phase 1 pilot recipe (`scripts/train_phase1_pilot.py` settings), which produced the best development checkpoint. Start from `runs/training/reference-transfer-7/mix3e4/stage-2.zip`. 32 simulators with 128 steps, clip range 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, learning rate decaying from 3e-4 to 3e-5 over the run, the Phase 1 profile mix (medium 8, passages-mid 12, passages 4, passages-wide 4, gate-two 4), unchanged reward, original goals, coordinated dynamics, 98,304 added transitions in three stages. No planner actions, no imitation. Full connectome.
- Five training seeds: 501, 502, 503, 504, 505. Nothing else varies.
- Runs are sequential. Evaluation goes through the resource guard.

## Evaluation

For the final checkpoint of each run, 32 episodes per cell on:

- The seven selection cells (medium 860000, medium-b 861000, gate-two 862000, gate-long 862000, passages-wide 863000, passages-mid 864000, passages 865000).
- Regression pools A and B (medium 100000 and 840000), which complete the [medium-room regression suite](../../methods/MEDIUM_REGRESSION_SUITE.md) together with the two medium selection cells.

The report pools stay unopened.

## What gets reported (frozen before running)

- For every cell: the five values, mean, standard deviation and range.
- The regression suite verdict for each run.
- The hard-profile sum (passages-wide plus passages-mid plus passages) per run.
- The best run by the hard-profile sum among runs that pass the regression suite and keep gate-two at 28/32 or more. This is a best-of-5 selected on the selection pools. Its numbers are optimistic until it is evaluated on a pool that selection never used.
- The share of runs that reach passages-mid of 20/32 or more, as the pilot checkpoint did.

## Decision rule (frozen before running)

- If the range of passages-mid or of passages-wide across the five runs is at least 10 episodes of 32, single-run comparisons below 10 episodes are not valid. Every later comparison then needs at least three seeds and 64 episodes per cell, and best-of-N with a separate report pool becomes the method for choosing candidates.
- Otherwise a threshold of 6 episodes with two seeds stays acceptable.

## Limits

Five runs from one start. Thirty-two episodes per cell add sampling noise on top of training variance, so the measured range includes both. The number separates neither source, and the evaluation noise is known to be about one episode.
