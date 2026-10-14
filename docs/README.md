# Documentation

Start with the root [README](../README.md) for what the project is, where it stands, installation and the demos. This index lists every document, grouped by topic. Detailed machine evidence and the development journal stay under the ignored `private/` folder and are summarized in the project history; the small tracked evidence files are indexed in [evidence/README.md](evidence/README.md).

## Start here, by question

| If you want to know | Read |
| --- | --- |
| Where the project stands and what is supported | [Findings](results/FINDINGS.md), then [Key numbers](results/KEY_NUMBERS.md) |
| The whole story, iteration by iteration | [Project history](overview/PROJECT_HISTORY.md) |
| What every experiment asked and found | [Experiment catalog](experiments/README.md) and the [experiment log](EXPERIMENT_LOG.md) |
| What is done, open and next | [Roadmap](../ROADMAP.md) (live board, decisions, pools registry, artifact hashes) |
| How the maps work and what each family is | [Maps](methods/MAPS.md) |
| How the connectome is used as a controller | [Brain](methods/BRAIN.md), [Data and model](overview/DATA_AND_MODEL.md), [Mathematics](methods/MATHEMATICS.md) |
| What a term or metric means | [Glossary](overview/GLOSSARY.md) |
| How to rerun a result | [Reproduce](operations/REPRODUCE.md), [Commands](operations/COMMANDS.md), the [script index](../scripts/README.md) |
| How the explicit planner was built | [Navigation resolution](planner/NAVIGATION_RESOLUTION.md), [Maze navigation](planner/MAZE_NAVIGATION.md), [Controller versions](planner/CONTROLLER_VERSIONS.md) |
| Where each figure comes from | [Image provenance](images/README.md) |
| Credits, licenses and citations | [References](reference/REFERENCES.md) |

## Folder layout

| Folder | Contents |
| --- | --- |
| `overview/` | Plans, architecture, data, the project history, the glossary and the archived earlier README |
| `methods/` | Formulas, sensors, maps, the brain, protocol specifications and the held-out definitions |
| `planner/` | The explicit planner line: large rooms, maze, architectural scenes, guided navigation |
| `learning/` | The early learned-policy line and autonomous learning |
| `experiments/` | One folder per experiment family with protocols and results, and the catalog |
| `results/` | The consolidated findings, the key-numbers tables and the earlier aggregate results |
| `operations/` | Commands, reproduction, verification, publication, storage and recovery |
| `reference/` | Credits, references and the bibliography |
| `evidence/` | Small tracked evidence files from the planner, maze, architectural and learning iterations |
| `images/` | Geometry previews, report figures (`images/figures/`) and provenance |

[EXPERIMENT_LOG.md](EXPERIMENT_LOG.md) is the one-row-per-experiment index and stays at this level. Contribution rules are in [CONTRIBUTING.md](../CONTRIBUTING.md).

Public result summaries distinguish validation selection from final assessment and identify changes in task or initialization. Different final pools are not a paired comparison. Full checkpoints, data downloads and flight archives are not tracked.

## Overview: plans, architecture, data and the project story

| Document | What it covers |
| --- | --- |
| [Architecture](overview/ARCHITECTURE.md) | The project separates the biological dataset from the engineered controller, the physical environment, and the tools used to observe a run. |
| [Data and model contract](overview/DATA_AND_MODEL.md) | The MaleCNS v1.0 source data, graph coverage, engineered assumptions and the model contract. |
| [Earlier README (archived)](overview/EARLIER_README.md) | This is the root README as it stood at the end of the planner and autonomous-learning iterations (Iterations 1 to 9 of the project history), before the zero-shot program. |
| [Glossary](overview/GLOSSARY.md) | Terms used across the documentation, in alphabetical order. |
| [Project completion plan](overview/PROJECT_COMPLETION.md) | The original completion brief: objective, gate, controls and release requirements. |
| [Project history](overview/PROJECT_HISTORY.md) | This document tells the whole story of the fly-rl project in numbered Iterations, from the first flight to the current zero-shot program. |
| [Plan to unseen-map navigation](overview/ZERO_SHOT_PLAN.md) | The phase design toward navigation in maps never seen in training, with the three novelty levels and the release gate. |

## Methods: formulas, sensors, maps, brain and protocol specifications

