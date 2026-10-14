# Experiment catalog

This page lists every experiment series in the repository: the question it asked, its design, its outcome, the protocol and results documents, the scripts that implement it, and where its local run artifacts live. The chronological log is [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md); the live status is [ROADMAP.md](../../ROADMAP.md). Commands for reproducing each series are in [REPRODUCE.md](../operations/REPRODUCE.md).

## How to read the catalog

- **Protocol before run.** Each series has a protocol document committed before its training or evaluation started. The commit hash is quoted in the matching results document. A result is judged only against the rule in its protocol. Where a rule was missed, the results document says so; thresholds were not adjusted afterwards.
- **Pools discipline.** Every episode set is drawn from a named seed range (see the [pools registry](#pools-registry)). Selection pools choose checkpoints. Development pools are inspected but select nothing. Reserved and sealed pools have not been opened. A pool that has been used for selection is never reported as a test.
- **Negative results are reported.** Several series are negative or inconclusive by their own rule (for example R5, the students, the connectome control, and the level B part of B4). Those results are kept with the same detail as positive ones.
- **Denominators.** Outcomes are counts of successes out of the episodes in the cell (usually 64, or 32 for early experiments, 168 for level C). A success is a goal reached before the deadline without a collision; a collision or a timeout is a failure.
- **Local artifacts.** Checkpoints, logs, and per-episode records live in `runs/` and `private/`, which are not in git. Run directory names are given below as plain text. Checkpoint hashes are the first 16 hex digits of SHA-256 and are listed in [ROADMAP.md, section 9](../../ROADMAP.md#9-artifact-index).
- **Scope.** Experiments measure the learned controllers and the planner on the stated distributions. None of them establishes navigation on unseen maps in general, and the connectome is never credited by itself (see [Connectome control](#connectome-control-c10-c11-c12)).

## Reference recovery and transfer experiments 1 to 8

[Overview](reference-recovery/TRANSFER_SUMMARY.md) · [Historical reference](reference-recovery/HISTORICAL_REFERENCE.md) · [Failure classification](reference-recovery/PASSAGES_FAILURE_CLASSIFICATION.md)

**Question.** Can the recovered historical policy (50/64 on medium rooms) learn the partitioned maps (`passages`, `passages-wide`, gates) without losing medium-room skill?

**Design.** Each experiment continues the retained checkpoint (or starts a matched fresh v3 control) on a changed training mix, with a protocol committed before training. Evaluation uses the development pools only.

**Series and outcomes.**

| Experiment | Change | Outcome (successes of cell size) | Protocol / results |
| --- | --- | --- | --- |
| R0 (historical recovery) | Read-only recovery, hash check and replay of the medium winners | All winners recovered; replay matched per episode; reference 0/16 on `large` and `passages` | [HISTORICAL_REFERENCE.md](reference-recovery/HISTORICAL_REFERENCE.md) |
| F1 (failure classification) | Evaluation-only classification of two policies, 16 episodes each, `passages` seeds 810000 to 810015 | Collisions into partitions and hovering near them; no episode crossed all partitions | [PASSAGES_FAILURE_CLASSIFICATION.md](reference-recovery/PASSAGES_FAILURE_CLASSIFICATION.md) |
| T1 | Retained 48/64 policy and a fresh control on `passages`, 65,536 transitions | `passages` 0/32; medium 24/32 retained, 11/32 fresh. No candidate | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS.md) |
| T2 | Route-progress reward, and separately 262,144 transitions | `passages` 0/32; medium fell to 17/32. Neither accepted | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL_2.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS_2.md) |
| T3 | Graded gate maps with the 50/64 policy | `gate-long` 32/32, `gate-two` 28/32, `passages-wide` 4/16; medium 19/32, rejected | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL_3.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS_3.md) |
| T4 | Medium share raised to 50% | Positive: medium 24/32, gates 32/32 | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL_4.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS_4.md) |
| T5 | `passages` added to the mix | `passages-wide` 26/32, `passages` 2/32. Not positive | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL_5.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS_5.md) |
| T6 | `passages-mid` added | `passages-mid` 9 to 12/32, swings of 21 episodes between checkpoints. Not positive | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL_6.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS_6.md) |
| T7 | Profiles mixed inside every PPO update (8 simulators) | `passages-mid` 15/32, `passages` 4/32; one episode short of the rule | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL_7.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS_7.md) |
| T8 | Longer mixed-batch run, two training seeds | Negative: no checkpoint of either seed met the rule; gains lost | [protocol](reference-recovery/REFERENCE_TRANSFER_PROTOCOL_8.md) · [results](reference-recovery/REFERENCE_TRANSFER_RESULTS_8.md) |

