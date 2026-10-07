# Architectural adapter contract checks

October 7, 2026. The private architectural world prototype was checked against all six user-revised architecture-0.2 scenes. These are original realistic designs, not reconstructions of actual buildings or streets.

| Scene | Isolated solids checked | Boundary-adjacent solids excluded from the isolated fixture |
| --- | ---: | ---: |
| office-floor | 365 | 39 |
| apartment | 108 | 29 |
| street-block | 224 | 0 |
| atrium | 165 | 23 |
| warehouse | 383 | 12 |
| courtyard | 97 | 4 |

Each isolated fixture places the fly outside one solid, checks the ray distance to its surface, then verifies a collision and unsuccessful termination under the existing swept body collision model. The fixtures include solid glass and thin parts. They do not test combined-scene route accessibility or a navigation controller. Boundary-adjacent solids excluded from these fixtures remain in the scene collision data; exclusion is a fixture limitation, not removal from the simulation.

All six scenes also passed six physical room-boundary checks each, including floor and ceiling. Full-scene initial observations contain 3,869 finite sensor values. Reset restores position, heading, zero velocity, action memory and episode counters reproducibly. Snapshot scene fingerprints match the source geometry; reference polylines are absent from controller-facing snapshots and world reference routes.

No brain flights, training or policy optimization were performed by this check. GPU full-connectome integration, complete autonomous routes, rendering and launch controls remain unverified. Detailed named-solid checks, geometry fingerprints and the private runner are retained in private/architectural-collision-contract-checks.json and private/check_architectural_collision_contract.py.

## All 21 situation input contracts

The private room-dimension controller draft was checked at the original start and goal of every situation. All 21 sensor vectors are finite and have 3,869 coordinates. Decoded altitude and goal distance/direction match the world sensor contract: the largest goal-vector error is 0.000003864 meters and the largest altitude error is 0.000000239 meters. Both estimated start and goal lie inside the declared draft grid. Each seed reset reproduces the original pose, target and observation. The world exposes no reference polyline to the controller.

The draft uses a separate 0.25-meter architectural grid; this does not alter frozen maze or large-room controllers. These initial-state checks do not prove grid performance, continuous pose estimation, doorway traversal or neural reconstruction accuracy during a flight. The situation evidence records each source-scene hash, start, goal and physical deadline in private/architectural-situation-contract-checks.json. No brain flight, optimizer update or training transition occurred.
