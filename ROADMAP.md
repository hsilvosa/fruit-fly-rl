# Roadmap

Current as of October 7, 2026. This is proposed work, not an active training schedule. New collection, optimization, or evaluation needs a declared budget and protocol. Preserve historical results, frozen controllers, and original checkpoint aliases.

## Starting point

| Capability | Current evidence | Status |
| --- | --- | --- |
| Full connectome, 3D flight, anatomical inspection, recording/replay | Implemented and checked; full graph retained | Available |
| Learned single-opening navigation | `gate-long`: 61/64 final goals, zero collisions, three timeouts; 95% interval 87.1–98.4% | Successful on that distribution |
| Learned medium dense-room navigation | Historical independent pools range from 54.7% to 78.1%; several results around 67–78% | Useful, variable performance; not interchangeable with new profiles |
| Learned structured large-room navigation | Initial final result 0/64; best recent student v34 is 3/8 on reused optimization maps | Unresolved |
| Explicit large-room planner-1.0 | 8/8 reused optimization; 13/16 frozen prospective development, zero collisions, three timeouts; interval 57.0–93.4% | Working demo, incomplete robustness |
| Experimental large-room planner-1.1 | 3/3 corrected known failures; separate frozen paired development 14/16, zero collisions, two timeouts; interval 64.0–96.5%. planner-1.0 reached 12/16 on the same new rooms | Available explicitly; two new failures remain |
| Distance-stable planner-1.2-exp.1 | Stationary known case corrected; new paired development 13/16 with two collisions and one timeout versus planner-1.1’s 15/16 with one collision | Regressed; not selected as the stronger candidate |
| Dual mapping/safety planner-1.2 | Four known collision/control goals, stationary known goal; new frozen development 15/16 with zero collisions and one timeout, identical to planner-1.1’s paired outcomes | Available explicitly; retained detours and independent final objective remain open |
| Latest large-room planner-1.3-exp.9 | Six retained goals and eight fresh development goals, zero collisions or timeouts | Development gate passed; large launcher available |
| Experimental maze planner-1.3-exp.25 | Seven of eight retained goals, then five of eight fresh goals, zero collisions and three fresh timeouts | Fresh criterion failed; not promoted; follow-up corrections active |
| Noise, wind, moving obstacles | Proposed capabilities without verified navigation results | Future work |

The planner is the operational solution today. It has explicit map memory, bounded search, and proportional flight control, not learned movement weights. Its result does not fulfill the learned-policy objective or prove biological benefit. [Results](docs/RESULTS.md) and [resolution history](docs/NAVIGATION_RESOLUTION.md) retain the full evidence.

## Priority 1: Diagnose and resolve planner timeouts

October 5 progress: bounded full-graph checks reproduced all three failures. Experimental planner-1.0.1-exp.1 corrected the observed-free goal-margin blockage in room 8500011 (arrival at step 1,939); rooms 8500012 and 8500013 still timed out. Both versions had zero collisions. The checks used 21,204 physical transitions, no optimization, and no reserved tests. All six aliases and frozen planner-1.0 retained their hashes. Priority 1 remains open; planner-1.0 remains the demo default. [Diagnosis, regression checks, and outcomes](docs/evidence/planner-timeouts-v56-results.md).

Follow-up: planner-1.1-exp.1 isolated higher cruise speed, planner-1.1-exp.2 isolated broader known-free margin traversal, and planner-1.1-exp.3 combined them but regressed one room. planner-1.1 enables the broader margin rule only after a capped search; it reached **3/3 known failures**, with zero collisions or timeouts. This addresses the retained cases without establishing generalization. The four follow-up checks used 41,226 physical transitions, zero training transitions, and no final test. Twenty-eight navigation checks passed. planner-1.1 and its dependencies were frozen before the paired priority-2 development check; planner-1.0 remains the operational reference. [Detailed attempts and outcomes](docs/evidence/planner-followup-v57-v60.md).

The later planner-1.2-exp.1 readout diagnosis corrected false stopping on one inspected room, but a fresh sixteen-room paired comparison regressed to 13/16 versus planner-1.1’s 15/16, with two versus one collisions. planner-1.2-exp.2 route persistence and planner-1.2-exp.3 ray-consistent interpolation still timed out in the retained detour room. Diagnose momentum, physical clearance, and route execution before another change; do not promote a semantic fix solely because one tuned room improved. [Known-case report](docs/evidence/planner-readout-v61-v63.md) and [paired results](docs/evidence/planner-v61-development-results.md).

