# Documentation

Start with the root [README](../README.md) for installation, demos and controls. These guides explain the implementation and its limits; detailed decisions, launch records and original machine evidence are kept locally under ignored `private/`.

| Topic | Guide |
| --- | --- |
| Live status, checklist and next actions | [Roadmap](../ROADMAP.md) |
| Index of every experiment since the reference recovery | [Experiment log](EXPERIMENT_LOG.md) |
| Randomized map sampler and the level B held-out region | [Map sampler](methods/MAP_SAMPLER.md) |
| Sealed held-out definitions and reserved seeds | [Held-out specification](methods/HELD_OUT_SPEC.md) |
| Randomized distribution run, negative result | [R5 results](experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md) |
| Exposure and reward-horizon audit | [Light audit](experiments/diagnostics/LIGHT_AUDIT_RESULTS.md) |
| Run 601 confirmation and stochastic evaluation | [Committee evaluation](experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md) |
| Anatomy of passages collisions | [Collision anatomy](experiments/diagnostics/COLLISION_ANATOMY.md) |
| Probe of the policy features | [Feature probe](experiments/diagnostics/FEATURE_PROBE.md) |
| Privileged-waypoint diagnostic | [Waypoint diagnostic](experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md) |
| History, range and synthetic probes | [Sensing probes](experiments/diagnostics/SENSING_PROBES.md) |
| Auxiliary-head and privileged-critic students, negative | [Student results](experiments/students/AUXILIARY_STUDENT_RESULTS.md) |
| Supervised pretraining then PPO, negative | [Pretrain results](experiments/students/PRETRAIN_RESULTS.md) |
| Phase design toward unseen-map navigation | [Zero-shot plan](overview/ZERO_SHOT_PLAN.md) |
| Recovered historical learned reference | [Historical reference](experiments/reference-recovery/HISTORICAL_REFERENCE.md) |
| Transfer experiments 1 to 8 | [Transfer summary](experiments/reference-recovery/TRANSFER_SUMMARY.md) |
| Cleanup of the local runs directory | [Runs cleanup](operations/RUNS_CLEANUP.md) |
| Source data, graph coverage and engineered assumptions | [Data and model](overview/DATA_AND_MODEL.md) |
| Original creators, license and scientific references | [Credits and references](reference/REFERENCES.md) |
| Data flow and code responsibilities | [Architecture](overview/ARCHITECTURE.md) |
| Recurrent activity, flight, rewards and optimization formulas | [Mathematics](methods/MATHEMATICS.md) |
| Launchers and CLI commands | [Commands](operations/COMMANDS.md) |
| Cameras, neural colors and activity traces | [Flight and neuron inspection](methods/FLIGHT_AND_NEURONS.md) |
| Original building and street drafts, mesh export and future real-place integration | [Architectural scenes](methods/ARCHITECTURAL_SCENES.md) |
| Progressive map generation and geometry curriculum | [Progressive maps](methods/GEOMETRY_CURRICULUM.md) |
| Independent suites, selection and route measurements | [Generalization and routes](methods/GENERALIZATION_AND_ROUTES.md) |
| Controller revision numbers, descriptions, and historical aliases | [Controller versions](planner/CONTROLLER_VERSIONS.md) |
| Revision order, experimental candidates, and choosing the next number | [Versioning](planner/VERSIONING.md) |
| Sensor contracts and explicit transfer | [Sensors v3](methods/SENSORS_V3.md) |
| Bounded diagnostic trajectories | [Validation traces](methods/VALIDATION_TRACES.md) |
| Fresh initialization comparison | [Fresh comparison](methods/VALIDATION_AND_FRESH_COMPARISON.md) |
| Near-goal reset curriculum | [Approach curriculum](methods/APPROACH_CURRICULUM.md) |
| Observed-ray risk objective | [Collision risk](methods/COLLISION_RISK.md) |
| Aggregate outcomes and uncertainty | [Results](results/RESULTS.md) |
| Complete large-room diagnosis, attempts, and operational solution | [Navigation resolution](planner/NAVIGATION_RESOLUTION.md) |
| Bounded timeout diagnosis and experimental goal-margin correction | [Planner timeout results](evidence/planner-timeouts-v56-results.md) |
| Speed/clearance isolation, regression, and conditional planner-1.1 recovery | [Planner follow-up](evidence/planner-followup-v57-v60.md) |
| Frozen paired measurement, budgets, and experimental viewing | [Planner development protocol](planner/PLANNER_DEVELOPMENT.md) |
| planner-1.0/planner-1.1 matched room outcomes and uncertainty | [Paired development results](evidence/planner-v60-development-results.md) |
| False stopping, stable distances, and unsuccessful route/mapping attempts | [planner-1.2-exp.1–planner-1.2-exp.3 readout diagnosis](evidence/planner-readout-v61-v63.md) |
| Actual-motion braking, known collision fixes, and fresh regression | [Momentum correction](evidence/planner-momentum-v64-results.md) |
| planner-1.1/planner-1.2-exp.1 declared readout comparison and regression | [Readout development results](evidence/planner-v61-development-results.md) |
| Dual mapping/safety interface, retained corrections, and matched fresh result | [planner-1.2 results](evidence/planner-dual-v65-results.md) |
| Twelve procedural map configurations and figure provenance | [Map gallery](images/README.md) |
| Source release checks, licensing, and history separation | [Public release](operations/PUBLICATION.md) |
| Verified causes, limitations and correction order after zero success | [Geometry failure diagnosis](learning/GEOMETRY_DIAGNOSIS.md) |
| Correctness checks and remaining QA limits | [Verification](operations/VERIFICATION.md) |
| Recordings, recovery, backups and publication | [Operations](operations/OPERATIONS.md) |

Public result summaries distinguish validation selection from final assessment and identify changes in task or initialization. Different final pools are not a paired comparison. Full checkpoints, data tables, trajectories and generated QA output are local artifacts, so a source clone cannot reproduce a trained flight until those artifacts are restored or explicitly regenerated.

Use the [contribution workflow](../CONTRIBUTING.md) for changes and the [roadmap](../ROADMAP.md) for proposed work. Public guides retain useful formulas, protocols and measured limits without including the detailed journal.

[Guided navigation](planner/GUIDED_NAVIGATION.md) explains privileged training supervision, teacher-free inference and the bounded correction protocol.

[Large-room corrections and maze navigation](planner/MAZE_NAVIGATION.md) records the room-contract correction, opening-search attempts, retained outcomes, and remaining verification.

[Autonomous learning](learning/AUTONOMOUS_LEARNING.md) records the return to planner-free learned actions, closure of planner development and the bounded PPO smoke.
