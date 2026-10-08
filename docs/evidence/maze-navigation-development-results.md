# Room-aware navigation development results

Recorded October 6, 2026. Full graph: 167,184 annotated neurons and 25,583,622 directed connections. Every task keeps its original room geometry and episode deadlines. No optimizer ran and no training transitions were added. Reserved final pools were not evaluated.

## Current outcome

Large: planner-1.3-exp.9 reached 6/6 retained and 8/8 predeclared fresh development goals, with zero collisions or timeouts. It met its 7/8, zero-collision development rule. Fresh Wilson 95% interval: 67.6–100%; no paired superiority or independent-final claim.

Maze: planner-1.3-exp.11 reached both original retained goals, then only 5/8 in its fresh development suite, with zero collisions and three timeouts. That failed its 7/8 rule. Those eight rooms are now retained; exp.12 tests goal-relative portal priority on all of them. It has no new generalization result yet.

| Controller | Profile | Cohort | Seed | Outcome | Decisions | Flown distance | Final goal distance |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: |
| planner-1.3-exp.1 | large | retained development | 13000013 | goal | 3275 | 221.56 | 0.417 |
| planner-1.3-exp.1 | large | retained development | 9500014 | timeout | 3480 | 233.10 | 23.884 |
| planner-1.3-exp.2 | large | retained development | 13000013 | timeout | 3499 | 207.61 | 31.317 |
| planner-1.3-exp.2 | large | retained development | 9500014 | timeout | 3480 | 197.93 | 37.301 |
| planner-1.3-exp.3 | large | retained development | 13000013 | timeout | 3499 | 214.70 | 14.516 |
| planner-1.3-exp.3 | large | retained development | 9500014 | timeout | 3480 | 208.42 | 17.177 |
| planner-1.3-exp.4 | large | retained development | 13000013 | goal | 2056 | 149.39 | 0.431 |
| planner-1.3-exp.4 | large | retained development | 9500014 | goal | 3343 | 218.23 | 0.418 |
| planner-1.3-exp.1 | maze | retained development | 14000000 | timeout | 6736 | 495.14 | 41.391 |
| planner-1.3-exp.1 | maze | retained development | 14000001 | timeout | 6352 | 402.39 | 37.913 |
| planner-1.3-exp.4 | maze | retained development | 14000000 | timeout | 6736 | 452.36 | 22.711 |
| planner-1.3-exp.4 | maze | retained development | 14000001 | timeout | 6352 | 382.23 | 29.694 |
| planner-1.3-exp.5 | maze | retained development | 14000000 | timeout | 6736 | 332.23 | 49.532 |
| planner-1.3-exp.5 | maze | retained development | 14000001 | timeout | 6352 | 326.87 | 53.542 |
| planner-1.3-exp.6 | maze | retained development | 14000000 | timeout | 6736 | 395.51 | 56.036 |
| planner-1.3-exp.6 | maze | retained development | 14000001 | timeout | 6352 | 356.12 | 44.428 |
| planner-1.3-exp.7 | maze | retained development | 14000000 | timeout | 6736 | 460.65 | 26.123 |
| planner-1.3-exp.7 | maze | retained development | 14000001 | timeout | 6352 | 387.98 | 29.527 |
| planner-1.3-exp.8 | maze | retained development | 14000000 | goal | 5441 | 339.87 | 0.430 |
| planner-1.3-exp.8 | maze | retained development | 14000001 | timeout | 6352 | 401.20 | 11.535 |
| planner-1.3-exp.4 | large | retained development | 10000005 | goal | 2731 | 174.44 | 0.425 |
| planner-1.3-exp.4 | large | retained development | 10000006 | timeout | 3614 | 238.71 | 12.684 |
| planner-1.3-exp.4 | large | retained development | 10000007 | goal | 2160 | 141.07 | 0.444 |
| planner-1.3-exp.4 | large | retained development | 10000008 | goal | 2648 | 172.39 | 0.443 |
| planner-1.3-exp.9 | large | retained development | 10000005 | goal | 2204 | 144.74 | 0.434 |
| planner-1.3-exp.9 | large | retained development | 10000006 | goal | 2343 | 163.84 | 0.446 |
| planner-1.3-exp.9 | large | retained development | 10000007 | goal | 2251 | 144.57 | 0.403 |
| planner-1.3-exp.9 | large | retained development | 10000008 | goal | 3403 | 207.32 | 0.418 |
| planner-1.3-exp.9 | large | retained development | 13000013 | goal | 3017 | 195.05 | 0.435 |
| planner-1.3-exp.9 | large | retained development | 9500014 | goal | 2870 | 180.07 | 0.448 |
| planner-1.3-exp.9 | large | fresh development | 15000000 | goal | 2880 | 164.06 | 0.447 |
| planner-1.3-exp.9 | large | fresh development | 15000001 | goal | 3114 | 191.55 | 0.418 |
| planner-1.3-exp.9 | large | fresh development | 15000002 | goal | 3145 | 198.98 | 0.427 |
| planner-1.3-exp.9 | large | fresh development | 15000003 | goal | 1931 | 141.77 | 0.412 |
| planner-1.3-exp.9 | large | fresh development | 15000004 | goal | 2613 | 160.51 | 0.442 |
| planner-1.3-exp.9 | large | fresh development | 15000005 | goal | 2330 | 145.71 | 0.442 |
| planner-1.3-exp.9 | large | fresh development | 15000006 | goal | 2161 | 139.34 | 0.449 |
| planner-1.3-exp.9 | large | fresh development | 15000007 | goal | 2463 | 156.82 | 0.442 |
| planner-1.3-exp.9 | maze | retained development | 14000000 | timeout | 6736 | 43.47 | 47.336 |
| planner-1.3-exp.9 | maze | retained development | 14000001 | timeout | 6352 | 416.68 | 30.517 |
| planner-1.3-exp.10 | maze | retained development | 14000000 | goal | 5215 | 346.41 | 0.427 |
| planner-1.3-exp.10 | maze | retained development | 14000001 | timeout | 6352 | 398.94 | 22.610 |
| planner-1.3-exp.11 | maze | retained development | 14000000 | goal | 6630 | 420.76 | 0.396 |
| planner-1.3-exp.11 | maze | retained development | 14000001 | goal | 6028 | 392.08 | 0.429 |
| planner-1.3-exp.11 | maze | fresh development | 16000000 | goal | 5283 | 365.14 | 0.436 |
| planner-1.3-exp.11 | maze | fresh development | 16000001 | timeout | 6562 | 456.48 | 33.511 |
| planner-1.3-exp.11 | maze | fresh development | 16000002 | goal | 5729 | 384.53 | 0.410 |
| planner-1.3-exp.11 | maze | fresh development | 16000003 | goal | 5026 | 318.25 | 0.434 |
| planner-1.3-exp.11 | maze | fresh development | 16000004 | timeout | 7006 | 457.07 | 2.455 |
| planner-1.3-exp.11 | maze | fresh development | 16000005 | goal | 5540 | 364.06 | 0.432 |
| planner-1.3-exp.11 | maze | fresh development | 16000006 | timeout | 6687 | 442.32 | 15.185 |
| planner-1.3-exp.11 | maze | fresh development | 16000007 | goal | 5957 | 395.09 | 0.437 |

