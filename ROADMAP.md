# Roadmap

The full-connectome controller, procedural 3D rooms, anatomical inspection, recording, replay and bounded experiment tools are implemented. This roadmap describes proposed work; it does not start another training run.

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

## Improve navigation in structured rooms

Use retained validation failures to distinguish collision, altitude, passage and stopping errors. Test one intervention at a time under a declared budget with repeated initialization seeds. Progressive profiles allow a comparison between direct training on difficult rooms and a mixture of easier and harder rooms. A curriculum is a hypothesis whose benefit must be measured.

The target remains at least 80% success on a declared independent final suite, with counts, confidence intervals, collisions, timeouts and compute reported. A point estimate on one small suite does not demonstrate general robustness. Test outcomes must not select checkpoints or curriculum settings.

## Extend map complexity

The available progression is `open`, `passages`, `large` and `maze`. Future geometry can vary openings, required turns, altitude changes and branches while preserving reachable goals and explicit clearance checks. Difficulty should reflect these properties rather than obstacle count alone.

Retain easier examples during training to limit loss of earlier skills. Assess generalization on layouts and distributions separated from training. Add moving obstacles, wind, sensor noise and delay as subsequent versions once static navigation is understood.

## Proposed navigation interventions

Start with retained validation trajectories to identify passage collisions, idle flight and failed detours. The next geometry proposal inserts intermediate tasks: an open room, one wall with a wide opening and nearby goal, then longer routes, multiple turns and changes in altitude before the existing large rooms. Change one difficulty dimension at a time. Advance using a separate training-practice pool and retain easier examples; validation and final pools must not drive the schedule. This design is proposed, not implemented or measured.

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