The original planner-1.0 diagnosis separated search saturation, frontier selection, route oscillation, accumulated odometry error, conservative occupancy, and insufficient remaining flight time in rooms 8500011, 8500012, and 8500013. The first two ended at the 12,000-expansion cap; the third found a route but did not finish. Those retained cases now succeed with planner-1.1, while the frozen planner-1.0 source remains unchanged. Increasing the cap alone was not established as a fix.

Trajectory, search-effort, command, pose-error, and final observed-evidence diagnostics are now implemented. Visited/frontier arrays are not recorded yet. Use the retained planner-1.2 records from rooms 9500014 and 13000013 to examine reference advancement, unknown-space commitment, and detours before another bounded intervention or increased compute. Compare individual changes first, then declare any combined candidate. Preserve the physical collision checks and original room deadlines.

Completion requires reproducible diagnoses from retained data, focused regression checks for selected fixes, and explicit reporting of both remaining timeout outcomes while preserving the corrected stationary and collision cases. Fixing known rooms establishes a correction on those rooms, not generalization.


Latest correction: planner-1.2-exp.4’s actual-motion braking fixed the retained collisions, but its fresh suite regressed to 12/16 versus planner-1.1’s 15/16. planner-1.2 preserves the original contextual mapping prefix while using separate clean neural ranges for braking. It reached 4/4 retained collision/control rooms, resolved the stationary room at step 1,782, and matched planner-1.1 at 15/16 on a new paired suite with zero collisions. Retained room 9500014 and shared fresh timeout 13000013 remain unresolved. Preserve all variants and diagnose those detours before another narrow intervention. [Known cases and contracts](docs/evidence/planner-dual-v65-results.md) and [fresh paired evidence](docs/evidence/planner-v65-development-results.md).

## Priority 2: Measure the corrected planner independently

October 5 progress: the predeclared sixteen-room paired development check completed with frozen planner-1.0 and planner-1.1. Results were 12/16 versus 14/16, no collisions, with two added planner-1.1 successes and no lost baseline successes. Both arms used 55,680 physical transitions; source, layout, graph, and alias checks passed. The [protocol](docs/PLANNER_DEVELOPMENT.md) and [per-room report](docs/evidence/planner-v60-development-results.md) retain the evidence. This is development, not the reserved final suite; the independent-final 80% objective remains open. Once inspected, the two new failures become design cases for subsequent corrections.

Predeclare fresh development layouts, selection rules, compute limits, and an untouched final pool. Freeze code and sensor/readout contracts before prospective measurement. Use development only for selecting versions; assess the frozen winner once on its final pool and mark that pool consumed. Do not use earlier final pools again to select changes.

Report goals, collisions, timeouts, Wilson confidence intervals, elapsed compute, peak memory, flight time, and flown distance. Compare successful routes with a feasible geometric reference while retaining failures separately. The geometric reference is not a global optimum or guaranteed executable flight.

The existing goal is at least 80% on a declared independent final suite, with uncertainty shown. The protocol must state whether that means a point estimate or a stronger confidence-bound requirement. A small point estimate alone cannot establish broad robustness. If claiming improvement over planner-1.0, use a predeclared paired comparison on the same fresh layouts, without selecting either controller from that final result.

Completion requires a frozen protocol, verified dataset/source/suite fingerprints, one final report with all failures, and an explicit conclusion about whether the stated target was met.


The latest planner-1.1/planner-1.2 comparison used a schema-three protocol that explicitly declares 3,869 versus 5,669 neural features with unchanged sensor input, graph, projection, and layouts. Both arms reached the same fifteen goals and timed out in the same room; neither collided. The Wilson interval is 71.7–98.9%. This is further development evidence, not the untouched final assessment or a demonstrated success-rate improvement.

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

Do not advance solely because a step budget expired. Record stage exposure and both practice batches, preserve easier skills, and measure new layouts separately. Before running the planner on `maze`, verify grid bounds, goal/altitude normalization, range, deadlines, checkpoint/readout contracts, and reset memory. Frozen planner-1.0 through planner-1.2 support `large` only. Experimental planner-1.3 candidates also support the declared `maze` contract. The normalization and grid checks pass. Exp.11 reaches both retained maze goals but only 5/8 fresh development goals; reliability remains unresolved. See [maze development](docs/MAZE_NAVIGATION.md).

Completion requires demonstrated navigation at each declared stage and explicit disclosure of any changed task or interface. Add moving obstacles, wind, sensor noise, and delay only after static navigation is reliable.

## Priority 5: Measure the contribution of the connectome

