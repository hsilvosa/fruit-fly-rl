# Randomized distribution run (action R5)

Declared October 10, 2026 before any training on the randomized distribution. It follows the rules set by the variance study ([VARIANCE_STUDY_RESULTS.md](VARIANCE_STUDY_RESULTS.md)): at least three seeds, at least 64 episodes per comparison cell, best-of-N selection on a pool that the report does not use. Sealed definitions: [HELD_OUT_SPEC.md](HELD_OUT_SPEC.md). Sampler: [MAP_SAMPLER.md](MAP_SAMPLER.md).

## Question

Does training on a broad random map distribution, with medium rooms and two-gate rooms kept in the mix, give better performance on random and held-out-parameter maps than the fixed-profile recipe of the variance study?

## Design

- Start: `runs/training/reference-transfer-7/mix3e4/stage-2.zip`, the start of the variance study.
- Recipe: the variance study recipe (stabilization bundle: 32 simulators with 128 steps, clip range 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, learning rate decaying from 3e-4 to 3e-5 over the run, unchanged reward, original goals, coordinated dynamics, no planner actions, no imitation, full connectome). 98,304 added transitions in three stages, as in the variance study.
- One change: the mix. 8 original medium rooms, 4 two-gate rooms, and 20 randomized partitioned rooms from the training sampler (the level B region excluded), under the adaptive difficulty controller (initial 0.2, window 64, steps of 0.05).
- Seeds: 601, 602, 603.
- Control: the five variance-study runs (seeds 501 to 505), which share the start, recipe and budget and differ only in the mix (fixed profiles).
- Script: `scripts/train_random.py`. Runs are sequential. Evaluation goes through the resource guard.

## Evaluation

Final checkpoint of every run, R5 and control.

| Cell | What | Episodes |
| --- | --- | --- |
| Random A, difficulty 0.5 | Training sampler, seeds 890000 to 890063 | 64 |
| Random A, difficulty 0.9 | Training sampler, seeds 891000 to 891063 | 64 |
| Random B development | Held-out sampler (level B region), difficulty 0.8, seeds 950000 to 950063. Inspected, never used for selection | 64 |

R5 runs also get the fixed selection cells (medium, medium-b, gate-two, gate-long, passages-wide, passages-mid, passages, 32 episodes each) and the medium regression pools A and B, so they can be compared with the variance study on the same cells. The reserved pools (940000 to 949999, 960000 to 969999 and 970000 to 979999) are not opened.

Level C: one baseline measurement of the start checkpoint on the 21 architectural situations with 8 headings each (`scripts/eval_architecture.py`, seed 900000). It is allowed by the held-out specification because it cannot influence a recipe. No level C measurement of any R5 run is made here.

## Decision rules (frozen before running)

- Selection among R5 runs: the highest sum of successes on the two random A cells, among runs that pass the medium regression suite and keep gate-two at 28/32 or more. Random B development is not used for selection.
- Positive result: the mean of the three R5 runs on random A difficulty 0.9 and the mean on random B development are each at least 8 episodes of 64 above the mean of the five control runs, and every R5 run passes the regression suite.
- If only one of the two cells meets the margin, the result is mixed and is reported as such. If neither does, the result is negative.
- Always reported: every run's values, mean, range, and the fixed-profile cells for R5 against the variance study.
- The adaptive difficulty value reached at each stage is reported. A controller that stays at the minimum or the maximum is a finding about the training distribution.

## Limits

Three seeds against five control runs, from one start. The control runs were not trained on random maps, so a gain on random A may only show that more diverse training helps on diverse maps. Level B development shows behavior beyond the trained range for these checkpoints, and does not show generalization to an unseen family. The report pools are not opened. The level C baseline is a single measurement.
