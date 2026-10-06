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
