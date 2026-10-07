# October 7 maze opening-range correction

Planner-1.3-exp.26 extends opening detection from 6 to 12 units only when the unchanged nearby detector returns no candidate. It preserves exp.25 handover, physics, sensors and segmented full-connectome readout.

The completed retained suite reached **6/8 goals, zero collisions and two timeouts**, versus exp.25's five goals on these same inspected maps. The formerly fresh 17000000–17000007 layouts were already used to diagnose exp.25 and are not independent evidence for exp.26. It preserves all five prior successes and fixes 17000005, but does not meet the existing 7/8 retained rule and is not promoted.

| Seed | Outcome | Decisions | Final goal distance |
| --- | --- | --- | --- |
| 17000000 | Goal | 6720 | 0.446 |
| 17000001 | Goal | 4090 | 0.443 |
| 17000002 | Timeout | 6752 | 22.160 |
| 17000003 | Goal | 4905 | 0.405 |
| 17000004 | Goal | 5434 | 0.422 |
| 17000005 | Goal | 4205 | 0.450 |
| 17000006 | Goal | 5473 | 0.417 |
| 17000007 | Timeout | 6666 | 13.211 |

The check used 54,016 physical transitions, took 734.58 seconds and peaked at 1.952 GiB allocated VRAM. All 167,184 neurons and 25,583,622 directed edges were retained. All frozen-source and protected checkpoint/source hashes matched. There were zero optimizer updates and no reserved-test access. The slower 17000000 arrival is retained in the table rather than omitted.

Seven focused range/handover checks passed before flights. A further progress-gated wall-search candidate has eleven focused checks and requires its own frozen complete-flight measurement; those tests are not performance evidence. See [the maze record](../MAZE_NAVIGATION.md#october-7-opening-range-diagnosis) for the hypothesis, offline diagnostic limitations and next correction. Detailed source snapshots, protocol hashes and traces remain in ignored local records.