**Scripts.** `scripts/train_reference_transfer.py` (T1, arms `retained` and `fresh`), `scripts/train_reference_transfer2.py` (T2, `route65` or `budget262`), `scripts/train_reference_transfer3.py` (T3), `scripts/train_reference_transfer4.py` (T4), `scripts/train_reference_transfer5.py` (T5), `scripts/train_reference_transfer6.py` (T6), `scripts/train_reference_transfer7.py` (T7, `mix3e4` or `mix1e4`), `scripts/train_reference_transfer8.py` (T8, `seed442` or `seed443`), `scripts/profile_edge_ladder.py`, `scripts/classify_failures.py`, `scripts/build_reference_manifest.py`, `scripts/replay_reference_validation.py`, `scripts/transfer_ladder_reference.py`. Full list in [scripts/README.md](../../scripts/README.md).

**Run directories.** `runs/training/reference-transfer-1` to `reference-transfer-8` (T1 to T8), `runs/verification/reference-recovery-1` (replay). Chain hashes: the 50/64 source `0a1a6569549a958a`; the experiment 7 start `773dff8d53e2e115`.

## Regression suite (medium rooms)

[Frozen regression suite](../methods/MEDIUM_REGRESSION_SUITE.md) · [Experiment log, R2](../EXPERIMENT_LOG.md)

**Question.** Does a candidate keep the medium-room skill of the historical winners?

**Design.** A frozen evaluation of 32 episodes on each of four medium pools (A 100000, B 840000, C 860000, D 861000), 128 episodes in total, with a declared pass rule (per-pool floor 17 of 32, total floor 88 of 128, and an original-pool floor of 21 of 32 that was declared first and amended after the baselines were measured).

**Outcome.** Historical winners scored 90 to 98 of 128; the experiment 7 start scored 111; the pilot candidate 104. The first per-pool rule failed two winners and was relaxed, openly.

**Scripts.** `scripts/regression_medium.py <checkpoint.zip> <label> <output-dir> [reference-result.json]`; it calls `scripts/resource_guard.py` through `run_limited`.

**Run directories.** Output written where the caller points it (no fixed directory in the script).

## Variance study (R1)

[Protocol](variance-and-stability/VARIANCE_STUDY_PROTOCOL.md) · [Results](variance-and-stability/VARIANCE_STUDY_RESULTS.md)

**Question.** How much does one recipe vary between training runs?

**Design.** The Phase 1 pilot recipe trained with five seeds (501 to 505), 98,304 added transitions each, from the experiment 7 checkpoint; each final checkpoint evaluated on the seven selection cells and on regression pools A and B, 32 episodes per cell.

**Outcome.** Training variance is large: the passages-wide range across seeds was 11 of 32. The pilot checkpoint was a real outlier (58% on `passages-mid` and 27% on `passages` on a fresh pool, from the confirmation). The rule now requires at least three seeds and 64 episodes per cell for later comparisons.

**Scripts.** `scripts/variance_driver.py` (driver), `scripts/train_variance.py <seedNNN> <output-dir>` (training, run with `NOEVAL=1`), `scripts/eval_checkpoint.py`, `scripts/summarize_variance.py`, `scripts/confirm_variance_best.py` (fresh pool 880000, 64 episodes per cell).

**Run directories.** `runs/training/variance-study/seed501` to `seed505`.

## Phase 1: stabilized trainer (pilot and run)