Compare real wiring with randomized wiring, disconnected recurrence, and a conventional controller under matched sensors, budgets, initialization seeds, and selection rules. Account for readout transformations: planner-1.0 cancels recurrence in base channels and retains only the declared panoramic fraction. Keeping every neuron in computation is not evidence that biological anatomy is necessary for navigation.

Predeclare ablations and use paired evaluation where appropriate. Report compute and capacity differences. A navigation advantage must survive the stated controls before attributing it to the connectome; no such advantage has been demonstrated so far.

More realistic vision, synaptic plasticity, spiking dynamics, and wing aerodynamics require separate designs and validation. They are not implied by the current reservoir equations or anatomical visualization.

## Future stage: Navigate simulations of real places

After completing the maze experiment and its navigation and rendering checks, extend the task from procedural rooms to 3D reconstructions of real building interiors and streets. This stage is planned; it does not start a new experiment or training budget. A planner and a learned student remain separate experimental tracks.

CPU-only asset preparation is now available: six original architectural drafts (revision 0.2: office, apartment, street, atrium, warehouse, courtyard), 21 geometrically checked situations, OBJ/MTL meshes, collision JSON, hashes, floor plans and inspection previews. This is development preparation, not a completed real-place reconstruction or navigation experiment. No GPU training or maze run was started. [Assets, checks and remaining integration](docs/ARCHITECTURAL_SCENES.md).

1. **Static building interiors.** Begin with one floor, corridors, doors and furniture; then add larger interiors, multiple floors and stairs or atria with sufficient flight clearance. Select openly licensed geometry, record source attribution and asset hashes, and verify units, traversable openings, watertight collision surfaces and feasible start/goal pairs. Visual detail alone is not a harder navigation benchmark.
2. **Static outdoor streets.** Add building facades, street furniture, vegetation and intersections, then connected indoor/outdoor routes. Audit map bounds, sensor range, memory cost and physical episode deadlines for the new scale before comparing results.
3. **Observation changes.** First keep the current range/beacon interface to isolate geometry transfer. Treat camera-based perception, removal or replacement of the goal beacon, sensor noise, localization drift and latency as separate task changes. A detailed scene viewed through range sensors is not evidence of visual recognition.
4. **Dynamic conditions.** Once static navigation is reliable, introduce wind and moving pedestrians or vehicles separately, then combine them under declared protocols. Record collisions, near misses, clearance and recovery as well as arrival rate and flight efficiency.

Split by entire building or geographic area, not just different starts within the same mesh. Keep test assets and routes out of training, tuning and demonstration collection; disclose any pretrained model exposure that cannot be ruled out. Freeze each suite before measurement and report uncertainty, timeouts, compute, and failures alongside successful flights. Do not compare success rates across different sensor contracts or deadlines as if they were the same task.

Completion requires a verified asset-import and collision pipeline, documented licenses, reproducible frozen suites, and measured navigation on held-out places under a predeclared criterion. Maintain the full connectome and protected checkpoint references. Simulation success does not establish readiness for physical flight or biological realism.

## Supporting engineering work

Anatomical replay should read recorded full-neuron snapshots with correct before/after-action phases and episode boundaries. Missing snapshots or soma coordinates must not be fabricated. Extend region summaries and selected-neuron exports while labeling gradient sensitivity according to its actual basis.

Exact resumption should include random streams, recurrent state, partial episodes, curriculum state, and planner memory. Current checkpoint loading starts fresh episodes. Extend snapshot checksums and show achieved simulation speed, not just requested speed. Broader physical keyboard, focus, and multiple-window QA remains useful.

Keep public documentation synchronized with verified results. Maintain the [map gallery](docs/images/README.md), [publication protocol](docs/PUBLICATION.md), source-only archive audit, and clean separation of public evidence from ignored local records. Experimental tools belong in their existing modules; keep root launchers compatible rather than moving them without migration.

## Rules for the next experiment

Declare the hypothesis, unchanged baseline, task/sensor/readout contracts, added-transition budget, repeated initialization seeds, selection rule, and final-access rule before launch. Freeze sources and original alias hashes. Short implementation smokes are separate from substantive training and are not evidence of navigation quality.

Preserve unsuccessful results and do not extend a budget silently. Validation chooses a checkpoint; an independent final result measures it and must not choose a replacement. If no trained candidate succeeds, report failure and leave the final pool untouched. Dataset attribution and the distinction between modeled activity and biological evidence apply throughout.


## Immediate follow-up from the October 5 cutoff

