# Project history

This document tells the whole story of the fly-rl project in numbered Iterations, from the first flight to the current zero-shot program. A reader should be able to reconstruct what was built, what was tried, what was measured and what was concluded without opening the development journal. Every number below is taken from a repository file, and the links point to the document that records it. Where a fact exists only in the private development journal, it is stated as such in the text.

## What the project is

A virtual fruit fly flies in procedurally generated 3D rooms. Its controller is the full annotated MaleCNS v1.0 connectome: 167,184 neurons and 25,583,622 directed connections, with 124,176,995 represented synapses in the original audit. The connectome is used as a fixed recurrent reservoir. Its synaptic weights are not optimized. A small readout is trained on top of it with PPO (proximal policy optimization). The reservoir is driven by engineered sensory projections of the fly's ray sensors, and its activity is read out as 256 features or richer neural features. See [DATA_AND_MODEL.md](DATA_AND_MODEL.md), [ARCHITECTURE.md](ARCHITECTURE.md) and [MATHEMATICS.md](../methods/MATHEMATICS.md).

The project has three lines, and the narrative keeps them apart:

- **The learned-policy line.** A PPO readout over the connectome decides every flight action. Most iterations below belong to this line. Its best results are on simpler distributions: single-opening rooms and medium dense rooms. Reliable navigation in large rooms, mazes and architectural scenes is not established.
- **The planner line.** An explicit observed-map planner builds map memory from the sensors, searches for routes and steers the fly. It uses full-connectome activity as its sensing path, but it does not learn movement and never counts as a learned result. It is the working demonstration for large rooms, mazes and architectural scenes, and it serves as a reference for the learned line.
- **The zero-shot program.** The current plan asks for a learned policy that reaches goals in maps it has never trained on, measured at three levels of novelty (new seeds, held-out parameters, held-out map family). It is defined in [ZERO_SHOT_PLAN.md](ZERO_SHOT_PLAN.md) and tracked in [ROADMAP.md](../../ROADMAP.md). Its release gate is not met.

The development journal that records the project from its first commit is private and not published. The published narrative is assembled from [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md), [RESULTS](../results/RESULTS.md), the planner, learning and experiment documents, the evidence files and the roadmaps ([ROADMAP.md](../../ROADMAP.md) and the archived [ROADMAP_HISTORY.md](../../ROADMAP_HISTORY.md)).

## How to read the numbers

