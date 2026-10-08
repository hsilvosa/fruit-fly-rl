# Architectural full-connectome integration

October 7, 2026. The revised architecture-0.2 scenes now have a public flight-world adapter, full-connectome environment and separate known-dimension explicit planner (planner-1.4-exp.1). This begins architectural runtime integration; it does not establish reliable navigation.

The six original designs and their starts/goals remain unchanged. The world uses coordinated dynamics, swept 0.16-meter body collision checks, physical room boundaries and all v6 sensors. The planner receives room dimensions and reconstructed neural features, without a reference route or hidden layout. Its 0.25-meter grid is a separate architecture contract and does not change historical maze controllers. Scene selection clears brain state and history.

## Verification

Forty-nine focused world/scene tests passed. They cover all 21 original situation observations, altitude and goal decoding, grid bounds, independent resets, thin solid glass, physical ceilings, invalid situation indices and policy input validation.

A bounded CUDA smoke executed the complete 167,184-neuron, 25,583,622-edge graph with segmented dual readout and CUDA sensor generation. It ran 48 physical transitions with finite observations, actions and rewards, zero collisions, zero training transitions and zero optimizer updates. All protected checkpoint alias hashes matched before and after. The active phase took 3.47 seconds after initialization; peak allocated VRAM was 0.592 GiB for this single-environment smoke.

| Scene | Transitions | Displacement, meters | Collisions |
| --- | ---: | ---: | ---: |
| office-floor | 8 | 0.2321 | 0 |
| apartment | 8 | 0.1114 | 0 |
| street-block | 8 | 0.2524 | 0 |
| atrium | 8 | 0.2294 | 0 |
| warehouse | 8 | 0.2524 | 0 |
| courtyard | 8 | 0.1808 | 0 |

Eight transitions per scene cover 0.4 seconds of simulated time. These short displacements do not prove doorway traversal, complete routes, target arrivals, efficiency or generalization. Situation zero was used in each scene, with seed 42. The scenes are inspected development assets, not independent test evidence or reconstructions of actual places.

The interactive architectural launcher, material rendering, full-route checks, scene-switch controls and separate brain-window verification remain pending. No architectural training process is running. Detailed smoke evidence and alias hashes are retained in private/architecture-fullgraph-smoke-evidence.json; the console and original report are in reports.