## Verification and provenance

Existing checkpoint aliases and eleven historical planner implementations match their before/after protected hashes. Source and layout fingerprints are retained with the local run records. The multi-plane run had a briefly reordered naming catalog restored to its frozen bytes; the loaded implementation was unchanged, but that run is not described as uninterrupted on-disk source freezing.

Physical counts include inactive vector slots. Fresh large: 25,160 physical transitions, 281.83 seconds, 0.547 GiB peak allocated CUDA memory. Fresh maze exp.11: 56,048 transitions, 533.47 seconds, 0.572 GiB. The latter's three failures remain in the table.

Full regression after center refinement: 420 passed, one strict expected failure for the discarded false-plane detector. Goal-priority navigation checks: 141 passed, one expected failure. Short rendered large and maze checks produced finite full-graph activity; the maze launcher opened the separate anatomical soma window and its 20-step archive passed integrity inspection. These rendering checks contain no completed episodes and are not success measurements.

The [detailed report](../MAZE_NAVIGATION.md) records mechanisms, formulas, failed attempts, and limitations. Detailed evidence remains in local runs/diagnostics and private. Checkpoints, data, generated telemetry, and environments remain excluded from Git.


### Maze follow-up: rejected fine grid and surface fallback

The retained check for `planner-1.3-exp.12` reached six of eight goals with no collisions. It corrected one previous failure but regressed another layout, so it was not selected. `planner-1.3-exp.13` then returned to the opening-refinement controller and changed the grid from 0.6 to 0.4 units. All eight retained flights timed out without collisions. The change also reduced the physical thickness of the one-cell planning buffer; it is not an isolated resolution ablation. This candidate was rejected.

