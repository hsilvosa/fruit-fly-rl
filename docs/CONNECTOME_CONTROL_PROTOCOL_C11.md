# No-connectome control (C1), stage C1.1: protocol

Declared October 13, 2026, before any training or evaluation of this stage. Continues [CONNECTOME_CONTROL_PROTOCOL.md](CONNECTOME_CONTROL_PROTOCOL.md) after the C1.0 gate ([results](CONNECTOME_CONTROL_RESULTS_C10.md)): a fresh policy reaches medium-room competence with the real connectome (61/64) and with the edge-shuffled reservoir (54/64). Question: on the harder cells that the retained policy improved, does the real connectome do better than the edge-shuffled control under the same chain, budget and seeds?

## Design

- Arms: `real` (full MaleCNS connectome) and `shuffled` (edge targets permuted, shuffle seed 1; see the C1 protocol). Everything else is identical.
- Chain: phase 1 (884,736 transitions of medium rooms from random weights, seed 1001 done in C1.0, seed 1051 new) then phase 2 (61 stages of 32,768 = 1,998,848 transitions with the B2 recipe: 32 simulators with 8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two`; clip 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, gamma 0.995, learning rate 3e-4 falling to 3e-5). Total 2,883,584 transitions per run, the same as the retained lineage (2.88M).
- Seeds: 1001 and 1051 in both arms (four phase 2 runs). The seeds are 50 apart so that simulator layout streams do not overlap. Phase 2 code is `scripts/train_fresh_phase2.py` (the B2 trainer with a configurable brain and source; the source checkpoint hash is checked after training); a one-stage smoke test passed.
- Schedule under the 95 percent ceiling: pair A = phase 2 of seed 1001 (both arms in parallel), pair B = phase 1 of seed 1051 (both arms), pair C = phase 2 of seed 1051. Two jobs at a time, 5 threads each. If the mean CPU over two minutes of overlap exceeds 93 percent, the second job of the pair runs after the first. Resources are logged every 10 s and the trainings stop if memory exceeds 95 percent. The driver is `scripts/connectome_control_c11_driver.py`; it is resumable by job and cell.
- Reference (not retrained): the retained arm, stage 61 of seeds 801, 851 and 901 ([REPLICATION_2M_RESULTS.md](REPLICATION_2M_RESULTS.md) and [LEVEL_BC_RESULTS.md](LEVEL_BC_RESULTS.md)). The control cells below use the same pools as those results, so no retained checkpoint is re-evaluated.

## Evaluation (final checkpoint of every run, stage 61)

- `passages`, `passages-mid`, `passages-wide`, medium: pool 886000 to 886063, 64 episodes (the pool of the retained replication; inspected for the retained arm and selecting nothing here).
- Level B: held-out sampler, difficulty 0.8, seeds 950000 to 950063, 64 episodes (development pool).
- Level C: 21 architectural situations x 8 headings, seed 900000, 168 episodes (development headings; this extends the use recorded in [LEVEL_BC_PROTOCOL.md](LEVEL_BC_PROTOCOL.md) to four control checkpoints, with the same safeguards: nothing is chosen from these numbers; the sealed final pools stay closed).
- Both action modes everywhere. **The decision mode is deterministic.**
- The shuffled checkpoints are evaluated with the shuffled brain injected (`scripts/eval_cell_brain.py`, and the `shuffled` argument of `eval_random_cell.py` and `eval_architecture.py`); one-episode smoke tests passed for all three.

## Decision rules (frozen)

Let R be the mean over the two `real` seeds and S the mean over the two `shuffled` seeds, deterministic, final checkpoint.

**Check on the chain** (before reading the arm comparison): the `real` mean on `passages` must be at least 28/64 (the B2 threshold). If it is lower, the fresh chain does not reproduce the retained effect, and the arm comparison is reported but it cannot be used to speak about the retained lineage.

**Primary comparison, `passages` (64 episodes):**

- **No evidence that wiring matters**: S is at least R minus 5 (the control is no worse than the real connectome within 5 episodes).
- **Evidence that wiring matters**: S is at most R minus 10, and every shuffled seed is below every real seed.
- **Inconclusive**: anything else.

**Secondary comparisons**, same cuts scaled to the sample: level B (64 episodes, cuts 5 and 10), `passages-mid` (cuts 5 and 10) and level C (168 episodes, cuts 13 and 26, the same proportions). Reported with the same wording, never used to override the primary.

## What each outcome allows us to say

- **No evidence** on the primary cell: the project cannot claim that the biological connectome improves or is necessary for navigation (PROJECT_COMPLETION rule). The release says that the policy works with the full connectome in the loop and that a shuffled reservoir does as well within the measured uncertainty.
- **Evidence** on the primary cell, not contradicted by the secondary cells (no secondary cell shows S at least R plus 5): the release may say that, for this recipe, the edge-shuffled reservoir learns less on partitioned rooms. It still cannot say the connectome is necessary, since one shuffled graph and two seeds were tested.
- **Inconclusive**: report the numbers and the spread. More seeds or a second shuffled graph are the next options; the user decides.

## Limits

- Two seeds per arm and one shuffled graph realization. Seed spreads on `passages` have reached 6 episodes among the three retained seeds at stage 61 (36 to 42), and 10 or more in earlier smaller-budget runs, so the 5 and 10 cuts are narrow. The cuts are arbitrary and were set before the run.
- The retained and fresh chains differ in history (the retained start came from a chain that cannot be reproduced exactly), so the retained arm is a reference and not part of the matched comparison.
- The shuffle preserves in-degree, out-degree, weights and signs. It tests the specific wiring and not every property of the connectome (for example its sparsity pattern or hubs, which the shuffle keeps).
- Medium-room learning being equal in C1.0 (61 vs 54) already shows that the shuffled reservoir is a competent control, not that it is an equivalent one.
- The planner reference (C1.P) is a separate protocol.

## Estimate

Training: pair A, pair B and pair C. Phase 2 alone took 67 s per stage in the smoke test and 79 s in B2; two in parallel add about 5 to 10 percent (C1.0: 82 to 84 s against 82 alone), so about 85 s per stage, 61 stages is about 86 min per phase 2 pair. Phase 1 pair took about 38 min in C1.0. Total training about 3 h 30 (2 x 86 + 38 min). Evaluation: 48 runs, of which eight are level C (about 15 min each in B4 with parallel processes) and the rest about 1 to 2 min each; with up to 6 processes about 45 min. Total about 4 h 15. CPU mean about 66 percent with two trainings in parallel, peak 90 percent; memory about 66 percent. Nothing runs until the user says so.