Pilot: [protocol](variance-and-stability/PHASE1_PILOT_PROTOCOL.md) · [results](variance-and-stability/PHASE1_PILOT_RESULTS.md). Run: [protocol](variance-and-stability/PHASE1_RUN_PROTOCOL.md) · [results](variance-and-stability/PHASE1_RUN_RESULTS.md)

**Question.** Does a stabilized PPO recipe keep the gains on the harder profiles, and is it stable across seeds (Phase 1 exit criterion)?

**Design.** Pilot: one seed (442), 98,304 added transitions, one evaluation of the final checkpoint on new selection pools. Run: two seeds (442, 443), four stages of 32,768 transitions each, four evaluations per seed on the old and selection pools, 32 episodes per cell.

**Outcome.** Pilot: `passages-mid` 21/32, `passages` 5/32, `passages-wide` fell to 11 to 12 of 32. The first pilot launch started too many evaluation processes and the PC was restarted; none of that launch is used, and the guard was added afterwards. Run: negative for the exit criterion. Seed 442 alone met it (range 1); seed 443 let `passages-wide` swing by 18 episodes (the limit was 6) and had one accepted checkpoint of four.

**Scripts.** Pilot trainer `scripts/train_phase1_pilot.py <seed442|seed443> <output-dir>` (three stages; there is no separate pilot driver in `scripts/`). Run trainer `scripts/train_phase1_run.py <seed442|seed443> <output-dir>` (four stages), driven by `scripts/phase1_driver.py` (sends Telegram milestones) or `scripts/phase1_driver_quiet.py` (same flow, Telegram off). Evaluation `scripts/eval_checkpoint.py`, aggregation `scripts/summarize_phase1_run.py`.

**Run directories.** `runs/training/phase1-pilot/seed442`; `runs/training/phase1-run/` (seeds 442 and 443).

## Phase 3: memory screening and replication

Screening: [protocol](variance-and-stability/PHASE3_SCREENING_PROTOCOL.md) · [results](variance-and-stability/PHASE3_SCREENING_RESULTS.md). Replication: [protocol](variance-and-stability/PHASE3_REPLICATION_PROTOCOL.md) · [results](variance-and-stability/PHASE3_REPLICATION_RESULTS.md)

**Question.** Does a temporal (GRU) memory over the connectome features help, and at which window length?

**Design.** Screening: one seed (442), two history windows (short: 8 frames, stride 8, 3.2 s; long: 16 frames, stride 32, 25.6 s), 131,072 added transitions each, stages 2 and 4 evaluated. Replication: the long window with seed 443, four stages evaluated, against the Phase 1 run with seed 443 as control.

**Outcome.** Screening: the long window was promising at its last evaluation (+19 on the hard-profile sum); the short window was worse than the control. Replication: did not replicate (+5, -9 and 0 against the control). Memory is not established.

**Scripts.** `scripts/phase3_driver.py` (screening), `scripts/train_phase3.py <short442|long442> <output-dir>`, `scripts/phase3_replication_driver.py` (trains `long443`), `scripts/eval_checkpoint.py`.

**Run directories.** `runs/training/phase3-screen/short442`, `long442`, `long443`.

## Random-map distribution (R5)

[Protocol](random-distribution/RANDOM_DISTRIBUTION_PROTOCOL.md) · [Results](random-distribution/RANDOM_DISTRIBUTION_RESULTS.md)

**Question.** Does training on randomized maps from the sampler help?

**Design.** Three seeds (601 to 603), 98,304 added transitions each, from the experiment 7 checkpoint, with 32 simulators (8 original medium rooms, 4 two-gate rooms, 20 randomized). Compared with the five variance-study runs as control. Evaluation on randomized level A maps at difficulty 0.5 (pool 890000) and 0.9 (pool 891000), and on the level B development pool 950000 (`scripts/r5_driver.py`). Pools 890000 and 891000 do not appear in the pools registry, so the registry should be checked before they are cited as inspected or unopened.

**Outcome.** Negative by the frozen rule: +1.1 and +0.6 of 64 against the controls. The difficulty controller stayed between 0.2 and 0.25. Run 601 reached 32/32 on `passages-wide` and was treated as an outlier.

