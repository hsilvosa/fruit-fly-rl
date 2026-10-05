# Roadmap

Current as of October 5, 2026. This is proposed work, not an active training schedule. New collection, optimization, or evaluation needs a declared budget and protocol. Preserve historical results, frozen controllers, and original checkpoint aliases.

## Starting point

| Capability | Current evidence | Status |
| --- | --- | --- |
| Full connectome, 3D flight, anatomical inspection, recording/replay | Implemented and checked; full graph retained | Available |
| Learned single-opening navigation | `gate-long`: 61/64 final goals, zero collisions, three timeouts; 95% interval 87.1–98.4% | Successful on that distribution |
| Learned medium dense-room navigation | Historical independent pools range from 54.7% to 78.1%; several results around 67–78% | Useful, variable performance; not interchangeable with new profiles |
| Learned structured large-room navigation | Initial final result 0/64; best recent student v34 is 3/8 on reused optimization maps | Unresolved |
| Explicit large-room planner v55 | 8/8 reused optimization; 13/16 frozen prospective development, zero collisions, three timeouts; interval 57.0–93.4% | Working demo, incomplete robustness |
| `maze`, noise, wind, moving obstacles | Geometry or proposed capabilities without verified navigation results | Future work |

The planner is the operational solution today. It has explicit map memory, bounded search, and proportional flight control, not learned movement weights. Its result does not fulfill the learned-policy objective or prove biological benefit. [Results](docs/RESULTS.md) and [resolution history](docs/NAVIGATION_RESOLUTION.md) retain the full evidence.

## Priority 1: Diagnose and resolve planner timeouts

Keep v55 frozen as the reference. Use the existing traces from rooms 8500011, 8500012, and 8500013 to separate search saturation, frontier selection, route oscillation, accumulated odometry error, conservative occupancy, and insufficient remaining flight time. The first two ended at the 12,000-expansion cap; the third found a route but did not finish. Increasing the cap alone is not an established fix.

Add bounded diagnostic plots for visited/frontier cells, map evidence, selected route references, estimated pose, commands, and remaining time. Study the relevant local failures before increasing compute or changing deadlines. Compare individual changes first, then declare any combined candidate. Preserve the physical collision checks and original room deadlines.

Completion requires reproducible diagnoses from retained data, focused regression checks for the selected fixes, and explicit reporting of all three development outcomes. Fixing known rooms establishes a correction on those rooms, not generalization.

## Priority 2: Measure the corrected planner independently

Predeclare fresh development layouts, selection rules, compute limits, and an untouched final pool. Freeze code and sensor/readout contracts before prospective measurement. Use development only for selecting versions; assess the frozen winner once on its final pool and mark that pool consumed. Do not use earlier final pools again to select changes.

Report goals, collisions, timeouts, Wilson confidence intervals, elapsed compute, peak memory, flight time, and flown distance. Compare successful routes with a feasible geometric reference while retaining failures separately. The geometric reference is not a global optimum or guaranteed executable flight.

The existing goal is at least 80% on a declared independent final suite, with uncertainty shown. The protocol must state whether that means a point estimate or a stronger confidence-bound requirement. A small point estimate alone cannot establish broad robustness. If claiming improvement over v55, use a predeclared paired comparison on the same fresh layouts, without selecting either controller from that final result.

Completion requires a frozen protocol, verified dataset/source/suite fingerprints, one final report with all failures, and an explicit conclusion about whether the stated target was met.

## Priority 3: Learn complete large-room navigation

Use the working planner as a possible demonstration source. Collect complete trajectories from original starts and varied headings, including states encountered by the student and bounded teacher recovery. Geometry used to supervise training must stay outside inference inputs. Teacher arrivals, guided collection, supervised fitting, PPO transitions, and autonomous student results need separate counters.

Start with a bounded experiment that can distinguish perception errors from route memory and control errors. Preserve the successful gate policy and medium-room references; periodically check earlier skills on development layouts rather than assuming transfer. Reject zero-success selection instead of calling initialization a successful trained model.