- **Denominators.** Results are written as successes out of the pool size, for example 50/64. The denominator is the number of episodes or layouts in that pool. Development numbers and rates on reused pools are not presented as independent results.
- **Development and final pools.** A development pool is used for choosing a checkpoint, a variant or a protocol. A final pool is opened once for a frozen candidate and then consumed. Several results below are from final pools that are now consumed; later tuning requires a new untouched pool. Pool registries are listed in [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md) and in the [roadmap pools registry](../../ROADMAP.md#8-pools-registry).
- **Intervals.** Wilson 95% intervals are reported where the source document gives them. With 64 episodes, a 95% interval is roughly ±12 percentage points at 50% and narrower near the extremes.
- **Added and lifetime transitions.** "Added" counts the environment transitions of one training run. "Lifetime" counts the transitions already inside a checkpoint, including earlier training it inherited. Budgets were stated in added transitions.
- **Paired and unpaired comparisons.** Only some comparisons share layouts, initialization and budget. Where a table is not a paired ranking, the text says so.
- **Teacher and student.** When a privileged teacher or planner is used during training, its successes are reported separately from the autonomous student's successes.

## Summary table

| Iteration | Title | One-line outcome | Main documents |
| --- | --- | --- | --- |
| 1 | Full-connectome foundation (reservoir, small rooms, sensors, cameras, recording) | The full graph runs in a 3D room with sensors, cameras and replayable recordings. The behavior was untrained. | [ARCHITECTURE.md](ARCHITECTURE.md), [FLIGHT_AND_NEURONS.md](../methods/FLIGHT_AND_NEURONS.md), [DATA_AND_MODEL.md](DATA_AND_MODEL.md) |
| 2 | First PPO, rewards and curricula, small-room policy, larger dense rooms, coordinated movement, brain inspection windows, repository documentation | Small-room policy 32/32 on legacy seeds; coordinated dense policy 43/64 on a final pool, against 0/64 untrained; 80% target not met | [RESULTS.md](../results/RESULTS.md), [DENSE_ROOMS.md](../methods/DENSE_ROOMS.md), [GENERALIZATION_AND_ROUTES.md](../methods/GENERALIZATION_AND_ROUTES.md) |
| 3 | Versioned sensors and matched comparisons, approach curriculum, collision-risk objective, fresh-initialization comparison | Medium dense-room policies 35 to 50 of 64 on separate final pools; approach curriculum and risk penalty did not beat their controls | [SENSORS_V3.md](../methods/SENSORS_V3.md), [VALIDATION_AND_FRESH_COMPARISON.md](../methods/VALIDATION_AND_FRESH_COMPARISON.md), [APPROACH_CURRICULUM.md](../methods/APPROACH_CURRICULUM.md), [COLLISION_RISK.md](../methods/COLLISION_RISK.md), [VALIDATION_TRACES.md](../methods/VALIDATION_TRACES.md) |
| 4 | Progressive geometry curriculum, the zero-success outcome, diagnosis and passage-mastery corrections | Progressive large-room experiment 0/64 on its final pool; passage-mastery policy 61/64 on single-opening rooms only | [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md), [GEOMETRY_DIAGNOSIS.md](../learning/GEOMETRY_DIAGNOSIS.md), [passage-mastery-v2-results.md](../evidence/passage-mastery-v2-results.md) |
| 5 | Guided navigation, neural waypoint, panoramic sensors, the bounded two-hour window | Many large-room learned corrections, each at 0/8 development goals or lower; learned large-room navigation unresolved | [GUIDED_NAVIGATION.md](../planner/GUIDED_NAVIGATION.md), [large-continuous-v4-pause.md](../evidence/large-continuous-v4-pause.md), [neural-waypoint-v6-results.md](../evidence/neural-waypoint-v6-results.md), [panoramic-neural-v7-results.md](../evidence/panoramic-neural-v7-results.md), [two-hour-navigation-results.md](../evidence/two-hour-navigation-results.md) |
| 6 | The explicit observed-map planner for large rooms: timeouts, paired development, planner-1.0 to 1.2 | Explicit planner 13/16 in prospective development, then 15/16 tied with its successor; not a learned result | [NAVIGATION_RESOLUTION.md](../planner/NAVIGATION_RESOLUTION.md), [CONTROLLER_VERSIONS.md](../planner/CONTROLLER_VERSIONS.md), [observed-map-v55-results.md](../evidence/observed-map-v55-results.md), [planner-dual-v65-results.md](../evidence/planner-dual-v65-results.md) |
| 7 | Maze contract, opening diagnostics and the room-aware planner series (planner-1.3), maze closure | Maze reached 7/8 on retained maps and 5/8 on fresh maps; closed without a passing fresh gate | [MAZE_NAVIGATION.md](../planner/MAZE_NAVIGATION.md), [maze-wrap-up.md](../evidence/maze-wrap-up.md) |
| 8 | Architectural scenes and planner-1.4, the original-objective check | Architectural planner 19/21 on original objectives, zero collisions; two timeouts remain | [ARCHITECTURAL_SCENES.md](../methods/ARCHITECTURAL_SCENES.md), [ARCHITECTURAL_NAVIGATION.md](../planner/ARCHITECTURAL_NAVIGATION.md), [architectural-closing-results.md](../evidence/architectural-closing-results.md) |
| 9 | Autonomous learning restart: PPO pilots and architectural curricula (structured, balanced, mixed), closing results | Planner-free PPO pilots reached 0/6 to 1/6 validation goals; curricula did not resolve route navigation | [AUTONOMOUS_LEARNING.md](../learning/AUTONOMOUS_LEARNING.md), [MIXED_AUTONOMOUS_CURRICULUM.md](../learning/MIXED_AUTONOMOUS_CURRICULUM.md), [autonomous-architecture-curriculum-2-results.md](../evidence/autonomous-architecture-curriculum-2-results.md) |
| 10 | Zero-shot program begins: recovery and hash verification of the historical medium-room policies, transfer experiments 1 to 8, regression suite | Historical 50/64, 48/64 and 45/64 winners recovered and replayed; transfer to partitioned rooms gave gains that did not hold | [HISTORICAL_REFERENCE.md](../experiments/reference-recovery/HISTORICAL_REFERENCE.md), [TRANSFER_SUMMARY.md](../experiments/reference-recovery/TRANSFER_SUMMARY.md), [MEDIUM_REGRESSION_SUITE.md](../methods/MEDIUM_REGRESSION_SUITE.md) |
| 11 | Held-out specification, variance study, stabilization (Phase 1) and memory (Phase 3) screening and replication | Training-to-training spread up to 11 episodes; stabilization and memory did not meet their criteria | [HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md), [VARIANCE_STUDY_RESULTS.md](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md), [PHASE1_RUN_RESULTS.md](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md), [PHASE3_REPLICATION_RESULTS.md](../experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md) |
| 12 | Randomized map sampler, the random-distribution run (R5), committee reviews and diagnostics | Random-map training negative by its rule; diagnostics located the failure in information at decision time, not in the reward | [MAP_SAMPLER.md](../methods/MAP_SAMPLER.md), [RANDOM_DISTRIBUTION_RESULTS.md](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md), [LIGHT_AUDIT_RESULTS.md](../experiments/diagnostics/LIGHT_AUDIT_RESULTS.md), [FEATURE_PROBE.md](../experiments/diagnostics/FEATURE_PROBE.md) |
| 13 | Autonomous students: auxiliary head, privileged critic, supervised pretraining (all negative) | Three training-only route signals each failed their rule on `passages` | [AUXILIARY_STUDENT_RESULTS.md](../experiments/students/AUXILIARY_STUDENT_RESULTS.md), [PRETRAIN_RESULTS.md](../experiments/students/PRETRAIN_RESULTS.md) |
| 14 | Training budget: 1M, 2M, three-seed replication, level B and level C measurement | 2M budget raised `passages` to 36 to 42 of 64 on three seeds; level B inconclusive, level C positive | [LARGE_BUDGET_RESULTS.md](../experiments/large-budget/LARGE_BUDGET_RESULTS.md), [LARGE_BUDGET_2M_RESULTS.md](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md), [REPLICATION_2M_RESULTS.md](../experiments/large-budget/REPLICATION_2M_RESULTS.md), [LEVEL_BC_RESULTS.md](../experiments/large-budget/LEVEL_BC_RESULTS.md) |
| 15 | Connectome control (C1.0 to C1.2, edge-shuffled reservoir) and the planner reference (C1.P) | No measured advantage of the real wiring over an edge-shuffled reservoir; planner reaches 147 of 168 on level C | [CONNECTOME_CONTROL_RESULTS_C12.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md), [PLANNER_REFERENCE_RESULTS.md](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md) |
| 16 | Consolidation (this documentation reorganization, brief) | Documents organized into topic folders; the release gate is not met and the release decision is open | [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md), [ROADMAP.md](../../ROADMAP.md), [PUBLICATION.md](../operations/PUBLICATION.md) |

---

## Iteration 1. Full-connectome foundation (reservoir, small rooms, sensors, cameras, recording)

**Goal.** Build an autonomous fly, initially untrained, in a bounded 3D room, driven by the full annotated MaleCNS v1.0 graph on a single 12 GB GPU. The user asked for verification rather than extended training.

**Decision.** Use a fixed sparse recurrent graph and learn only a smaller movement policy from compressed activity. This makes full-connectome inference practical on the available hardware. The project does not claim to simulate biological membrane or wing dynamics. See [FLIGHT_AND_NEURONS.md](../methods/FLIGHT_AND_NEURONS.md) and [ARCHITECTURE.md](ARCHITECTURE.md).

**Built.**

- A project-local Conda environment and an audit of the official connectome tables. The audit retained all qualifying annotated neurons and their mutual connections: 167,184 neurons, 25,583,622 directed connections and 124,176,995 represented synapses. Runtime graph integrity and full coverage were verified (development journal).
- A Panda3D room with obstacles, a target, inertia, altitude and steering, ray sensing, collision detection, cameras, a trail, and reset and new-room controls.
- Checkpoint loading and explicit learning commands. Opening a demo does not invoke learning.
- A bounded full-graph inference benchmark and a 128-transition, one-update smoke test. These established inference and optimizer/checkpoint plumbing.

The historical benchmark report was regenerated later and has no recorded source revision, so its values cannot be attributed to an exact initial sensor configuration (development journal).

**Sensors and recording.** The sensor contract expanded to 128 distance rays, 128 approach readings and 13 state values. Free-camera controls were added. Each session was archived in a unique folder with room geometry, sensors, features, actions, outcomes, provenance and optional full-brain snapshots.

A Ctrl+C run exposed a real shutdown bug: the screenshot was captured before the last telemetry flush. The inspection found 512 intact transitions and 27 snapshots, including one at step 540, so the saved transition stream ended before the recorded brain activity. The exact final decision count was unavailable and the unwritten tail could not be recovered. The response was to finalize recording first, isolate optional screenshot failures and handle interruption explicitly. Transition chunks were reduced to 128 decisions to limit exposure to abrupt loss. Recovery can validate and mark retained files but cannot reconstruct decisions that were never written. This remains a documented limitation (development journal).

**Archive tools.** `inspect`, `recover`, `compare` and `replay` were added. Recovery defaults to a dry run and mutates a manifest only with an explicit `--apply`. Replay reads stored states without running a policy or a connectome. At this stage 18 tests passed, including corruption rejection and interrupted-manifest recovery. A two-second replay advanced 40 saved decisions on CPU with a nonexistent graph path, showing that replay does not depend on the live brain (development journal).

**Tried and stopped.** Nothing was learned here. The archives were untrained and contain no learning-performance evidence.

**Learned.** The plumbing works: the full graph runs in the loop, recordings are checkable, and interrupted sessions can be identified. Behavior was not established.

**Links.** [ARCHITECTURE.md](ARCHITECTURE.md), [DATA_AND_MODEL.md](DATA_AND_MODEL.md), [FLIGHT_AND_NEURONS.md](../methods/FLIGHT_AND_NEURONS.md), [README.md](../../README.md).

---

## Iteration 2. First PPO, rewards and curricula, small-room policy, larger dense rooms, coordinated movement, brain inspection windows, repository documentation

**Goal.** Make the fly reach goals. Then extend the policy to larger rooms and to coordinated movement, and make the brain inspectable.

### First PPO run and the reward change

The first substantial PPO run used 131,072 transitions, batch 16 and seed 42. Losses were finite and the process exited normally. The user observed that the fly went to the middle of the room and stopped. A later evaluation measured 0/16 arrivals, no collisions and a mean end distance of about 3.998 units (development journal). The run is preserved as a failure. Finite losses were not treated as success.

The reward was then rewritten as explicit terms for progress, time cost, arrival, collision and timeout. A curriculum moved through near targets, empty rooms and obstacle rooms, with development evaluations between stages. Three rounds of 65,536 transitions were used, 196,608 in total. Obstacle development success rose from 12/16 to 14/16 and then 16/16. Checkpoint counters are cumulative and their sum is not the training budget. The development pool was reused during iteration, so its perfect last score is not independent generalization (development journal).

The third round was selected as the demonstration policy. On separate legacy small-room seeds 20000 to 20031 it reached 32/32 arrivals with no collisions or timeouts and an average arrival in 83.625 decisions, about 4.18 simulated seconds. The development journal does not classify that pool as development or final. It covers only the original small room, not the later 48-obstacle rooms.

### Larger dense rooms

Dense rooms were 32 × 32 × 12 units with 48 boxes, randomized distant endpoints and randomized heading. The generator certifies a clear reference route but keeps that route out of the policy observations. The direct target direction remains part of the engineered sensor interface (development journal, [DENSE_ROOMS.md](../methods/DENSE_ROOMS.md)).

The dense suite froze 256 training, 32 validation and 64 test layouts with disjoint seeds and distinct recorded geometry fingerprints. Training sampled only the training pool and validation selected policies. The legacy adaptation added 131,072 transitions to the small-room policy, reaching 327,680 lifetime transitions. Validation improved from 13/32 to 21/32 and the policy was promoted to the demonstration alias. Its test was not used (development journal).

### Coordinated movement

Independent lateral control explained sideways travel that the user had noticed. The coordinated dynamics reduced lateral acceleration, increased lateral damping, smoothed turning and added motion-derived bank and pitch. Checkpoint dynamics were versioned so that a shape-compatible legacy policy could not silently be treated as suitable. Transferring the old policy into the coordinated controls gave 4/16 development arrivals and 56.25% collisions, which supported retraining rather than declaring the change harmless (development journal).

A fresh coordinated small-room policy trained for three rounds of 65,536 transitions (196,608 total). Development arrivals were 12/16, 14/16 and 15/16. The third round became the coordinated launcher's policy and the starting point for dense adaptation. This 15/16 was a development result on the iteration's own pool, not a held-out assessment (development journal).

### Coordinated dense adaptation and its final test

A bounded adaptation added two rounds of 65,536 transitions to the accepted coordinated controller, 131,072 in total and 327,680 lifetime. Validation went from 10/32 at the baseline to 15/32 and then 24/32. Selection considered the baseline and ranked validation success, collisions and end distance. Round two won. The selected checkpoint, metadata and suite were hashed before the single final comparison (development journal).

The selected and untrained deterministic policies were then evaluated on the same 64 reserved layouts without updates. The selected policy reached **43/64 goals (67.2%, Wilson 95% interval 55.0–77.4%)** with 11 collisions and 10 timeouts. The untrained policy timed out in all 64 episodes. Successful arrivals averaged 14.37 simulated seconds and 24.32 traveled units. The mean ratio of flown to straight-line distance was about 1.31. Straight-line distance is only a lower bound and no obstacle-aware optimal route was measured. The 80% held-out goal was not met ([RESULTS.md](../results/RESULTS.md), "Earlier dense-room results"). This is the launcher's original coordinated dense policy, and the same numbers appear in the results table.

### Brain inspection

The brain view moved from numbers to anatomy. The official soma coordinates were joined with retained body IDs and displayed 140,033 located neurons. The remaining 27,151 active neurons have no drawable official soma location and were not invented. Activity, recent change and local action sensitivity became colour modes. The display uses soma points, not neurite reconstructions or synaptic edges. Official soma-neuromere and superclass filters, real body-ID selection and a 240-sample decision-aligned timeline were added. The brain window runs in a separate Panda3D window that shares the live simulation and creates no second graph, policy or optimizer. Local sensitivity and correlation are not causal biological explanations (development journal).

### Speed control

The first response to the user's request about Shift strengthened camera movement, which was a scope misunderstanding. The corrected behaviour makes Shift request ten times the base simulation rate in either focused window. The simulation advances more fixed-size decisions rather than changing the physics timestep. Requested speed is not a throughput guarantee (development journal).

### Repository organization

The flat package was reorganized into five named areas (connectome, simulation, training, visualization, recordings) with mirrored tests. Launchers and the root CLI remained discoverable. Before and after runs of twenty decisions per profile agreed within numerical tolerance, with maximum absolute differences below 0.000001 (development journal). The documentation was rewritten to remove contradictory assertions and to disclose consumed test data and biological limits. The roadmap of that time prioritized fresh-suite generalization, feasible-path metrics and anatomical replay.

### Fresh-suite generalization and the route reference

The next bounded experiment tested whether the coordinated dense result generalizes to a fresh suite. It used two adaptations of 65,536 added transitions each, seeds 42 and 73, batch 8 and two rounds per seed. Both started from the same coordinated dense policy. These are repeated adaptation seeds, not independent from-scratch models.

The new suite used training seeds 30000 to 30255, validation seeds 40000 to 40031 and test seeds 50000 to 50063. All 352 layouts were checked against the original suites for seed reuse and matching geometry. An evaluation-only 3D reference route was added. It uses body-inflated boxes with extra clearance, exact swept-segment tests, sampled corner visibility and Dijkstra. Returned paths are feasible geometric references, not global optima or dynamic-flight claims. No obstacle map or reference path entered the policy observations (development journal, [GENERALIZATION_AND_ROUTES.md](../methods/GENERALIZATION_AND_ROUTES.md)).

Validation for seed 42 went 23/32, 23/32, 27/32. For seed 73 it went 23/32, 25/32, 25/32. Validation selected seed 42's second round, with 393,216 lifetime transitions. The final single comparison gave **43/64 goals** for the selected policy, with 15 collisions and 6 timeouts, and 0/64 for the untrained controller. The Wilson interval is about 55.0–77.4%. Successful arrivals averaged 15.33 seconds and 23.55 units, with a mean feasible-reference ratio of 1.219. All 128 selected and untrained references matched their endpoints and clearance constraints. The 80% criterion was not achieved. The test pool is consumed. The count of 43 matches the earlier final result but the layouts differ, so the two cannot be compared directly.

### Brain-inspection and documentation closeout

Later checks covered the frozen selected checkpoint through the dense launcher on a training seed, a one-second offscreen run and replay integrity. These were verification only and no further final test was run. Documentation was extended with formulas for the normalized connectivity, sensory projection, leaky activity, coordinated flight, rewards, PPO, GAE and route metrics, and with source-data attribution (see Iteration 16 for the later documentation consolidation).

**Tried and stopped.** The direct transfer of the small-room policy into coordinated controls (4/16 with 56.25% collisions) was stopped in favour of retraining. The first Shift change was reverted in favour of simulation acceleration.

**Learned.** A reward with explicit progress and timeout terms, a curriculum and a validation-selected policy can reach a high rate on simpler pools. A bounded adaptation to dense rooms reached 43/64 on a final pool, well above the untrained controller's 0/64, but short of the 80% target. Development pools and final pools must be kept apart, and a reserved pool can be used once.

**Links.** [DENSE_ROOMS.md](../methods/DENSE_ROOMS.md), [GENERALIZATION_AND_ROUTES.md](../methods/GENERALIZATION_AND_ROUTES.md), [FLIGHT_AND_NEURONS.md](../methods/FLIGHT_AND_NEURONS.md), [MATHEMATICS.md](../methods/MATHEMATICS.md), [RESULTS.md](../results/RESULTS.md), [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Iteration 3. Versioned sensors and matched comparisons, approach curriculum, collision-risk objective, fresh-initialization comparison

**Goal.** Test whether a better sensor contract, an approach curriculum or a collision-risk penalty improves medium dense-room policies, under matched conditions.

### Versioned room-scale sensors

Sensor version v3 added room-scale distance and altitude normalization and a measured yaw rate. The v2 default was left unchanged. Checkpoint metadata, world and brain validation, viewing, training, evaluation and archive labels follow the saved interface. An explicit migration preserves policy and optimizer bytes and records the semantic transfer ([SENSORS_V3.md](../methods/SENSORS_V3.md)).

### Warm-start comparison

The first matched comparison used two seeds per interface, 65,536 transitions per round and two rounds, 262,144 added in total ([VALIDATION_AND_FRESH_COMPARISON.md](../methods/VALIDATION_AND_FRESH_COMPARISON.md)). Validation rose as follows, out of 32:

| Interface | Seed | Baseline | Round 1 and 2 | Selected |
| --- | --- | ---: | --- | ---: |
| v2 | 42 | 17 | 23 → 23 | 23 |
| v2 | 73 | 17 | 19 → 21 | 21 |
| v3 | 42 | 18 | 19 → 17 | 19 |
| v3 | 73 | 18 | 20 → 21 | 21 |

Validation selected v2 before the single final test. The frozen winner reached **50/64 goals (78.1%, Wilson 66.6–86.5%)** with 5 collisions and 9 timeouts. The untrained controller with the same interface reached 0/64. Only the selected winner was final-tested, so this is not a paired comparison of v2 and v3, and the warm start means the two arms were not from scratch (development journal, [RESULTS.md](../results/RESULTS.md)).

### Fresh-initialization comparison

The second comparison started every run from fresh paired policy weights and empty optimizer state. It used 524,288 added transitions: 131,072 per seed and interface, in two rounds of 65,536 each. Elapsed time including validation and final assessment was 3729.47 seconds. Validation, out of 32, started at 0 for all runs and selected:

- v2 seed 42: 17/32 (2 collisions, 13 timeouts)
- v2 seed 73: 21/32 (6 collisions, 5 timeouts)
- v3 seed 42: 24/32 (6 collisions, 2 timeouts)
- v3 seed 73: 21/32 (5 collisions, 6 timeouts)

Validation selected v3 seed 42, round 2. Its single final assessment reached **35/64 goals (54.7%, Wilson 42.6–66.3%)** with 20 collisions and 9 timeouts. The untrained control reached 0/64. This does not establish a paired advantage of v3 over v2, and the different final rooms make cross-experiment comparisons unsafe. Two seeds and one generator do not establish broad robustness (development journal, [RESULTS.md](../results/RESULTS.md)).

### Validation traces and the collision question

Validation trajectories were recorded after the fresh comparison, with no optimizer updates and no final-test access. Two full-graph examples matched the recorded outcomes. Seed 140000 contacted obstacle 16 after 129 decisions. Seed 140020 timed out at distance 0.813 after 1,200 decisions. All 81 tests passed at that point. A training-layout terminal-approach curriculum was proposed for a controlled comparison ([VALIDATION_TRACES.md](../methods/VALIDATION_TRACES.md)).

### Approach curriculum

The approach curriculum placed some training resets close to the goal. Its probability starts at 50% and reaches zero halfway through the seed's transition budget. Success radius, collision rules and validation were unchanged. The equal-budget comparison used 524,288 added transitions, 131,072 per method and seed, in two rounds with batch 8 ([APPROACH_CURRICULUM.md](../methods/APPROACH_CURRICULUM.md)).

Validation, out of 32, was baseline 42: 27, baseline 73: 26, curriculum 42: 23 and curriculum 73: 26. Ordinary validation selected normal training, seed 42, round 2. Its single final assessment reached **45/64 goals (70.3%, Wilson 58.2–80.1%)** with 15 collisions and 4 timeouts. The untrained control reached 0/64.

The curriculum did not beat the normal-training arm on the declared validation criterion. Reset counters for the curriculum runs included 49 near and 284 ordinary resets for seed 42, and 44 near and 280 ordinary for seed 73. Round 2 used ordinary resets only. These counters include initialization, so they are not independent episode counts. This result holds for this budget, two seeds and this generator, and does not establish that all approach curricula are ineffective.

### Collision-risk objective

The collision-risk experiment added a pre-action penalty based on observed rays, in response to two retained collisions in which obstacles were visible through the last second while positive thrust persisted. Visibility to the rays is not neural recognition, and the penalty was treated as one testable hypothesis ([COLLISION_RISK.md](../methods/COLLISION_RISK.md)).

The experiment used 524,288 added transitions. Validation, out of 32, was:

- baseline 42: 27/32 (4 collisions, 1 timeout)
- baseline 73: 22/32 (4 collisions, 6 timeouts)
- risk 42: 26/32 (5 collisions, 1 timeout)
- risk 73: 22/32 (10 collisions, 0 timeouts)

Risk-active transitions summed to 5,668 for seed 42 and 8,732 for seed 73, with extra preprocessing of about 205.73 and 188.86 seconds. Validation selected baseline seed 42. Its final assessment reached **48/64 goals (75.0%, Wilson 63.2–84.0%)** with 16 collisions and 0 timeouts. The untrained control reached 0/64. The penalty did not beat normal training on the declared validation ranking for either seed. Its lower collision count must be read together with success and timeouts, and no paired final comparison was run.

**Tried and stopped.** The approach curriculum and the risk penalty were tested once at this budget and did not beat their normal-training controls on validation. The fresh sensor comparison did not show an advantage for v3 over v2 on a paired final test.

**Learned.** Initialization and sensor version each changed validation outcomes, and the spread between seeds was as large as the differences between arms. Finals on different pools cannot be ranked against each other. The medium-room policies reached 35 to 50 of 64 on their separate final pools, well above zero but below the 80% target.

**Links.** [SENSORS_V3.md](../methods/SENSORS_V3.md), [VALIDATION_AND_FRESH_COMPARISON.md](../methods/VALIDATION_AND_FRESH_COMPARISON.md), [APPROACH_CURRICULUM.md](../methods/APPROACH_CURRICULUM.md), [COLLISION_RISK.md](../methods/COLLISION_RISK.md), [VALIDATION_TRACES.md](../methods/VALIDATION_TRACES.md), [RESULTS.md](../results/RESULTS.md).

---

## Iteration 4. Progressive geometry curriculum, the zero-success outcome, diagnosis and passage-mastery corrections

**Goal.** Move from single dense rooms to maps that become harder in stages, with profiles that add partitions and openings, and test whether a curriculum helps on a fixed large room.

**Built.** Versioned map profiles were added in `simulation/map_profiles.py`, from a 24-box open room to a 192-box 64 × 64 × 20 chamber sequence with alternating openings that demand horizontal turns and altitude changes. A hidden route certificate protects geometric feasibility; the certificate is not an observation or an optimal plan. Route-dependent episode limits give longer routes an explicit allowance. The reset-mixture schedule and the matched comparison preparation were added as separate modules. Tall partitions render translucently in the overview, while collision surfaces remain solid. The original generator and launcher policies were preserved (development journal, [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md)).

The verification suite grew to 116 tests, and then to 117 after four side branches were added to the maze preset. The maze preset is an alternating chamber sequence with dead-end side wings, not an arbitrary branching topology.

### Geometry comparison with a zero-success outcome

The comparison used 524,288 added transitions across four fresh runs: baseline and curriculum, seeds 42 and 73. The reset schedule moved from mostly open rooms toward large rooms as global transition progress increased. Mixtures were 75/20/5%, 20/60/20% and 10/20/70% for open, passages and large, respectively. These are reset probabilities, not guaranteed transition fractions ([RESULTS.md](../results/RESULTS.md), "Geometry comparison"; [geometry-v1-results.json](../evidence/geometry-v1-results.json)).

Validation on 32 fixed large layouts was 0 goals for every candidate: baseline 42 had 1 collision and 31 timeouts; baseline 73 had 0 collisions and 32 timeouts; curriculum 42 had 1 collision and 31 timeouts; curriculum 73 had 0 collisions and 32 timeouts. The selection rule chose curriculum seed 73, whose selected checkpoint was the untrained initialization with 0 lifetime transitions. The method ranking used final ending distances of 44.2234894709623 and 44.2234894695337, a difference far too small to indicate a curriculum effect.

The single final assessment on 64 fixed large layouts reached **0/64 goals**, with 1 collision and 63 timeouts (Wilson 95% interval 0.0–5.7%). The untrained control also reached 0/64, with 1 collision and 63 timeouts. The pool is consumed. The results record that the complete comparison took 206.7 minutes including initialization.

### Diagnosis of the zero-success outcome

A review compared the frozen sources and all eight round validations with the earlier controllers ([GEOMETRY_DIAGNOSIS.md](../learning/GEOMETRY_DIAGNOSIS.md)). On four retained validation layouts from the earlier original room (seeds 240000 to 240003), the earlier ray-risk policy reached 3/4 goals, matching its stored outcomes. The same unchanged controller, explicitly transferred to new large layouts (seeds 290000 to 290003), reached 0/4 with 2 collisions and 2 timeouts. The legacy world matched its frozen implementation over 480 transitions across 16 layouts.

The review identified two process failures rather than one cause. Progression advanced without passage mastery, and initialization was selected after every trained target candidate had failed. It did not establish a single causal explanation.

### Passage-mastery corrections

The corrections added gate-near and gate-long profiles and a practice schedule called geometry-v2-practice-mastery. The last 16 training seeds were withheld as practice layouts from both arms. After each round, two deterministic practice batches, each of 8 episodes, had to reach at least 7/8 goals before the schedule advanced. Easier examples remained at 20% after stage zero. Gate metadata was preserved across rounds (development journal, [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md)).

The comparison used 524,288 added transitions, 131,072 per arm and seed, in eight rounds of 16,384. Validation on the 32 large layouts was:

- baseline 42: 30 goals, 0 collisions, 2 timeouts
- baseline 73: 25 goals, 6 collisions, 1 timeout
- curriculum 42: 29 goals, 2 collisions, 1 timeout
- curriculum 73: 1 goal, 0 collisions, 31 timeouts

Validation selected baseline seed 42, round 7, with 114,688 lifetime transitions. The final assessment on the single-opening `gate-long` pool reached **61/64 goals (95.3%)**, with zero collisions and 3 timeouts. The Wilson 95% interval is 87.1–98.4%. The untrained control reached 0/64, with 64 timeouts. Only the frozen winner and the control were final-tested. The complete comparison took 60.41 minutes including inference and initialization ([passage-mastery-v2-results.md](../evidence/passage-mastery-v2-results.md)).

This result is a strong one for the simpler single-opening distribution. It is not a result on the large rooms, which the same schedule did not address during this comparison. It is the strongest learned final result in this line, on its own pool, which is now consumed.

**Tried and stopped.** Plain curricula over the large target did not produce a validation-selectable policy in this budget. The large-room comparison was stopped as a development dead end, not as a claim that the approach is impossible.

**Learned.** Passing finite losses and tests did not make the outcome acceptable. Progression rules must include passage mastery. Selection must not pick an untrained initialization as a successful model. A mastery gate works on single-opening rooms, and its results are kept separate from the large target.

**Links.** [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md), [GEOMETRY_DIAGNOSIS.md](../learning/GEOMETRY_DIAGNOSIS.md), [passage-mastery-v2-results.md](../evidence/passage-mastery-v2-results.md), [geometry-v1-results.json](../evidence/geometry-v1-results.json), [RESULTS.md](../results/RESULTS.md).

---

## Iteration 5. Guided navigation, neural waypoint, panoramic sensors, the bounded two-hour window

**Goal.** Get a teacher-free student to reach goals in the original large rooms, using guided supervision, better sensing, memory and bounded budgets. Every step was declared with a budget and kept separate from the final pool.

### Large-room adaptation

A new nonoverlapping suite for the original large target was prepared: 128 training seeds (16 held back as practice), 32 validation seeds and 64 reserved test seeds. A seven-stage mastery curriculum ended at the unchanged 48 × 48 × 16, 112-box large profile, and training warm-started from the successful single-wall checkpoint and its Adam state. The declared rules were that test access requires at least 85% validation success and that completion requires at least 80% in one independent final assessment (development journal, [large-goal-v3 plan](../evidence/large-goal-v3-plan.md)).

A continuity defect then appeared. Chunks of 8,192 transitions with eight environments allowed only 1,024 decisions before recreation, below the profiled 1,200-decision timeout. The run was stopped after its saved checkpoints; validation at chunks four and eight had both reached 0/32 goals. A live training session that keeps observations, optimizer, world state, brain activity and randomness across chunks was implemented and verified with physics regression tests (development journal, [large-continuous-v4-plan.md](../evidence/large-continuous-v4-plan.md)).

The continuation, `large-continuous-v4`, had 425,984 remaining transitions in two seeds of 212,992 each, in 26 chunks. Its cumulative substantive budget stayed at 524,288. The run was paused after round 23 of seed 42, with 188,416 added transitions for that seed and 286,720 preserved across the earlier interrupted experiment. Round 20 validation on the original large profile reached **0/32 goals**, with 2 collisions and 30 timeouts. Mean path length was 226.27 units and mean target distance fell from 44.36 to 34.57 units ([large-continuous-v4-pause.md](../evidence/large-continuous-v4-pause.md)).

### Why the large runs timed out

A diagnosis recorded the exposure breakdown of the paused checkpoint. It had trained for 71,732 transitions on gate-near, 16,356 on gate-long, 9,130 on gate-two, 63,202 on passages-wide and 27,996 on large-wide. It had trained for **zero** transitions on the original large target and on large-narrow. Four diagnostic flights on optimization layouts 370000 to 370003 reached the 1,800-decision diagnostic cap three times and collided once; none reached its goal. Heading rotation ranged from 8.64 to 16.26 turns ([large-timeout-diagnosis.md](../evidence/large-timeout-diagnosis.md)).

Two learning-objective mismatches were found. At 50 ms per decision, gamma 0.995 gives an effective horizon of about 10 seconds. The large-profile route averages 118.85 units, and under an illustrative constant route speed the arrival bonus has a discounted value of 0.00748, against 4.84 on gate-long. The second mismatch was that the world penalizes an exhausted attempt but labels it truncated, so SB3 bootstraps its terminal value. A regression test fixed the rollout reward at 4.93 where a failure terminal would give -5.02. Both were treated as causes to test, not proven causes. The discount was made configurable and a failure-terminal option was added. A version of the sensors with a remaining-time channel followed (sensors-v4) ([timeout-correction-pilot-v1-results.md](../evidence/timeout-correction-pilot-v1-results.md)).

### Timeout correction pilot

The pilot used 32,768 transitions in four chunks: 16,384 on the unchanged original large target and 16,384 on the stage-four mixture, with gamma 0.9995, failure-terminal deadline handling and the sensors-v4 clock. On four development layouts the goals stayed at 0/4. Collisions fell from 3/4 to 1/4 and timeouts rose from 1/4 to 3/4. Mean end distance went from 36.82 to 32.54 and mean idle fraction from 0.0267 to 0.0209. The result showed no arrivals. A counterfactual that changed only the clock input from zero to one shifted pooled features by 32.72% and mean absolute action by 0.1395, so the transferred clock disrupts an already trained controller. Cumulative substantive transitions reached 319,488.

### Brain memory

A full-graph analysis measured how fast the reservoir forgets. Its maximum absolute row sum was 0.900000274. Under the recurrence h_next = 0.5 h + 0.5 tanh(W h + sensory), a bound gives about 0.95 contraction per 50 ms decision and a worst-case e-folding time of 0.975 seconds. A pulse test changed the target once and supplied identical sensors afterward. The relative maximum neuron-state difference was 0.159 after 0.25 seconds, 0.0441 after 0.5 seconds, 0.00295 after one second and about 9.53e-6 after 2.5 seconds ([brain-memory-diagnosis.md](../evidence/brain-memory-diagnosis.md)). The bound is mathematical and does not make a biological memory claim.

A temporal readout was added: a 64-unit GRU over 32 historical brain-feature samples at stride 8, about 12.8 seconds, with a linear residual initialized to zero so the initial predictions equal the previous controller ([brain-memory-comparison-v1-results.md](../evidence/brain-memory-comparison-v1-results.md)). A matched comparison gave each arm 65,536 added transitions, 32,768 on the original large target. Validation on eight layouts (430000 to 430007) was 0/8 for both arms: the current-feature arm had 2 collisions and 6 timeouts, and the memory arm had 1 collision and 7 timeouts. Training terminal outcomes on the original large target were 0 goals, 10 collisions and 2 timeouts for control, and 0 goals, 21 collisions and 2 timeouts for memory. Memory did not show navigation benefit. Cumulative use reached 450,560 transitions.

### Reward correction

The next diagnosis measured that the optimization certificates contained 5.1537 units of travel away from the direct target on average, penalized by 10.3074 progress units. This geometric witness is not a sole-cause proof. A physical diagnostic route follower collided on 12 of 16 original-large optimization layouts, so arbitrary route tracing could not be assumed safe. A training-only `certified-route-progress-v1` reward was implemented, with unchanged physics and observations and no runtime route bypass. It trained 32,768 transitions entirely on the original large room and reached **0/8 development goals**, with 1 collision and 7 timeouts. Mean final distance was 37.1256 and mean idle fraction 0.20549. Training had 0 goals, 3 collisions and 7 timeouts. Cumulative use reached 483,328.

### Guided navigation v1 to v4

Guided runs used a 3D teacher that couples horizontal and vertical velocity. The teacher completed 4 of 4 original-large training maps. The student received bounded imitation and DAgger-style corrective collection, critic initialization and low-noise PPO refinement. Neither route geometry nor teacher pose entered the policy tensors ([GUIDED_NAVIGATION.md](../planner/GUIDED_NAVIGATION.md)). Each result is listed separately.

- **Guided v1** completed 40,960 added transitions, exhausting the 524,288 cap. Final autonomous validation was **0/8 goals, 8 collisions, 0 timeouts**. PPO refinement caused 24 training collisions and no goals. The eight teacher successes are supervision, not student results ([guided-navigation-v1-results.md](../evidence/guided-navigation-v1-results.md)).
- A sensor audit of v1 found that the partition face distance of 8.3167 exceeded the 8-unit range. Moving the aperture left identical observations in all 16 counterfactuals while the teacher's actions differed. A 24-unit range with 128 beams detected 9/16 of the apertures, while a dense target-bearing scan detected 16/16. This led to sensors-v5, which adds 1,178 fan channels to the original 269 values for a total of 1,447 values ([visible-fan-v5.md](../evidence/visible-fan-v5.md)).
- **Guided v2** added 65,536 transitions, reaching the approved cumulative cap of 589,824. The teacher reached 8 goals on 32,768 transitions. The two corrective rounds reached 0 goals with 23 and 6 collisions. PPO reached 0 goals and 10 collisions. Final development validation was **0/8 goals, 4 collisions and 4 timeouts**, with mean ending distance 37.169201 and mean idle fraction 0.486032. An offline diagnosis found that teacher exposure covered only 15 optimization layouts and that actor and critic shared one GRU. This led to a separate critic memory ([guided-navigation-v2-results.md](../evidence/guided-navigation-v2-results.md)).
- **Guided v3** isolated the critic memory. Its development result was **0/8 goals, 8 collisions** ([guided-navigation-v3-results.md](../evidence/guided-navigation-v3-results.md)).
- **Guarded PPO v4** added an exact full-rollout Gaussian KL rollback with optimizer and RNG restoration. It completed 32,768 transitions. Development results before and after training were both **0/8 goals with 8 collisions**. Seven updates were accepted and nine candidates rejected ([guarded-navigation-v4-results.md](../evidence/guarded-navigation-v4-results.md)). The baseline result rejects a sole-cause account centered on PPO, since the original imitation already failed.

### Spatial neural readout v5

The spatial readout used seeded neuron-group projections along the sensory assignments. Its static prototype gave group-activity to ray-delta correlations of 0.998842 to 0.999152, with sign agreement of 100% in 15 cases and 83.3% in one. This supports testing a spatially organized readout but is not navigation evidence. The v5 worker consumed 98,304 transitions. Its student rounds reached 0 goals with 143 and then 3 collisions. Teacher fragments reached 19 goals from privileged starts. A post-save precision assertion then failed with maximum difference 0.000293; with TF32 disabled the difference fell to 6.50e-6 and reloads were identical. Development validation was **0/8 goals, 6 collisions, 2 timeouts**. Cumulative use reached 786,432 ([spatial-neural-v5-results.md](../evidence/spatial-neural-v5-results.md)).

### Neural waypoint v6

Waypoint v6 used 16,384 teacher and 65,536 student transitions (81,920 in total), 6,144 supervised updates and no PPO. Route labels were used only as training targets. The result was **0/8 goals with 8 collisions and no timeouts** on the original large rooms. Cumulative use reached 868,352 ([neural-waypoint-v6-results.md](../evidence/neural-waypoint-v6-results.md), [neural-waypoint-v6-diagnostics.md](../evidence/neural-waypoint-v6-diagnostics.md)). The diagnosis found large turn and altitude errors in the first autonomous rounds, and that 30.5% to 38.6% of the first rounds' local-point labels lay outside the dense fan.

### Panoramic sensing v7 and v8

A panoramic sensor of 1,800 rays around the body, 25 elevations, activity groups from the full graph and a circular controller was built and verified without training. The panoramic v7 run was bounded at 98,304 new transitions, 65,536 guided and 32,768 student, and 12,288 supervised updates at most. The first autonomous flight recorded 0 arrivals and 68 collisions in 16,384 transitions. The v7 run completed 98,304 transitions and saved a compatible checkpoint, but its final report failed on a path-separator lookup. Its separately recorded development score was **0/8 with 8 collisions** ([panoramic-neural-v7-results.md](../evidence/panoramic-neural-v7-results.md)).

Panorama coverage v8 added 301,056 transitions. Its 64 guide arrivals were teacher-only, and the student had none, with 15 and 30 collisions per chunk. Development result: **0/8 with 8 collisions** ([panorama-coverage-v8-results.md](../evidence/panorama-coverage-v8-results.md)).

### Directional attention, look-ahead and the rest of the two-hour window

The directional and look-ahead runs (v9 and v10) added 32,768 and 163,840 transitions. The v9 student had 0 arrivals and 36 and 31 collisions per chunk. The final look-ahead checkpoint timed out in all eight rooms, while the teacher-only and sparse-pooling diagnostics collided in all eight. Development results were **0/8** in every case ([directional-and-lookahead-results.md](../evidence/directional-and-lookahead-results.md)). Visible-plane and approach-speed inputs were checked by an invariance test to separate a visual shortcut hypothesis from the result, without claiming that shortcut to be the cause.

The final v12 run, bounded at 8,192 student transitions and 3,072 supervised updates, reached **0/8 development goals, 1 collision and 7 timeouts**. After v8 to v12, cumulative substantive use reached 1,472,512 transitions.

### The bounded two-hour window

The user extended the window by two hours with a request to pause afterwards. A watchdog recorded explicit process identities and stopped only training processes of this task, and checkpoints were saved before the soft deadline. When the window closed, all recorded original processes had finished. The work was paused with navigation unresolved and the reserved test unused. The demonstration of v12 was inspected for 40 steps and closed normally ([two-hour-navigation-results.md](../evidence/two-hour-navigation-results.md), [two-hour-navigation-plan.md](../evidence/two-hour-navigation-plan.md)).

**Tried and stopped.** A longer discount with a changed clock, the route-progress reward, an intermediate timeout correction, temporal memory, guided imitation with and without critic isolation, guarded PPO, the spatial readout, the waypoint readout, panoramic sensing, directional attention and look-ahead. Each was run with a bounded budget and each stayed at 0 goals on its development pool. Each correction was stopped at its declared result, not extended.

**Learned.** Large-room navigation did not respond to any of these corrections at the budgets used. The learned large-room result stayed at 0 in every final or development measurement that was clean. A teacher's arrivals and fitted losses do not count as student results. The most useful findings were diagnostic: the zero exposure to the original target, the discount mismatch, the clock-transfer disruption, the sensor range and the collision patterns.

**Links.** [GUIDED_NAVIGATION.md](../planner/GUIDED_NAVIGATION.md), [large-continuous-v4-plan.md](../evidence/large-continuous-v4-plan.md), [large-continuous-v4-pause.md](../evidence/large-continuous-v4-pause.md), [large-timeout-diagnosis.md](../evidence/large-timeout-diagnosis.md), [timeout-correction-pilot-v1-results.md](../evidence/timeout-correction-pilot-v1-results.md), [brain-memory-comparison-v1-results.md](../evidence/brain-memory-comparison-v1-results.md), [route-progress-correction-v1-results.md](../evidence/route-progress-correction-v1-results.md), [guided-navigation-v1-results.md](../evidence/guided-navigation-v1-results.md), [guided-navigation-v2-results.md](../evidence/guided-navigation-v2-results.md), [guided-navigation-v3-results.md](../evidence/guided-navigation-v3-results.md), [guarded-navigation-v4-results.md](../evidence/guarded-navigation-v4-results.md), [spatial-neural-v5-results.md](../evidence/spatial-neural-v5-results.md), [neural-waypoint-v6-results.md](../evidence/neural-waypoint-v6-results.md), [panoramic-neural-v7-results.md](../evidence/panoramic-neural-v7-results.md), [panorama-coverage-v8-results.md](../evidence/panorama-coverage-v8-results.md), [directional-and-lookahead-results.md](../evidence/directional-and-lookahead-results.md), [two-hour-navigation-results.md](../evidence/two-hour-navigation-results.md).

---

## Iteration 6. The explicit observed-map planner for large rooms: timeouts, paired development, planner-1.0 to 1.2

**Goal.** Solve the large-room navigation problem with an explicit planner that uses only observations, as a working demonstration and as a reference for the learned line. The planner is not a learned policy.

**Design.** The observed-map planner accumulates observed geometry and estimated motion, searches for routes through the observed map and steers the fly with proportional control. Braking follows the requested three-dimensional direction. The planner reads full-connectome activity through its readout, but it does not learn flight weights. Its decisions never enter the learned policy's observations (development journal, [NAVIGATION_RESOLUTION.md](../planner/NAVIGATION_RESOLUTION.md), [PLANNER_DEVELOPMENT.md](../planner/PLANNER_DEVELOPMENT.md)).

The problem history is recorded in detail in [NAVIGATION_RESOLUTION.md](../planner/NAVIGATION_RESOLUTION.md). Before the planner, the learned large-room attempts had not reached the goal. Learning, perception and readout corrections did not produce reliable large-room arrivals (see the summary table in [RESULTS.md](../results/RESULTS.md)). The earlier observed-map candidates v43 and v44 reached 5/8 each, without collisions, but stable motion readout alone did not remove every blockage.

### Planner-1.0 (`v55`)

The baseline observed-map planner, now named planner-1.0, reached **8/8 on the reused optimization maps** (25,168 checks). Its frozen prospective development cohort, seeds 8500000 to 8500015, reached **13/16 goals (81.25%) with zero collisions and three timeouts**, Wilson 95% interval 57.0–93.4%. These seeds were fixed before the run ([observed-map-v55-results.md](../evidence/observed-map-v55-results.md)). The planner is the operational demonstration for large rooms, and it is not a learned movement result.

### Timeout diagnosis and the first correction (`v56`)

The three prospective timeouts were reproduced. Two ended at the 12,000-expansion search cap and the third found a route but did not finish. The diagnosis separated search saturation, frontier selection, route oscillation, odometry error, conservative occupancy and insufficient remaining time. The experimental `planner-1.0.1-exp.1` corrected an observed-free goal-margin blockage in room 8500011, which reached the goal at step 1,939. Rooms 8500012 and 8500013 still timed out, and both versions had zero collisions. The checks used 21,204 physical transitions. The cap alone was not established as a fix ([planner-timeouts-v56-results.md](../evidence/planner-timeouts-v56-results.md)).

### Adaptive recovery (`v57` to `v60`)

Four bounded checks on the three known failures followed. Higher cruise speed (`v57`) reached 2/3. Broad observed-free margins (`v58`) removed search saturation but reached only 1/3. Their unconditional combination (`v59`) reached the room 12 goal but regressed room 13 (2/3). The adopted `v60` activates broader clearance only after a capped search, and reached all three known failures with no collisions or timeouts (`planner-1.1`). The four checks used 41,226 physical transitions and no training. Recovery appeared only in room 12 ([planner-followup-v57-v60.md](../evidence/planner-followup-v57-v60.md)).

### Paired development

On the fresh paired cohort 9500000 to 9500015, with frozen planner-1.0 and planner-1.1, the results were **12/16 for planner-1.0 and 14/16 for planner-1.1, with no collisions**. Twelve rooms succeeded in both arms, two only in planner-1.1 and two in neither. Both arms used 55,680 physical transitions. The Wilson 95% interval for planner-1.1 is 64.0–96.5%. The source, layout, graph and alias checks passed ([planner-v60-development-results.md](../evidence/planner-v60-development-results.md)). This result does not establish the independent-final 80% target.

### Distance semantics, momentum and the readout (`v61` to `v65`)

A near-field audit found 104 zero-speed samples that were false stops, identified against raw sensor auditing. `v61` (`planner-1.2-exp.1`) cancelled recurrence in every range coordinate and kept 5% in the panoramic closing speeds. On the fresh paired cohort 10000000 to 10000015, it regressed to **13/16 with two collisions and one timeout**, against planner-1.1's **15/16 with one collision**. Thirteen rooms succeeded in both arms, two only in planner-1.1 and one in neither ([planner-v61-development-results.md](../evidence/planner-v61-development-results.md), [planner-readout-v61-v63.md](../evidence/planner-readout-v61-v63.md)).

`v62` (prefix persistence) and `v63` (ray-consistent interpolation) still timed out in the retained detour room. `v64` (`planner-1.2-exp.4`) added momentum braking, which corrected the known contacts and reached all four known goals. On the paired cohort 11000000 to 11000015 it regressed to **12/16 against planner-1.1's 15/16** ([planner-momentum-v64-results.md](../evidence/planner-momentum-v64-results.md)).

`v65` (`planner-1.2`) separated contextual mapping from clean neural ranges for braking. It reached 4/4 known collision and control goals, reached the stationary room 9500001 at step 1,782 and still timed out in the retained detour 9500014. On the paired cohort 13000000 to 13000015 it tied planner-1.1 at **15/16 with zero collisions and one timeout**, identical in both arms. Each arm used 55,984 physical steps ([planner-dual-v65-results.md](../evidence/planner-dual-v65-results.md), [planner-v65-development-results.md](../evidence/planner-v65-development-results.md)). The tie is not evidence of superiority.

Offline inspection of the two remaining failures showed continuing movement, small estimated pose error, repeated reference-direction reversals and mostly unknown or ambiguous final route points: 25 of 39 in room 9500014 and 27 of 43 in room 13000013. These findings are clues for a successor, not proven causes.

### Controller naming

The public planner names became numbered revisions (`planner-1.0`, `planner-1.1`, `planner-1.2`), with experimental sub-numbers. The historical aliases `v55` to `v65` remain accepted, and [CONTROLLER_VERSIONS.md](../planner/CONTROLLER_VERSIONS.md) records the complete mapping. Frozen controller code, original checkpoints and historical records keep their identifiers. The migration passed 389 regression tests ([VERSIONING.md](../planner/VERSIONING.md)).

### Publication work in the same period

The public README was reorganized around the task-specific learned results, the large-room failure-to-planner progression and reproducible geometry previews, with an MIT project license and separate CC BY 4.0 attribution for the dataset. The navigation-resolution report was translated into English at the user's request, with formulas, tables, hashes and the separation of planner results from learned-policy results preserved. These documentation changes did not train or evaluate any policy ([PUBLICATION.md](../operations/PUBLICATION.md)).

**Tried and stopped.** Higher cruise speed alone, broad clearance alone, their unconditional combination, route persistence, ray-consistent interpolation, clean ranges alone, momentum braking alone, and the earlier readout variants each failed at least one gate on the paired or known cases. Those variants are kept as separate revisions with their measured outcomes.

**Learned.** A planner that accumulates observed geometry and handles three-dimensional braking can reach 13/16 to 15/16 in prospective large-room cohorts without collisions. Paired cohorts showed that most corrections trade one case for another. The explicit planner is not evidence for the learned objective.

**Links.** [NAVIGATION_RESOLUTION.md](../planner/NAVIGATION_RESOLUTION.md), [PLANNER_DEVELOPMENT.md](../planner/PLANNER_DEVELOPMENT.md), [CONTROLLER_VERSIONS.md](../planner/CONTROLLER_VERSIONS.md), [VERSIONING.md](../planner/VERSIONING.md), [observed-map-v55-results.md](../evidence/observed-map-v55-results.md), [planner-timeouts-v56-results.md](../evidence/planner-timeouts-v56-results.md), [planner-followup-v57-v60.md](../evidence/planner-followup-v57-v60.md), [planner-v60-development-results.md](../evidence/planner-v60-development-results.md), [planner-readout-v61-v63.md](../evidence/planner-readout-v61-v63.md), [planner-v61-development-results.md](../evidence/planner-v61-development-results.md), [planner-momentum-v64-results.md](../evidence/planner-momentum-v64-results.md), [planner-dual-v65-results.md](../evidence/planner-dual-v65-results.md), [planner-v65-development-results.md](../evidence/planner-v65-development-results.md).

---

## Iteration 7. Maze contract, opening diagnostics and the room-aware planner series (planner-1.3), maze closure

**Goal.** Extend the observed-map planner from large rooms to the maze preset, which has eight partitions, four dead-end branches and a 64 × 64 × 20 extent.

**Contract.** Room-aware decoding replaced the hard-coded large-room goal diagonal and altitude and grid limits. The fixed graph and readout were unchanged. Planner-1.3 candidates are declared for the maze contract, while frozen planner-1.0 to 1.2 support only large rooms ([MAZE_NAVIGATION.md](../planner/MAZE_NAVIGATION.md)).

**Retained cases and fresh cases.** Every maze experiment was judged on eight retained maze layouts (16000000 to 16000007) and, when it passed the retained gate, on a fresh eight-layout development suite. The development rule was at least 7 of 8 goals with zero collisions. Retained layouts became correction data after they had been inspected, so later results on them are not independent.

### Development sequence

- **Exp.1 to exp.7.** Room-aware decoding (exp.1) corrected one retained large failure but timed out in the other. Exp.4 (opening references, sample-aware clustering, tall observed surfaces and completed-plane memory) corrected both retained large failures, at 3,343 and 2,056 steps, without changing deadlines or geometry. Both actual maze retries still timed out. Relaxed wall candidates regressed both maze flights and exposed a diagonal false-fit unit failure.
- **Exp.8.** Clean occupancy from neural ranges produced the first actual maze arrival, layout 14000000 at 5,441 steps with no collision. Layout 14000001 timed out at 6,352 steps, 11.54 units from its goal.
- **Exp.9 (large launcher).** Faster clean-map cruise (3 units) and tight speed (1 unit) passed all six retained large cases and all eight fresh large cases with zero collisions and zero timeouts. The fresh suite used 25,160 physical transitions in 281.83 seconds with 0.547 GiB peak memory. Wilson 95% interval 67.6–100%. This met the large-room development gate. Exp.9 failed both retained maze cases. It remains the large launcher.
- **Exp.10 and exp.11.** Exp.10 recovered the stationary maze case but only one of two retained goals. Exp.11 center refinement reached both retained maze goals, at 6,630/6,736 and 6,028/6,352 decisions. Its fresh eight-layout check reached **5/8 goals with zero collisions and three timeouts**, failing the 7/8 rule. Exp.11 is the current maze launcher.
- **Exp.12 to exp.19.** Goal-priority targets (exp.12) reached 6/8 retained and failed the gate. A finer 0.4 unit grid with a one-voxel buffer (exp.13) reached 0/8 with all timeouts and was rejected. A surface fallback (exp.14) reached 0/8 with one collision and was rejected. Confined higher speed (exp.15) and visit-pressure costs (exp.16) each reached 4/8 and were rejected. Clean initial-beacon alignment (exp.17) reached 5/8 and regressed one success. Observed-clearance opening references (exp.18) reached 5/8 and regressed one case. Neural-ray visible-goal handover (exp.19) reached 6/8 with zero collisions.
- **Exp.20 and exp.21.** Each reached 6/8 on the retained layouts, with zero collisions and two timeouts (16000001 and 16000004 still failed). Neither met the 7/8 rule.
- **Numerical repeatability.** A probe that reset the full graph and replayed identical inputs found feature differences up to 4.77e-7. A deterministic-algorithms probe still differed (5.36e-7). Ordered CSR accumulation with deterministic `index_add_` produced bit-identical features and neuron states on the full graph, 167,184 neurons and 25,583,622 edges. This was a repeatability measure for this runtime, not a guarantee across hardware and not a navigation result ([RESULTS.md](../results/RESULTS.md), "Repeatable full-connectome execution").
- **Exp.22.** The repeatable readout run stopped at its declared 30-minute wall limit with five goals and three unfinished flights after 47,528 physical transitions. The unfinished episodes were not counted as timeouts.
- **Exp.23.** Segmented CSR sums over the full graph, with a new readout fingerprint, completed all eight retained flights: six goals, zero collisions and two timeouts (16000001 at 6,562 decisions, 8.75 units away; 16000004 at 7,006 decisions, 24.24 units away). It used 56,048 physical transitions in 1,268.79 seconds and failed the 7/8 criterion.
- **Exp.24.** A wall survey that fits a broad blocking surface, sweeps along it and reverses direction fixed both exp.23 failures but regressed 16000003 and 16000000 to timeouts. It reached six goals and was rejected.
- **Exp.25.** Clearance-aware goal handover, which requires no non-saturated short or panoramic endpoint inside the braking corridor before handing to the goal, fixed a braking deadlock (16000001) while preserving all six exp.23 successes. The retained check reached **7/8 goals with zero collisions**, passing the retained gate. The fresh eight-layout check then reached **5/8 goals (62.5%) with zero collisions and three timeouts**, Wilson 95% interval 30.6–86.3%, and failed the gate. Exp.25 was not promoted.
- **Exp.26 to exp.31.** A distant-opening candidate (exp.26) reached 6/8. A progress-gated wall scan (exp.27) regressed to 4/8. A scan-initiation gate (exp.28) kept 6/8 but missed the gate. Coverage-directed recovery (exp.29) reached 6/8. Releasing unreachable crossings (exp.30) regressed to 5/8 and was rejected. A consensus filter on completed surfaces (exp.31) fixed one timeout but regressed another, reaching 6/8.
- **Exp.32.** Restricting the consensus filter to the final approach (distance no greater than a quarter of the initial goal distance) reached **7/8 goals with zero collisions** on the retained layouts. The earlier-map regression on layouts 16000000 to 16000007 then reached **7/8 with zero collisions** and preserved all seven exp.25 successes. Layout 16000004 remained a timeout.

### Closure

At the user's request no further maze candidates or fresh suites were run in this iteration. The fresh runner was disabled pending new explicit authorization. Exp.32 passed its retained checks but was not freshly verified or inspected in the renderer, and it was not promoted. The default maze launcher remains exp.11. The closing summary is in [maze-wrap-up.md](../evidence/maze-wrap-up.md). Maze reliability is an open objective, not an achieved one.

**Tried and stopped.** Finer grids, wider surface fallbacks, speed increases, visit pressure, goal-priority targets, a progress-only wall scan, a crossing release and the consensus filter without the final-approach limit were each rejected by their measured outcomes.

**Learned.** The maze failures concentrated in opening discovery and in the handover from a visible opening to the goal, not in pose drift (estimated pose error at the final sampled decision was about 0.00045). Every candidate that fixed one timeout tended to regress another success. Exp.11 and exp.25 each reached both or all retained cases and then 5/8 on their fresh suites, which is why the retained gate alone was not treated as a result.

**Links.** [MAZE_NAVIGATION.md](../planner/MAZE_NAVIGATION.md), [maze-wrap-up.md](../evidence/maze-wrap-up.md), [maze-navigation-development-results.md](../evidence/maze-navigation-development-results.md), [maze-opening-range-results.md](../evidence/maze-opening-range-results.md), [maze-clearance-fresh-results.md](../evidence/maze-clearance-fresh-results.md), [planner-timeouts-v56-results.md](../evidence/planner-timeouts-v56-results.md), [RESULTS.md](../results/RESULTS.md).

---

## Iteration 8. Architectural scenes and planner-1.4, the original-objective check

**Goal.** Test the planner on architectural scenes. The learned line had not trained on these scenes before Iteration 9. Build six scenes (office, apartment, street, atrium, warehouse and courtyard), each with start and goal situations, and check them against the original objectives.

**Built.** Six original synthetic architectural drafts (revision 0.2) were prepared with outward-facing OBJ and MTL meshes, collision JSON, hashes, floor plans and inspection previews. Twenty-one situations were geometrically checked. Reference routes clear a 0.16 m body radius plus a 0.20 m margin. These routes are geometric references, not dynamically executable flight claims. The scenes are original, not reconstructions of real buildings ([ARCHITECTURAL_SCENES.md](../methods/ARCHITECTURAL_SCENES.md)).

Public world, environment and known-dimension planner adapters were implemented with 49 focused tests. A full-graph CUDA smoke ran 48 physical transitions across six scenes with finite actions and features, no collisions and zero optimizer updates. Viewer integration followed, with scene and situation selection, a separate brain window and archive integrity checks.

### Initial original-objective check

The initial check on all 21 situations, with the original starts, goals and deadlines, reached **18/21 goals with zero collisions and three timeouts**. It used 11,829 full-connectome physical transitions in 386.97 seconds after initialization and 0.592 GiB peak allocated VRAM. No training or reserved test was used ([architectural-initial-navigation-results.md](../evidence/architectural-initial-navigation-results.md), [ARCHITECTURAL_NAVIGATION.md](../planner/ARCHITECTURAL_NAVIGATION.md)).

### Escape candidate (exp.2)

Exp.2 reached 18/21 with zero collisions. It fixed the warehouse aisle route but regressed one apartment success, so it was not promoted ([architectural-escape-candidate-results.md](../evidence/architectural-escape-candidate-results.md)).

### Planner-1.4-exp.3

Exp.3 reached **19/21 goals with zero collisions and two timeouts**, in 11,017 transitions and 377.032 seconds. It preserved every exp.1 success and fixed the warehouse aisle route. The bathroom and atrium climbs remained unresolved. The demo kept exp.1 pending further verification ([architectural-closing-results.md](../evidence/architectural-closing-results.md)).

**Tried and stopped.** The recovery variants in exp.2 were not promoted because they regressed a case. The architectural planner work stopped at exp.3 as the iteration's closing candidate, with unresolved failures recorded.

**Learned.** Scene-level results are inspected development evidence, not independent real-world generalization. The planner transfers reasonably to the new scenes. After exp.3 the remaining failures were the bathroom and atrium climbs.

**Links.** [ARCHITECTURAL_SCENES.md](../methods/ARCHITECTURAL_SCENES.md), [ARCHITECTURAL_NAVIGATION.md](../planner/ARCHITECTURAL_NAVIGATION.md), [architectural-initial-navigation-results.md](../evidence/architectural-initial-navigation-results.md), [architectural-escape-candidate-results.md](../evidence/architectural-escape-candidate-results.md), [architectural-closing-results.md](../evidence/architectural-closing-results.md), [architectural-fullgraph-integration.md](../evidence/architectural-fullgraph-integration.md).

---

## Iteration 9. Autonomous learning restart: PPO pilots and architectural curricula (structured, balanced, mixed), closing results

**Goal.** Make a learned controller that chooses its own flight actions without a planner, portal detection or hand-written recovery, on the architectural scenes. The planner becomes a reference or a possible teacher, never the evaluated student's actions ([AUTONOMOUS_LEARNING.md](../learning/AUTONOMOUS_LEARNING.md)).

**Built.** `learned-architecture-1.0-exp.1` is a freshly initialized PPO actor and critic. It consumes nine frames of neural features from the complete graph through a learned frame encoder and a GRU. The actor outputs the existing four coordinated flight actions. The graph is not optimized. The goal input is the existing synthetic goal direction and distance; the learner does not discover goals from vision. The checkpoint contract records the graph fingerprint, readout, sensor version, history dimensions, flight dynamics and `planner_assistance=false`.

A 128-transition, one-update CUDA smoke passed with finite losses, changed parameters and deterministic reload, in 4.44 seconds after initialization. It verifies the learning pipeline, not navigation.

### Pilot 1

The first pilot used 131,072 fresh PPO transitions, seed 42, 512-step rollouts, five PPO epochs and 128-sample minibatches. It cycled 32 chunks of 4,096 transitions through 15 training situations across the six scenes. Each scene's last situation was withheld and checked before and after training. The pilot reached **0 goals in 457 training episodes and 0/6 validation goals before and after**, with five collisions and one timeout on final validation. Reload passed and no model was promoted ([autonomous-architecture-pilot-1-results.md](../evidence/autonomous-architecture-pilot-1-results.md)).

### Pilot 2 (structured representation)

The second pilot changed only the representation to `learned-architecture-1.0-exp.2`: learned circular convolutions over the three neural panorama channels, a separate near-body encoder, recurrent history and direct access to the 13 neural goal and state coordinates. It applied no goal-to-action formula. The first CUDA smoke failed because adaptive pooling backward was incompatible with deterministic CUDA; fixed-size average pooling preserved the mode and a repaired smoke passed. Pilot 2 used 131,072 transitions with the same tasks, seed and rules as pilot 1 ([autonomous-architecture-pilot-2-results.md](../evidence/autonomous-architecture-pilot-2-results.md)).

Deterministic validation improved from **0/6 to 1/6 goals**: the office succeeded, the courtyard collided and the apartment, street, atrium and warehouse timed out. Validation shares scene geometry with training, so it is not independent generalization. Losses were finite, reload matched and aliases were unchanged.

### Curriculum 1 (stage-wise lessons)

The training-only goal curriculum added short lessons at 1, 2, 4 and 8 metres, with the original goal restored at the final stage. Availability was audited on CPU before training. The body-clear endpoints were found at 1, 2 and 4 m in all 45 samples per distance. At 8 m the audit found 39 of 45, and both apartment training starts failed on all three seeds, so the common stage order was reduced to 1, 2 and 4 m followed by the original task ([architectural curriculum availability](../evidence/autonomous-architecture-curriculum-1-results.md)).

A mastery gate required two consecutive disjoint rounds in which each training task reached at least six goals in eight completed episodes. The first curriculum pilot (131,072 transitions) remained at 1 metre: one round failed and one passed, and the second passing round was incomplete. Lesson training recorded 2,429 goals in 2,776 episodes. Original-goal validation reached **1/6 (apartment), five collisions and no timeouts**. This did not preserve the office success of pilot 2. Lesson successes are adaptive training evidence, not independent validation ([autonomous-architecture-curriculum-1-results.md](../evidence/autonomous-architecture-curriculum-1-results.md)).

### Curriculum 2 (balanced)

The second curriculum used balanced exposure with 131,072 fresh PPO transitions. It reached the 2 metre lessons after two complete passing 1 metre rounds, but its original-goal validation was **0/6 with six collisions and no timeouts**. Lesson progress therefore did not resolve complete-route navigation ([autonomous-architecture-curriculum-2-results.md](../evidence/autonomous-architecture-curriculum-2-results.md)).

### Mixed curriculum

The next runner alternates original training goals with nearby lessons, continuing PPO and curriculum state from the previous checkpoint. It was verified with eight CPU tests and a full-connectome 128-transition smoke. No substantial mixed training was run in this iteration. A budget had to be agreed first ([MIXED_AUTONOMOUS_CURRICULUM.md](../learning/MIXED_AUTONOMOUS_CURRICULUM.md)).

**Tried and stopped.** The two PPO pilots, the stage-wise curriculum and the balanced curriculum each gave 0 to 1 original-goal validation successes on six situations. The work paused at the user's request after the balanced result, with the next step being a review of task scheduling and original-goal exposure.

**Learned.** The learning pipeline works end to end: finite losses, reload and protected aliases. Navigation on the architectural scenes is not learned. Lesson performance and original-goal performance are different measurements, and the second is the one that counts.

**Links.** [AUTONOMOUS_LEARNING.md](../learning/AUTONOMOUS_LEARNING.md), [MIXED_AUTONOMOUS_CURRICULUM.md](../learning/MIXED_AUTONOMOUS_CURRICULUM.md), [autonomous-architecture-pilot-1-results.md](../evidence/autonomous-architecture-pilot-1-results.md), [autonomous-architecture-pilot-2-results.md](../evidence/autonomous-architecture-pilot-2-results.md), [autonomous-architecture-curriculum-1-results.md](../evidence/autonomous-architecture-curriculum-1-results.md), [autonomous-architecture-curriculum-2-results.md](../evidence/autonomous-architecture-curriculum-2-results.md), [autonomous-large-completion-protocol.md](../evidence/autonomous-large-completion-protocol.md).

---

## Iteration 10. Zero-shot program begins: recovery and hash verification of the historical medium-room policies, transfer experiments 1 to 8, regression suite

**Goal.** Start the zero-shot program ([ZERO_SHOT_PLAN.md](ZERO_SHOT_PLAN.md)) by recovering the learned reference behind the earlier 70% to 80% medium-room results, verifying it, and then testing transfer to partitioned maps.

### Recovery and replay

All historical winners were recovered from preserved checkpoints. Each checkpoint and metadata hash matched the hash recorded when its single final test ran, and the original aliases were unchanged ([HISTORICAL_REFERENCE.md](../experiments/reference-recovery/HISTORICAL_REFERENCE.md)). The table records these winners:

| Experiment | Final result | Collisions | Timeouts | Lifetime transitions |
| --- | --- | ---: | ---: | ---: |
| Warm-start sensor comparison (v2) | 50/64 (78.1%) | 5 | 9 | 360,448 |
| Observed-ray risk comparison | 48/64 (75.0%) | 16 | 0 | 131,072 |
| Near-goal curriculum comparison | 45/64 (70.3%) | 15 | 4 | 131,072 |
| Original coordinated dense launcher | 43/64 (67.2%) | 11 | 10 | 327,680 |
| Fresh sensor comparison | 35/64 (54.7%) | 20 | 9 | 131,072 |

The three top checkpoints were replayed on their recorded validation pools with the current code: 23/32, 27/32 and 27/32, and every per-episode outcome matched (32/32 each). Source drift in `learning.py` and `dense_training.py` affects continued training but not evaluation.

### Transfer ladder

The frozen historical checkpoints were evaluated without training on new development seeds (800000 and above, 16 episodes per cell). These seeds are development observations, not tests:

- The observed-ray v3 checkpoint reached 12/16 on the original medium room and 12/16 on the `open` profile, but 0/16 on `passages` (7 collisions, 9 timeouts, mean final distance about 20 m of 28 m) and 0/16 on `large` (4 collisions, 12 timeouts).
- The warm-start v2 checkpoint reached 11/16 on the original medium room and 0/16 on `large` (2 collisions, 14 timeouts).

The reference solves medium rooms and fails when mandatory partitions appear. The failure is a task-capability gap, not a loading, scaling or physics regression. Sixteen episodes give wide intervals, so these numbers are indicative only ([HISTORICAL_REFERENCE.md](../experiments/reference-recovery/HISTORICAL_REFERENCE.md)).

### Transfer experiments 1 to 8

Eight bounded experiments continued the recovered reference toward partitioned maps. Every protocol was committed before training, and the reserved pools were not used ([TRANSFER_SUMMARY.md](../experiments/reference-recovery/TRANSFER_SUMMARY.md)).

| Experiment | Change | Best partitioned-map result | Medium rooms | Outcome |
| --- | --- | --- | --- | --- |
| T1 | Retained 48/64 policy and a fresh control on `passages`, 65,536 transitions | passages 0/32 | 24/32 retained, 11/32 fresh | No candidate |
| T2 | Route-progress reward, and separately 262,144 transitions | passages 0/32 | fell to 17/32 | No candidate |
| T3 | Graded single and double gates from the 50/64 policy | gate-long 32/32, gate-two 28/32, passages-wide 4/16 | 19/32 | Rejected (medium) |
| T4 | Medium share 50%, passages-wide in the mix | passages-wide 6/32 | 24/32 | Positive |
| T5 | `passages` in the mix | passages-wide 26/32, passages 2/32 | 22 to 23/32 | Not positive |
| T6 | Intermediate profile `passages-mid` | passages-mid 12/32 | 23 to 26/32 | Not positive, unstable |
| T7 | Profiles mixed inside every update | passages-mid 15/32, passages 4/32 | 26/32 | One episode short of positive |
| T8 | 262,144 transitions, two seeds | no gain | 16 to 25/32 | Negative |

Experiment 7 selected its checkpoint from several noisy evaluations on pools it also reports, so its numbers are optimistic. Plain PPO at a constant learning rate oscillated on this policy: performance on a profile moved by 20 episodes or more between checkpoints 65,536 transitions apart, and experiment 8 lost the experiment 7 gains. No candidate met the release gate.

### Regression suite

A frozen medium-room regression suite was defined with four pools and five baseline checkpoints. The historical winners scored 90 to 98 of 128. Experiment 7's start scored 111 and the pilot candidate 104. The first per-pool rule failed two historical winners and was relaxed in the open, with the change recorded ([MEDIUM_REGRESSION_SUITE.md](../methods/MEDIUM_REGRESSION_SUITE.md)). Every later candidate was checked against this suite.

### Storage cleanup

Regenerable raw datasets, 84.5 GB in total, were removed so that the run directory fell from 87 GB to 1.9 GB ([RUNS_CLEANUP.md](../operations/RUNS_CLEANUP.md)).

**Tried and stopped.** Transfer by graded gates, route-progress rewards, longer training and intermediate profiles were each tested once and did not hold their gains across seeds or budgets.

**Learned.** The reference is real and traceable, and medium rooms are solved at roughly the historical rate. Partitioned rooms are not, and the gains that did appear in transfer were not stable under more training and a second seed.

**Links.** [HISTORICAL_REFERENCE.md](../experiments/reference-recovery/HISTORICAL_REFERENCE.md), [TRANSFER_SUMMARY.md](../experiments/reference-recovery/TRANSFER_SUMMARY.md), [REFERENCE_TRANSFER_RESULTS.md](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS.md), [REFERENCE_TRANSFER_RESULTS_8.md](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_8.md), [PASSAGES_FAILURE_CLASSIFICATION.md](../experiments/reference-recovery/PASSAGES_FAILURE_CLASSIFICATION.md), [MEDIUM_REGRESSION_SUITE.md](../methods/MEDIUM_REGRESSION_SUITE.md), [RUNS_CLEANUP.md](../operations/RUNS_CLEANUP.md).

---

## Iteration 11. Held-out specification, variance study, stabilization (Phase 1) and memory (Phase 3) screening and replication

**Goal.** Define what counts as an unseen map, measure how much a training recipe varies between runs, and test a stabilized trainer and a memory window against that variance.

### Held-out specification

The unseen-map levels were fixed in advance. Level B is a sealed parameter region (narrower openings and other parameters the generator never produced in training). Level C is a sealed family of synthetic architectural scenes. The reserved seeds were fixed, and a five-test check confirmed that the level C geometry equals the protected world ([HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md)).

### Phase 1 pilot

A stabilization bundle was implemented. The first launch used 28 parallel evaluations, which restarted the machine; a resource guard (`scripts/resource_guard.py`) was added afterwards. The pilot, on one seed with 98,304 transitions, reached passages-mid 21/32, passages 5/32 and passages-wide 12/32, a fall on the wide profile ([PHASE1_PILOT_RESULTS.md](../experiments/variance-and-stability/PHASE1_PILOT_RESULTS.md)).

### Phase 1 run

Two seeds with four evaluations each. Seed 442 was stable (range 1 episode) and seed 443 was not (range 18). The hardest profile was not raised. The Phase 1 exit criterion was **not met** ([PHASE1_RUN_RESULTS.md](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md)).

### Variance study (R1)

Five training runs of the Phase 1 recipe (seeds 501 to 505, 98,304 added transitions each) were evaluated on seven selection cells and on regression pools A and B, with 32 episodes per cell. Passages-wide ranged over 11 episodes (12 to 23), above the decision rule's threshold of 10. Passages-mid ranged over 6 and passages over 2. All five runs passed the amended regression suite. None reached 20/32 on passages-mid ([VARIANCE_STUDY_RESULTS.md](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md)).

The best run by the hard-profile sum (seed 505) and the pilot checkpoint were then evaluated on a fresh pool, seeds 880000 to 880063, with 64 episodes per cell:

| Checkpoint | Passages-wide | Passages-mid | Passages | Medium |
| --- | --- | --- | --- | --- |
| Seed 505 | 41/64 (64%) | 17/64 (27%) | 2/64 (3%) | 55/64 (86%) |
| Pilot candidate | 14/64 (22%) | 37/64 (58%) | 17/64 (27%) | 57/64 (89%) |

The pilot candidate is a real outlier on passages-mid, not a measurement fluke, and it gives up passages-wide to get the harder profiles. The rule adopted from this study was that every later comparison needs at least three seeds and 64 episodes per cell, with candidates chosen by best-of-N on a selection pool and reported on a separate pool. The confirmation was added after seeing the five results and is labeled as such.

### Memory screening and replication (Phase 3)

The memory screen compared two history windows on seed 442. The long window was +19 on the hard-profile sum and the short window was worse ([PHASE3_SCREENING_RESULTS.md](../experiments/variance-and-stability/PHASE3_SCREENING_RESULTS.md)). The replication on seed 443 gave +5, -9 and 0 against the control, so the gain **did not replicate** ([PHASE3_REPLICATION_RESULTS.md](../experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md)).

### Evaluation repeatability

Repeating the pilot checkpoint's evaluation gave results within one episode, so evaluation noise is about one episode per 32. Training varies much more ([VARIANCE_STUDY_RESULTS.md](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md)).

**Tried and stopped.** The stabilization bundle held one seed and not the other, so Phase 1's exit criterion was not met. The history window did not replicate, so Phase 3 closed as not established.

**Learned.** Training-to-training spread is the dominant noise. A single run cannot establish a difference smaller than about 10 episodes of 32. This rule governed every later comparison.

**Links.** [HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md), [PHASE1_PILOT_RESULTS.md](../experiments/variance-and-stability/PHASE1_PILOT_RESULTS.md), [PHASE1_RUN_RESULTS.md](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md), [VARIANCE_STUDY_RESULTS.md](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md), [PHASE3_SCREENING_RESULTS.md](../experiments/variance-and-stability/PHASE3_SCREENING_RESULTS.md), [PHASE3_REPLICATION_RESULTS.md](../experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md).

---

## Iteration 12. Randomized map sampler, the random-distribution run (R5), committee reviews and diagnostics

**Goal.** Train on randomly drawn maps with adaptive difficulty, then find out why the policy fails on the partitioned profiles.

### Sampler

A map sampler with declared parameter ranges and an adaptive difficulty controller was implemented, with 14 tests and a sample gallery. No generation failure occurred in 600 resets, and a reset takes at most 0.05 seconds ([MAP_SAMPLER.md](../methods/MAP_SAMPLER.md)).

### Random-distribution run (R5)

Three seeds (601 to 603) trained 98,304 added transitions each from the experiment 7 checkpoint, against five variance-study runs as control. The positive rule required a margin of at least 8 episodes of 64 on both the d = 0.9 random cell and level B development. The margins were **+1.1 and +0.6**, so the result was negative. The difficulty controller stayed at 0.2 to 0.25, so training saw mostly easy maps. No run solved hard random maps: the best scored 6/64 on d = 0.9 and 5/64 on level B. Run 601 was selected by the rule and scored 32/32 on passages-wide, 19/32 on passages-mid and 7/32 on passages. It was an outlier and was not confirmed by the rule ([RANDOM_DISTRIBUTION_RESULTS.md](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md)).

A fresh 64-episode evaluation of run 601 gave medium 92%, passages-wide 86%, passages-mid 55% and passages 14%: the first checkpoint that kept medium, wide and mid together. Sampled actions raised the pilot's passages-wide from 14 to 55 of 64, so deterministic and sampled evaluations disagree ([COMMITTEE_EVAL_RESULTS.md](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md)).

### Diagnostics

- **Light audit.** The randomized simulators finished 64 to 127 episodes in a whole run. An ideal route follower beat hovering at every route point, which refutes the idea that the reward favors hovering ([LIGHT_AUDIT_RESULTS.md](../experiments/diagnostics/LIGHT_AUDIT_RESULTS.md)).
- **Collision anatomy.** Passages collisions ended 1.5 to 3.5 m off the certified route, around mid-route. Edge clips were rare. This does not separate exposure from information ([COLLISION_ANATOMY.md](../experiments/diagnostics/COLLISION_ANATOMY.md)).
- **Feature probe.** The 256 pooled features matched raw sensors within 5 degrees in 16 of 16 pairs, but decoded the route direction only to 45 to 53 degrees on hard samples, against 90 degrees for guessing. The readout was not the lever ([FEATURE_PROBE.md](../experiments/diagnostics/FEATURE_PROBE.md)).
- **Sensing probes.** With 700 synthetic maps the 8 m rays decoded the route direction to about 34 degrees on the hard subset, and 24 m rays to about 28 degrees. The rollout probes were too small to decide. This pointed to a learning problem rather than a sensor limit for passages ([SENSING_PROBES.md](../experiments/diagnostics/SENSING_PROBES.md)).
- **Privileged waypoint.** Giving the actor the route direction as an input lifted passages from 11 to 37.5 of 64 (threshold 40) on two seeds each. This is a partial result and a diagnostic, not a student, because a student cannot read the certified route ([WAYPOINT_DIAGNOSTIC_RESULTS.md](../experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md)).

Three committee reviews were conducted, and the diagnostics together located the failure in the information available at decision time, not in the reward or the readout. That was the working conclusion of this iteration.

**Tried and stopped.** The reward-hovering hypothesis was refuted by the route-follower audit. The readout change was ruled out as the main lever by the feature probe.

**Learned.** Random training did not help the hard cells. Route direction is the information that matters for partitioned rooms, and a learned policy in this setup does not recover it from its sensors.

**Links.** [MAP_SAMPLER.md](../methods/MAP_SAMPLER.md), [RANDOM_DISTRIBUTION_RESULTS.md](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md), [COMMITTEE_EVAL_RESULTS.md](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md), [LIGHT_AUDIT_RESULTS.md](../experiments/diagnostics/LIGHT_AUDIT_RESULTS.md), [COLLISION_ANATOMY.md](../experiments/diagnostics/COLLISION_ANATOMY.md), [FEATURE_PROBE.md](../experiments/diagnostics/FEATURE_PROBE.md), [SENSING_PROBES.md](../experiments/diagnostics/SENSING_PROBES.md), [WAYPOINT_DIAGNOSTIC_RESULTS.md](../experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md).

---

## Iteration 13. Autonomous students: auxiliary head, privileged critic, supervised pretraining (all negative)

**Goal.** Test whether a route signal available only during training helps an autonomous actor, either as an auxiliary prediction target, as a privileged critic input or through supervised pretraining of the actor trunk.

### Auxiliary head and privileged critic

Seven new training runs of 262,144 added transitions each started from the experiment 7 checkpoint: three auxiliary-head runs, three privileged-critic runs and one control, plus the two earlier controls re-evaluated on the same pool. All nine checkpoints were evaluated on pool 882000 ([AUXILIARY_STUDENT_RESULTS.md](../experiments/students/AUXILIARY_STUDENT_RESULTS.md)).

On passages, deterministic, the control mean was 12.3/64, the auxiliary mean 14.7/64 (+2.3) and the privileged-critic mean 13.0/64 (+0.7). The negative line was +6 and the positive line +12, so both arms were negative by the frozen rule. Runs of each arm fell inside the control range. With sampled actions the auxiliary arm gained +6.3 (17.0 against 10.7), a difference the frozen rule does not use as its primary metric. The actor-reads-the-route diagnostic reached 36 and 39 on a different pool, and the students did not move toward it.

### Supervised pretraining

The actor trunk was pretrained on 512 maps by supervised imitation of the route direction, with a 45-degree gate. The gate passed at 41.6 degrees and the learned behavior was kept. PPO on top of the pretrained trunk, over three seeds, gave passages +2.0 of 64 against the control, which is negative ([PRETRAIN_RESULTS.md](../experiments/students/PRETRAIN_RESULTS.md), [PRETRAIN_PROTOCOL.md](../experiments/students/PRETRAIN_PROTOCOL.md)).

**Tried and stopped.** Training-only route signals at 262,144 transitions were closed: the auxiliary head, the privileged critic and supervised pretraining each failed their rule.

**Learned.** A better representation of the route direction does not translate into steering under PPO. The trunk can encode the direction, but the policy does not use it to avoid collisions in these budgets.

**Links.** [AUXILIARY_STUDENT_PROTOCOL.md](../experiments/students/AUXILIARY_STUDENT_PROTOCOL.md), [AUXILIARY_STUDENT_RESULTS.md](../experiments/students/AUXILIARY_STUDENT_RESULTS.md), [PRETRAIN_PROTOCOL.md](../experiments/students/PRETRAIN_PROTOCOL.md), [PRETRAIN_RESULTS.md](../experiments/students/PRETRAIN_RESULTS.md), [critic-history-diagnosis.md](../evidence/critic-history-diagnosis.md), [input-group-readout-diagnosis.md](../evidence/input-group-readout-diagnosis.md).

---

## Iteration 14. Training budget: 1M, 2M, three-seed replication, level B and level C measurement

**Goal.** Test whether a larger training budget is the lever for `passages`, then check whether any gain reaches the held-out levels B and C.

### B1: 1M transitions, one seed

The pilot recipe was trained for 1,015,808 added transitions on seed 801. Its learning curve was measured at 98k, 295k, 590k and 1M, on new pool 884000. The result was **inconclusive by the frozen rule**: `passages` 23 of 64 against a positive line of 24 (negative at 16 or fewer). The deterministic curve was 11, 12, 17 and 23. Medium scored 55 to 60 and passages-mid 48. Passages-wide and gate-two reached 64. Collisions on passages stayed at 18 to 30 ([LARGE_BUDGET_RESULTS.md](../experiments/large-budget/LARGE_BUDGET_RESULTS.md)).

### B2: 2M transitions, one seed

The same recipe was trained for 1,998,848 added transitions on seed 801 and evaluated on new pool 885000. Its `passages` score was **38 of 64 with 6 collisions**. On the same pool the 1M checkpoint scored 27 with 20 collisions. Medium scored 54 and passages-mid 56. The deterministic curve was 16, 26, 48 and 38. The drop from 48 to 38 came from timeouts. The rule was positive for this single seed ([LARGE_BUDGET_2M_RESULTS.md](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md)).

Two pools are involved: the 1M checkpoint scored 23 on pool 884000 and 27 on pool 885000. The two pools differ, so these numbers are not a paired comparison of the 1M and 2M checkpoints. The 2M comparison on pool 885000 is the one the record reports against the 1M checkpoint.

### B3: three-seed replication

Seeds 851 and 901 trained the same 2M recipe, with seed 801 re-evaluated, on the fresh pool 886000. Stage 61 `passages` results were **42, 36 and 39 of 64 (mean 39, start checkpoint 5)**. Passages-mid was 54 to 57, medium 49, 54 and 55. Collisions were 8, 16 and 8 against a gate of 3. The rule was positive ([REPLICATION_2M_RESULTS.md](../experiments/large-budget/REPLICATION_2M_RESULTS.md)).

### B4: level B and level C

Level B (held-out sampler, difficulty 0.8, 64 episodes on pool 950000) gave **26, 17 and 12 of 64 (mean 18.3, positive needed 20; start 1)**. The rule was inconclusive. Level C (architectural scenes, 168 headings across six scenes) gave **95, 108 and 108 of 168 (mean 103.7, positive needed 88; start 71)**. The rule was positive. Level C gains came from street-block (12 to 32 to 40 of 40) and warehouse (10 to 17 to 24 of 32), with office-floor at 10 to 16 of 24. Apartment (7 to 8 of 24) and atrium (8 to 9 of 24) did not move. Courtyard regressed: the start scored 24 of 24 and the trained seeds 7, 23 and 17 ([LEVEL_BC_RESULTS.md](../experiments/large-budget/LEVEL_BC_RESULTS.md)).

**Tried and stopped.** The budget curve was extended once to 2M and replicated on three seeds. Further budget was not used for the level B measurement, which was measured once.

**Learned.** Budget is a real lever for passages at this scale, with a large seed spread and collisions still above the gate. The level B result fell short of its threshold by 1.7 episodes of mean. The level C gain is uneven across scenes, so it is not a general architectural result.

**Links.** [LARGE_BUDGET_PROTOCOL.md](../experiments/large-budget/LARGE_BUDGET_PROTOCOL.md), [LARGE_BUDGET_RESULTS.md](../experiments/large-budget/LARGE_BUDGET_RESULTS.md), [LARGE_BUDGET_2M_PROTOCOL.md](../experiments/large-budget/LARGE_BUDGET_2M_PROTOCOL.md), [LARGE_BUDGET_2M_RESULTS.md](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md), [REPLICATION_2M_PROTOCOL.md](../experiments/large-budget/REPLICATION_2M_PROTOCOL.md), [REPLICATION_2M_RESULTS.md](../experiments/large-budget/REPLICATION_2M_RESULTS.md), [LEVEL_BC_PROTOCOL.md](../experiments/large-budget/LEVEL_BC_PROTOCOL.md), [LEVEL_BC_RESULTS.md](../experiments/large-budget/LEVEL_BC_RESULTS.md).

---

## Iteration 15. Connectome control (C1.0 to C1.2, edge-shuffled reservoir) and the planner reference (C1.P)

**Goal.** Ask whether the real connectome wiring matters, by comparing it with an edge-shuffled reservoir trained under the same recipe, and then measure the explicit planner on the same level C headings.

**Design.** Predeclared ablations: the edge-shuffled control permutes edge targets (shuffle seed 1), so the graph keeps its size and edge count but not its wiring. Both arms start from random weights. Each stage is evaluated on medium, `passages`, `passages-mid`, `passages-wide`, level B and level C ([CONNECTOME_CONTROL_PROTOCOL.md](../experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL.md)).

### C1.0: fresh medium-room competence

Phase 1 of the fresh chain used 884,736 transitions of medium rooms, seed 1001 and pool 887000. The real arm reached **61/64** deterministic (gate 40) and the edge-shuffled arm **54/64** on the same pool. Sampled results were 59 and 60. The retained start scored 55 on that pool. A gap of 7 episodes with one seed is not separable. The chain was valid ([CONNECTOME_CONTROL_RESULTS_C10.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md)).

### C1.1: the hard cells at 2.88M transitions

Two seeds per arm (1001 and 1051) trained two phases, 2.88M transitions in total, and were evaluated on `passages`, `passages-mid`, `passages-wide`, medium, level B and level C. The chain check **failed**: the real arm reached 16.0 of 64 on `passages` against 28 needed, while the retained checkpoints reached 36 to 42. The shuffled arm was not worse. On `passages` it reached 25.5 against 16.0 for the real arm. On `passages-mid` it reached 51.0 against 41.5, on level B 6.5 against 5.5 and on level C 86 against 79 of 168. With one seed per arm these differences are inside the seed spread ([CONNECTOME_CONTROL_RESULTS_C11.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md)).

### C1.2: 4.88M transitions

The four C1.1 runs were extended by 61 stages to 4,882,432 transitions each, with the B2 recipe. The chain check **failed by half an episode**: the real mean on `passages` was 27.5 of 64 against the needed 28, the shuffled mean 21.0 and the retained mean 38.0. Other cells were: `passages-mid` real 51.0 against shuffled 47.0; level B 9.5 against 12.0; level C 98.0 against 105.5. Within each arm the two seeds differed by 13 (real) and 16 (shuffled) episodes on `passages`, as much as the difference between arms. No cell showed an advantage of the real connectome. Settling the question at this effect size would take about eight seeds per arm ([CONNECTOME_CONTROL_RESULTS_C12.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md)).

### C1.P: the planner reference on level C

The planner-1.4-exp.3 controller was run on 168 level C headings (the same headings as the learned measurement) and on fresh `large` (pool 892000) and `maze` (pool 893000) pools with 32 episodes per cell. It reached **147 of 168 on level C (87.5%; 4 collisions and 17 timeouts)**, 43 above the learned candidate's mean of 103.7. The retained learned candidate reached 2, 0 and 0 of 32 on `large` and 0, 0 and 0 of 32 on `maze`, mostly timeouts. The four-family gate was not met in any family ([PLANNER_REFERENCE_RESULTS.md](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md)). This comparison shows the learned line trails the planner on these families, and it is not a learned result.

**Tried and stopped.** The connectome comparison was run at two budgets (2.88M and 4.88M) and did not settle the question. Further comparison would require about eight seeds per arm, and that comparison was not run.

**Learned.** The real connectome and the shuffled reservoir were indistinguishable within measured uncertainty on every cell. The project therefore cannot claim that the real connectome improves or is necessary for navigation. The planner reference is far ahead of the learned candidate on level C, and the learned candidate has no meaningful success on `large` and `maze`.

**Links.** [CONNECTOME_CONTROL_PROTOCOL.md](../experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL.md), [CONNECTOME_CONTROL_RESULTS_C10.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md), [CONNECTOME_CONTROL_PROTOCOL_C11.md](../experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C11.md), [CONNECTOME_CONTROL_RESULTS_C11.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md), [CONNECTOME_CONTROL_PROTOCOL_C12.md](../experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C12.md), [CONNECTOME_CONTROL_RESULTS_C12.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md), [PLANNER_REFERENCE_PROTOCOL.md](../experiments/connectome-control/PLANNER_REFERENCE_PROTOCOL.md), [PLANNER_REFERENCE_RESULTS.md](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md).

---

## Iteration 16. Consolidation (this documentation reorganization, brief)

**Goal.** Make the repository readable: one current status, one experiment index, a history of earlier plans, and a published narrative that stands alone.

**Changes.** The documents were moved into topic folders with every link and path rewritten: `docs/overview` (architecture, data, completion and zero-shot plans, this history, the glossary), `docs/methods` (formulas, sensors, map families, the brain, protocols and generators), `docs/planner` (planner development and maze, architectural and guided material), `docs/learning` (autonomous learning and diagnosis), `docs/experiments` (one folder per experiment family, with protocols, results and a catalog), `docs/results` (the consolidated findings and the key-numbers tables), `docs/operations` (commands, reproduction, verification, publication), `docs/reference` and `docs/evidence` (small tracked evidence files, now indexed). New documents were written for the whole record: this history, [FINDINGS.md](../results/FINDINGS.md), [KEY_NUMBERS.md](../results/KEY_NUMBERS.md), the experiment catalog, the evidence and script indexes, the reproduction guide, the map and brain guides and the glossary. Report figures were generated from the recorded results and the geometry code (`scripts/make_report_figures.py`). The README was rewritten around what exists, what was tried, what was best and where to read more. The index is [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md), one row per experiment in order, and the live status is [ROADMAP.md](../../ROADMAP.md). The earlier roadmap is preserved in [ROADMAP_HISTORY.md](../../ROADMAP_HISTORY.md). Historical run artifacts and checkpoints keep their identifiers, so earlier results can still be traced.

**Current status.** The release gate (at least 52 of 64 successes and at most 3 collisions in each of four families, with intervals and matched controls) is **not met**. The learned line is strongest on single openings (61/64 on the gate-long pool) and medium dense rooms (49 to 55 of 64 for the 2M seeds), reaches about 60 percent on `passages` after the 2M budget (36 to 42 of 64), transfers partly to the architectural family (95 to 108 of 168) and has no meaningful success on `large` and `maze`. The planner reference reaches 147 of 168 on level C. The connectome's contribution is not shown. The decision taken after the planner reference was to consolidate and write up before any further training; the short paper, the long paper and the extended academic report are planned from these documents, and one more training step aimed at collisions or at `large` and `maze` remains open.

**Learned.** The project's most reliable findings are the negative and diagnostic ones: finite losses and teacher arrivals are not navigation, seed spread is larger than most effects, deterministic and sampled evaluation can disagree, and a route-direction input helps but cannot be read by a real student.

**Links.** [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md), [ROADMAP.md](../../ROADMAP.md), [ROADMAP_HISTORY.md](../../ROADMAP_HISTORY.md), [ZERO_SHOT_PLAN.md](ZERO_SHOT_PLAN.md), [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md), [PUBLICATION.md](../operations/PUBLICATION.md), [VERIFICATION.md](../operations/VERIFICATION.md), [REFERENCES.md](../reference/REFERENCES.md), [README.md](../../README.md).

---

## Threads that run through the whole project

**Seed variance.** Training runs from the same start differ by up to 11 to 18 episodes on one profile (Iteration 11, Iteration 14, Iteration 15). Single-run differences under about 10 episodes of 32 are not results. Most later comparisons were made with two or three seeds, and the rule that a comparison needs at least three seeds and 64 episodes per cell came from the variance study.

**Deterministic and sampled evaluation.** The same checkpoint can score very differently under deterministic and sampled actions (for example, 14 deterministic and 55 sampled on passages-wide in Iteration 12). One seed in the connectome control had a hover fixed point visible only in deterministic mode (Iteration 15). Protocols since then declare the mode and report both where possible.

**Development and final pools.** Development pools were used for selection and for diagnosis. Final pools were opened once for a frozen candidate, and each opened pool is then consumed. Several results in this history use consumed pools, and a tuned candidate needs a new pool. The pool registry is in [the roadmap](../../ROADMAP.md#8-pools-registry).

**Teacher and student.** Planner arrivals, teacher arrivals in guided runs, and lesson successes in curricula are never counted as autonomous student navigation. Each is reported in its own column.

**Negative results.** Each negative result was recorded with the same detail as a positive one, including the zero-success geometry comparison (Iteration 4), the guided and memory failures (Iteration 5), the route-direction diagnostics (Iteration 12), and the connectome control that did not settle the question (Iteration 15).

**Warm starts and fresh starts.** Warm-start and fresh-start comparisons were kept apart. The warm-start 50/64 result, the fresh 35/64 result and the warm-start and fresh arms of the geometry comparison are not directly ranked (Iteration 3, Iteration 4).

**Versioned contracts.** Sensor versions (v2 to v6), readout fingerprints, planner revisions (planner-1.0 to planner-1.4 and its experiments), map profiles, and checkpoint contracts are versioned. A checkpoint loads only with its declared contract. Changing a contract requires a new version, a migration and its own evaluation.

**Protected artifacts.** Launcher aliases, source files and original checkpoints were hashed before and after each experiment. The repeated statement across the records is that the protected hashes matched and no alias was promoted without a declared decision.

**Modeled activity, not biology.** The connectome is used as a fixed reservoir with engineered sensory projection and readout. Local sensitivities and correlations are modeled values, not measured neural firing. No experiment in this history establishes a biological benefit.

**Budgets.** Budgets were stated in added transitions per run and in cumulative substantive use. The first authorized cap was 524,288 transitions, and later authorized corrections raised cumulative use past it (Iteration 5). Budget extensions were recorded rather than made silently, and stops were recorded at the declared points.

**Visual and diagnostic evidence.** Renders, traces and figures were inspected and labelled as diagnostic. A figure made from retained records does not establish a new result.

**Honesty rules.** Failed launches, interrupted runs, reported defects and rejected candidates stayed in the record. Where a rule was adjusted after results, the adjustment was labelled as such, for example the relaxed per-pool rule in the regression suite (Iteration 10), and a labelled confirmation added after seeing results (Iteration 11).

**Open items at the end of the record.** The release gate of 52 of 64 successes with at most 3 collisions per family is not met. Large-room and maze reliability are open. A new untouched pool and an explicit budget are required for any tuned final claim. The write-up (short paper, long paper, extended report) comes next, and one more training step aimed at collisions or at the large and maze families remains open.