**Scripts.** `scripts/r5_driver.py` (driver; it also runs the level C baseline of the start checkpoint), `scripts/train_random.py <start-without-zip> <seed> <output-dir> <stages>` (trainer), `scripts/eval_random_cell.py`, `scripts/eval_checkpoint.py`, `scripts/eval_architecture.py` (level C baseline, 168 episodes).

**Run directories.** `runs/training/random-run/seed601` to `seed603`; `runs/training/random-run/control-seed*`.

## Light audit (reward horizon)

[Results](diagnostics/LIGHT_AUDIT_RESULTS.md)

**Question.** Is hard-map exposure the gap, and does the reward make hovering look better than route following?

**Design.** No training, no policy, no GPU. The discounted return of an ideal route follower on certified `passages` routes is compared with hovering under the real reward (gamma 0.995).

**Outcome.** The ideal route follower beats hovering at every point, so the reward does not favor hovering. R5 randomized simulators completed 64 to 127 episodes in a whole run, which is a limited exposure count.

**Scripts.** `scripts/audit_reward_horizon.py` (no arguments; prints its result). Also `scripts/audit_architectural_curriculum_goals.py` for the architectural goals.

## Committee evaluation

[Results](diagnostics/COMMITTEE_EVAL_RESULTS.md)

**Question.** Is R5 run 601 a real candidate, and is the pilot's hovering a fixed point under stochastic actions?

**Design.** Fresh pool 880000 to 880063 (64 episodes), deterministic and stochastic sampling, for run 601 and the pilot. Evaluation only.

**Outcome.** Run 601 holds medium 92, wide 86, mid 55 and passages 14 percent. The pilot's wide-profile results ranged 14 to 55 of 64 when sampled, so the hover was not a general fixed point.

**Scripts.** `scripts/committee_evals.py` (drives `scripts/eval_cell.py` with `STOCHASTIC=1` for the stochastic cells). `scripts/eval_cell.py <checkpoint> <profile|none> <seed> <episodes> <out.json>`.

**Run directories.** Stored under the run directory of run 601 and the pilot; not a separate fixed path in the script.

## Collision anatomy

[Results](diagnostics/COLLISION_ANATOMY.md)

**Question.** Are `passages` collisions edge clips or navigation errors, and where along the route do they happen?

**Design.** Evaluation on pool 880000 to 880063 (64 episodes of `passages`), deterministic, recording the final position relative to the certified route and the obstacle hit.

**Outcome.** Collisions end 1.5 to 3.5 m off the route, around mid-route; edge clips are rare. The result does not separate missing exposure from missing information.

**Scripts.** `scripts/collision_anatomy.py <label> <checkpoint.zip> <profile> <seed> <episodes> <output.json>`. Also `scripts/collect_probe_data.py` for rollouts.

## Feature probe

[Results](diagnostics/FEATURE_PROBE.md)

**Question.** Do the 256 pooled connectome features carry the direction to the next opening on `passages`?

**Design.** Offline: rollouts of 64 episodes on seeds 881000 to 881063 (deterministic, every third step stored; run 601 gave 18,044 samples and the pilot 22,304). Ridge and small MLP probes split by episode.

**Outcome.** The features equal the raw sensors within 5 degrees, but decode the route direction only to 45 to 53 degrees on hard samples. The readout is not the lever; the sensors or the memory are.

**Scripts.** `scripts/collect_probe_data.py <checkpoint.zip> <profile> <seed> <episodes> <output.npz>`; `scripts/analyze_probe.py <name> ...` (reads the collected data).

**Run directories.** `runs/verification/probe/` (raw data).

## Sensing probes

[Results](diagnostics/SENSING_PROBES.md)

**Question.** Do feature history, longer rays or a panorama carry the route direction better than the 8 m rays?

**Design.** Offline. Feature-history probe on rollouts; long-range probe (rays and panorama cast to 24 m); a synthetic probe on 700 maps (seeds 895000 to 895699, no policy).

