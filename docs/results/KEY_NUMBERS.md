# Key numbers

A reference table of the headline measurements in the fly-rl project. Each row gives the cell, the policy or arm, the result with its denominator, the evaluation mode, the pool status and the source. Interpretation is in [FINDINGS.md](FINDINGS.md).

## How to read the columns

- **Result** is successes of the denominator unless the row says otherwise. Denominators: 32 (one 32-episode cell), 64 (one 64-episode cell), 168 (level C, 21 situations times 8 headings), 16 (small early cells).
- **Mode**: `det` is deterministic action selection (the roadmap decision mode). `samp` is sampled actions from the policy. `not recorded` means the source does not state the mode.
- **Pool status**: `Development (inspected)` means the pool has been looked at and used for development. `Selection` means it was used to choose checkpoints. `Consumed final` means a final assessment that cannot be used again. `Probe` means offline analysis only. `Reserved` means not yet opened. The registry is in [ROADMAP.md](../../ROADMAP.md#8-pools-registry).
- **Seeds** are listed where the source records them. A single-seed value is labelled as such and is not a claim.
- Values marked *derived* are means or differences computed from per-seed values listed in the same source, not stated in it.

## 1. Medium rooms

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Medium, historical final | Warm-start sensor comparison (50/64 reference) | 50 of 64 (78.1%); 5 collisions, 9 timeouts; Wilson 66.6 to 86.5 | not recorded | Consumed final | Seed 42 | [RESULTS](RESULTS.md#earlier-dense-room-results) |
| Medium, historical final | Observed-ray risk comparison (48/64) | 48 of 64 (75.0%); 16 collisions, 0 timeouts; Wilson 63.2 to 84.0 | not recorded | Consumed final | Seed 42 | same |
| Medium, historical final | Near-goal curriculum (45/64) | 45 of 64 (70.3%); 15 collisions, 4 timeouts; Wilson 58.2 to 80.1 | not recorded | Consumed final | Seed 42 | same |
| Medium, historical final | Original dense launcher (43/64) | 43 of 64 (67.2%); 11 collisions, 10 timeouts; Wilson 55.0 to 77.4 | not recorded | Consumed final | Warm-start line of earlier work | same |
| Medium, historical final | Fresh sensor comparison (35/64) | 35 of 64 (54.7%); 20 collisions, 9 timeouts; Wilson 42.6 to 66.3 | not recorded | Consumed final | Seed 42 | same |
| Medium, reference replay | 50/64 reference on validation pool 100000 to 100031 | 23 of 32 recorded; replayed 23 of 32; 32 of 32 episodes match | det (replay) | Development (inspected) | Reproduction check | [HISTORICAL_REFERENCE](../experiments/reference-recovery/HISTORICAL_REFERENCE.md) |
| Medium, reference replay | 48/64 and 45/64 checkpoints on their recorded pools | 27 of 32 and 27 of 32 replayed; 32 of 32 episodes match each | det (replay) | Development (inspected) | Reproduction check | same |
| Medium | Run 601 (R5 seed) | 59 of 64 (92%); 2 collisions, 3 timeouts; Wilson 83 to 97 | det | Development (inspected) pool 880000 | One run, chosen from three | [COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md) |
| Medium | Phase 1 pilot checkpoint (seed 442, stage 3) | 57 of 64 (89%); Wilson 79 to 95 | det | Development (inspected) pool 880000 | | same |
| Medium | Seed 505 (best of variance study) | 55 of 64 (86%); Wilson 75 to 92 | det | Development (inspected) pool 880000 | | same |
| Medium, 2M recipe | Seeds 801, 851, 901, stage 61 | 49, 54, 55 of 64; collisions 11, 7, 5; timeouts 4, 3, 4 | det | Development (inspected) pool 886000 | Three seeds | [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md) |
| Medium, 2M recipe | Same seeds, sampled | 51, 50, 54 of 64 | samp | Development (inspected) pool 886000 | | same |
| Medium, start checkpoint | Experiment 7 start (`mix3e4/stage-2`) | 51 of 64 det (7 collisions, 6 timeouts); 54 of 64 samp | det, samp | Development (inspected) pool 886000 | | same |
| Medium, 2M recipe | Seed 801, stage 61 | 54 of 64 det (7 collisions, 3 timeouts); 55 samp | det, samp | Development (inspected) pool 885000 | Final of B2 | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| Medium, B1 checkpoint | 1,015,808 transitions, seed 801 | 59 of 64 det; 58 samp | det, samp | Development (inspected) pool 884000 | Final of B1 | [LARGE_BUDGET_RESULTS](../experiments/large-budget/LARGE_BUDGET_RESULTS.md) |
| Medium, budget curve (B2 pool) | 491,520 / 1,015,808 / 1,507,328 / 1,998,848 transitions | det 50, 56, 54, 54 of 64; samp 50, 53, 57, 55 | det, samp | Development (inspected) pool 885000 | Seed 801 | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| Medium, budget curve (B1 pool) | 98,304 / 294,912 / 589,824 / 1,015,808 transitions | det 55, 51, 60, 59 of 64; samp 56, 54, 52, 58 | det, samp | Development (inspected) pool 884000 | Seed 801 | [LARGE_BUDGET_RESULTS](../experiments/large-budget/LARGE_BUDGET_RESULTS.md) |
| Medium, fresh chain (C1.0) | Real connectome, 884,736 transitions from random weights | 61 of 64 det (2 collisions, 1 timeout); 59 samp | det, samp | Development (inspected) pool 887000 | Seed 1001; gate was 40 | [CONNECTOME_CONTROL_RESULTS_C10](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md) |
| Medium, fresh chain (C1.0) | Edge-shuffled, same budget | 54 of 64 det; 60 samp | det, samp | Development (inspected) pool 887000 | Seed 1001, shuffle seed 1 | same |
| Medium, C1.0 start | Retained start on the same pool | 55 of 64 det; 59 samp | det, samp | Development (inspected) pool 887000 | | same |
| Medium, C1.2 | Real connectome, 4.88M transitions (seeds 1001, 1051) | 58 and 54 of 64 det (mean 56.0); 59 and 59 samp (mean 59.0) | det, samp | Development (inspected) pool 888000 | Two seeds | [CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md) |
| Medium, C1.2 | Edge-shuffled, 4.88M transitions | 54 and 53 of 64 det (mean 53.5); 55 and 57 samp (mean 56.0) | det, samp | Development (inspected) pool 888000 | Two seeds | same |
| Medium, C1.1 | Real (seeds 1001, 1051) and shuffled, 2.88M transitions | Real 57, 61 det (mean 59.0); shuffled 52, 55 det (mean 53.5) | det | Development (inspected); pool not stated in source | Two seeds per arm | [CONNECTOME_CONTROL_RESULTS_C11](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md) |
| Medium, regression (R1 selection) | Five variance-study runs, selection cells | 23, 25, 27, 24, 26 of 32 (mean 25.0); pass amended regression rule | not recorded | Selection | Seeds 501 to 505 | [VARIANCE_STUDY_RESULTS](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md) |
| Medium, level A report | Reserved report pool 940000 to 949999 | Not run | n/a | Reserved | | [ROADMAP](../../ROADMAP.md#8-pools-registry) |

## 2. Partitioned rooms (`passages` family)

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| `passages` | 2M recipe, stage 61 | Seeds 801, 851, 901: 42, 36, 39 of 64 (mean 39.0); collisions 8, 16, 8; timeouts 14, 12, 17 | det | Development (inspected) pool 886000 | Three seeds, one recipe | [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md) |
| `passages` | 2M recipe, same seeds | 45, 43, 42 of 64 | samp | Development (inspected) pool 886000 | | same |
| `passages` | Experiment 7 start checkpoint | 5 of 64 det (27 collisions, 32 timeouts); 7 of 64 samp | det, samp | Development (inspected) pool 886000 | | same |
| `passages` | 2M seed 801, stage 61 | 38 of 64 det (6 collisions, 20 timeouts); 45 samp | det, samp | Development (inspected) pool 885000 | One seed | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| `passages` | 2M seed 801 at 1,507,328 transitions | 48 of 64 det (6 collisions, 10 timeouts); 43 samp | det, samp | Development (inspected) pool 885000 | Reported, not used for decision | same |
| `passages` | B1 seed 801 at 1,015,808 transitions, same pool | 27 of 64 det (20 collisions, 17 timeouts); 30 samp | det, samp | Development (inspected) pool 885000 | | same |
| `passages` | B1 final, 1,015,808 transitions | 23 of 64 det (22 collisions, 19 timeouts); 25 samp | det, samp | Development (inspected) pool 884000 | Missed positive rule (24) by one | [LARGE_BUDGET_RESULTS](../experiments/large-budget/LARGE_BUDGET_RESULTS.md) |
| `passages`, budget curve | 98,304 / 294,912 / 589,824 / 1,015,808 transitions | det 11, 12, 17, 23 of 64; samp 15, 13, 15, 25 | det, samp | Development (inspected) pool 884000 | Seed 801 | same |
| `passages`, budget curve | 491,520 / 1,015,808 / 1,507,328 / 1,998,848 transitions | det 16, 26, 48, 38 of 64; samp 20, 23, 43, 45 | det, samp | Development (inspected) pool 885000 | Seed 801 | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| `passages`, controls at 262k | Three control runs (701, 702, 703) | 11, 11, 15 of 64 det (mean 12.3); 11, 10, 11 samp (mean 10.7) | det, samp | Development (inspected) pool 882000 | | [AUXILIARY_STUDENT_RESULTS](../experiments/students/AUXILIARY_STUDENT_RESULTS.md) |
| `passages`, transfer ladder | Experiment 1, retained arm at 65,536 transitions | 0 of 32 | not recorded | Development (inspected) pool 810000 | | [REFERENCE_TRANSFER_RESULTS](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS.md) |
| `passages` | Experiment 7 selected checkpoint | 4 of 32 | not recorded | Selection (reported pools, optimistic) | | [REFERENCE_TRANSFER_RESULTS_7](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_7.md) |
| `passages` | Experiment 8, seed 442 at 262,144 transitions | 0 of 32 | not recorded | Development (inspected) | Two seeds, both 0 at the last point | [REFERENCE_TRANSFER_RESULTS_8](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_8.md) |
| `passages` | Phase 1 pilot checkpoint (seed 442) | 17 of 64 det; 14 samp | det, samp | Development (inspected) pool 880000 | | [COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md) |
| `passages` | Run 601 | 9 of 64 det (34 collisions, 21 timeouts); samp not run | det | Development (inspected) pool 880000 | | same |
| `passages` | Seed 505 | 2 of 64 det; 5 samp | det, samp | Development (inspected) pool 880000 | | same |
| `passages` | Phase 1 selection, seed 442 at 32,768 added transitions | 2 of 32 (selection pool) | not recorded | Selection | Accepted; not an improvement over start | [PHASE1_RUN_RESULTS](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md) |
| `passages` | Phase 3 long memory window, seed 442, stage 4 | 6 of 32 (selection pools) | not recorded | Selection | Control 2 of 32 | [PHASE3_SCREENING_RESULTS](../experiments/variance-and-stability/PHASE3_SCREENING_RESULTS.md) |
| `passages` | Phase 3 long memory window, seed 443, stage 4 | 2 of 32 (selection pools) | not recorded | Selection | Control 1 of 32 at stage 4 | [PHASE3_REPLICATION_RESULTS](../experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md) |
| `passages`, waypoint diagnostic | Waypoint input (exact route direction, not a student), seeds 701, 702 | 39 and 36 of 64 det (mean 37.5); collisions 16 and 19 | det | Development (inspected) pool 880000 | Diagnostic only | [WAYPOINT_DIAGNOSTIC_RESULTS](../experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md) |
| `passages`, waypoint control | Zero-input control, seeds 701, 702 | 14 and 8 of 64 det (mean 11) | det | Development (inspected) pool 880000 | | same |
| `passages`, auxiliary student | Auxiliary waypoint head, seeds 801 to 803 | 18, 14, 12 of 64 det (mean 14.7); 19, 19, 13 samp | det, samp | Development (inspected) pool 882000 | Gain +2.3 of 64 over control | [AUXILIARY_STUDENT_RESULTS](../experiments/students/AUXILIARY_STUDENT_RESULTS.md) |
| `passages`, privileged critic | Critic arm, seeds 801 to 803 | 17, 10, 12 of 64 det (mean 13.0) | det | Development (inspected) pool 882000 | Gain +0.7 of 64 | same |
| `passages`, pretraining | Supervised pretrained trunk then PPO, seeds 901 to 903 | 20, 14, 9 of 64 det (mean 14.3); 14, 23, 11 samp (mean 16.0) | det, samp | Development (inspected) pool 882000 | Gain +2.0 of 64 | [PRETRAIN_RESULTS](../experiments/students/PRETRAIN_RESULTS.md) |
| `passages-mid` | 2M recipe, stage 61 | Seeds 801, 851, 901: 56, 57, 54 of 64 det; collisions 2, 0, 2 | det | Development (inspected) pool 886000 | Three seeds | [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md) |
| `passages-mid` | 2M seed 801, stage 61 | 56 of 64 det; 60 samp | det, samp | Development (inspected) pool 885000 | | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| `passages-mid` | B1 final | 48 of 64 det; 52 samp | det, samp | Development (inspected) pool 884000 | | [LARGE_BUDGET_RESULTS](../experiments/large-budget/LARGE_BUDGET_RESULTS.md) |
| `passages-mid` | Phase 1 pilot checkpoint | 37 of 64 det (58%); 21 of 32 on selection pool | det | Development (inspected) pool 880000 (fresh) | Outlier draw; five repeats of its recipe reached 13 of 32 at most | [VARIANCE_STUDY_RESULTS](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md) |
| `passages-mid` | Run 601 | 35 of 64 det | det | Development (inspected) pool 880000 | | [COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md) |
| `passages-mid`, budget curve | Stage 61 of seed 801 (B2) vs B1 | 56 vs 48 of 64 det | det | Development (inspected) pools 885000 and 884000 | Different pools | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| `passages-mid`, controls | Controls 701 to 703 | 39, 30, 30 of 64 det (mean 33.0) | det | Development (inspected) pool 882000 | | [AUXILIARY_STUDENT_RESULTS](../experiments/students/AUXILIARY_STUDENT_RESULTS.md) |
| `passages-wide` | 2M recipe, stage 61 | 64, 64, 64 of 64 det (seeds 801, 851, 901); 0 collisions | det | Development (inspected) pool 886000 | Three seeds | [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md) |
| `passages-wide` | Run 601 | 55 of 64 det (86%) | det | Development (inspected) pool 880000 | | [COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md) |
| `passages-wide` | Pilot checkpoint | 14 of 64 det (50 timeouts, 0 collisions); 55 of 64 samp (6 timeouts) | det, samp | Development (inspected) pool 880000 | Hover fixed point | same |
| `passages-wide` | Phase 1 seed 442, four evaluations | 22 to 23 of 32 | det | Development (inspected) old pools | Stable on this seed | [PHASE1_RUN_RESULTS](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md) |
| `passages-wide` | Phase 1 seed 443, four evaluations | 0, 2, 18, 3 of 32 | det | Development (inspected) old pools | Range 18 | same |
| `passages-wide` | Variance study, five runs (selection) | 12 to 23 of 32 (range 11) | not recorded | Selection | Seeds 501 to 505 | [VARIANCE_STUDY_RESULTS](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md) |
| `passages-wide` | Transfer experiment 5 (pool 830000) | 6, 26, 20 of 32 across checkpoints | not recorded | Development (inspected) | Oscillation | [REFERENCE_TRANSFER_RESULTS_5](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_5.md) |
| `gate-two` | 2M recipe, stage 61 | 64, 64, 64 of 64 det (seeds 801, 851, 901) | det | Development (inspected) pool 886000 | | [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md) |
| `gate-two` | 2M seed 801, stage 61 | 63 of 64 det; 64 samp | det, samp | Development (inspected) pool 885000 | | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |

## 3. Budget curve (B1, B2, B3)

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| B1 rule | Positive threshold for `passages` at 1,015,808 transitions | 24 of 64; negative 16 or fewer | det | Frozen rule | Missed by one; reported inconclusive | [LARGE_BUDGET_RESULTS](../experiments/large-budget/LARGE_BUDGET_RESULTS.md) |
| B2 result | 1,998,848 transitions, seed 801, `passages` | 38 of 64 (threshold 28; B1 checkpoint 27 on the same pool) | det | Development (inspected) pool 885000 | One seed | [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| B3 result | Three seeds, 1,998,848 transitions, `passages` | 42, 36, 39 of 64 (mean 39.0; threshold mean 28) | det | Development (inspected) pool 886000 | Start 5 of 64 | [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md) |
| B3 stage 46 | 1,507,328 transitions, three seeds, `passages` | 40, 33, 33 of 64 det | det | Development (inspected) pool 886000 | Reported, not used for decision | same |
| B3 medium | Stage 61, three seeds | 49, 54, 55 of 64 det; the 48 line is the frozen minimum | det | Development (inspected) pool 886000 | | same |

## 4. Level B (held-out parameter region)

Level B is an opening width below 3.8 m with at least four partitions. Development pool 950000 to 950063, 64 episodes per cell, difficulty 0.8 unless stated. Final pool 960000 to 969999 is reserved.

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Level B | 2M recipe, stage 61 | Seeds 801, 851, 901: 26, 17, 12 of 64 (mean 18.3; positive threshold mean 20; 12 to 26 range); collisions 10, 14, 17 | det | Development (inspected) pool 950000 | Three seeds; inconclusive | [LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md) |
| Level B | 2M recipe, same seeds | 23, 16, 20 of 64 | samp | Development (inspected) pool 950000 | | same |
| Level B | Experiment 7 start | 1 of 64 det (28 collisions, 35 timeouts); 1 of 64 samp | det, samp | Development (inspected) pool 950000 | | same |
| Level B | Earlier runs on this pool | 1 to 6 of 64 | not recorded | Development (inspected) | | [RANDOM_DISTRIBUTION_RESULTS](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md) |
| Level B | R5 random-map runs 601, 602, 603 | 5, 1, 0 of 64 | not recorded | Development (inspected) pool 950000 | Mean 2.0 | same |
| Level B | R5 control runs 501 to 505 | 2, 1, 2, 2, 0 of 64 | not recorded | Development (inspected) pool 950000 | Mean 1.4 | same |
| Level B | C1.1 real connectome, seeds 1001, 1051 | 5, 6 of 64 det (mean 5.5); 8, 11 samp | det, samp | Development (inspected) pool not stated in source | Two seeds | [CONNECTOME_CONTROL_RESULTS_C11](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md) |
| Level B | C1.1 shuffled, seeds 1001, 1051 | 10, 3 of 64 det (mean 6.5); 13, 10 samp (derived mean 11.5) | det, samp | Development (inspected) pool not stated in source | | same |
| Level B | C1.2 real connectome, four-step extension | 7, 12 of 64 det (mean 9.5); 7, 20 samp (mean 13.5) | det, samp | Development (inspected) pool 888000 | Two seeds | [CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md) |
| Level B | C1.2 shuffled | 11, 13 of 64 det (mean 12.0); 12, 17 samp (mean 14.5) | det, samp | Development (inspected) pool 888000 | Two seeds | same |
| Level B | Auxiliary student arm (aux 801 to 803) | Mean 3.7 of 64 det; control mean 1.7 | det | Development (inspected) pool 882000 | Stated in source | [AUXILIARY_STUDENT_RESULTS](../experiments/students/AUXILIARY_STUDENT_RESULTS.md) |
| Level B | Reserved final | Not run | n/a | Reserved | | [HELD_OUT_SPEC](../methods/HELD_OUT_SPEC.md) |

## 5. Level C (held-out architectural family)

21 synthetic situations with 8 headings each (168 episodes), development headings from seed 900000. Final headings 970000 to 979999 are reserved.

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Level C | Experiment 7 start, deterministic | 71 of 168 (42%); 51 collisions, 46 timeouts; Wilson 35 to 50% | det | Development (inspected) headings 900000 | Baseline | [LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md), [RANDOM_DISTRIBUTION_RESULTS](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md) |
| Level C | Experiment 7 start, sampled | 93 of 168; 64 collisions, 11 timeouts | samp | Development (inspected) headings 900000 | | [LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md) |
| Level C | 2M recipe, seed 801 | 95 of 168 det (52 collisions, 21 timeouts); 113 samp | det, samp | Development (inspected) headings 900000 | | same |
| Level C | 2M recipe, seed 851 | 108 of 168 det (45, 15); 108 samp | det, samp | Development (inspected) headings 900000 | | same |
| Level C | 2M recipe, seed 901 | 108 of 168 det (54, 6); 105 samp | det, samp | Development (inspected) headings 900000 | | same |
| Level C | 2M recipe, mean | 103.7 of 168 det (positive threshold 88); 108.7 samp (derived) | det, samp | Development (inspected) | Rule outcome positive | same |
| Level C, per scene | Street-block (40 episodes): start 12; seeds 801, 851, 901: 32, 36, 40 | det | Development (inspected) | | same |
| Level C, per scene | Warehouse (32 episodes): start 10; 24, 17, 18 | det | Development (inspected) | | same |
| Level C, per scene | Office-floor (24 episodes): start 10; 16, 16, 16 | det | Development (inspected) | | same |
| Level C, per scene | Atrium (24 episodes): start 8; 8, 8, 9 | det | Development (inspected) | Does not move | same |
| Level C, per scene | Apartment (24 episodes): start 7; 8, 8, 8 | det | Development (inspected) | Does not move | same |
| Level C, per scene | Courtyard (24 episodes): start 24; 7, 23, 17 | det | Development (inspected) | Regressed on seed 801 | same |
| Level C | C1.1 real connectome, seeds 1001, 1051 | 77 and 81 det (mean 79.0); 83 and 93 samp (derived mean 88.0) | det, samp | Development (inspected); pool not stated in source | Two seeds | [CONNECTOME_CONTROL_RESULTS_C11](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md) |
| Level C | C1.1 shuffled | 75 and 97 det (mean 86.0); 96 and 94 samp (derived mean 95.0) | det, samp | Development (inspected); pool not stated in source | | same |
| Level C | C1.2 real connectome, 4.88M transitions | 91 and 105 det (mean 98.0) | det | Development (inspected) headings 900000 | Deterministic only | [CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md) |
| Level C | C1.2 shuffled | 111 and 100 det (mean 105.5) | det | Development (inspected) headings 900000 | | same |
| Level C | Planner-1.4-exp.3 (explicit planner reference) | 147 of 168 det (87.5%; Wilson 82 to 92); 4 collisions, 17 timeouts | det | Development (inspected) headings 900000 | Planner, not learned | [PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md) |
| Level C, planner per scene | Planner by scene (episodes): office-floor 20 (24), apartment 12 (24), street-block 38 (40), atrium 21 (24), warehouse 32 (32), courtyard 24 (24) | det | Development (inspected) headings 900000 | Planner, not learned | same |
| Architectural, original objectives | Planner-1.4-exp.1 | 18 of 21 goals, 0 collisions, 3 timeouts | not recorded (planner) | Development (inspected) | Seed 42 | [architectural-closing-results](../evidence/architectural-closing-results.md) |
| Architectural, original objectives | Planner-1.4-exp.2 (broad escape) | 18 of 21, 0 collisions, 3 timeouts; regressed apartment sofa-to-bedroom | not recorded (planner) | Development (inspected) | Not promoted | same |
| Architectural, original objectives | Planner-1.4-exp.3 (portal escape) | 19 of 21, 0 collisions, 2 timeouts | not recorded (planner) | Development (inspected) | Not promoted | same |
| Architectural, learned | Autonomous PPO pilot 1 (131,072 transitions) | 0 of 6 validation goals before and after; final 5 collisions, 1 timeout | not recorded | Development (inspected) | Six situations shared with training | [autonomous-architecture-pilot-1-results](../evidence/autonomous-architecture-pilot-1-results.md) |
| Architectural, learned | Autonomous PPO pilot 2 | 0 of 6 before, 1 of 6 after (deterministic validation) | det | Development (inspected) | | [autonomous-architecture-pilot-2-results](../evidence/autonomous-architecture-pilot-2-results.md) |
| Architectural, learned | Curriculum 1 | 1 of 6 original-goal validation, 5 collisions | not recorded | Development (inspected) | | [autonomous-architecture-curriculum-1-results](../evidence/autonomous-architecture-curriculum-1-results.md) |
| Architectural, learned | Curriculum 2 | 0 of 6, 6 collisions | not recorded | Development (inspected) | | [autonomous-architecture-curriculum-2-results](../evidence/autonomous-architecture-curriculum-2-results.md) |
| Level C, reserved final | Not run | n/a | n/a | Reserved | | [HELD_OUT_SPEC](../methods/HELD_OUT_SPEC.md) |

## 6. Large rooms and mazes

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| `large`, earlier ray-risk baseline (v3) | Retained original rooms, then new large rooms | 3 of 4 on retained original rooms; 0 of 4 on new large rooms | not recorded | Development (inspected) seeds 290000 to 290003 | Diagnostic, four rooms each | [GEOMETRY_DIAGNOSIS](../learning/GEOMETRY_DIAGNOSIS.md) |
| `large`, historical reference | Historical reference, large | 0 of 16 | not recorded | Development (inspected) | | [HISTORICAL_REFERENCE](../experiments/reference-recovery/HISTORICAL_REFERENCE.md) |
| `large`, geometry comparison, validation | Baseline and curriculum, seeds 42 and 73 (32 layouts each) | 0 of 32 in all four runs | not recorded | Selection | Selected candidates had 0 goals | [RESULTS](RESULTS.md#shared-target-validation) |
| `large`, geometry comparison, final | Selected checkpoint and untrained control | 0 of 64 each; collisions 1 each, timeouts 63 each | not recorded | Consumed final | Pool now consumed | [RESULTS](RESULTS.md#one-reserved-final-assessment) |
| `large`, 2M retained candidate | Seeds 801, 851, 901, deterministic | 2, 0, 0 of 32 (collisions 7, 11, 5) | det | Development (inspected) pool 892000 | Most failures are timeouts (21 to 27 of 32) | [PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md) |
| `large`, 2M retained candidate | Same seeds, sampled | 2, 0, 1 of 32 | samp | Development (inspected) pool 892000 | | same |
| `large`, student v34 | Learned approach and crossing | 3 of 8 on reused optimization goals; 1 collision, 4 timeouts | not recorded | Development (inspected, reused) | Best learned student in its batch | [README](../../README.md) |
| `large`, passage-mastery v2 (single wide opening) | Gate-long, selected checkpoint | 61 of 64 (95.3%); 0 collisions, 3 timeouts; Wilson 87.1 to 98.4 | not recorded | Final pool (status as recorded in source) | Single opening, not large rooms; untrained control 0 of 64 | [passage-mastery-v2](../evidence/passage-mastery-v2-results.md) |
| `large`, planner-1.0 | Observed-map planner, prospective development | 8 of 8 on reused optimization rooms; 13 of 16 on frozen prospective development (Wilson 57.0 to 93.4); 0 collisions, 3 timeouts | planner | Development (inspected) | Explicit planning, not learned | [observed-map-v55-results](../evidence/observed-map-v55-results.md) |
| `large`, planner-1.1 vs 1.0 | Cohort 9500000 | Planner-1.1 14 of 16 (Wilson 64.0 to 96.5); planner-1.0 12 of 16 | planner | Development (inspected) | | [planner-v60-development-results](../evidence/planner-v60-development-results.md) |
| `large`, planner-1.2 | Cohort 13000000 | 15 of 16 (Wilson 71.7 to 98.9); planner-1.1 also 15 of 16 | planner | Development (inspected) | Tied with 1.1 | [planner-dual-v65-results](../evidence/planner-dual-v65-results.md) |
| `large`, planner-1.3-exp.9 | Retained, then fresh | 6 of 6 retained; 8 of 8 fresh, 0 collisions (fresh Wilson 67.6 to 100) | planner | Development (inspected) | Predeclared rule met; not an independent final test | [MAZE_NAVIGATION](../planner/MAZE_NAVIGATION.md) |
| `maze`, 2M retained candidate | Seeds 801, 851, 901, deterministic | 0, 0, 0 of 32 (collisions 3, 1, 5) | det | Development (inspected) pool 893000 | Most failures are timeouts (27 to 31 of 32) | [PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md) |
| `maze`, 2M retained candidate | Same seeds, sampled | 0, 0, 0 of 32 (collisions 2, 3, 8) | samp | Development (inspected) pool 893000 | | same |
| `maze`, planner-1.3-exp.11 | Retained, then fresh | 2 of 2 retained; 5 of 8 fresh, 0 collisions, 3 timeouts | planner | Development (inspected) | Missed 7 of 8 rule; launcher still selects it | [MAZE_NAVIGATION](../planner/MAZE_NAVIGATION.md) |
| `maze`, planner-1.3-exp.25 | Retained, then fresh 17000000 to 17000007 | 7 of 8 retained (1 timeout); 5 of 8 fresh, 0 collisions (Wilson 30.6 to 86.3) | planner | Development (inspected) | Not promoted | [MAZE_NAVIGATION](../planner/MAZE_NAVIGATION.md) |
| `maze`, planner-1.3-exp.23 | Retained | 6 of 8 retained, 0 collisions, 2 timeouts | planner | Development (inspected) | Rejected | same |
| `maze`, planner-1.3-exp.24 | Retained | 6 of 8 retained | planner | Development (inspected) | Rejected (regressed two successes) | same |

## 7. Connectome control (edge-shuffled reservoir)

Chain-check rules: the C1.1 and C1.2 chain checks required a real-arm mean of at least 28 of 64 on `passages`. All three failed (16.0, 27.5 and 26.0). Comparisons below are therefore fresh-chain results only and are not tests of the retained lineage. C1.1 and C1.2 used two seeds per arm (1001 and 1051); C1.3 adds seeds 1101 and 1151 for four per arm. One shuffled graph.

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Chain check, C1.1 | Real arm, `passages` | 13 and 19 of 64 det (mean 16.0); 18 and 20 samp (derived mean 19.0) | det, samp | Development (inspected); pool not stated in source | Needed 28 | [CONNECTOME_CONTROL_RESULTS_C11](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md) |
| `passages`, C1.1 | Shuffled arm | 25 and 26 of 64 det (mean 25.5); 26 and 32 samp (derived mean 29.0) | det, samp | Development (inspected); pool not stated | Nominal shuffled advantage, inside seed spread | same |
| `passages`, C1.1 | Retained lineage (B3 seeds) | 39.0 of 64 det (mean of 42, 36, 39) | det | Development (inspected) pool 886000 | Reference | same |
| Chain check, C1.2 | Real arm, `passages`, 4.88M transitions | 21 and 34 of 64 det (mean 27.5, required 28); 25 and 37 samp (mean 31.0) | det, samp | Development (inspected) pool 888000 | Failed by 0.5 episode | [CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md) |
| `passages`, C1.2 | Shuffled arm | 13 and 29 of 64 det (mean 21.0); 27 and 35 samp (mean 31.0) | det, samp | Development (inspected) pool 888000 | Seed 1001 deterministic value is a hover fixed point (44 timeouts) | same |
| `passages`, C1.2 | Retained lineage | 38.0 det (mean of 41, 35, 38 on pool 888000 in the source's retained row); 38.7 samp | det, samp | Development (inspected) pool 888000 | | same |
| `passages-mid`, C1.2 | Real and shuffled | Real 51.0 det (56.0 samp); shuffled 47.0 det (54.5 samp); retained 52.3 det | det, samp | Development (inspected) pool 888000 | | same |
| `passages-wide`, C1.2 | Real and shuffled | Real 63.0 det (63.5 samp); shuffled 64.0 det (64.0 samp); retained 64.0 det | det, samp | Development (inspected) pool 888000 | | same |
| `passages-mid`, C1.1 | Real and shuffled | Real 41.5 det; shuffled 51.0 det; retained 55.7 det | det | Development (inspected); pool not stated | Shuffled higher, below 10-episode cut | [CONNECTOME_CONTROL_RESULTS_C11](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md) |
| `passages-wide`, C1.1 | Real and shuffled | Real 59.5 det; shuffled 64.0 det; retained 64.0 det | det | Development (inspected); pool not stated | | same |
| Connectome, seed spread | C1.2 real and shuffled `passages` | Real seeds differ by 13; shuffled seeds by 16 | det | Development (inspected) pool 888000 | Equal to the arm difference | [CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md) |
| `passages`, C1.3 | Real, four seeds (1001, 1051, 1101, 1151) | 21, 34, 21, 28 of 64 det (mean 26.0); 25, 37, 26, 29 samp (mean 29.25) | det, samp | Development (inspected) pool 888000 | Chain check fails (26.0 < 28) | [CONNECTOME_CONTROL_RESULTS_C13](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C13.md) |
| `passages`, C1.3 | Shuffled, four seeds | 13, 29, 22, 25 of 64 det (mean 22.25); 27, 35, 31, 36 samp (mean 32.25) | det, samp | Development (inspected) pool 888000 | | same |
| `passages`, C1.3 | Difference real minus shuffled | +3.75 det; 95 percent interval [-7.6, +15.1]; 90 percent interval [-5.2, +12.7] | det | Development (inspected) pool 888000 | Inconclusive by the frozen rule (equivalence margin 10) | same |
| `passages-mid`, C1.3 | Real and shuffled, four seeds | Real 50.0 det (54.0 samp); shuffled 48.0 det (54.25 samp); D +2.0 | det, samp | Development (inspected) pool 888000 | Equivalent within 10 | same |
| `passages-wide`, C1.3 | Real and shuffled | Real 63.5 det; shuffled 62.75 det; D +0.75 | det, samp | Development (inspected) pool 888000 | Near ceiling | same |
| Medium, C1.3 | Real and shuffled | Real 53.5 det (55.5 samp); shuffled 54.5 det (55.25 samp); D -1.0 | det, samp | Development (inspected) pool 888000 | Equivalent within 10 | same |
| Level B, C1.3 | Real and shuffled | Real 7, 12, 11, 4 (mean 8.5); shuffled 11, 13, 6, 18 (mean 12.0); D -3.5 | det | Development (inspected) pool 950000 range | Equivalent within 10 | same |
| Level C, C1.3 | Real and shuffled | Real 91, 105, 109, 95 (mean 100.0); shuffled 111, 100, 97, 107 (mean 103.75); D -3.75 of 168 | det | Development (inspected) headings 900000 | Equivalent within 26 | same |
| Connectome, seed spread, C1.3 | `passages` four seeds per arm | Sample standard deviation 6.3 (real), 6.8 (shuffled) | det | Development (inspected) pool 888000 | Smaller than the two-seed estimate (9 and 11) | same |
| Connectome, sample size | Seeds needed for 10-episode difference at 80% power | About 8 seeds per arm (C1.2 estimate); about 7 per arm for an equivalence verdict if the true difference is near +3.75 (C1.3, spread 6.5) | n/a | n/a | Estimates | same |

## 8. Planner (explicit reference, not learned)

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Level C | Planner-1.4-exp.3 | 147 of 168 (87.5%); 4 collisions, 17 timeouts | det (planner) | Development (inspected) headings 900000 | Scenes it was built for | [PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md) |
| Level C | Learned 2M retained candidate, same 168 cases | 95, 108, 108 of 168 (mean 103.7) | det | Development (inspected) headings 900000 | Difference 43 episodes | same |
| Architectural (original 21) | Planner-1.4-exp.3 | 19 of 21, 0 collisions, 2 timeouts | planner | Development (inspected) | | [architectural-closing-results](../evidence/architectural-closing-results.md) |
| Architectural (original 21) | Planner-1.4-exp.1 | 18 of 21 | planner | Development (inspected) | | same |
| Repeatability | Full graph (167,184 neurons, 25,583,622 edges), ordered accumulation | Zero differing feature values in replay; 32 steps; 0 transitions, 0 updates | n/a | Probe | This runtime only | [RESULTS](RESULTS.md#repeatable-full-connectome-execution) |
| Repeatability | Full-graph COO storage, two replay probes | Feature differences 4.77e-7 and 5.36e-7 | n/a | Probe | Before the ordered-accumulation change | [RESULTS](RESULTS.md#repeatable-full-connectome-execution) |

## 9. Historical reference and transfer ladder

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Medium, transfer ladder (16 episodes) | Observed-ray risk (v3), original medium | 12 of 16; 3 collisions, 1 timeout | not recorded | Development (inspected) seeds 800000 and above | Seeds created for this check | [HISTORICAL_REFERENCE](../experiments/reference-recovery/HISTORICAL_REFERENCE.md) |
| `passages` (16 episodes) | Observed-ray risk (v3) | 0 of 16; 7 collisions, 9 timeouts | not recorded | Development (inspected) | Mean final distance 20 m of 28 m | same |
| `large` (16 episodes) | Observed-ray risk (v3) | 0 of 16; 4 collisions, 12 timeouts | not recorded | Development (inspected) | Mean final distance 38 m of 44 m | same |
| Medium, transfer experiment 4 | Selected checkpoint, medium 100000 pool | 24 of 32 (source 23 of 32) | not recorded | Development (inspected) | | [REFERENCE_TRANSFER_RESULTS_4](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_4.md) |
| Gate-long, transfer experiment 3 | After 131,072 added | 32 of 32 | not recorded | Development (inspected) | Gate maps | [REFERENCE_TRANSFER_RESULTS_3](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_3.md) |
| Transfer experiment 8 | Seed 442, 262,144 added | Medium 24, wide 5, mid 4, passages 0 of 32 | not recorded | Development (inspected) | Gains lost | [REFERENCE_TRANSFER_RESULTS_8](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_8.md) |

## 10. Earlier results (memory, random maps, stabilization, reward)

| Cell | Policy or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Memory, selection pool stage 4 | Long window, seed 442 vs control | Wide 28 vs 22, mid 15 vs 6, passages 6 vs 2 of 32 | not recorded | Selection | Hard-profile sum +19 at stage 4 | [PHASE3_SCREENING_RESULTS](../experiments/variance-and-stability/PHASE3_SCREENING_RESULTS.md) |
| Memory, seed 443 replication, stage 4 | Long window vs control | Wide +5, mid -9, passages 0 (differences) | not recorded | Selection | Not replicated | [PHASE3_REPLICATION_RESULTS](../experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md) |
| Memory, short window, stage 4 | 8-frame window | Hard-profile sum 9 vs 30 control | not recorded | Selection | Negative | [PHASE3_SCREENING_RESULTS](../experiments/variance-and-stability/PHASE3_SCREENING_RESULTS.md) |
| Random maps (R5), d=0.5 | Runs 601, 602, 603 vs controls | Mean 16.0 vs 13.2 of 64 | not recorded | Development (inspected) | Margin needed 8 for positive; not met | [RANDOM_DISTRIBUTION_RESULTS](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md) |
| Random maps (R5), d=0.9 | Same runs | Mean 2.7 vs 1.6 of 64 (margin +1.1); best run 6 of 64 | not recorded | Development (inspected) | Negative by rule | same |
| Random maps (R5), controller | Difficulty at end of runs | 0.20 to 0.25; 64 to 127 randomized episodes per run | n/a | n/a | Audit | [LIGHT_AUDIT_RESULTS](../experiments/diagnostics/LIGHT_AUDIT_RESULTS.md) |
| Reward audit | Ideal route follower vs hover | Return 7.8 at 1 m/s on 16 `passages` maps; hover -4.0 | n/a | Probe (seeds 870000 to 870015) | Refutes reward-hover for ideal follower | same |
| Stabilization, seed 442 | Phase 1 run, passages-wide over four evaluations | 22 to 23 of 32 (range 1) | det | Development (inspected) old pools | | [PHASE1_RUN_RESULTS](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md) |
| Stabilization, seed 443 | Same | 0 to 18 of 32 (range 18) | det | Development (inspected) old pools | Criterion not met | same |
| Phase 1 pilot, selection | Seed 442 at 98,304 transitions | Medium 25, medium-b 27, gate-two 32, gate-long 32, wide 12, mid 21, passages 5 of 32 | det | Selection | Repeat evaluation within one episode | [PHASE1_PILOT_RESULTS](../experiments/variance-and-stability/PHASE1_PILOT_RESULTS.md) |
| Waypoint diagnostic (not a student) | Privileged waypoint vs control, `passages-mid` | 58, 57 vs 42, 25 of 64 (mean 57.5 vs 33.5) | det | Development (inspected) pool 880000 | Diagnostic | [WAYPOINT_DIAGNOSTIC_RESULTS](../experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md) |

## 11. Diagnostics and probes (offline, no training)

Errors are median angular errors in degrees. Lower is better. Hard subset is the 40-degree-blocked-goal subset defined in the source.

| Cell | Input or arm | Result | Mode | Pool status | Seeds / notes | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Feature probe, route 4 m ahead, run 601 | MLP, 256 features, hard subset | 53 degrees (features); 51 degrees (raw sensors) | n/a | Probe (rollouts 881000 to 881063) | 40 train episodes | [FEATURE_PROBE](../experiments/diagnostics/FEATURE_PROBE.md) |
| Feature probe, route 4 m ahead, pilot | MLP, 256 features, hard subset | 49 degrees (features); 49 degrees (raw sensors) | n/a | Probe | | same |
| Feature probe, goal direction only | MLP, run 601 hard subset | 64 degrees | n/a | Probe | Baseline | same |
| Synthetic probe, 700 maps | MLP, 8 m rays, hard subset, 4 m target | 34 degrees | n/a | Probe (seeds 895000 to 895699) | 500 train maps, 150 test maps | [SENSING_PROBES](../experiments/diagnostics/SENSING_PROBES.md) |
| Synthetic probe, 700 maps | MLP, 24 m rays, hard subset, 4 m target | 28 degrees | n/a | Probe | | same |
| Synthetic probe, 700 maps | Goal direction only, MLP, hard subset | 63 degrees | n/a | Probe | | same |
| Pretraining gate | Actor trunk, held-out maps, hard subset | 41.6 degrees (104 degrees before pretraining) | n/a | Probe (pretraining data 896000 to 896799) | Gate 45 | [PRETRAIN_RESULTS](../experiments/students/PRETRAIN_RESULTS.md) |
| Collision anatomy, `passages`, run 601 | Deterministic, pool 880000 | 9 success, 33 collisions, 22 timeouts; 23 partition-piece hits; 11 within 1.5 m of route | det | Development (inspected) pool 880000 | One checkpoint | [COLLISION_ANATOMY](../experiments/diagnostics/COLLISION_ANATOMY.md) |
| Collision anatomy, `passages`, run 601 sampled | Sampled, pool 880000 | 11 success, 42 collisions, 11 timeouts | samp | Development (inspected) pool 880000 | | same |
| Collision anatomy, `passages`, pilot | Deterministic, pool 880000 | 18 success, 20 collisions, 26 timeouts | det | Development (inspected) pool 880000 | | same |
| Collision anatomy, `passages`, seed 505 | Deterministic, pool 880000 | 3 success, 19 collisions, 42 timeouts | det | Development (inspected) pool 880000 | | same |
| Light audit, exposure | Randomized simulators in R5 | 64 to 127 finished episodes per run | n/a | Audit | | [LIGHT_AUDIT_RESULTS](../experiments/diagnostics/LIGHT_AUDIT_RESULTS.md) |

## 12. Pools used in these results

Status follows the roadmap registry. Pools listed as inspected have been used for development and cannot serve as fresh evidence.

| Pool | Seeds | Used for | Status |
| --- | --- | --- | --- |
| Medium regression pools A, B, C, D | 100000 to 100031; 840000 to 840031; 860000 to 860031; 861000 to 861031 | Frozen regression suite and some selection | Inspected |
| Gate, `passages-wide` | 830000 to 830031 | Development | Inspected |
| `passages-mid` | 850000 to 850031 | Development | Inspected |
| `passages` | 810000 to 810031 | Development and failure classification | Inspected |
| Selection pools | 860000 to 865000 | Checkpoint selection, Phases 1 and 3 | Selection |
| Confirmation and comparison | 880000 to 880063; 882000 to 882063 | Fresh-pool confirmations, student comparisons | Inspected |
| Probe | 881000 to 881063; 895000 to 895699; 896000 to 896799 | Offline probes and pretraining data | Probe |
| Large-budget curve | 884000 to 884063 (B1) | Curve evaluation | Inspected |
| 2M test | 885000 to 885063 (B2) | Curve evaluation | Inspected |
| 2M replication | 886000 to 886063 (B3) | Replication of three seeds | Inspected |
| Controls | 887000 to 887063 (C1.0) | Medium chain | Inspected |
| C1.2 pool | 888000 to 888063 | Extended controls | Inspected |
| Planner pools | `large` 892000 to 892031; `maze` 893000 to 893031 | Retained candidate and planner | Inspected |
| Level B development | 950000 to 959999 | Progress only | Inspected (950000 to 950063) |
| Level C development headings | 900000 and above | Baseline and B4 | Inspected |
| Random A and B cells | Recorded in R5 document | Random map cells | Inspected |
| Reserved: level A report | 940000 to 949999 | Final report | Reserved |
| Reserved: level B final | 960000 to 969999 | Final assessment | Reserved |
| Reserved: level C final headings | 970000 to 979999 | Final assessment | Reserved |
| Historical final pools | Recorded in `runs/suites/consumed` | Earlier final tests, including the 0 of 64 `large` pool | Consumed |
