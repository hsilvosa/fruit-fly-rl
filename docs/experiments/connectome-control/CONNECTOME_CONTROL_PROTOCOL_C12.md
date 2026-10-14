# No-connectome control (C1), stage C1.2: protocol

Declared October 14, 2026, before any training or evaluation of this stage. Follows [CONNECTOME_CONTROL_RESULTS_C11.md](CONNECTOME_CONTROL_RESULTS_C11.md): the fresh two-arm chain (2,883,584 transitions) failed the chain check, since its real arm scored 16.0 of 64 on `passages` against 36 to 42 for the retained lineage, and the edge-shuffled arm scored 25.5. So the comparison was made far below the retained level. The user chose to strengthen the control. This stage tests the cheapest explanation, a larger budget, using the four runs that exist.

## Question

Does doubling the training of the fresh chain bring the real arm to the retained level on `passages`? B1 and B2 showed that budget raised the retained recipe from 26 to 38 between 1M and 2M, so a fresh chain may simply need more. If it does, the real-versus-shuffled comparison can be made at a level where a connectome advantage could appear. If it does not, the retained lineage owes its advantage to something the fresh chain lacks (the history of its start), which is a different question.

## Design

- Change (one): each of the four C1.1 final checkpoints (real and shuffled, seeds 1001 and 1051; `runs/training/connectome-control/phase2-<arm><seed>/stage-61.zip`) is trained for 61 more stages of 32,768 = 1,998,848 transitions with the unchanged B2 recipe (32 simulators with 8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two`; clip 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, gamma 0.995; learning rate restarts at 3e-4 and falls to 3e-5 over the 61 stages). Total per run 4,882,432 transitions (the retained lineage has 2.88M). Output `phase3-<arm><seed>`.
- The simulator layout seeds are shifted by 100 (`train_fresh_phase2.py` has a new optional offset, default 0, so earlier runs are unchanged; a one-stage smoke test passed) so that the continuation does not replay the layouts of phase 2.
- Same brains: the real connectome and the edge-shuffled reservoir with shuffle seed 1. One shuffled graph realization remains a limit; a second graph is a later stage (C1.3) only if this one is informative.
- Schedule: pair A = seed 1001 (real and shuffled in parallel, 5 threads each), then pair B = seed 1051. Same ceiling (95 percent) and same fallback to serial if the mean CPU over two minutes of overlap exceeds 93 percent. Driver `scripts/connectome_control_c12_driver.py`; `train-only` as first argument stops before the evaluation.

## Evaluation (final checkpoint of every run, both arms and seeds)

- New pool 888000 to 888063 (64 episodes, never used) for `passages`, `passages-mid`, `passages-wide` and medium, both modes. The three retained checkpoints (B3 stage 61 of seeds 801, 851, 901) are evaluated on the same pool in the same cells, so the retained reference does not depend on pool 886000.
- Level B (development maps 950000 to 950063, both modes) and level C (development headings, seed 900000, 168 episodes, **deterministic only** to save the slowest cell; the sampled level C numbers of C1.1 are not extended). The retained level B and level C numbers are those of [LEVEL_BC_RESULTS.md](../large-budget/LEVEL_BC_RESULTS.md).
- **The decision mode is deterministic.**

## Decision rules (frozen)

R is the mean of the two `real` seeds and S the mean of the two `shuffled` seeds, deterministic, final checkpoint, `passages`, pool 888000.

**Chain check**: R at least 28/64 (the B2 threshold and the C1.1 check). If it fails, the larger budget does not bring the fresh chain to the retained level. Then the result is "budget does not close the gap" and the comparison stays as in C1.1; nothing further is concluded about the connectome and the next question is the history of the retained start.

If the chain check passes, the comparison applies with the C1.1 cuts:

- **No evidence that wiring matters**: S at least R minus 5.
- **Evidence that wiring matters**: S at most R minus 10, and every shuffled seed below every real seed.
- **Inconclusive**: anything else.

Secondary cells with the same cuts: `passages-mid` (5 and 10), level B (5 and 10), level C (13 and 26 of 168). They are reported and never override the primary result.

Also reported: the retained mean on the same pool and the gap of each arm to it; the change from C1.1 (2.88M) to C1.2 (4.88M) for each run; collisions and timeouts.

## What each outcome allows us to say

- **Chain check passes and no evidence**: the shuffled control matches the real connectome at a performance close to the retained one, with two seeds and one graph. The release states that no connectome advantage was found.
- **Chain check passes and evidence**: the release may say that a degree-preserving shuffled reservoir learns less on partitioned rooms with this recipe, not that the connectome is necessary. A second graph (C1.3) is needed before anything stronger.
- **Chain check fails**: report that the fresh chain at 4.88M transitions stays below the retained level; the question becomes why (curriculum history), and the comparison between the arms stays a weaker-regime result.

## Limits

- Two seeds per arm, one shuffled graph, development pools. Seed spread among the retained seeds on `passages` is 6 and among the C1.1 real seeds 6; the 5 and 10 cuts are narrow.
- The extra budget also adds a second learning-rate cycle, which is part of the continuation and cannot be separated from the budget here.
- The fresh chain at 4.88M exceeds the retained lineage's 2.88M in transitions, so even a pass does not make the arms equal in compute with the retained policy; the retained policy remains a reference.
- Level C is clustered by scene and inspected; it is descriptive. Its sampled mode is not repeated in this stage.
- A negative result here does not say the connectome is useless; it says the control found nothing to separate it.

## Estimate

Training: two pairs of 61 stages. Phase 2 stages took 79 to 80 s on average in C1.1 (pair A, 21:52 finish, 83 min; pair C, 84 min) and 70 s alone in the smoke test, so about 84 min per pair, 2 h 48 for both. Evaluation: 68 runs (four level C passes, 8 level B, 32 cells on the new pool, 24 retained cells). C1.1 evaluated 48 runs including eight level C passes in 85 min, so this is about 80 min with a range of 60 to 100. Total about 4 h 10. CPU mean 66 to 76 percent with two trainings, peak 90; memory peak about 70. Nothing runs until the user says so, and the evaluation will not start by itself if the user asks for `train-only`.