**Outcome.** With enough maps the 8 m rays already decode the direction to 34 degrees on the hard subset; 24 m rays reach 28 degrees. Rollout probes were too small to decide. The result points to a learning problem rather than a sensor limit for `passages`.

**Scripts.** `scripts/analyze_probe_variants.py history <name> | range <name-long>`; `scripts/collect_probe_data_long.py <checkpoint.zip> <profile> <seed> <episodes> <output.npz>`; `scripts/probe_synthetic.py <maps> <output-prefix>`.

## Waypoint diagnostic

[Protocol](diagnostics/WAYPOINT_DIAGNOSTIC_PROTOCOL.md) · [Results](diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md)

**Question.** Is missing route information the limit on `passages`?

**Design.** Four trainings of 262,144 added transitions from the experiment 7 start: a privileged-waypoint arm and a zero-input control arm, seeds 701 and 702. Final checkpoints evaluated on pool 880000 (64 episodes per cell).

**Outcome.** Partial by the rule: `passages` 37.5 against 11 of 64 (threshold 40). Route information is a major limit, but even exact information leaves `passages` below the gate.

**Scripts.** `scripts/waypoint_driver.py` (driver), `scripts/train_waypoint.py <waypoint|control> <seed> <output-dir> <stages>`, `scripts/eval_waypoint_cell.py <checkpoint.zip> <profile|none|heldout_b> <seed> <episodes> <out.json> <arm>`.

**Run directories.** `runs/training/waypoint-diagnostic/waypoint701` (and the other arm and seed names).

## Auxiliary and privileged-critic students

[Protocol](students/AUXILIARY_STUDENT_PROTOCOL.md) · [Results](students/AUXILIARY_STUDENT_RESULTS.md)

**Question.** Can a route signal that exists only during training help an autonomous actor?

**Design.** Seven trainings of 262,144 added transitions from the experiment 7 start: auxiliary waypoint-prediction head (`aux`, seeds 801 to 803), privileged critic with a blind actor (`critic`, seeds 801 to 803) and matched controls. The actor never receives the route input.

**Outcome.** Negative by the rule: `passages` +2.3 (aux) and +0.7 (critic) of 64. The auxiliary arm with sampled actions was +6.3 on average, the only positive signal, and it was not a decision under the protocol. Seed spread was of the same order as the effects.

**Scripts.** `scripts/student_driver.py` (driver), `scripts/train_student.py <aux|critic|pre> <seed> <output-dir> <stages>`, `scripts/train_waypoint.py` (the `control` arm), `scripts/eval_waypoint_cell.py` (`aux` and `critic` arms).

**Run directories.** `runs/training/student-experiment/`.

## Supervised pretraining of the actor trunk

[Protocol](students/PRETRAIN_PROTOCOL.md) · [Results](students/PRETRAIN_RESULTS.md)

**Question.** Does supervised pretraining of the actor trunk on route-direction labels help PPO?

**Design.** Data: sampled-action rollouts of the source policy on 512 maps (pretraining data pool 896000 to 896799). Pretraining with a cosine-plus-regression loss, a gate at 45 degrees, then three PPO trainings (seeds 901 to 903, `scripts/pretrain_driver.py`) and evaluation on pool 882000.

**Outcome.** The gate passed (41.6 degrees, behavior kept). PPO was negative: `passages` +2.0 of 64. The representation is not the bottleneck; using it in steering is.

**Scripts.** `scripts/pretrain_driver.py` (driver), `scripts/collect_pretrain.py` (data), `scripts/pretrain_trunk.py <data-dir> <output-dir>` (pretraining), `scripts/train_student.py pre <seed> <output-dir> 8` (seeds 901 to 903), `scripts/eval_waypoint_cell.py`.

**Run directories.** `runs/training/pretrain/data`, `runs/training/pretrain/pre901` to `pre903`.

## Large budget B1

[Protocol](large-budget/LARGE_BUDGET_PROTOCOL.md) · [Results](large-budget/LARGE_BUDGET_RESULTS.md)

