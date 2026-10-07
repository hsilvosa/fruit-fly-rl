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
