# Documentation

Start with the root [README](../README.md) for installation, demos and controls. These guides explain the implementation and its limits; detailed decisions, launch records and original machine evidence are kept locally under ignored `private/`.

| Topic | Guide |
| --- | --- |
| Source data, graph coverage and engineered assumptions | [Data and model](DATA_AND_MODEL.md) |
| Original creators, license and scientific references | [Credits and references](REFERENCES.md) |
| Data flow and code responsibilities | [Architecture](ARCHITECTURE.md) |
| Recurrent activity, flight, rewards and optimization formulas | [Mathematics](MATHEMATICS.md) |
| Launchers and CLI commands | [Commands](COMMANDS.md) |
| Cameras, neural colors and activity traces | [Flight and neuron inspection](FLIGHT_AND_NEURONS.md) |
| Progressive map generation and geometry curriculum | [Progressive maps](GEOMETRY_CURRICULUM.md) |
| Independent suites, selection and route measurements | [Generalization and routes](GENERALIZATION_AND_ROUTES.md) |
| Controller revision numbers, descriptions, and historical aliases | [Controller versions](CONTROLLER_VERSIONS.md) |
| Sensor contracts and explicit transfer | [Sensors v3](SENSORS_V3.md) |
| Bounded diagnostic trajectories | [Validation traces](VALIDATION_TRACES.md) |
| Fresh initialization comparison | [Fresh comparison](VALIDATION_AND_FRESH_COMPARISON.md) |
| Near-goal reset curriculum | [Approach curriculum](APPROACH_CURRICULUM.md) |
| Observed-ray risk objective | [Collision risk](COLLISION_RISK.md) |
| Aggregate outcomes and uncertainty | [Results](RESULTS.md) |
| Complete large-room diagnosis, attempts, and operational solution | [Navigation resolution](NAVIGATION_RESOLUTION.md) |
| Bounded timeout diagnosis and experimental goal-margin correction | [Planner timeout results](evidence/planner-timeouts-v56-results.md) |
| Speed/clearance isolation, regression, and conditional planner-1.1 recovery | [Planner follow-up](evidence/planner-followup-v57-v60.md) |
| Frozen paired measurement, budgets, and experimental viewing | [Planner development protocol](PLANNER_DEVELOPMENT.md) |
| planner-1.0/planner-1.1 matched room outcomes and uncertainty | [Paired development results](evidence/planner-v60-development-results.md) |
| False stopping, stable distances, and unsuccessful route/mapping attempts | [planner-1.2-exp.1–planner-1.2-exp.3 readout diagnosis](evidence/planner-readout-v61-v63.md) |
| Actual-motion braking, known collision fixes, and fresh regression | [Momentum correction](evidence/planner-momentum-v64-results.md) |
| planner-1.1/planner-1.2-exp.1 declared readout comparison and regression | [Readout development results](evidence/planner-v61-development-results.md) |
| Dual mapping/safety interface, retained corrections, and matched fresh result | [planner-1.2 results](evidence/planner-dual-v65-results.md) |
| Twelve procedural map configurations and figure provenance | [Map gallery](images/README.md) |
| Source release checks, licensing, and history separation | [Public release](PUBLICATION.md) |
| Verified causes, limitations and correction order after zero success | [Geometry failure diagnosis](GEOMETRY_DIAGNOSIS.md) |
| Correctness checks and remaining QA limits | [Verification](VERIFICATION.md) |
| Recordings, recovery, backups and publication | [Operations](OPERATIONS.md) |

Public result summaries distinguish validation selection from final assessment and identify changes in task or initialization. Different final pools are not a paired comparison. Full checkpoints, data tables, trajectories and generated QA output are local artifacts, so a source clone cannot reproduce a trained flight until those artifacts are restored or explicitly regenerated.

Use the [contribution workflow](../CONTRIBUTING.md) for changes and the [roadmap](../ROADMAP.md) for proposed work. Public guides retain useful formulas, protocols and measured limits without including the detailed journal.

[Guided navigation](GUIDED_NAVIGATION.md) explains privileged training supervision, teacher-free inference and the bounded correction protocol.