**Question.** Is the training budget the lever for `passages`?

**Design.** The Phase 1 pilot recipe at 31 stages (1,015,808 added transitions), seed 801, from the experiment 7 start. Curve points at 98k, 295k, 590k and 1M, on pool 884000 to 884063 (64 episodes per cell, both modes).

**Outcome.** Inconclusive by the rule: `passages` 23/64 against the 24 needed (the negative threshold was 16 or fewer). Medium 59/64 at the final checkpoint. Collisions on `passages` ranged 18 to 30 along the curve.

**Scripts.** `scripts/large_budget_driver.py` (driver), `scripts/train_large_budget.py <seed> <output-dir> [stages, default 31]`, `scripts/eval_cell_mode.py <checkpoint> <profile|none> <seed> <episodes> <out.json> <det|sampled>`.

**Run directories.** `runs/training/large-budget/seed801`.

## Large budget 2M (B2)

[Protocol](large-budget/LARGE_BUDGET_2M_PROTOCOL.md) · [Results](large-budget/LARGE_BUDGET_2M_RESULTS.md)

**Question.** Does a 2M budget keep raising `passages`?

**Design.** The B1 recipe at 61 stages (1,998,848 added transitions), seed 801, on new pool 885000 to 885063. The B1 final checkpoint is re-evaluated on the same pool, so the 1M and 2M comparison does not depend on pool difficulty.

**Outcome.** Positive by the rule: `passages` 38/64 with 6 collisions (the 1M checkpoint scored 27 with 20 collisions), medium 54/64, `passages-mid` 56/64 . One seed, so the result is a replication target, not a confirmed effect.

**Scripts.** `scripts/large_budget_2m_driver.py` (driver), `scripts/train_large_budget.py 801 <output-dir> 61`, `scripts/eval_cell_mode.py`.

**Run directories.** `runs/training/large-budget-2m/seed801`.

## Replication of the 2M recipe (B3)

[Protocol](large-budget/REPLICATION_2M_PROTOCOL.md) · [Results](large-budget/REPLICATION_2M_RESULTS.md)

**Question.** Does the 2M effect replicate on other seeds?

**Design.** The B2 recipe on seeds 851 and 901 (seed 801 re-evaluated), stages 46 and 61 evaluated on pool 886000 (64 episodes per cell), with the experiment 7 start as baseline. Final stage also on `passages-mid`, `passages-wide` and the gates.

**Outcome.** Positive by the rule: stage 61 `passages` 42, 36 and 39 of 64 (mean 39.0; the start scored 5/64; threshold 28), medium 49, 54 and 55 of 64. Collisions 8, 16 and 8.

**Scripts.** `scripts/replication_2m_driver.py` (driver), `scripts/train_large_budget.py <seed> <output-dir> 61`, `scripts/eval_cell_mode.py`.

**Run directories.** `runs/training/large-budget-2m/seed851`, `seed901`, and evaluation in `runs/training/large-budget-2m/b3-eval/`.

## Level B and level C (B4)

[Protocol](large-budget/LEVEL_BC_PROTOCOL.md) · [Results](large-budget/LEVEL_BC_RESULTS.md)

**Question.** Does the 2M effect reach held-out level B maps or the level C architectural scenes?

**Design.** Frozen stage 61 of seeds 801, 851 and 901, plus the start checkpoint. Level B: held-out sampler, difficulty 0.8, pool 950000 to 950063 (64 episodes, development pool). Level C: 21 architectural situations with 8 headings each, seed 900000 (168 episodes, development headings).

**Outcome.** Level B inconclusive: mean 18.3 of 64 (26, 17 and 12; positive needed 20; start 1). Level C positive: 95, 108 and 108 of 168 (start 71); the courtyard scene regressed while the apartment and atrium were flat.

**Scripts.** `scripts/level_bc_driver.py` (driver), `scripts/eval_architecture.py <checkpoint.zip> <headings> <output.json> [seed] [sampled] [shuffled]`, `scripts/eval_random_cell.py <checkpoint.zip> heldout_b 0.8 950000 64 <output.json> [sampled]`.