| Document | What it covers |
| --- | --- |
| [Terminal-approach curriculum](methods/APPROACH_CURRICULUM.md) | This training-only reset schedule tests whether practice near the goal helps terminal approach while preserving the ordinary success condition. |
| [Architectural scene drafts](methods/ARCHITECTURAL_SCENES.md) | The six original architectural scenes (office, apartment, street block, atrium, warehouse, courtyard): meshes, collision boxes, situations and the interactive preview. |
| [The connectome reservoir, sensors, readouts and policy](methods/BRAIN.md) | This page covers the biological part of the controller: where the wiring comes from, how it is turned into a fixed recurrent network, what the flight sensors feed into it, how its... |
| [Observed-ray risk](methods/COLLISION_RISK.md) | This training-only penalty uses available range and closing-speed sensors. |
| [Dense rooms](methods/DENSE_ROOMS.md) | The original dense task uses a 32 × 32 × 12 room with 48 box obstacles, randomized endpoints at least 14 units apart and a randomized initial heading. |
| [Flight and anatomical inspection](methods/FLIGHT_AND_NEURONS.md) | Cameras, coordinated flight dynamics, neural colors, activity traces and the anatomical brain view. |
| [Generalization and routes](methods/GENERALIZATION_AND_ROUTES.md) | Separate layout pools, frozen selection and explicit geometric references make navigation measurements interpretable. |
| [Progressive maps and the geometry curriculum](methods/GEOMETRY_CURRICULUM.md) | Progressive map generation, the geometry profiles and the large-room curriculum. |
| [Held-out specification (levels B and C)](methods/HELD_OUT_SPEC.md) | The sealed definitions of the held-out parameter region (level B) and held-out family (level C), and the reserved seed ranges. |
| [Maps: profiles, families and geometry rules](methods/MAPS.md) | This page describes every map family the project generates or renders: the parameters of each profile, how a profile is chosen for a run, the geometry rules that apply to all of them,... |
| [Randomized map sampler (Phase 2, action R3)](methods/MAP_SAMPLER.md) | The geometry, the certified route and the validity checks come from the existing generator (`map_profiles.generate_layout`). |
| [Mathematical model and optimization](methods/MATHEMATICS.md) | The equations of the reservoir, flight, rewards and optimization. |
| [Medium-room regression suite](methods/MEDIUM_REGRESSION_SUITE.md) | This suite checks that a candidate keeps the skill of the recovered historical reference on the original medium dense-room task. |
| [Sensors v3](methods/SENSORS_V3.md) | Version 3 changes three sensor values while preserving the 269-value order, 128 distance rays, 128 approach readings and full connectome. |
| [Fresh initialization comparisons](methods/VALIDATION_AND_FRESH_COMPARISON.md) | Matched fresh initialization separates an interface change from transferring previously trained weights. |
| [Validation flight traces](methods/VALIDATION_TRACES.md) | Bounded diagnostic inference records behavior on retained validation failures. |

## The explicit planner line: large rooms, maze, architectural scenes

| Document | What it covers |
| --- | --- |
| [Architectural navigation development](planner/ARCHITECTURAL_NAVIGATION.md) | The architectural stage uses the user's six architecture-0.2 designs and 21 original situations. |
| [Controller versions](planner/CONTROLLER_VERSIONS.md) | Controller names now combine a revision number with a description. |
| [Guided training and autonomous inference](planner/GUIDED_NAVIGATION.md) | The frozen guided-navigation v1 protocol uses the remaining 40,960 transitions of the existing budget. |
| [Large-room corrections and maze navigation](planner/MAZE_NAVIGATION.md) | The task is to preserve large-room navigation while extending the explicit planner to the existing maze. |
| [Navigation design](planner/NAVIGATION_ITERATION.md) | The controller must learn both progress toward the target and safe movement around obstacles. |
| [Resolving navigation in large maps](planner/NAVIGATION_RESOLUTION.md) | This history retains original experiment IDs and measured source snapshots. |
| [Frozen planner development comparison](planner/PLANNER_DEVELOPMENT.md) | This protocol compares frozen planner-1.0 and planner-1.1 on the same sixteen new `large` rooms. |
| [Versioning and revision order](planner/VERSIONING.md) | Controller revisions describe the progression of a controller design. |

## The early learned-policy line and autonomous learning

| Document | What it covers |
| --- | --- |
| [Autonomous architectural learning](learning/AUTONOMOUS_LEARNING.md) | The primary objective is a policy that learns navigation through reinforcement learning and chooses its own flight actions. |
| [Diagnosis of the zero-success geometry experiment](learning/GEOMETRY_DIAGNOSIS.md) | The geometry experiment failed to learn target navigation. |
| [Mixed autonomous architectural curriculum](learning/MIXED_AUTONOMOUS_CURRICULUM.md) | The balanced curriculum learned short, unobstructed goals but failed all six full-route development validation tasks. |

