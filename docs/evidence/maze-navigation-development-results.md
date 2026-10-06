# Room-aware navigation development results

Recorded October 6, 2026. These are retained development diagnostics, not reserved final tests. All original room geometry and episode deadlines are unchanged. Full graph:167,184 annotated neurons and25,583,622 directed connections. Zero optimizer updates and zero training transitions.

| Controller | Profile | Seed | Outcome | Decisions | Flown distance | Final goal distance |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| planner-1.3-exp.1 | large | 13000013 | goal | 3275 | 221.56 | 0.417 |
| planner-1.3-exp.1 | large | 9500014 | timeout | 3480 | 233.10 | 23.884 |
| planner-1.3-exp.2 | large | 13000013 | timeout | 3499 | 207.61 | 31.317 |
| planner-1.3-exp.2 | large | 9500014 | timeout | 3480 | 197.93 | 37.301 |
| planner-1.3-exp.3 | large | 13000013 | timeout | 3499 | 214.70 | 14.516 |
| planner-1.3-exp.3 | large | 9500014 | timeout | 3480 | 208.42 | 17.177 |
| planner-1.3-exp.4 | large | 13000013 | goal | 2056 | 149.39 | 0.431 |
| planner-1.3-exp.4 | large | 9500014 | goal | 3343 | 218.23 | 0.418 |
| planner-1.3-exp.1 | maze | 14000001 | timeout | 6352 | 402.39 | 37.913 |
| planner-1.3-exp.1 | maze | 14000000 | timeout | 6736 | 495.14 | 41.391 |
| planner-1.3-exp.4 | maze | 14000001 | timeout | 6352 | 382.23 | 29.694 |
| planner-1.3-exp.4 | maze | 14000000 | timeout | 6736 | 452.36 | 22.711 |
| planner-1.3-exp.5 | maze | 14000001 | timeout | 6352 | 326.87 | 53.542 |
| planner-1.3-exp.5 | maze | 14000000 | timeout | 6736 | 332.23 | 49.532 |
| planner-1.3-exp.6 | maze | 14000001 | timeout | 6352 | 356.12 | 44.428 |
| planner-1.3-exp.6 | maze | 14000000 | timeout | 6736 | 395.51 | 56.036 |

Planner-1.3-exp.4 corrects both retained large failures without collisions. This does not establish a fresh success-rate improvement. All completed maze diagnostics still fail. Planner-1.3-exp.7 is undergoing a bounded retained diagnostic; it is not selected as a maze solution.

Existing checkpoint aliases and eleven historical planner implementations match their before/after protected hashes. Sources and layouts are hashed in the local run records. The multi-plane run had a briefly reordered naming catalog restored to its frozen bytes; the loaded controller was unchanged, but it is not presented as uninterrupted on-disk source freezing. No reserved pool was accessed. Physical counts include inactive vector slots.

Regression verification:408 passed, one expected failure for the discarded multi-plane detector. A separate20-step rendered maze check had finite activity and clean archive integrity, but no completed episode. The [detailed report](../MAZE_NAVIGATION.md) explains mechanisms, formulas, failed attempts, and limitations. Full local records are under runs/diagnostics and private; generated telemetry and checkpoint binaries remain excluded from Git.