**Run directories.** `runs/training/large-budget-2m/b4-eval/`.

## Connectome control: C1.0, C1.1, C1.2

C1.0: [protocol](connectome-control/CONNECTOME_CONTROL_PROTOCOL.md) · [results](connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md). C1.1: [protocol](connectome-control/CONNECTOME_CONTROL_PROTOCOL_C11.md) · [results](connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md). C1.2: [protocol](connectome-control/CONNECTOME_CONTROL_PROTOCOL_C12.md) · [results](connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md). C1.3 (prepared, not launched): [protocol](connectome-control/CONNECTOME_CONTROL_PROTOCOL_C13.md)

**Question.** Does the real MaleCNS wiring do better than an edge-shuffled reservoir with the same degree structure, when a fresh policy is trained with the same chain?

**Design.** A fresh two-phase chain from random weights, both arms (`real` and `shuffled`), seeds 1001 and 1051. C1.0: phase 1 only (27 stages, 884,736 transitions of medium rooms, seed 1001), pool 887000. C1.1: phase 1 for seed 1051, then phase 2 (61 stages, the B2 recipe), evaluated on the retained cells. C1.2: the four C1.1 phase 2 runs extended by 61 more stages (4.88M transitions in total), evaluated on pool 888000 and on level B and C.

**Outcome.** C1.0: gate passed (real 61/64, shuffled 54/64, retained start 55), with a gap of 7 that one seed cannot separate. C1.1: chain check failed (real 16.0 of 64 on `passages`, needed 28); shuffled 25.5, so no evidence that the wiring matters. C1.2: chain check failed by half an episode (real mean 27.5, needed 28); no cell favors the real connectome.

**Scripts.** `scripts/connectome_control_c10_driver.py`, `scripts/connectome_control_c11_driver.py`, `scripts/connectome_control_c12_driver.py` (optional first argument `train-only`). Trainers `scripts/train_fresh_chain.py <real|shuffled> <seed> <output-dir> [stages]` (phase 1) and `scripts/train_fresh_phase2.py <arm> <seed> <source> <output-dir> [stages] [offset]` (phase 2 and extension). Shuffled evaluation `scripts/eval_cell_brain.py`; graph check `scripts/check_shuffled_graph.py`.

**Run directories.** `runs/training/connectome-control/phase1-real1001`, `phase1-shuffled1001`, `phase1-real1051`, `phase1-shuffled1051`; `phase2-<arm><seed>`; `phase3-<arm><seed>`; evaluation in `c10-eval/`, `c11-eval/`, `c12-eval/`.

## Planner reference (C1.P)

[Protocol](connectome-control/PLANNER_REFERENCE_PROTOCOL.md) · [Results](connectome-control/PLANNER_REFERENCE_RESULTS.md)

**Question.** Where does the retained learned candidate stand against the four-family gate (medium, `large`, `maze`, architectural), and what does the explicit planner reach on level C?

**Design.** The explicit planner-1.4-exp.3 on the 168 level C cases (same headings as the learned baseline), and the retained stage 61 checkpoints of seeds 801, 851 and 901 on fresh `large` (pool 892000 to 892031) and `maze` (pool 893000 to 893031) cells, 32 episodes per cell, both modes. The planner does not run on medium rooms, `passages` or level B, so those cells are not applicable.

**Outcome.** Planner 147 of 168 on level C (4 collisions, 17 timeouts), 43 above the learned mean. Learned policy: `large` 2, 0 and 0 of 32; `maze` 0, 0 and 0 of 32. The gate was not met in any family.

**Scripts.** `scripts/planner_reference_driver.py` (driver), `scripts/eval_planner_architecture.py <output> <first> <last> [seed]` (planner, two headings per process), `scripts/eval_cell_mode.py` (learned cells).

**Run directories.** `runs/training/planner-reference/` (`planner-levelC-h*.json`, `seed*-large-*.json`, `seed*-maze-*.json`).

## Pools registry

