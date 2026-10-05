# Planner follow-up: speed, clearance, and conditional recovery

October 5, 2026. These checks reuse rooms 8500011, 8500012, and 8500013, whose v55 failures were already inspected. They guide implementation and are not independent generalization evidence. Frozen v55 remains the demo default. No trained checkpoints are changed.

## Why the next correction was needed

[V56](planner-timeouts-v56-results.md) corrected an observed-free goal cell blocked by an inflated margin, but two rooms still timed out. In their final maps, six-neighbor connectivity showed that the start and goal belonged to the same traversable component. This does not guarantee a physical flight or adequate bounded search.

Room 8500013 found routes throughout its v56 flight but traveled substantial detours. Room 8500012 repeatedly saturated the 12,000-expansion search. Increasing cruising speed and changing clearance were therefore checked separately before combining them.

## Isolated changes and observed tradeoffs

| Version | Change relative to v56 | Goals / 3 | Collisions | Timeouts |
| --- | --- | ---: | ---: | ---: |
| v56 | Local observed-free goal margin | 1 | 0 | 2 |
| v57 | Clear-space cruise limit 2.6 instead of 1.8 units/s | 2 | 0 | 1 |
| v58 | Observed-free inflated cells admitted at cost 8 throughout the map; original speed | 1 | 0 | 2 |
| v59 | Combine v57 speed with v58 grid | 2 | 0 | 1 |
| v60 | v57 speed; enable known-free margin recovery only after search saturation | 3 | 0 | 0 |

V57 retains the 0.8 tight-margin speed, requested-direction braking, acceleration law, physics, and deadlines. It reaches room 8500013 at step 2,499, but room 8500012 still times out. Higher speed changes when observations are collected and can change the reconstructed map; it is not a replay of the same route with time compressed.

V58 preserves observed solids, unknown blocked margins, evidence, and top/bottom boundaries. Room 8500012 no longer saturates search in any sampled frame, but still times out. The rule trades conservative clearance for costly traversal of known-free cells. Collision checks remain active; three collision-free rooms do not establish broader safety.

V59 reaches room 8500012 at step 3,441 but regresses room 8500013 to a timeout. This is why combining individually useful changes is not automatically a successful correction.

| Room | v57 steps / outcome | v58 steps / outcome | v59 steps / outcome | v60 steps / outcome |
| --- | --- | --- | --- | --- |
| 8500011 | 1,628 / goal | 1,984 / goal | 1,745 / goal | 1,628 / goal |
| 8500012 | 3,534 / timeout | 3,534 / timeout | 3,441 / goal | 3,171 / goal |
| 8500013 | 2,499 / goal | 3,503 / timeout | 3,503 / timeout | 2,499 / goal |

## Offline diagnosis

Raising unknown-cell costs on a retained v56 map did not resolve room 8500012's capped search and could make room 8500013's search saturate too. Reversing the search direction also failed to resolve the capped room. These offline computations execute no physical transitions and are not navigation outcomes.

On room 8500012's final v57 map, a diagnostic 100,000-expansion limit found a route after 28,514 expansions, about 81.75 units long. This was an offline capacity probe only; live checks retained the original 12,000 cap. Admitting observed-free inflated cells at cost 8 found a roughly 52.10-unit route in 4,591 expansions on that same snapshot. The comparison identifies an interaction between reconstructed clearance and search effort, not an optimal or guaranteed executable route.

## Conditional candidate v60

V60 starts with v57 speed and normal v56 clearance. Only a failed search reaching 12,000 expansions activates known-free margin recovery for later plans in that episode. It does not run an extra search in the triggering decision. Recovery preserves observed solids, unknown blocked cells, boundaries, and the per-plan expansion cap. A new controller resets the recovery flag, so it cannot leak into another episode.

The candidate reached all three known goals, without collisions or timeouts. Margin recovery first appeared in room 8500012's sampled trace at decision 2,480, and did not activate in the other two rooms. Room 8500012 had one sampled capped search, compared with 53 in v57. The other two retained their v57 arrival steps. These observations support a targeted correction, not a broad safety or success-rate claim.

Regression checks cover conditional activation, uncapped failure, reset behavior, surface preservation, speed, and directional braking. Twenty-eight navigation checks passed. The frozen candidate source SHA-256 is `585e172043ada92b4779b857e8af80b7504420ab6e853dc487d9a2c1514c266d`; its inheritance dependencies are separately recorded in the local status. Preserve those sources together when reproducing the controller.

## Budget, integrity, and tooling

Each known-failure check has a 12,000-physical-transition cap. V57 and v58 each used 10,602; v59 used 10,509; v60 used 9,513. The four follow-up checks used **41,226 physical transitions**; including the preceding v55/v56 pair gives 62,430. Training transitions and optimizer updates are zero. No reserved test was accessed. Completed checks and failures remain in ignored `runs/diagnostics/planner-timeouts-v<version>/`; detailed evidence is retained under `private/`.

All checks use the full 167,184-neuron, 25,583,622-edge graph and the same three-instance flight/readout contract. Original alias hashes remain unchanged; the runner also protects frozen reference modules. Source hashes include the candidate's controller inheritance dependencies.

The plotter now handles near-goal frames without a recorded route reference. It marks those samples missing and reports their count, rather than inventing values. Sampled distances underestimate full paths, and reference reversals alone do not prove their cause.

V55's earlier prospective 13/16 remains its own historical result. Do not add these tuned successes to it. A selected correction needs a predeclared fresh development assessment before changing the operational default or claiming broader improvement.