`planner-1.3-exp.14` keeps the 0.6 unit grid and the existing flight guards. It checks other strongly supported surfaces when the highest-scoring surface has no observed through-rays, and hands over to global goal planning only within three units of the beacon. Its eight-layout retained check is running. It has no verified outcome yet. No optimizer update or reserved final evaluation was performed. Large-room development verification remains eight of eight fresh goals with `planner-1.3-exp.9`.


### Rejected surface fallback and confined-speed check

Exp.14 completed with zero of eight goals, one collision and seven timeouts. Its source and protected-checkpoint hashes remained unchanged. Broadening surface selection did not solve wall search and introduced a collision. It is rejected. Exp.15 returns to the exp.11 surface detector and0.6unit grid, increases the requested confined speed from 1.0 to 1.3 under unchanged range/momentum limits, and restricts goal handover to beacon distances below 3 units. Its retained eight-room check is running; no success claim is made. Four candidate contract tests pass. The previous full focused suite passed 145 tests with one expected failure.


### Confined-speed outcome and search-memory correction

Exp.15 reached four of eight retained maze goals, with zero collisions and four timeouts. It corrected 16000006 but lost prior successes in 16000000 and 16000007. Sources and protected checkpoints were unchanged. It is not selected. Raising a requested speed did not preserve reliable passage search.

Exp.16 retains exp.11 cruise and surface selection. Every tenth decision records a visit to the estimated current cell. After 600 decisions with less than 2 units of reduction in estimated beacon distance, it enables a bounded additive visit cost, `min(0.15 * visits, 4)`, while no portal is active. It never writes this preference into occupancy evidence, never makes blocked cells finite, and disables it during a committed opening approach/crossing. It retains close beacon handover below 3 units. Two tests verify evidence preservation, blocked-cell preservation, inactive portal behavior, and independent memory. Its eight-layout retained flight check is running; no outcome is claimed yet.


### Search-memory outcome and clean alignment check

Exp.16 completed at four of eight goals, zero collisions, four timeouts. It regressed 16000007 and failed all three earlier timeout cases. Visit pressure changed routes but did not establish reliable progress. All source and protected-checkpoint hashes remained unchanged. It is not selected.

Exp.17 combines exp.11 clean occupancy and center refinement with surface normals aligned to the initial observed beacon direction (`normal dot initial_direction >= 0.9`). It retains the original exp.11 cruise, grid, guards and portal planning. The earlier alignment-only candidate used context mapping and did not solve its two cases; this combination must be measured rather than assumed successful. It adds a declared straight-corridor structural assumption appropriate to the present procedural maze and is not a solver for arbitrary wall orientations. The controller receives no hidden heading, partition list, true pose or certified route. Two observed-gap/solid-wall tests pass. The full eight-layout retained check is running.


### Observed-clearance opening reference

Exp.17 reached five of eight retained goals without collisions. It corrected 16000006 but regressed 16000007, and 16000001/16000004 still timed out. It failed the 7/8 rule. Frozen-source and protected-checkpoint hashes matched before/after.

Exp.18 returns to exp.11 surface selection, grid, speed, guards and stronger-support refinement. Let `C` be through-ray intersections belonging to an observed opening cluster, and `W` be observed endpoints on its fitted surface. Both are represented in the wall tangent/height plane. The new reference is `argmax(p in C) min(w in W) ||p - w||`, followed by the existing projection onto the fitted plane. This replaces the median of visible through-rays, which can be biased toward the visible edge of a partially observed opening. It uses no known aperture size or hidden mesh.

The distance to sparse wall endpoints is a reference-selection heuristic, not a guaranteed continuous clearance radius. The actual fly body, collision model, range braking, momentum braking and episode deadlines remain unchanged. Three reference tests pass, including a fixture with the actual maze opening width 2.4 and height 2.8. The selected point lies inside that fixture with body clearance; this does not prove arbitrary sampled surfaces safe. The eight-layout retained full-connectome check is running. No optimizer or reserved final evaluation is involved.


### Neural-ray visible-goal handover

Exp.18 completed at five of eight retained goals, zero collisions and three timeouts. It corrected 16000006 and preserved 16000007, but regressed 16000000; 16000001 and 16000004 still timed out. Sources and protected hashes matched. It failed the 7/8 rule and is not selected.