## Experiments: reference recovery and transfer experiments 1 to 8

Every protocol was committed before its run; the question, design and outcome of each experiment are in the [experiment catalog](experiments/README.md).

- [Historical learned reference](experiments/reference-recovery/HISTORICAL_REFERENCE.md)
- [Passages failure classification](experiments/reference-recovery/PASSAGES_FAILURE_CLASSIFICATION.md)
- [Reference-preserving transfer experiment 1](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL.md)
- [Reference-preserving transfer experiment 2](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL_2.md)
- [Reference-preserving transfer experiment 3: graded gates](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL_3.md)
- [Reference-preserving transfer experiment 4: recover medium rooms, keep the gate gains](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL_4.md)
- [Reference-preserving transfer experiment 5: full passages in the mix](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL_5.md)
- [Reference-preserving transfer experiment 6: an intermediate partition profile](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL_6.md)
- [Reference-preserving transfer experiment 7: profiles mixed inside every update](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL_7.md)
- [Reference-preserving transfer experiment 8: longer run, two seeds](experiments/reference-recovery/REFERENCE_TRANSFER_PROTOCOL_8.md)
- [Reference-preserving transfer experiment 1: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS.md)
- [Reference-preserving transfer experiment 2: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_2.md)
- [Reference-preserving transfer experiment 3: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_3.md)
- [Reference-preserving transfer experiment 4: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_4.md)
- [Reference-preserving transfer experiment 5: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_5.md)
- [Reference-preserving transfer experiment 6: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_6.md)
- [Reference-preserving transfer experiment 7: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_7.md)
- [Reference-preserving transfer experiment 8: results](experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_8.md)
- [Transfer experiments 1 to 8: summary](experiments/reference-recovery/TRANSFER_SUMMARY.md)

## Experiments: variance study, stabilization (Phase 1) and memory (Phase 3)

Every protocol was committed before its run; the question, design and outcome of each experiment are in the [experiment catalog](experiments/README.md).

- [Phase 1: stable-trainer pilot (experiment 9)](experiments/variance-and-stability/PHASE1_PILOT_PROTOCOL.md)
- [Phase 1 pilot (experiment 9): results](experiments/variance-and-stability/PHASE1_PILOT_RESULTS.md)
- [Phase 1 run (experiment 10): stable trainer, two seeds, four evaluations](experiments/variance-and-stability/PHASE1_RUN_PROTOCOL.md)
- [Phase 1 run (experiment 10): results](experiments/variance-and-stability/PHASE1_RUN_RESULTS.md)
- [Phase 3 replication (experiment 12): long memory window, seed 443](experiments/variance-and-stability/PHASE3_REPLICATION_PROTOCOL.md)
- [Phase 3 replication (experiment 12): results](experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md)
- [Phase 3 screening (experiment 11): memory](experiments/variance-and-stability/PHASE3_SCREENING_PROTOCOL.md)
- [Phase 3 screening (experiment 11): results](experiments/variance-and-stability/PHASE3_SCREENING_RESULTS.md)
- [Variance study (action R1)](experiments/variance-and-stability/VARIANCE_STUDY_PROTOCOL.md)
- [Variance study (action R1): results](experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md)

## Experiments: randomized map distribution (R5)

Every protocol was committed before its run; the question, design and outcome of each experiment are in the [experiment catalog](experiments/README.md).

- [Randomized distribution run (action R5)](experiments/random-distribution/RANDOM_DISTRIBUTION_PROTOCOL.md)
- [Randomized distribution run (action R5): results](experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md)

## Experiments: diagnostics and probes

Every protocol was committed before its run; the question, design and outcome of each experiment are in the [experiment catalog](experiments/README.md).

- [Collision anatomy on passages](experiments/diagnostics/COLLISION_ANATOMY.md)
- [Run 601 confirmation and stochastic check](experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md)
- [Feature probe on passages](experiments/diagnostics/FEATURE_PROBE.md)
- [Light audit before the next experiments (no training, no policy evaluation)](experiments/diagnostics/LIGHT_AUDIT_RESULTS.md)
- [Sensing and memory probes (committee follow-up)](experiments/diagnostics/SENSING_PROBES.md)
- [Privileged-waypoint diagnostic: protocol](experiments/diagnostics/WAYPOINT_DIAGNOSTIC_PROTOCOL.md)
- [Privileged-waypoint diagnostic: results](experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md)

