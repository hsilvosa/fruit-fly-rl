# Roadmap

The observed-map planner v55 now navigates `large` rooms: 8/8 arrivals on reused optimization maps and 13/16 in prospective development, without collisions and with three development timeouts. This is explicit planning from full-connectome activity, not a learned movement policy. Student v34 retains its 3/8 result; reliable learning remains unresolved. The [results and limits](docs/evidence/observed-map-v55-results.md) distinguish the two. Original aliases and the reserved test remain intact.

The [resolution history](docs/NAVIGATION_RESOLUTION.md) explains the original problem, learning and perception attempts that were insufficient, corrected blockages, and the final solution. The operational improvement combines observed-map memory, correct reference advancement, and braking in the requested three-dimensional direction; it does not turn the planner's 13/16 into a PPO result.

Next steps are to reduce the planner's three timeouts and check the corrected version on another prospective sample, then use observed trajectories to supervise a student while separating planner arrivals from learned-model arrivals. Any version tuned using development failures requires new maps to measure generalization. Do not expand to `maze` before checking size contracts and navigation. The target of 80% on an independent test with uncertainty remains open; 13/16 has a lower confidence bound near 57%.

The full-connectome controller, procedural 3D rooms, anatomical inspection, recording, replay and bounded experiment tools are implemented. This roadmap describes proposed work; it does not start another training run.

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0-5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

The [post-v2 controller diagnosis](docs/evidence/critic-history-diagnosis.md) records teacher-to-student distribution errors, actor degradation after PPO and a verified option to isolate critic memory gradients. The matched 65,536-transition experiment completed with 0/8 goals and eight collisions on original-large development validation. [Frozen comparison](docs/evidence/guided-navigation-v3-plan.md) records the scope.

## Improve navigation in structured rooms

The [zero-success diagnosis](docs/GEOMETRY_DIAGNOSIS.md) puts single-opening navigation and training-practice mastery ahead of further map expansion. The earlier controller still reproduced its outcomes in four retained original validation rooms. The latest curriculum advanced without any successful passage training episode, and its overall selection retained initialization. Establish a usable passage controller and a declared failure outcome for zero-success selection before another large comparison.

Use retained validation failures to distinguish collision, altitude, passage and stopping errors. Test one intervention at a time under a declared budget with repeated initialization seeds. Progressive profiles allow a comparison between direct training on difficult rooms and a mixture of easier and harder rooms. A curriculum is a hypothesis whose benefit must be measured.

The target remains at least 80% success on a declared independent final suite, with counts, confidence intervals, collisions, timeouts and compute reported. A point estimate on one small suite does not demonstrate general robustness. Test outcomes must not select checkpoints or curriculum settings.

## Extend map complexity

The available progression is `open`, `passages`, `large` and `maze`. Future geometry can vary openings, required turns, altitude changes and branches while preserving reachable goals and explicit clearance checks. Difficulty should reflect these properties rather than obstacle count alone.

Retain easier examples during training to limit loss of earlier skills. Assess generalization on layouts and distributions separated from training. Add moving obstacles, wind, sensor noise and delay as subsequent versions once static navigation is understood.

## Proposed navigation interventions

