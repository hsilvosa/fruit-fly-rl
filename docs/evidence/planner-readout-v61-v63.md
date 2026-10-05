# Distance-readout diagnosis and unsuccessful route corrections

These October 5 checks reuse two inspected v60 development failures. They are design evidence, not independent generalization measurements. All flights advance the full prepared graph: 167,184 neurons and 25,583,622 directed aggregated connections. None trains a movement policy, changes a checkpoint, or accesses a reserved test.

## Why the fly stopped

In room 9500001, v60 repeatedly found routes but travelled only 0.61 units before its deadline. The requested speed became zero despite a nearby waypoint. A 128-transition audit compared the planner's decoded ranges with the simulator's sensor readings after each action had already been chosen. Raw readings were used only for this diagnostic, never to choose actions.

There were 104 zero-speed samples, and all 104 had raw requested-direction clearance greater than the 0.27-unit stopping threshold. At one representative sample, a panoramic range decoded as approximately 0.223 units while its raw range was approximately 0.383. The decoded point entered the planner's 0.25-unit braking tube and yielded approximately 0.048 units of forward clearance. The same raw observation yielded approximately 10.05 units along that requested direction. This supports readout interference as the immediate cause of this stationary flight; it does not establish that every timeout has that cause.

The motion-stable reader retained five percent projected recurrent context in every panoramic channel. That is reasonable as a contextual feature, but the planner interpreted the range coordinates as literal physical distances. A contextual offset could therefore trigger a false obstacle stop.

## V61: make distance coordinates stable

[DistanceStableActivityBrain](../../fly_rl/connectome/distance_readout.py) retains the same full recurrent graph and fixed sensory projection. It changes only how activity is decoded: all base and panoramic distance coordinates cancel projected recurrent drive, while panoramic closing-speed coordinates retain five percent context. The controller inherits v60's mapping, search, recovery, braking thresholds, speed, collision rules, and deadlines unchanged.

For the fixed projection reader, let `d` be the inverse-activation drive reconstructed from previous and current neural states, `r = W h_previous` the recurrent drive, and `L` the numerically stabilized projection inverse. The emitted features are:

```text
features = L(d - r) + gain * L(r)
v60: gain[0:269] = 0; gain[269:3869] = 0.05
v61: gain[0:2069] = 0; gain[2069:3869] = 0.05
```

Indices 269–2068 are the 1,800 panoramic distances; 2069–3868 are their closing speeds. Reconstruction consumes full previous/current activity and the known projection, not a raw-sensor bypass. This engineered information bound should not be described as biological perception or proof of a connectome advantage. The readout receives its own version and fingerprint; old checkpoint contracts are rejected rather than silently reinterpreted.

## Known-case outcomes

Each flight declared a maximum of 4,000 physical transitions before execution. A timeout preserves the original route-dependent deadline.

| Version | Known room | Outcome | Steps | Flown distance | Ending goal distance |
| --- | ---: | --- | ---: | ---: | ---: |
| v61 | 9500001 | Goal | 2,276 | 195.70 | 0.43 |
| v61 | 9500014 | Timeout | 3,480 | 312.39 | 17.92 |
| v62 | 9500014 | Timeout | 3,480 | 274.45 | 19.50 |
| v63 | 9500014 | Timeout | 3,480 | 296.47 | 16.71 |

All four flights had zero collisions. They used 12,716 physical transitions in total, separately from the 128-transition prefix audit. Zero optimizer updates were performed. Preserved aliases and frozen controller references match before/after.

V61 resolves the stationary known case, but the other room remains unresolved. The following attempts are retained because a shorter flown path or a more consistent map is not equivalent to reaching the target.

## V62: retain a clear local route

[PersistentRouteController](../../fly_rl/navigation/persistent_route.py) keeps an existing complete route if its first eight units remain traversable in the current grid. It samples that prefix at no more than 0.1-unit spacing and replans on a blockage or three checks with less than 0.03-unit movement. Far-future map changes alone no longer replace a locally usable route. Actual flight safety checks remain active.

The known room still timed out. Its shorter flown distance does not establish improved navigation. This version is experimental and is not selected as a solution. Its `plan_reused` trace field distinguishes reuse from a new search; a retained `found` value describes the earlier search, not a fresh search outcome.

## V63: reconcile free rays and virtual surfaces

The original mapper interpolates surfaces between neighboring ray endpoints. A static audit of nine previously inspected poses found 92–150 cells per frame classified occupied after virtual interpolation, despite a current ray passing through them. Directly measured endpoint cells were excluded from that count. A ray traversing a voxel does not prove that every part of that voxel is empty, so this audit identifies conflicting evidence rather than a guaranteed safe corridor.

[RayConsistentController](../../fly_rl/navigation/ray_consistent.py) preserves directly measured hits and suppresses virtual surface writes over current free-ray cells. It retains the original evidence increments, free carving, grid resolution, flight safety, and deadlines. Component tests confirm that direct endpoint evidence is retained and input readings are not changed. The full-graph flight still timed out, so this correction is not a navigation solution.

The v63 runner received a metadata-only graph-fingerprint addition after this pilot had initialized. Its recorded launch hash therefore differs from the current runner file. Controller/readout sources and preserved references did not change. This pilot remains known-case diagnostic evidence; it is not represented as a frozen prospective comparison.

## Verification and next measurement

Algebra tests use an explicitly synthetic sparse graph to check channel reconstruction and independent state reset. A temporary untrained checkpoint was saved/reloaded with identical actions and zero lifetime training transitions; loading it with the older motion-stable readout is rejected. These tests do not replace the full-connectome flight results above.

V60 and v61 are separately frozen for a new sixteen-room development comparison on seeds 10000000–10000015. Their different readouts are declared explicitly, while graph data, projection, geometry, layouts, dynamics, sensor history, and budgets must match. The comparison can reveal regressions as well as gains. See the [development protocol](../PLANNER_DEVELOPMENT.md); both arms have now completed. V60 reached 15/16 with one collision, whereas v61 reached 13/16 with two collisions and one timeout. This regressed suite does not support promoting v61. The [paired report](planner-v61-development-results.md) retains all rooms and confidence intervals.
