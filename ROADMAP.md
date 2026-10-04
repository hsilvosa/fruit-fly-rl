# Roadmap

Original-large navigation remains unresolved. The [guided initialization](docs/evidence/guided-navigation-v1-results.md) achieved 0/8 autonomous validation goals, all failures by collision. Its teacher successes are separate training outcomes. The existing cumulative 524,288-transition budget is exhausted; all original aliases and reserved final tests remain preserved.

A [perception diagnosis and sensors-v5 correction](docs/evidence/visible-fan-v5.md) found early teacher actions that require information absent from the short-range observations. The new dense visible scan resolves the tested aperture ambiguities and reaches the full-connectome brain features. Code, CUDA activity, demo recording and replay are verified; navigation benefit is not yet measured. The authorized 65,536-transition sensors-v5 correction completed on 2026-10-04. Autonomous validation on the original large maps reached 0/8 goals, four collisions and four timeouts; navigation remains unresolved. Cumulative substantive use is 589,824. The source, all original aliases and reserved final tests remain preserved. [Verified v2 results](docs/evidence/guided-navigation-v2-results.md) separate teacher outcomes from autonomous flights.

The full-connectome controller, procedural 3D rooms, anatomical inspection, recording, replay and bounded experiment tools are implemented. This roadmap describes proposed work; it does not start another training run.

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0Ã¢â‚¬â€œ5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

The [post-v2 controller diagnosis](docs/evidence/critic-history-diagnosis.md) records teacher-to-student distribution errors, actor degradation after PPO and a verified option to isolate critic memory gradients. The user-authorized matched 65,536-transition experiment is running on original-large navigation; no isolated-memory navigation result exists yet. [Frozen comparison](docs/evidence/guided-navigation-v3-plan.md) records the scope.

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