Reproduced from [ROADMAP.md, section 8](../../ROADMAP.md#8-pools-registry). Seed ranges are the only source of episode layouts. "Reserved" and "sealed" pools have not been opened and must stay unopened until the final assessment (Phase 5 or the release decision).

| Pool | Seeds | Use | Status |
| --- | --- | --- | --- |
| Historical final pools | Recorded in `runs/suites/consumed` | Earlier final tests, including the 0/64 large-room pool | Consumed. Never a test again |
| Medium regression pool A (validation of the 50/64 policy) | 100000 to 100031 | Frozen regression suite | Inspected |
| Medium regression pool B | 840000 to 840031 | Frozen regression suite | Inspected |
| Medium regression pools C and D | 860000 to 860031 and 861000 to 861031 | Frozen regression suite. Also Phase 1 and 3 selection pools for medium | Inspected. Do not select on them for medium performance |
| Gate pools | 830000 to 830031 | Development | Inspected |
| `passages-wide` | 830000 to 830031 | Development | Inspected |
| `passages-mid` | 850000 to 850031 | Development | Inspected |
| `passages` | 810000 to 810031 | Development and failure classification | Inspected |
| Selection pools | 860000 to 865000 (one range per cell) | Choosing checkpoints (Phases 1 and 3) | Used for selection only |
| Report pools | Not yet drawn | Final Phase 1 style reports | Reserved, unopened |
| Level A report | 940000 to 949999 | Report pool | Reserved, unopened |
| Confirmation and comparison pools | 880000 to 880063; 882000 to 882063 | Fresh-pool confirmations, student comparisons (882000 reused for the pretraining comparison). Selected nothing | Inspected. 880000 also drove the committee analyses: not a selection set from now on |
| Probe pools | 881000 to 881063 (rollouts), 895000 to 895699 (synthetic poses), 896000 to 896799 (pretraining data) | Offline probes and supervised pretraining | Used. Never evaluation pools |
| Large-budget test pool (B1) | 884000 to 884063 | Curve evaluation of the 1M run, `passages` and medium, both modes ([protocol](large-budget/LARGE_BUDGET_PROTOCOL.md)) | Inspected. Selects nothing |
| 2M test pool (B2) | 885000 to 885063 | Curve evaluation of the 2M run and of the B1 final checkpoint, `passages` and medium ([protocol](large-budget/LARGE_BUDGET_2M_PROTOCOL.md)) | Inspected. Selects nothing |
| 2M replication pool (B3) | 886000 to 886063 | Stages 46 and 61 of seeds 801, 851 and 901 and the start checkpoint, `passages` and medium (final stage also mid, wide, gates) | Inspected. Selects nothing |
| C1.2 pool | 888000 to 888063 | `passages`, `passages-mid`, `passages-wide`, medium for the four extended control runs and the three retained seeds (reused by C1.3) | Inspected. Selects nothing |
| C1.P pools | `large` 892000 to 892031, `maze` 893000 to 893031 | Retained candidate on large and maze rooms; level C development headings for the planner | Inspected. Selects nothing |
| C1.0 pool | 887000 to 887063 | Medium rooms: retained start and the two fresh phase 1 arms | Inspected. Selects nothing |
| Level B region, development | Held-out sampler, 950000 to 959999 | Look at progress, not for selection | Drawn: 950000 to 950063 inspected for every R5 and student run |
| Level B region, final | Held-out sampler, 960000 to 969999 | Final assessment | **Reserved, unopened** |
| Level C scenes, development headings | 900000 and above | Baseline measurements only before Phase 5, with one declared exception (B4) | Used twice: baseline of the start checkpoint (71 of 168) and the three 2M checkpoints in B4 ([LEVEL_BC_PROTOCOL.md](large-budget/LEVEL_BC_PROTOCOL.md), results in [LEVEL_BC_RESULTS.md](large-budget/LEVEL_BC_RESULTS.md)) |
| Level C scenes, final headings | 970000 to 979999 | Final assessment | **Reserved, unopened** |

The roadmap's own rule applies here: a pool that has been inspected for one question is not a test for another, and the report pools remain unopened until the release decision.
