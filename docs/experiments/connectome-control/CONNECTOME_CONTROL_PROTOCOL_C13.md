# No-connectome control (C1), stage C1.3: protocol

Declared before any training or evaluation of this stage. Follows [CONNECTOME_CONTROL_RESULTS_C12.md](CONNECTOME_CONTROL_RESULTS_C12.md): at 4.88M transitions the fresh real arm scored 27.5 of 64 on `passages` (the chain check needed 28), the shuffled arm 21.0 and the retained lineage 38.0, with two seeds per arm. The per-seed counts were 21 and 34 (real) and 13 and 29 (shuffled), so the spread inside an arm (13 and 16 episodes) was larger than the difference between arms (6.5). That comparison could neither show nor exclude an effect of the wiring.

## Question

Does the real MaleCNS wiring give the learned policy any advantage over an edge-shuffled reservoir with the same degrees, weights and signs, once the seed spread is estimated from four seeds per arm instead of two?

## What this stage does not do

- **No interior-only shuffle.** The idea was a control that keeps the sensory-to-motor boundary of the real graph and rewires only the interior. The reservoir has no such boundary: `Brain` feeds each neuron two sensor channels chosen uniformly at random and pools the state of every neuron into 256 random buckets (`fly_rl/connectome/brain.py`, input and bucket assignment, fixed seed 42). Sensors and readout are not attached to sensory, descending or motor neuron classes, so there is no boundary to preserve. A connectome with anatomically placed inputs and outputs is a different experiment (call it C2): it needs new code and cannot reuse any retained checkpoint. It is listed as future work in the findings.
- **No second shuffle realization.** The shuffle seed stays 1. A second graph draw is a later stage (C1.4) and only if this one is informative; one change per experiment.

## Design

- Change (one): two more training seeds, 1101 and 1151, for both arms (`real` and `shuffled`), with the code and recipe of the earlier seeds. Seeds 1001 and 1051 are not rerun; their checkpoints and C1.2 results are used as they are.
- Chain per run, as in C1.0 to C1.2: phase 1 (27 stages of medium rooms from random weights, `train_fresh_chain.py`), phase 2 (61 stages of the B2 recipe, `train_fresh_phase2.py`), phase 3 (61 more stages with layout offset 100). In all, 149 stages of 32,768 = 4,882,432 transitions, the same total as C1.2.
- Recipe, unchanged: 32 simulators (8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two` in phases 2 and 3), clip 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, gamma 0.995, learning rate 3e-4 to 3e-5 in each phase.
- Same brains: the real connectome and the edge-shuffled reservoir with shuffle seed 1.
- Schedule: one pair at a time (real and shuffled of the same seed in parallel, 5 threads each), phases in order, seed 1101 first and then seed 1151. Ceiling 95 percent, same fallback as C1.2: if the mean CPU over two minutes of overlap exceeds 93 percent, the second job of the pair runs after the first. Driver `scripts/connectome_control_c13_driver.py` (`train-only` as first argument stops before the evaluation; `dry-run` prints the pending jobs and exits). Resumable by job and cell; an interrupted training is restarted from scratch.

## Evaluation (final checkpoint of each new run)

The cells and pools are those of C1.2, so all four seeds of an arm are compared on the same maps.

- Pool 888000 to 888063 (64 episodes) for `passages`, `passages-mid`, `passages-wide` and medium, deterministic and sampled. The pool was inspected in C1.2 but nothing was selected on it, and keeping it makes the new seeds directly comparable with seeds 1001 and 1051 and with the retained reference (41, 35, 38 on `passages`, not rerun).
- Level B development maps (950000 to 950063, both modes) and level C development headings (seed 900000, 168 episodes, deterministic only).
- **The decision mode is deterministic.** Sampled results are reported.
- The reserved pools (940000 to 949999, 960000 to 969999, 970000 to 979999) are not touched.

## Decision rules (frozen)

R is the list of the four `real` seeds (1001, 1051, 1101, 1151) and S the four `shuffled` seeds, final checkpoint, deterministic, pool 888000. `D = mean(R) - mean(S)` with a Welch interval (unequal variances; the arms are independent trainings). The computation is `scripts/connectome_control_stats.py`, checked against `scipy.stats.ttest_ind(equal_var=False)`. Verdicts, evaluated in this order:

- **Wiring matters**: `D >= 10` and the 95 percent interval of D lies above 0.
- **Shuffled better**: the 95 percent interval of D lies below 0.
- **Equivalent within 10 episodes of 64**: the 90 percent interval of D lies inside (-10, +10) (two one-sided tests at 5 percent).
- **Inconclusive**: anything else.

Primary cell: `passages`. Secondary cells with the same rules: `passages-mid`, `passages-wide`, medium and level B (margin 10), and level C (margin 26 of 168). Secondary results are reported and never override the primary one. `passages-wide` and medium sit near the ceiling for every run, so an "equivalent" verdict there says little.

**Chain check** (reported, not a gate): the real mean on `passages` of at least 28 of 64, the B2 threshold. If it fails again, the sentence in the release is that the fresh chain at 4.88M transitions stays below the retained lineage whatever the wiring.

## What each outcome allows us to say

- **Wiring matters**: with this recipe and this one shuffled graph, the real wiring learned more on partitioned rooms. Not that the connectome is necessary. A second graph draw (C1.4) is needed before anything stronger.
- **Equivalent**: no advantage of the real wiring larger than 10 episodes of 64 on `passages`, in this setup with randomly placed inputs and outputs.
- **Shuffled better**: reported as it is; it would say that the real wiring is not an advantage for this readout.
- **Inconclusive**: the release reports the interval and the number of seeds the question needs. It does not claim an effect or its absence.

## Expected precision

The C1.2 spread (standard deviations of about 9 for the real arm and 11 for the shuffled arm on `passages`) gives a standard error of D of about 7 with four seeds per arm, so a 95 percent interval of about plus or minus 17 episodes and a 90 percent interval of about plus or minus 14. Under that spread the stage can show a large effect (D of 17 or more) but is unlikely to reach "equivalent within 10", which needs a smaller spread or about seven seeds per arm. The stage narrows the interval; it will probably not settle the question by itself. The measured spread of the four seeds is reported whatever the verdict.

## Limits

- Four seeds per arm, one shuffled graph, development pools, one recipe and one start (random weights).
- Input and output placement is random for both arms, so the experiment tests the wiring inside the reservoir, not the anatomical sensorimotor organization.
- The retained lineage started from a different history (experiment 7); it stays a reference and not a matched arm.
- Level C is clustered by scene and inspected; it is descriptive.
- A negative result here does not say the connectome is useless; it says this control found nothing to separate it.

## Estimate

Basis (measured in C1.1 and C1.2 with a pair of parallel runs): phase 1, 27 stages, 40 min; phase 2, 61 stages, 83 to 84 min; phase 3, 61 stages, 78 to 81 min. One seed is about 203 min of training, two seeds about 6 h 46 min. Evaluation: 44 runs (four level C passes, eight level B runs, 32 cells), against 68 runs in 86 min 51 s for C1.2, of which 24 were the light retained cells, so about 60 to 70 min. In all about 7 h 50 min, of which the last hour is evaluation. CPU peaked at 90 percent and averaged 66 to 72 percent with one pair in C1.0 to C1.2, memory peaked at 66 percent. Disk use is small (about 76 MB per run). Two pairs at once have not been measured and are not used.