Possible interventions include learned output memory, longer temporal credit, potential-based shaping with correct terminal handling, and guarded PPO after imitation. These are hypotheses. The prior timeout correction already tried a longer discount and changed sensors without establishing large-room arrivals; repeating it without controlling transfer effects would not identify the cause. Test matched contracts and one intervention at a time, across repeated initializations.

Completion requires a teacher-free student that reaches large-room goals under the declared validation rule, finite and compatible optimization/reload, and a new independent final assessment. Planner arrivals cannot count toward that objective. No biological claim follows from student success alone.

## Priority 4: Increase map complexity through measured mastery

Separate geometry factors before combining them:

| Stage | Profiles or change | What to isolate |
| --- | --- | --- |
| Single opening | `gate-near` → `gate-long` | Travel distance with the same opening |
| Repeated crossings | `gate-two` → `passages-wide` | Additional walls and route memory |
| Long travel | `large-wide` | Larger room with five wide gates |
| Narrow openings | `large-narrow` | Clearance and altitude precision without extra clutter |
| Combined difficulty | `passages`, then original `large` | Narrow passages plus scattered obstacles |
| Branching routes | `maze` | Dead ends, revisits, and larger map limits |

The original `dense-v3` task remains a retained reference, not an equivalent stage of the new profiled generator. Define mastery criteria before running each experiment. The existing practice protocol uses two distinct withheld training-practice batches and retains easier reset examples; its success does not establish independent generalization. The previous curriculum did not outperform baseline on single-gate validation, and one seed never advanced, so a curriculum benefit must be measured rather than assumed.

Do not advance solely because a step budget expired. Record stage exposure and both practice batches, preserve easier skills, and measure new layouts separately. Before running the planner on `maze`, verify grid bounds, goal/altitude normalization, range, deadlines, checkpoint/readout contracts, and reset memory. The current observed-map launcher intentionally supports `large` only.

Completion requires demonstrated navigation at each declared stage and explicit disclosure of any changed task or interface. Add moving obstacles, wind, sensor noise, and delay only after static navigation is reliable.

## Priority 5: Measure the contribution of the connectome

Compare real wiring with randomized wiring, disconnected recurrence, and a conventional controller under matched sensors, budgets, initialization seeds, and selection rules. Account for readout transformations: v55 cancels recurrence in base channels and retains only the declared panoramic fraction. Keeping every neuron in computation is not evidence that biological anatomy is necessary for navigation.

Predeclare ablations and use paired evaluation where appropriate. Report compute and capacity differences. A navigation advantage must survive the stated controls before attributing it to the connectome; no such advantage has been demonstrated so far.

More realistic vision, synaptic plasticity, spiking dynamics, and wing aerodynamics require separate designs and validation. They are not implied by the current reservoir equations or anatomical visualization.

## Supporting engineering work

Anatomical replay should read recorded full-neuron snapshots with correct before/after-action phases and episode boundaries. Missing snapshots or soma coordinates must not be fabricated. Extend region summaries and selected-neuron exports while labeling gradient sensitivity according to its actual basis.

Exact resumption should include random streams, recurrent state, partial episodes, curriculum state, and planner memory. Current checkpoint loading starts fresh episodes. Extend snapshot checksums and show achieved simulation speed, not just requested speed. Broader physical keyboard, focus, and multiple-window QA remains useful.

Keep public documentation synchronized with verified results. Maintain the [map gallery](docs/images/README.md), [publication protocol](docs/PUBLICATION.md), source-only archive audit, and clean separation of public evidence from ignored local records. Experimental tools belong in their existing modules; keep root launchers compatible rather than moving them without migration.

## Rules for the next experiment

Declare the hypothesis, unchanged baseline, task/sensor/readout contracts, added-transition budget, repeated initialization seeds, selection rule, and final-access rule before launch. Freeze sources and original alias hashes. Short implementation smokes are separate from substantive training and are not evidence of navigation quality.

Preserve unsuccessful results and do not extend a budget silently. Validation chooses a checkpoint; an independent final result measures it and must not choose a replacement. If no trained candidate succeeds, report failure and leave the final pool untouched. Dataset attribution and the distinction between modeled activity and biological evidence apply throughout.