Use the saved planner-1.2 timeout diagnostics before another training run. Both retained failures continued moving with low estimated pose drift, and their final planned routes contained mostly unknown or ambiguous points. A found grid route is not a fully observed, dynamically executable corridor. Log route identity, observed-free segment length, frontier commitment, progress, and turn cost. Test whether local route-reference changes cause repeated corridor traversals; do not assume that simple route persistence works, since planner-1.2-exp.2 already failed its retained pilot.

Any correction should live in a new version, leaving planner-1.0 and the measured planner-1.1/planner-1.2 sources intact. Check known failures first, then freeze new paired development layouts. Keep a final independent pool inaccessible during tuning, preserve original aliases, and stop at the declared budget. The eight focused offline-reporter tests and saved plots add diagnostic tooling, not new navigation results.


## October 6 development checkpoint

The room-size normalization and maze grid correction are implemented. Planner-1.3-exp.4 fixes both original retained large timeouts but reaches only three of four retained collision controls, so promotion is premature. Clean-range occupancy in exp.8 reaches the first actual maze goal; its second retained flight still times out. The faster clean-map candidate exp.9 passed all six retained large cases and all eight fresh large development cases without collisions or timeouts. It regressed both maze flights. Exp.10 recovers a stationary maze flight but still times out in the second; exp.11 reaches both retained maze goals after center refinement. Large development criteria and retained maze correction are met; the fresh maze suite later reached 5/8 and failed its 7/8 rule. The new launchers and separate brain-window rendering are verified. Earlier final pools remain untouched by this follow-up. See [maze development](docs/MAZE_NAVIGATION.md).

The exp.11 fresh maze check ended at 5/8 goals, zero collisions, three timeouts; its 7/8 development rule was not met. Exp.12 reached 6/8 retained goals; exp.13 reached 0/8. Neither was selected. Supported-surface fallback failed with one collision; bounded confined speed reached 4/8. Visit pressure also reached 4/8. Clean initial-beacon alignment and observed opening clearance each reached 5/8 with regressions. Visible-goal, stable and committed handover checks each reached 6/8 retained goals without collisions. None passed the rule. Investigate full-graph numerical repeatability and remaining wall search before any new fresh suite. Maze reliability remains an active objective.

Exp.12 reached 6/8 retained goals, failing its gate. Exp.13 tested a finer map and smaller one-voxel planning buffer, while preserving original physical geometry and collision/braking rules. It finished at 0/8 goals and was rejected.

The repeatable full-graph exp.22 check ended incomplete at its wall limit. Exp.23 tests faster segmented sums on the eight retained maze maps before any fresh suite. A systematic observed-wall survey is prepared separately to address the long first-partition search seen in a retained failure trace; it needs complete flight evidence before selection.

Exp.23 completed at 6/8 retained goals with no collisions and failed its gate. Exp.24 observed-wall surveying finished at 6/8 goals with two regressions and was rejected. Next: require the retained gate, then a new frozen development suite, then verify the selected demo and document the remaining statistical limits.

Exp.24 finished at 6/8 retained goals, fixing both prior failures but regressing two successes, and was rejected. Exp.25 excludes that survey and isolates the confirmed visibility/braking handover inconsistency. Its retained check reached 7/8 goals; the subsequent fresh suite reached 5/8 and failed its gate. The reserved final test remains untouched.

Exp.25 passed the retained gate at 7/8 goals without collisions. Its unchanged eight-map fresh development check finished at 5/8 and failed its gate. Retain the newly inspected maps as correction data and diagnose before another fresh suite. Preserve every historical checkpoint alias.

The exp.25 fresh result is 5/8 and is not promoted. Work resumed on October 7; exp.26 reached 6/8 on those now-retained maps, and exp.27 regressed to 4/8 and was rejected; exp.28 preserved 6/8 but failed its gate; exp.29 finished at 6/8; exp.30 regressed to 5/8 and was rejected; exp.31 fixed one timeout but regressed another success (6/8); exp.32 passed the retained gate at 7/8 without collisions; earlier-map regressions passed at 7/8 without collisions; further maze experiments are deferred. The preceding paragraphs retain chronological development history.
On resumption, diagnose the three new fresh timeouts as retained correction data, preserve the successful flights, and declare the next bounded protocol. Do not reuse these eight maps as fresh evidence or change the demo default until navigation and rendering checks pass.

## Maze wrap-up decision

New maze candidates and the fresh suite are deferred at the user's request. The earlier-map regression completed at 7/8 without collisions and preserved all seven prior successes. Preserve aliases and report the remaining timeouts. Exp.32 has passed both retained checks; do not mark independent maze reliability achieved or promote the launcher. The next implementation stage is the revised architectural simulation. See [closing evidence](docs/evidence/maze-wrap-up.md).