Exp.19 returns to exp.11 opening inference, grid and cruise. It uses the current decoded local beacon vector and clean neural panorama ranges to recognize a direct goal corridor. For distance `d` below 23, choose the four panorama directions with greatest alignment to the beacon unit vector. Each must have dot product above 0.98 and projected range `r * alignment > d + 0.3`. If these observations pass, the controller relinquishes the opening reference and steers toward the beacon using the existing range/momentum flight guards. Otherwise normal opening planning continues.

This is sampled visibility, not a continuous swept-body clearance proof. No hidden geometry, true pose, certified route or seed enters the action controller. Two tests reject blocked and out-of-range handovers. The full retained eight-layout check is running with unchanged original deadlines and no optimizer or final reserved evaluation.


### Stable distant goal visibility

Exp.19 completed at six of eight retained goals, zero collisions and two timeouts. It corrected 16000006 and kept the other successes, but 16000001 and 16000004 still timed out. Source and protected hashes matched. It still fails the 7/8 rule, so no fresh suite or promotion followed.

Exp.20 retains exp.19 rays, ranges and flight law. A visible beacon below 8 units can hand over immediately. Between 8 and 23 units, all four nearest rays must pass the same visibility check for 20 consecutive decisions (one simulated second). A blocked observation immediately resets that counter and cancels handover. This tests whether brief distant visibility causes premature opening-reference changes. It is not a claim that flicker was proven to be the cause of every failure. Two continuity, cancellation and reset-memory tests pass; the full retained check is running with original deadlines.


## Completed handover checks and numerical repeatability

Planner-1.3-exp.20 and exp.21 each completed at six of eight retained maze goals, zero collisions and two timeouts. Seeds 16000001 and 16000004 remained failures. Both runs preserved their frozen source hashes and protected checkpoint hashes. Neither meets the predeclared seven-of-eight development rule, so no fresh maze suite or promotion followed. The original episode deadlines and physical geometry were preserved.

A separate numerical probe reset the full graph and replayed identical synthetic inputs twice, using eight slots and sixteen steps per replay. It advanced all 167,184 neurons and 25,583,622 directed edges. It performed zero environment transitions and zero optimizer updates. All outputs were finite, but feature values differed by up to 4.76837158203125e-7 and final neuron states by 1.1920928955078125e-7. A second probe with deterministic PyTorch algorithms and `CUBLAS_WORKSPACE_CONFIG=:4096:8` still differed, with maximum feature difference 5.364418029785156e-7. The installed runtime was PyTorch 2.7.1+cu128.

These probes establish small numerical variation for this execution path, not that it causes every navigation failure. Earlier recorded trajectories also diverged before goal handover was possible. The next prepared diagnostic converts the same full matrices to COO storage and checks repeatability; it has not run and has no result. Automatic approval review could not execute it because the account usage limit was reached. This was an unavailable approval review, not a judgment that the operation was unsafe.

Large navigation remains verified on six retained and eight fresh development rooms with planner-1.3-exp.9. Maze reliability remains unresolved. The demo continues to select exp.11, which reached both original retained maze cases and five of eight fresh development layouts. Later six-of-eight outcomes are on reused layouts and must not be presented as independent generalization. No training was initiated during these checks.


## Repeatable full-connectome execution

Execution became available again. The full COO probe still had numerical variation, so storage conversion alone was rejected as a repeatability solution. Ordered CSR accumulation using deterministic `index_add_` produced bit-identical features and final neuron states across both sixteen-step, eight-slot replays. The actual implemented `RepeatableDualActivityBrain` repeated that result on all 167,184 neurons and 25,583,622 edges: zero differing feature values, zero maximum feature/state difference, finite outputs, 32 full-graph steps, and zero environment transitions or optimizer updates. Its probe elapsed 6.477 seconds including initialization.

Planner-1.3-exp.22 keeps exp.19 visible-goal control and selects this explicit experimental readout. Sparse multiplication retains every signed matrix value and edge; it forms weighted presynaptic contributions and accumulates them in deterministic row order. The sensory projection, centering, recurrence, leak, nonlinearity and dual reconstruction formulas remain the same. The discarded pooled output is not computed by the new step method; it never feeds recurrent state or dual reconstruction. Floating-point accumulation order changes and therefore receives a separate readout/fingerprint: `neural-projection-dual-repeatable-index-add-v1`. Historical readouts and checkpoints remain unchanged.

