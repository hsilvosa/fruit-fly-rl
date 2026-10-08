# Architectural closing results

October 7, 2026. Work pauses at the user's request after the active bounded check completed. No further experiments are authorized by this closing step. Maze experiments remain closed.

## Measured progression

| Controller | Original goals | Collisions | Timeouts | Decision |
| --- | ---: | ---: | ---: | --- |
| Planner-1.4-exp.1 | 18/21 | 0 | 3 | Current demo default |
| Planner-1.4-exp.2, broad escape | 18/21 | 0 | 3 | Not promoted; warehouse fix trades away apartment success |
| Planner-1.4-exp.3, planned portal escape | 19/21 | 0 | 2 | Preserves all 18 original successes; candidate awaiting further verification |

The architectural scenes are six inspected synthetic designs, not reconstructions of real places. These are retained development checks with seed 42, not independent generalization results. Controllers use explicit planning from full-connectome neural features; these checks did not train weights.

## Final candidate results

| Scene | Situation | Outcome | Physical steps |
| --- | --- | --- | ---: |
| office-floor | reception-to-meeting-room | Goal | 175 |
| office-floor | open-plan-to-private-office | Goal | 405 |
| office-floor | over-the-desks | Goal | 76 |
| apartment | sofa-to-bedroom | Goal | 1091 |
| apartment | study-to-bathroom | Timeout | 1200 |
| apartment | kitchen-low-to-high | Goal | 40 |
| street-block | street-traverse | Goal | 869 |
| street-block | intersection-turn | Goal | 1130 |
| street-block | under-the-skybridge | Goal | 776 |
| street-block | through-the-passage | Goal | 920 |
| street-block | over-the-bus | Goal | 406 |
| atrium | lobby-to-first-gallery | Goal | 246 |
| atrium | void-climb-to-top-gallery | Timeout | 1200 |
| atrium | bridge-crossing | Goal | 252 |
| warehouse | aisle-run | Goal | 523 |
| warehouse | aisle-switch | Goal | 194 |
| warehouse | over-the-racks | Goal | 503 |
| warehouse | under-mezzanine-and-up | Goal | 167 |
| courtyard | gate-over-fountain | Goal | 221 |
| courtyard | arcade-walk | Goal | 308 |
| courtyard | courtyard-to-lobby | Goal | 315 |

Exp.3 restricts the exp.2 escape to blocked portal crossings for which a route exists. Warehouse aisle-run now reaches its goal in 523 steps. The apartment sofa-to-bedroom success and all other prior successful cases are retained. Courtyard arcade-walk improves from 443 to 308 steps; every other previously successful case retains its step count. Bathroom navigation and the atrium climb remain unresolved.

Execution used the complete 167,184-neuron, 25,583,622-edge graph with CUDA sensing: 11,017 physical transitions, 377.03 seconds after initialization and 0.592 GiB peak allocated VRAM. All original endpoints, geometry and physical deadlines were preserved. Frozen sources and all six protected checkpoint aliases matched. There were zero training transitions and optimizer updates, and no reserved-test access. Protocol SHA-256: `ffafe83749680105b2fe7ea391d45642e76cbe2dca6984ca2a2bb39519f5ea6c`.

## Resume from here

Keep exp.1 as the demo default until candidate rendering, controls and an explicitly declared held-out check have passed. Diagnose the apartment same-cell/no-path deadlock separately from the atrium portal/altitude behavior; the portal-only escape does not solve either. Preserve exp.3's warehouse fix and the 18 prior successes as regression requirements. Do not shorten objectives, change collision margins or reuse inspected scenes as fresh evidence. No process remains running after the check. Detailed run artifacts are preserved locally in private/architecture-portal-escape-candidate.
