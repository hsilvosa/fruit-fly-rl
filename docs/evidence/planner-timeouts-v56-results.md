# Planner timeout diagnosis and local goal-margin correction

Verified on October 5, 2026. This is a bounded correction on three already inspected development failures, not an independent test. The operational demo still uses frozen v55. Experimental v56 is available through the diagnostic runner only.

## Problem and hypothesis

V55 previously reached 13 of 16 prospective development goals without collisions. Rooms 8500011, 8500012, and 8500013 timed out. Their existing traces showed long detours and changing route references. The first two repeatedly exhausted the 12,000-expansion search limit; the third found routes throughout. Increasing that limit alone would not explain the third failure.

We instrumented the same three rooms to record the goal cell's evidence and traversal cost, route references, search effort, commands, and estimated-pose error. Simulator poses are used after action selection for auditing only; the controller does not receive them. Final snapshots preserve observed evidence and routes. Visited/frontier arrays were not recorded, so the figures do not claim to show them.

The full graph remains active: 167,184 neurons and 25,583,622 directed edges. Both checks use three parallel instances, the `large` profile, coordinated flight, sensors v6, eight history frames at stride eight, and the stable motion readout. Physics, deadlines, search limits, and collision detection are unchanged.

## Measured cause and correction

In room 8500011 the goal was observed as free, but the inflated obstacle safety margin made its cell impassable. All 75 sampled capped searches coincided with that blocked goal. No sampled goal cell was itself classified as solid. Maximum measured position error was below 0.003 units in every room; these checks do not support pose drift as the main cause.

V56 changes only grid construction. If the goal cell has negative evidence (observed free) but infinite traversal cost, it admits observed-free margin cells within one cell of the goal at cost 8. It retains observed solids, unknown blocked cells, and the top and bottom grid boundaries. It does not erase observations, change flight weights, increase search capacity, or extend deadlines. The local allowance is a reduction in conservative clearance, not a physical collision exemption; its broader safety has not been established.

Four synthetic regression checks verify exact-goal reachability, solid preservation, refusal to relax unknown or solid goals, and locality/boundary preservation. Together with the existing navigation checks, ten tests passed.

## Outcomes

| Room | V55 outcome / steps | V56 outcome / steps | V55 / V56 ending distance |
| --- | --- | --- | --- |
| 8500011 | Timeout / 3,345 | Goal / 1,939 | 9.804 / 0.403 |
| 8500012 | Timeout / 3,534 | Timeout / 3,534 | 26.763 / 26.763 |
| 8500013 | Timeout / 3,503 | Timeout / 3,503 | 14.086 / 14.086 |

Both checks had zero collisions. V55 reached 0/3 goals; v56 reached 1/3. This is a targeted correction on known failures, not a new overall success estimate. Do not combine this tuned result with the original 13/16 to claim 14/16 independent performance.

For room 8500011, sampled capped searches fell from 75 to zero and requested-reference direction reversals over 90 degrees fell from 38 to one. Sampled path length fell from 193.16 to 131.53 units. These lengths underestimate full flight paths because recording samples every twenty decisions. Direction changes describe references, not a causal proof of oscillation.

Room 8500012 still had 49 sampled capped searches, with an unknown but traversable goal cell, and 23 reference reversals. Room 8500013 had no capped samples, found a route in every recorded sample, and had 18 reversals. Their unresolved failures require examination of route execution, detours, and remaining time rather than assuming the goal-margin correction applies everywhere.

The new baseline reproduces the three historical failures, but its paths are not bit-identical to the earlier sixteen-instance run. Batch size and numerical effects can alter subsequent decisions. The baseline/candidate checks here use the same three-instance contract.

## Budget and preservation

Each run was capped at 12,000 physical environment transitions. Each used 10,602, for **21,204 total**, below the declared 24,000 limit. Finished instances continue stepping in the vector batch while unfinished instances complete; those physical transitions are counted too. They are not additional scored episodes. There were **zero training transitions, zero optimizer updates, and no reserved-test access**. Both processes completed; no training process was left running.

Elapsed time after runner initialization was 163.75 seconds for v55 and 139.68 seconds for v56. This is not a general throughput comparison: episode lengths and search effort differ.

All protected artifacts retained identical before/after SHA-256 hashes in both runs:

| Artifact | SHA-256 |
| --- | --- |
| `fly_rl/navigation/observed_map.py` | `faec0e96a8fb6e26a88675a25c7fb4468593aca481e70a4e50d463c621053dd2` |
| `runs/dense-flight-policy.json` | `0ca02c89a6e17d16cfd949a56d46909cdf8638758a4536953e3e3d8ecef5e2db` |
| `runs/dense-flight-policy.zip` | `085963d6e95b2a25647e3e6dd7ad2dc61f8f3c61bbfaaf3ce0db2c067a287d66` |
| `runs/dense-policy.json` | `88c3e01eb7926dedfc1679f23b4a92c3783384782ad4203013afa8d38fe4e3c3` |
| `runs/dense-policy.zip` | `db0839a921ae8775bbad9dbea62c28ab3752d33dad0e8edcfa72c7dc1318cab6` |
| `runs/navigation-policy.json` | `aa47f7ef830c491958a16bd121497c703d689b2a9717c566ad9888de5815460f` |
| `runs/navigation-policy.zip` | `2aa3469b6c56fa7f29c56399a7737b29c1870432e005714782d8efe23bf6be01` |

## Reproduction and retained evidence

From the repository root, with prepared data and CUDA dependencies, the following commands explicitly run bounded diagnostics. Use new output directories; the runner refuses to overwrite an existing one. Running them again requires a new declared budget.

```powershell
.\.conda\python.exe -s scripts/check_planner_failures.py --controller v55 --output runs/diagnostics/planner-timeouts-v55 --cap 12000
.\.conda\python.exe -s scripts/check_planner_failures.py --controller v56 --output runs/diagnostics/planner-timeouts-v56 --cap 12000
```

Offline plotting reads saved records and executes no environment transitions:

```powershell
.\.conda\python.exe -s scripts/plot_planner_diagnostics.py runs/diagnostics/planner-timeouts-v56 --output reports/planner-timeouts-v56
```

Each ignored run directory contains `status.json`, `trace.json`, and three `map-<seed>.npz` snapshots. Generated report directories contain trajectory/search/control plots, goal-altitude map slices, and `summary.json`. The slice distinguishes observed evidence from inflated traversal costs; a route's XY projection can cross a solid at a different altitude. Local detailed evidence stays outside Git; this public report retains aggregate outcomes and preservation hashes.

## Next work

Priority 1 is partially implemented: one concrete blockage is corrected, two failures remain. Diagnose route-reference advancement and detour decisions in rooms 8500012 and 8500013 using the retained traces before another bounded intervention. Keep v55 frozen and v56 experimental. Only after a candidate addresses the known cases should a fresh prospective protocol measure robustness. No learned-navigation or biological advantage follows from these planner checks.