Repeatability here is measured on this installed runtime and device, not guaranteed across hardware or library versions. It is also not a navigation-performance or biological-benefit claim. The eight retained maze layouts are under verification with the same 81,920 physical cap and original episode deadlines. A predeclared 30-minute wall-clock safety bound accommodates slower full-graph execution. All application source files and the runner are frozen by hash for this check. The development rule remains at least 7/8 goals with zero collisions before any new fresh suite. No training or reserved final evaluation is running.

## Repeatable execution follow-up

Exp.22 stopped at its predeclared 30-minute wall limit after 47,528 physical transitions. Five retained maze flights reached their goals, with no collisions; three flights were unfinished. This is an incomplete run, not a five-of-eight completed success rate. All frozen source and protected checkpoint hashes matched. No training or reserved-test evaluation occurred.

The brain inspector now recognizes the repeatable dual readout and correctly combines its two feature contributions. The old and both new readout contracts pass the three-case regression.

Exp.23 preserves exp.19 control logic and uses segmented sums over the complete CSR graph. Its numerical fingerprint differs from both the original CSR and exp.22 index-add kernels. A 32-call, batch-eight full-connectome probe produced finite, bit-identical replayed features and final neuron states: 167,184 neurons and 25,583,622 directed edges, zero physical transitions and optimizer updates. Total probe time was 3.51 seconds, including initialization; this is not a warmed throughput benchmark or a navigation result.

The eight retained maze flights are under verification with their original physical episode deadlines, an 81,920-transition cap, and a predeclared 45-minute wall limit. At least seven goals and zero collisions are required before another fresh development suite. All application source bytes and the diagnostic runner were frozen and archived before evaluation. The numerical optimization retains every neuron, edge, signed weight and sensory projection; it changes summation order, not the physical environment. The large-map launcher remains exp.9 and the maze launcher remains exp.11 until new complete evidence warrants a change.

## Completed segmented run and observed-wall correction

Planner-1.3-exp.23 completed all eight retained maze flights: six goals, zero collisions and two physical episode timeouts. Successful decision counts were 4,608 (16000003), 5,053 (16000005), 5,200 (16000000), 5,448 (16000007), 5,496 (16000002) and 6,194 (16000006). Seed 16000001 timed out at 6,562 decisions, 8.75 units from its goal; seed 16000004 timed out at 7,006 decisions, 24.24 units away. The run used 56,048 physical transitions, took 1,268.79 seconds and allocated a peak 1.952 GiB of VRAM. All source and protected checkpoint hashes matched. There were no optimizer updates or reserved-test evaluations. It failed the existing seven-of-eight criterion and was not selected.

Planner-1.3-exp.24 addresses the observed first-partition search delay. If no opening is acquired for 80 decisions, it fits a nearby broad blocking surface from clean neuronal range endpoints, chooses a near-side sweep reference two units from that surface and moves along its tangent in four-unit increments. After 160 decisions without improving distance to the survey target, it reverses direction. Opening acquisition or a ray-supported visible goal cancels the survey. Original route occupancy, body geometry, braking, speed limits and physical deadlines are unchanged. The survey is enabled for the maze contract; it receives no hidden obstacle list, true pose or certified route.

Twelve focused tests passed, covering surface fitting, rejection of distant surfaces, near-side reference geometry, sweep continuation, reversal, independent episode search state and versioned policy selection. All eight retained maze flights are now under a separately frozen diagnostic, with the same 81,920-transition cap, original episode deadlines and a predeclared 45-minute wall limit. The entire 117-file runtime source set is archived byte-for-byte. No navigation improvement is claimed until the flights complete. No fresh maze suite or promotion has occurred.

## Wall survey result and isolated handover correction

Planner-1.3-exp.24 completed at six retained goals, zero collisions and two timeouts. It reached seeds 16000007/06/02/05/01/04 in 4,452/4,492/4,580/4,855/5,588/5,652 decisions. Both previous failures were fixed, but 16000003 and 16000000 regressed to timeouts at 6,535 and 6,885 decisions, ending 24.49 and 36.79 units from the goal. It used 55,080 physical transitions, took 1,321.94 seconds, and peaked at 1.952 GiB allocated VRAM. All source and protected checkpoint hashes matched; no optimization or reserved evaluation occurred. It failed the existing gate and was not selected. Surveying was helpful on several layouts but did not preserve prior successful behavior.

