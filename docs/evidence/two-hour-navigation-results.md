# Results of the additional two-hour window

The authorized deadline is October 4, 2026 at 20:40:52 UTC (22:40:52 Madrid time). Batches and their evaluations finished before the deadline. Autonomous navigation in the original large maps remained unresolved at this stage.

| Experiment | New transitions | Development goals | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Panoramic coverage v8 | 301,056 | 0/8 | 8 | 0 |
| Directional attention v9 | 32,768 | 0/8 | 8 | 0 |
| Lookahead guidance v10 | 163,840 | 0/8 | 0 | 8 |
| Distance perception v12 | 8,192 | 0/8 | 1 | 7 |

Since v8, 505,856 transitions were added. Batch v7, started before this window, finished its 98,304 transitions but failed at report completion because of differing path separators. That lookup was corrected, and a separate evaluation was recovered without modifying its weights: 0/8, eight collisions. Completed substantive training totals 1,472,512 transitions; verification steps are counted separately.

The eight development maps were reused to diagnose corrections. They are not an independent generalization test. No candidate met the selection criterion, and the reserved test was not run. No original alias was promoted either.

The teacher reached 64 goals in v8 and 35 in v10. These are guided flights with privileged geometry during training, not student successes. Autonomous optimization batches v8, v9, v10, and v12 reached no goals. Optimizers recorded finite losses, and reloads reproduced the checked tensors and actions. This verifies execution but does not establish useful navigation.

Directional attention avoids compressing the entire panoramic image into a single mean; v10 guidance progresses along the route without requiring a stop at every vertex; v12 removes the panoramic approach-velocity channel from its visual encoder. These interventions produced no development arrivals. No single cause was isolated, and no biological advantage was established.

Batched CUDA sensor computation and its episode cache were integrated. Checks compare geometry with NumPy and verify independent resets, finite gradients, and checkpoint compatibility. All 167,184 neurons and 25,583,622 connections of the full graph are retained. Brief inspection of the latest demo confirmed a rendered scene and finite activity during 40 steps; it was neither a navigation evaluation nor manual testing of every control.

Hashes of frozen sources, source checkpoints, and the six original alias files were preserved, according to detailed private audits. The latest experimental checkpoint is `runs/training/distance-only-perception-v12/policy.zip`, SHA256 `eaded4b6b600be5bd563a1b23907e727cf21d0e1b6d1def6d1e93dc6a06456ea`. Local manifest `runs/latest-large-demo.json` identifies it; `launch-panorama.ps1` checks its hash before opening it.

From the project folder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\launch-panorama.ps1
```

This demo uses the autonomous student, without a teacher or training. It remains experimental. Detailed results, trajectories, and losses are retained locally in `private` and `runs/training`. The watchdog enforces the deadline using PID, start time, and executable, without restarting any task. Work pauses at the deadline at the user's request.

Before another batch, examine states where the student stops or turns, check what information the neural projection retains near an opening, and improve coverage of those states. Any new intervention requires a separate budget and evaluation; this result does not permit marking navigation complete.
