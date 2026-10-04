# Timeout correction pilot results

The 32,768-transition pilot completed on 2026-10-04T08:34:44.312907+00:00. It included exactly 16,384 transitions on the unchanged original large target. It retained live episodes across four chunks, used gamma=0.9995 in PPO and its rollout buffer, failure-terminal deadline handling and the sensors-v4 clock. The other 16,384 transitions came from the fixed stage-four curriculum mixture. All optimizer losses were finite.

| Development outcome | Before | After |
| --- | --- | --- |
| Goals | 0/4 | 0/4 |
| Collisions | 3/4 | 1/4 |
| Timeouts | 1/4 | 3/4 |
| Mean end distance | 36.82 | 32.54 |
| Mean idle fraction | 0.0267 | 0.0209 |

The same four optimization-layout seeds were measured before and after training. These are development diagnostics, not held-out validation or a final test. The before policy had already been transferred to sensors v4, so this is not a clean comparison with the old sensors-v3 controller. It cannot attribute changes to individual interventions or demonstrate generalization. Fewer collisions and smaller end distance did not produce any arrivals. The navigation issue is unresolved.

The target environments completed five training episodes: zero successes, two collisions and three timeouts. Only three target timeout penalties were observed within this budget. This is actual target exposure but little complete-episode learning experience. Adding exposure and fixing learning semantics alone did not resolve the repeated-turning failure in this pilot.

A subsequent full-graph counterfactual changed only the clock from zero to one in the four initial development worlds. Relative pooled-feature shift was 32.72 percent and mean absolute action change was 0.1395. The clock was added to an already-trained controller through a new projection; preserved archive bytes do not mean preserved flight behavior. This newly measured transfer disruption needs calibrated verification before another pilot. It does not explain the original sensors-v3 zero-success results, which preceded the clock.

The complete frozen source manifest matched after training. All six original alias files and the original source ZIP and metadata retained their initial hashes. No alias was promoted. Detailed before/after episodes, source hashes, losses and exposure counters are in private artifacts and runs/training/timeout-correction-pilot-v1/status.json. The original independent final test remains unused. No training process remains running.

Cumulative substantive added transitions are 319,488 of the earlier 524,288 budget, leaving 204,800. Separate smoke verification remains excluded. The last checkpoint is runs/training/timeout-correction-pilot-v1/round-4/policy.zip; it is not a successful navigation model.