Planner-1.3-exp.25 isolates the visibility/braking correction on exp.23, without the rejected wall survey. It requires no nonsaturated short or panoramic endpoint inside the same 0.25-unit corridor used by braking before direct goal handover. Saturated maximum-range values are not treated as wall hits. An active opening approach/crossing must complete before goal handover. Sensor, connectome, geometry, speed, collision and episode-deadline contracts remain unchanged. Thirteen focused geometry/visibility/version tests passed. The eight retained maps are running with original episode deadlines, the 81,920-transition cap and a separately declared 45-minute wall limit. All 118 runtime source files are frozen and archived. No flight improvement is claimed until the check completes, and no fresh suite or promotion has occurred.

## Clearance-aware handover: retained gate passed

Planner-1.3-exp.25 completed the eight retained maze flights at seven goals, zero collisions and one timeout. Arrival decisions were 4,710 (16000003), 5,051 (16000005), 5,200 (16000000), 5,544 (16000002), 5,614 (16000007), 5,909 (16000001) and 6,357 (16000006). The remaining seed 16000004 timed out at its original 7,006-decision limit, 24.24 units from its goal. The visibility/braking deadlock in 16000001 was corrected, and all six exp.23 successes were preserved.

The check used 56,048 physical transitions and zero optimizer updates, took 1,273.43 seconds, and peaked at 1.952 GiB allocated VRAM. The full 167,184-neuron, 25,583,622-edge graph was retained. All frozen source and protected checkpoint hashes matched. This passes the predeclared seven-of-eight retained gate. It is tuned development evidence, not an independent success-rate estimate or a biological advantage claim.

A separate frozen prospective development suite is now running on seeds 17000000–17000007. An integer-bounded audit of 1,769 archived JSON/Markdown records found no previous occurrences before its seed declaration; undocumented use cannot be ruled out by that audit. No candidate-room geometry was generated or inspected before launch. The fresh run uses exactly the same 118 runtime source hashes as the completed retained run, with an 81,920-transition cap, original physical episode deadlines and a predeclared 45-minute wall limit. At least seven fresh goals and zero collisions are required. The source bytes are archived separately. There is no tuning, optimization, reserved-test access, checkpoint modification or demo promotion during this check. Its outcomes are pending.

## Completed fresh maze check and requested pause

Planner-1.3-exp.25 finished its frozen prospective maze check at **5/8 goals (62.5%)**, zero collisions and three timeouts. The Wilson 95% interval is **30.6–86.3%**. This is a small development sample, not the reserved final test and not an independent paired comparison with exp.11. Its earlier 7/8 retained outcome is tuned correction evidence and must remain separate.

| Fresh seed | Outcome | Decisions | Final goal distance |
| --- | --- | ---: | ---: |
| 17000000 | Goal | 5,916 | 0.439 |
| 17000001 | Goal | 4,090 | 0.443 |
| 17000002 | Timeout | 6,752 | 22.160 |
| 17000003 | Goal | 4,905 | 0.405 |
| 17000004 | Goal | 5,434 | 0.422 |
| 17000005 | Timeout | 6,534 | 20.371 |
| 17000006 | Goal | 5,473 | 0.417 |
| 17000007 | Timeout | 6,666 | 13.211 |

The run completed all eight original episode deadlines with no incomplete flights. It used 54,016 physical transitions, took 1,234.24 seconds and peaked at 1.952 GiB allocated VRAM. Every transition used the full 167,184-neuron, 25,583,622-edge graph. All 118 frozen runtime sources and every protected checkpoint alias matched their before/after hashes. There were zero optimizer updates and no reserved-test access. The process exited normally.

The fresh seven-of-eight criterion was not met, so exp.25 is not promoted. The large launcher remains exp.9, with its six retained and eight fresh goals. The maze launcher remains exp.11. Large-room development criteria are met; reliable maze navigation remains unresolved. The three new timeouts require search/reference diagnosis when work resumes. These newly inspected maps are now correction data for future changes, not reusable fresh evidence.

Navigation, connectome and visualization integration checks passed: 212 passed and one expected failure for a rejected historical candidate. Repository checks passed for 79 documents, 378 links, module imports and CLI help; the public-file audit had no errors. No additional training or navigation experiments followed this check. At the user's request, work pauses after saving and pushing these results; a selected-candidate rendered demo check is deferred until the navigation criterion is met.