The corrected [practice-mastery v2](docs/GEOMETRY_CURRICULUM.md#corrected-practice-mastery-protocol) implements a nearby single-opening task, then a longer room with the same opening and box count. It advances only after two withheld training-practice batches pass, retains easier tasks and records failure when no trained target candidate succeeds. Physical passage checks and the 128-transition full-graph optimizer smoke pass; navigation was subsequently measured in the bounded comparison. The completed passage experiment selected baseline seed 42 with 61/64 final goals, no collisions and three timeouts on one wide opening. The curriculum was weaker in validation and seed 73 never left the first stage. Next, diagnose retained validation and practice failures before introducing a second wall or narrower opening under a newly declared budget and final pool. [Verified results](docs/evidence/passage-mastery-v2-results.md) keep this simpler task separate from the failed large-room comparison.

Review reward and temporal credit together. Current Euclidean progress can discourage the initial part of a necessary detour. With a 0.05-second decision interval and discount 0.995, distant rewards are strongly attenuated. A bounded comparison could test a longer horizon or [potential-based shaping](https://people.eecs.berkeley.edu/~russell/papers/icml99-shaping.pdf), including correct terminal handling. Any use of hidden geometry in a training reward must be disclosed and excluded from policy inputs. Such a change needs a versioned objective and cannot be inferred to improve navigation from its formula alone.

A small learned recurrent output policy could retain observed openings and branches while still consuming connectome features. The existing fixed recurrent graph is not evidence that useful long-term spatial memory has been learned. [Recurrent reinforcement learning for partial observations](https://arxiv.org/abs/1507.06527) motivates this hypothesis; it does not validate this controller. Compare it with the current output policy under matching interfaces and declared budgets.

These proposals require their own implementation checks and bounded experiments. The completed geometry comparison is not authorization to start them or extend training.

## Measure route quality

Report arrival time and flown distance alongside success. Successful routes can be compared with the clearance-aware visibility roadmap, which supplies an approximate feasible geometric path. Failed flights remain separate, and missing references must be reported. The reference is neither a global optimum nor a dynamically executable trajectory.

## Improve neural inspection and replay

Add anatomical replay from recorded full-neuron snapshots with correct before/after-action phases and episode boundaries. Extend selectable traces, exports and region summaries. Do not reconstruct unsaved neuron values from pooled features or fabricate missing anatomical coordinates.

## Strengthen operational reliability

Improve exact resumption to include random generators, curriculum, partial episodes and recurrent state. Current checkpoint resume starts fresh episodes. Extend snapshot checksums and measure achieved simulation speed in the viewer. Broader physical keyboard, focus and multiple-window QA remains useful.

Keep journals, launch records, full evidence and machine-specific paths private. Public documentation should explain behavior, equations, protocols and aggregate results. Publication checks must cover the exported source tree, its links and excluded files.

## Test the connectome's contribution

Compare the real graph with randomized wiring, disconnected recurrence and a conventional controller under comparable sensors, budgets, initialization seeds and selection rules. Navigation results alone cannot establish a biological advantage. Visual perception, internal synaptic plasticity and more realistic aerodynamics require separate designs and evidence.

See [public results](docs/RESULTS.md), [mathematics](docs/MATHEMATICS.md), [map protocol](docs/GEOMETRY_CURRICULUM.md) and [verification](docs/VERIFICATION.md).


The earlier [critic-isolation v3 run](docs/evidence/guided-navigation-v3-results.md) and subsequent guarded corrections did not resolve original large-room navigation. Their checkpoints and evidence remain available; those experiments are no longer running.


## Panoramic correction and waypoint v6 result

The waypoint v6 batch completed 81,920 new transitions, with finite losses and compatible reload, but autonomous validation on original `large` rooms remained at 0/8: eight collisions and no timeouts. Completed substantive training totals 868,352 transitions. Original aliases and the source checkpoint remain intact. The reserved test was not used, and navigation remained unresolved at this stage.

The [verified results](docs/evidence/neural-waypoint-v6-results.md) and [control and coverage diagnosis](docs/evidence/neural-waypoint-v6-diagnostics.md) are retained. The next correction uses panoramic vision measured around the body and complete guided flights from original states. Its controller receives only neural activity; the hidden route labels data only during training.
The [panoramic v7 protocol](docs/evidence/panoramic-neural-v7-plan.md) sets a limit of 98,304 new transitions, 12,288 supervised updates, and a single development validation. It starts a new controller because dimensions change, preserves all previous checkpoints, and does not consume the reserved test.

The [coverage correction within the two-hour limit](docs/evidence/two-hour-navigation-plan.md) continues on the original large maps. First, the student will be measured without guidance on reused development maps. If it keeps failing, navigation will remain unresolved and work will pause on October 4 at 22:40:52 Madrid time. Only a frozen candidate meeting prior criteria could enter the independent protocol; the test will not be consumed to diagnose failures.

## Completion of the panoramic corrections

Batches v8, v9, v10, and v12 finished and added 505,856 transitions. The latest autonomous assessment on reused development maps reached 0/8 goals, with one collision and seven timeouts. Completed substantive training totals 1,472,512 transitions. Navigation in the original large maps remained unresolved; the reserved test was not used and original aliases were not promoted. The [two-hour window report](docs/evidence/two-hour-navigation-results.md), its checkpoints, and experimental launcher `launch-panorama.ps1` are retained. Work paused at the requested deadline, October 4 at 22:40:52 Madrid time.
