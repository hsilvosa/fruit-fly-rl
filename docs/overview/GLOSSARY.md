# Glossary

Terms used across the documentation, in alphabetical order. Each entry gives a short definition and a link to where the term is defined or most fully used. Numbers are the values in the code unless a document is named.

**Aperture.** The opening through a partition, given by `aperture_width` and `aperture_height` in a profile. Openings alternate across the room in both horizontal position and altitude. See [MAPS.md](../methods/MAPS.md#profile-table) and `map_profiles.py`.

**Architectural scene.** One of six original synthetic buildings or streets (`office-floor`, `apartment`, `street-block`, `atrium`, `warehouse`, `courtyard`), with 21 situations in total. Used as level C. See [MAPS.md](../methods/MAPS.md#architectural-scenes-level-c) and [ARCHITECTURAL_SCENES.md](../methods/ARCHITECTURAL_SCENES.md).

**Archive.** A recorded flight: telemetry, actions, sensors and features saved in chunks. Inspected with `inspect` and rebuilt with `recover`. See [COMMANDS.md](../operations/COMMANDS.md#archive-analysis-and-recovery).

**Approach reading.** One of the 128 sensor values per ray: the ray direction dotted with the world velocity, divided by 3. It tells the policy whether the fly is closing on a surface. See [BRAIN.md](../methods/BRAIN.md#sensor-versions).

**Body radius.** The fly's collision radius, 0.16. Every collision test inflates boxes by this amount. See [MAPS.md](../methods/MAPS.md#geometry-rules) and `world.py`.

**Brain.** The fixed MaleCNS reservoir plus its sensor mapping and pooling, as a class (`Brain` in `connectome/brain.py`). It contains no learned parameters. See [BRAIN.md](../methods/BRAIN.md#the-reservoir-update).

**Branch (dead-end branch).** A side wing of a partitioned room with a single doorway, used in the `maze` profile (four branches). The doorway is the only entry; the other sides are closed by neighboring partitions and the room wall. See [MAPS.md](../methods/MAPS.md#profile-table).

**Certified route (reference route).** A collision-clear polyline through every opening, computed when a layout is generated (`world.reference_route`). It is used for generation, geometry checks, evaluation references and training rewards only. It is never in the policy's observations. See [MAPS.md](../methods/MAPS.md#geometry-rules) and [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md).

**Chain check.** A pre-declared gate on the first arm of a fresh training chain, which must reproduce a known result before the arms can be compared. In connectome control stage C1.1 and C1.2, the fresh real arm had to score at least 28/64 on `passages`. Both stages failed it, so their comparison is not used to speak about the retained lineage. See [CONNECTOME_CONTROL_RESULTS_C11.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md) and [C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md).

**Chunk.** A saved block of an archive or of a long training run, used to split work into resumable pieces. See [COMMANDS.md](../operations/COMMANDS.md#archive-analysis-and-recovery).

**Clearance (route clearance).** The extra distance kept between the certified route and the boxes, beyond the body radius. It is 0.25 for most profiles, 0.22 for `large`, and 0.18 for `maze`. Profiles accept values from 0.05 to 0.35. See [MAPS.md](../methods/MAPS.md#profile-table).

**Collision.** A step in which the fly's swept path meets a box inflated by the body radius, or leaves the room bounds inflated by the radius. It ends the episode with reward -5 and `success = False`. See [MAPS.md](../methods/MAPS.md#geometry-rules) and `world.py` (`FlightWorld.step`).

**Connectome.** The wiring diagram of the neurons and synapses, here the MaleCNS v1.0 release. Used as the fixed recurrent matrix. See [DATA_AND_MODEL.md](../overview/DATA_AND_MODEL.md) and [BRAIN.md](../methods/BRAIN.md#data-source).

**Coordinated dynamics.** The flight model that reduces lateral acceleration, favors forward motion, smooths yaw and derives visible bank and pitch. The other option is `legacy`. See [FLIGHT_AND_NEURONS.md](../methods/FLIGHT_AND_NEURONS.md).

**Decision (decision step).** One policy action, applied for a fixed 0.05 s (`DT`). A decision is the unit of episode limits and of reward. See [MATHEMATICS.md](../methods/MATHEMATICS.md).

**Deterministic vs sampled evaluation.** Deterministic evaluation applies the actor's mean action. Sampled evaluation draws the action from the actor's Gaussian. Training always samples. A policy can behave differently in the two modes, so both are reported where relevant. See [MATHEMATICS.md](../methods/MATHEMATICS.md#ppo-what-is-optimized) and [CONNECTOME_CONTROL_RESULTS_C10.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md).

**Development pool.** A seed set used for progress checks and design decisions. Its results may be inspected. It cannot choose a checkpoint on its own terms after it has informed a change, and a pool that has informed a design is no longer independent. See [HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md) and [GENERALIZATION_AND_ROUTES.md](../methods/GENERALIZATION_AND_ROUTES.md).

**Dense rooms.** The original medium task: 32 x 32 x 12 m, 48 boxes, 1,200-decision limit (`dense-v3`). See [DENSE_ROOMS.md](../methods/DENSE_ROOMS.md).

**Dual readout.** A feature set that keeps contextual map coordinates separate from clean distance ranges, so the braking logic uses only literal ranges. Used by planner-1.2 and later. See [BRAIN.md](../methods/BRAIN.md#readout-variants) and [MATHEMATICS.md](../methods/MATHEMATICS.md).

**Edge-shuffled reservoir.** The control graph in which each edge's target is reassigned by one random permutation. It keeps every source's out-degree and weights, every target's in-degree, and the weight distribution, and changes only who connects to whom. See [BRAIN.md](../methods/BRAIN.md#the-edge-shuffled-control) and `connectome/shuffled.py`.

**Episode.** One flight from reset to termination (success or collision) or truncation (timeout). See [MAPS.md](../methods/MAPS.md#geometry-rules).

**Episode limit.** The maximum number of decisions in one episode. For generated profiles it is `max(60, 2 L / 1.5 + 15)` seconds, where `L` is the certified route length, converted to decisions. The `dense-v3` limit is 1,200 and the legacy small room is 600. See [MAPS.md](../methods/MAPS.md#geometry-rules).

**Family.** A group of maps reported together for the release gate: the medium dense rooms, the large rooms, mazes and the architectural scenes. Each family has its own outcome count, collision limit and interval. See [PROJECT_COMPLETION.md](../overview/PROJECT_COMPLETION.md) and [MAPS.md](../methods/MAPS.md#what-each-family-means-for-the-release-gate).

**Fan rays (sensor v5).** 589 rays fanned around the observed target bearing (31 azimuths by 19 elevations, range 24). They are synthetic goal-direction vision, not the certified route or aperture. See [BRAIN.md](../methods/BRAIN.md#sensor-versions).

**Feature (pooled feature).** One of 256 numbers that summarize the neural activity in one bucket, normalized by the square root of the bucket size. These are the policy's input in the default readout. See [BRAIN.md](../methods/BRAIN.md#the-reservoir-update).

**Fingerprint.** A string that identifies a graph, a sensor contract, a readout or a suite. Checkpoints and suites refuse to load when fingerprints differ. See [BRAIN.md](../methods/BRAIN.md#checks-before-use) and `learning.py`.

**Fresh chain.** A training chain started from random weights rather than from the retained lineage, with the same total budget. Used as a control so that the connectome is not confounded with the history of the retained policy. See [CONNECTOME_CONTROL_PROTOCOL.md](../experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL.md).

**Gate.** A pre-declared pass/fail rule that must hold before the next step is allowed. Examples: the release gate (52 of 64 per family), the medium regression suite (17 of 32 per pool) and the practice gate (at least seven of eight goals in two batches). See [PROJECT_COMPLETION.md](../overview/PROJECT_COMPLETION.md), [MEDIUM_REGRESSION_SUITE.md](../methods/MEDIUM_REGRESSION_SUITE.md) and [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md).

**Goal (target).** The point the fly must reach. It is placed at the end of the certified route. Its direction and distance are provided to the policy through the state values. See [MAPS.md](../methods/MAPS.md#geometry-rules).

**Gate-near / gate-long / gate-two.** Compact profiles with one or two partitions in a 12 or 24 m room, used as the first passage-mastery stages. See [MAPS.md](../methods/MAPS.md#profile-table).

**Held-out.** A region or family whose data the training sampler never uses. Level B is a parameter region, and level C is the architectural family. See [HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md).

**Hover fixed point.** A failure mode in which deterministic action selection makes the policy stop short of the goal and time out without a collision, while sampling the same policy often succeeds. The connectome control recorded one such case (13 deterministic successes against 27 sampled). See [CONNECTOME_CONTROL_RESULTS_C12.md](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md) and [COMMITTEE_EVAL_RESULTS.md](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md).

**Inspected pool.** A seed set whose layouts or outcomes have been looked at by the project. The original medium pools, the maze and architectural sets are all inspected. An inspected pool is never fresh evidence. See [MEDIUM_REGRESSION_SUITE.md](../methods/MEDIUM_REGRESSION_SUITE.md) and [HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md).

**Layout.** One concrete map, created from a profile and a seed. See [MAPS.md](../methods/MAPS.md#seeds-layouts-and-evaluation-pools).

**Leak.** The fraction of old activity kept each step in the reservoir update (0.5), so each new state is 0.5 old state plus 0.5 new tanh term. See [BRAIN.md](../methods/BRAIN.md#the-reservoir-update).

**Level A, B and C.** The three generalization tests in [HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md). Level A is new layouts of a trained family. Level B is a held-out parameter region (narrow openings with many partitions). Level C is the held-out architectural scene family.

**Lifetime transitions.** The total number of environment steps a checkpoint has seen, counting earlier rounds. A saved checkpoint can have zero if the selection rule kept the initial controller. See [DATA_AND_MODEL.md](../overview/DATA_AND_MODEL.md).

**Maze.** The `maze` profile: 64 x 64 x 20 m, eight partitions plus four dead-end wings. It is its own family. See [MAZE_NAVIGATION.md](../planner/MAZE_NAVIGATION.md).

**MaleCNS.** The male central nervous system connectome of *Drosophila*, release v1.0, used as the fixed graph. See [DATA_AND_MODEL.md](../overview/DATA_AND_MODEL.md) and [REFERENCES.md](../reference/REFERENCES.md).

**Map profile.** A complete set of parameters for a generated room: room size, box count, partitions, openings, clearance, endpoint separation, branches, version. Named profiles are listed in [MAPS.md](../methods/MAPS.md#profile-table). See `map_profiles.py`.

**Medium rooms.** The `dense-v3` task and the other 32 x 32 x 12 m profiles. See [DENSE_ROOMS.md](../methods/DENSE_ROOMS.md).

**Neuromere.** A segment of the central nervous system, given by the official `somaNeuromere` annotation. The brain viewer can filter by it (G). See [FLIGHT_AND_NEURONS.md](../methods/FLIGHT_AND_NEURONS.md).

**Observed-map planner.** A hand-written controller that builds a map from sensor readings and the dual neural features, then plans toward the goal. It is a reference line, not a PPO policy. See [PLANNER_DEVELOPMENT.md](../planner/PLANNER_DEVELOPMENT.md) and [CONTROLLER_VERSIONS.md](../planner/CONTROLLER_VERSIONS.md).

**Pool.** A named, frozen list of seeds used for one split (training, validation or test). Pools are stored in suite files and checked when loaded. See [GENERALIZATION_AND_ROUTES.md](../methods/GENERALIZATION_AND_ROUTES.md).

**Partition.** A wall across the room with one or more openings, built from four boxes. The `passages` profiles have three partitions; `large` has five. See [MAPS.md](../methods/MAPS.md#profile-table).

**Panorama (sensor v6).** 1,800 body-frame rays covering 25 elevations and 72 azimuths, range 24. It does not use the route or the aperture. See [BRAIN.md](../methods/BRAIN.md#sensor-versions).

**Planner.** A hand-written observed-map controller, distinct from the PPO policy. Its versions are listed in [CONTROLLER_VERSIONS.md](../planner/CONTROLLER_VERSIONS.md). Planner-1.x controllers are reference lines for the learned policy.

**Policy.** The PPO actor-critic MLP (two layers of 128 units) that maps the pooled features to four commands. The only learned component. See [BRAIN.md](../methods/BRAIN.md#ppo-policy-and-what-is-learned).

**Practice pool.** A subset of training layouts held out from optimizer rollouts and used only to decide curriculum stages in the passage-mastery protocol. See [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md).

**Privileged signal.** Information that the simulator knows but the policy does not receive: the certified route, the aperture positions, the hidden boxes and the teacher's labels. It may be used for rewards, labels, diagnostics or validation of geometry, but never as a policy input. See [MATHEMATICS.md](../methods/MATHEMATICS.md) and [GUIDED_NAVIGATION.md](../planner/GUIDED_NAVIGATION.md).

**Profile.** See *Map profile*.

**Readout.** The rule that turns neural activity into the vector the policy or planner reads: the 256 pooled features, or one of the dual or segmented readouts. Each readout has its own version string. See [BRAIN.md](../methods/BRAIN.md#readout-variants).

**Recurrent update.** The step `h(t+1) = 0.5 h(t) + 0.5 tanh(W h(t) + u(t))`, applied once per decision. See [BRAIN.md](../methods/BRAIN.md#the-reservoir-update).

**Reserved pool.** A seed set held back for a final assessment. It is not opened before the phase that names it, and once used it is consumed. See [HELD_OUT_SPEC.md](../methods/HELD_OUT_SPEC.md) and [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md).

**Reservoir.** A fixed recurrent network whose weights are not trained. Here, the MaleCNS connectome, driven by sensors and read through pooling. See [BRAIN.md](../methods/BRAIN.md#the-reservoir-update).

**Retained lineage.** The earlier training chain whose checkpoints, histories and results the project keeps and reuses (for example, the 50/64 medium reference). Its history cannot be reproduced exactly, so a fresh chain is used for controls. See [CONNECTOME_CONTROL_PROTOCOL.md](../experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL.md) and [HISTORICAL_REFERENCE.md](../experiments/reference-recovery/HISTORICAL_REFERENCE.md).

**Reward.** The per-decision signal, version `navigation-v2-progress-timeout`: `2 * (previous distance - distance) - 0.02`, plus +20 on success, -5 on collision and -5 on timeout. See [MATHEMATICS.md](../methods/MATHEMATICS.md) and `world.py`.

**Sensor version.** The declared layout of the sensor vector: v2 (269 values), v3 (269, room-scaled), v4 (270, with a remaining-time value), v5 (1,447, with fan rays) and v6 (3,869, with panorama rays). See [SENSORS_V3.md](../methods/SENSORS_V3.md) and [BRAIN.md](../methods/BRAIN.md#sensor-versions).

**Shuffled control.** See *Edge-shuffled reservoir*.

**Student.** A policy trained to imitate a privileged teacher's labels (supervised learning and a bounded data-collection loop), rather than by ordinary PPO alone. Its results are reported separately from the teacher's. See [AUXILIARY_STUDENT_PROTOCOL.md](../experiments/students/AUXILIARY_STUDENT_PROTOCOL.md) and [GUIDED_NAVIGATION.md](../planner/GUIDED_NAVIGATION.md).

**Success.** An episode ends with the fly closer than 0.45 to the goal and no collision on that step. See [MAPS.md](../methods/MAPS.md#geometry-rules) and `world.py`.

**Suite.** A file that freezes the seeds, profiles and split ranges for an experiment, with fingerprints. See [GENERALIZATION_AND_ROUTES.md](../methods/GENERALIZATION_AND_ROUTES.md) and [COMMANDS.md](../operations/COMMANDS.md#evaluation-and-frozen-suites).

**Teacher.** A privileged controller that reads the certified route and produces labels for supervised training. Teacher arrivals are training outcomes, not autonomous results. See [GUIDED_NAVIGATION.md](../planner/GUIDED_NAVIGATION.md).

**Timeout.** The episode reaches its limit without success or collision. It is a failure in every reported rate. See [MAPS.md](../methods/MAPS.md#geometry-rules).

**Tick.** The internal decision counter used against the episode limit. One tick is one decision. See `world.py`.

**Validation pool.** A seed set used to choose a checkpoint or a method before the final assessment. Validation ranks success, then fewer collisions, then lower mean ending distance. See [DENSE_ROOMS.md](../methods/DENSE_ROOMS.md) and [GEOMETRY_CURRICULUM.md](../methods/GEOMETRY_CURRICULUM.md).

**Wilson 95% interval.** The score interval for a success rate. With `n` episodes, `k` successes, `p = k/n` and `z = 1.959964`, it is the center plus or minus the margin given in [MATHEMATICS.md](../methods/MATHEMATICS.md#model-selection-and-evaluation). An observed 80% rate does not mean its lower bound is 80%. Example: 0/64 gives an interval of 0.0 to 5.7%, and 61/64 gives 87.1 to 98.4%.