## Experiments: autonomous students (auxiliary head, privileged critic, pretraining)

Every protocol was committed before its run; the question, design and outcome of each experiment are in the [experiment catalog](experiments/README.md).

- [Autonomous students with a training-only route signal: protocol](experiments/students/AUXILIARY_STUDENT_PROTOCOL.md)
- [Autonomous students with a training-only route signal: results](experiments/students/AUXILIARY_STUDENT_RESULTS.md)
- [Supervised pretraining of the actor trunk, then PPO: protocol](experiments/students/PRETRAIN_PROTOCOL.md)
- [Supervised pretraining of the actor trunk, then PPO: results](experiments/students/PRETRAIN_RESULTS.md)

## Experiments: training budget, replication and levels B and C

Every protocol was committed before its run; the question, design and outcome of each experiment are in the [experiment catalog](experiments/README.md).

- [Two-million-transition test (B2): protocol](experiments/large-budget/LARGE_BUDGET_2M_PROTOCOL.md)
- [Two-million-transition test (B2): results](experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md)
- [Large-budget test (B1): protocol](experiments/large-budget/LARGE_BUDGET_PROTOCOL.md)
- [Large-budget test (B1): results](experiments/large-budget/LARGE_BUDGET_RESULTS.md)
- [Level B and level C measurement (B4): protocol](experiments/large-budget/LEVEL_BC_PROTOCOL.md)
- [Level B and level C measurement (B4): results](experiments/large-budget/LEVEL_BC_RESULTS.md)
- [Replication of the 2M recipe (B3): protocol](experiments/large-budget/REPLICATION_2M_PROTOCOL.md)
- [Replication of the 2M recipe (B3): results](experiments/large-budget/REPLICATION_2M_RESULTS.md)

## Experiments: connectome control and planner reference

Every protocol was committed before its run; the question, design and outcome of each experiment are in the [experiment catalog](experiments/README.md).

- [No-connectome control (C1): protocol, stage C1.0](experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL.md)
- [No-connectome control (C1), stage C1.1: protocol](experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C11.md)
- [No-connectome control (C1), stage C1.2: protocol](experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C12.md)
- [No-connectome control (C1), stage C1.3: protocol](experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C13.md)
- [No-connectome control, stage C1.0: results](experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md)
- [No-connectome control, stage C1.1: results](experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md)
- [No-connectome control, stage C1.2: results](experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md)
- [Planner reference and the four-family picture (C1.P): protocol](experiments/connectome-control/PLANNER_REFERENCE_PROTOCOL.md)
- [Planner reference and the four-family picture (C1.P): results](experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md)

## Results

| Document | What it covers |
| --- | --- |
| [Findings](results/FINDINGS.md) | This document consolidates the fly-rl results into one place: what worked, what failed, which configuration was best, and which claims the evidence does and does not support. |
| [Key numbers](results/KEY_NUMBERS.md) | A reference table of the headline measurements in the fly-rl project. |
| [Results](results/RESULTS.md) | The latest experimental planner-1.2 preserves contextual mapping while using separate clean neural ranges for braking. |

## Operations: commands, reproduction, verification, publication

| Document | What it covers |
| --- | --- |
| [Command reference](operations/COMMANDS.md) | Run commands from the repository root with the project-local interpreter. |
| [Operations and saved information](operations/OPERATIONS.md) | Use the project-local `.conda` interpreter or root launchers from the repository root. |
| [Preparing a public source release](operations/PUBLICATION.md) | The public repository is a source distribution with guides, aggregate experiment evidence, and original map illustrations. |
| [Reproducing the results](operations/REPRODUCE.md) | This guide shows how to rerun each result in the repository: the environment, the verification commands, and then the drivers and trainers for each experiment series, in order. |
| [Runs directory cleanup](operations/RUNS_CLEANUP.md) | The `runs/` directory held 87 GB. |
| [Verification](operations/VERIFICATION.md) | The correction verification on 2026-10-03 passed the full suite of 138 tests in 58.59 seconds. |

## Reference: credits and bibliography

| Document | What it covers |
| --- | --- |
| [Credits and references](reference/REFERENCES.md) | Fly RL uses the released MaleCNS v1.0 connectivity tables, biological annotations, neurotransmitter predictions, and soma coordinates. |

## Evidence and images

- [Evidence index](evidence/README.md): the small tracked evidence files from the planner, maze, architectural, guided-navigation and autonomous-curriculum iterations.
- [Image provenance](images/README.md): how every map preview and report figure was made.
