# Large-room corrections and maze navigation

This development work began on October 6, 2026. The task is to preserve large-room navigation while extending the explicit planner to the existing maze. A generated feasible maze is not a navigation result. The learned-policy objective remains separate.

## Room contract correction

Earlier planners assumed a 48 x 48 x 16 room when decoding the normalized goal distance and altitude. The maze is 64 x 64 x 20. Its altitude exceeded the original occupancy grid. Planner-1.3-exp.1 uses the declared room dimensions for both normalization and grid bounds, and commits to a local route reference until it is reached, blocked, or six seconds old. Existing measured planners remain unchanged and reject the maze contract.

Room dimensions are allowed configuration. Hidden obstacle boxes, true pose, generator seed, opening centers, and the certified route are not controller inputs. The controller estimates pose and reconstructs ranges from the full-connectome readout. True geometry is used afterward to audit flights.

## Development attempts

The two retained large rooms are 9500014 and 13000013. Their original episode deadlines remain 3,480 and 3,499 decisions. They were already inspected; corrections on them are development evidence, not independent generalization.

| Candidate | Mechanism | Retained large outcomes | Maze outcomes |
| --- | --- | --- | --- |
| planner-1.3-exp.1 | Room-aware decoding and committed references | One goal at 3,275 steps; one timeout | Two timeouts, no collisions |
| planner-1.3-exp.2 | Increase unknown-cell cost from 2.8 to 12 | Two timeouts; regression | Not run |
| planner-1.3-exp.3 | Detect broad vertical surfaces and through-rays; approach an opening before crossing | Two timeouts | Not run |
| planner-1.3-exp.4 | Angular-distance clustering, tall-surface filter, and completed-plane memory | Two goals at 3,343 and 2,056 steps; no collisions | Two timeouts, no collisions |
| planner-1.3-exp.5 | Consider multiple observed wall candidates and partially occluded vertical surfaces | Not measured | Two timeouts; regression |
| planner-1.3-exp.6 | Require beacon-aligned fitted surfaces and stronger support | Not measured | Two timeouts; regression |
| planner-1.3-exp.7 | Scale vertical surface support with observed plane distance | Not yet measured | Bounded retained diagnostic in progress |

The exp.4 large-room flown distances were 218.23 and 149.39 units; final goal distances were 0.418 and 0.431. Both arrivals met the unchanged deadlines. This fixes two retained cases; broader large-room verification is still required.

The maze has eight narrow partitions, four dead-end branches, 192 boxes, and unchanged openings of 2.4 x 2.8. Seeds 14000000 and 14000001 have original deadlines of 6,736 and 6,352 decisions. Exp.1 timed out at goal distances 41.39 and 37.91. Exp.4 improved these to 22.71 and 29.69, but still failed. Its traces show partial partition progress and prolonged searches along walls. Progress is not success.

## Opening inference

The portal candidates fit vertical planes to reconstructed panoramic range endpoints. A ray that travels beyond a fitted surface suggests an opening. Intersections are clustered in wall tangent and altitude coordinates; the controller plans to a near-side approach and then a beyond-wall crossing reference. Candidate centers come from these observations, not from the map generator.

Exp.3 sometimes reacquired crossed surfaces and fitted clutter. Exp.4 requires a tall observed span and remembers completed planes. Its acceptance of a single through-ray provides an approach seed, not a proof that an opening fits the body. The debug counter `portal_crossings` counts inferred planes passed; it must not be reported as certified maze gates crossed.

Exp.5 tests another failure mode: the highest-support surface can have no visible opening while a secondary surface does. Its search considers multiple distinct planes and tolerates partial vertical occlusion. The sources and budget are recorded before launch. Results must be added before selecting it.

## Verification and limits

Every flight uses all 167,184 annotated neurons and 25,583,622 aggregated directed connections. There are zero training transitions and zero optimizer updates in these planner checks. A full regression run passed 404 tests before exp.5 was introduced.

Existing policy aliases and frozen planner implementations are protected by before/after SHA-256 hashes. The reserved final pools are not accessed. Diagnostics record all outcomes, physical transitions including inactive vector slots, source hashes, layout hashes, and elapsed compute. Detailed records stay in local `runs/diagnostics` and `private` directories; public evidence summarizes verified results.

The maze retry uses retained maps. It cannot establish independent generalization, a biological wiring advantage, a learned policy, or optimal routes. The default remains planner-1.0. Completion requires actual maze arrivals, retained large-room regression checks, a predeclared fresh development suite, and a rendered demonstration.

## Running experimental controllers

```powershell
.\launch-observed-map.cmd --controller-version 1.3-exp.4 --map-profile large --seed 9500014
.\launch-observed-map.cmd --controller-version 1.3-exp.5 --map-profile maze --seed 14000000
```

The second command currently selects a development candidate, not a verified maze solution. Opening a demo does not train or modify weights.

## Relevant formulas

The neural beacon returns a unit body-frame goal direction and distance normalized by the room diagonal. The room-aware decoder uses `distance * norm(room_size - 0.32)` and rotates the reconstructed vector into its estimated frame. Altitude uses `normalized_altitude * room_height`. These are engineering sensor contracts; the subtraction accounts for the simulation body margin.

For a candidate vertical plane with unit horizontal normal `n` and signed distance `d`, a ray direction `u` intersects at `t = d / dot(u_xy, n)`. A finite positive intersection within range becomes a through-ray candidate when its observed range exceeds `t + 1`. The one-unit allowance separates a surface return from evidence beyond it; it is not a collision clearance certificate.

Candidate intersections are grouped in tangent/altitude coordinates. Exp.4 uses radius `min(3.2, max(0.9, 0.35 + 0.17 * median(t)))`. The center is their coordinate-wise median projected onto the fitted plane. Selection minimizes approach distance plus 0.3 times remaining goal distance. The near-side reference is `center - 1.1 * normal`; the crossing reference is `center + 1.3 * normal`. Local occupancy search and flight safety remain active.

Exp.5 has a recorded unit-test failure: with a simple wall and centered opening it accepts a diagonal fit centered away from the real hole. This is a strict expected failure retained as evidence, not a passing geometry check. A subsequent candidate requires fitted normals to align with the observed initial beacon direction and restores the minimum 80 supporting endpoints. This adds a straight-corridor structural assumption; it is not a general solver for arbitrarily oriented mazes. It receives no true world heading or partition coordinates.


The subsequent full regression passed 408 tests with one strict expected failure for the discarded exp.5 detector. A 20-step offscreen maze flight with exp.6 produced finite full-graph activity, a rendered scene, complete transition chunks, and a clean archive integrity report. No complete episode was measured by that rendering check.


Exp.6 also regressed both retained maze flights, ending 56.04 and 44.43 units from the goal. Passing its simple opening fixture did not establish reliable surface inference in clutter. Exp.7 returns to the strongest-surface selection of exp.4 and changes the minimum vertical span to `min(0.65 * room_height, 3 * plane_distance)`. This is a development hypothesis about angular near-wall coverage; its full-flight results are pending.

[Per-room development outcomes](evidence/maze-navigation-development-results.md) retain every completed large and maze result from this iteration.
