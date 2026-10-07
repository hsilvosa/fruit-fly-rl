# Initial architectural navigation results

October 7, 2026. Planner-1.4-exp.1 reached **18/21 original objectives (85.7%)**, with **zero collisions and three timeouts**. All 21 cases completed their flight or physical deadline; none were incomplete or unattempted.

This is a development check on six inspected synthetic designs, using seed 42 for each situation. It is not independent real-world generalization, a reserved test, or a learned-policy result. The controller uses explicit planning over decoded full-connectome features.

## Results by scene

| Scene | Goals | Collisions | Timeouts |
| --- | ---: | ---: | ---: |
| office-floor | 3/3 | 0 | 0 |
| apartment | 2/3 | 0 | 1 |
| street-block | 5/5 | 0 | 0 |
| atrium | 2/3 | 0 | 1 |
| warehouse | 3/4 | 0 | 1 |
| courtyard | 3/3 | 0 | 0 |

## Original situations

| Scene | Situation | Outcome | Physical steps | Final goal distance (m) |
| --- | --- | --- | ---: | ---: |
| office-floor | reception-to-meeting-room | Goal | 175 | 0.442 |
| office-floor | open-plan-to-private-office | Goal | 405 | 0.445 |
| office-floor | over-the-desks | Goal | 76 | 0.396 |
| apartment | sofa-to-bedroom | Goal | 1091 | 0.420 |
| apartment | study-to-bathroom | Timeout | 1200 | 3.810 |
| apartment | kitchen-low-to-high | Goal | 40 | 0.438 |
| street-block | street-traverse | Goal | 869 | 0.438 |
| street-block | intersection-turn | Goal | 1130 | 0.394 |
| street-block | under-the-skybridge | Goal | 776 | 0.419 |
| street-block | through-the-passage | Goal | 920 | 0.422 |
| street-block | over-the-bus | Goal | 406 | 0.416 |
| atrium | lobby-to-first-gallery | Goal | 246 | 0.445 |
| atrium | void-climb-to-top-gallery | Timeout | 1200 | 4.152 |
| atrium | bridge-crossing | Goal | 252 | 0.414 |
| warehouse | aisle-run | Timeout | 1200 | 12.374 |
| warehouse | aisle-switch | Goal | 194 | 0.439 |
| warehouse | over-the-racks | Goal | 503 | 0.414 |
| warehouse | under-mezzanine-and-up | Goal | 167 | 0.409 |
| courtyard | gate-over-fountain | Goal | 221 | 0.418 |
| courtyard | arcade-walk | Goal | 443 | 0.435 |
| courtyard | courtyard-to-lobby | Goal | 315 | 0.446 |

## Execution and integrity

The full 167,184-neuron, 25,583,622-edge graph executed 11,829 physical transitions with CUDA sensing. Execution took 386.97 seconds after initialization and peaked at 0.592 GiB allocated VRAM. Starts, goals, geometry and original per-case deadlines were preserved. There were zero training transitions, zero optimizer updates and no reserved-test access.

The protocol SHA-256 is `f19f790a17be03041c21d5bae1a6264bda75702abe143d45e855f19fbadd0968`. Frozen runtime sources matched, and all six protected checkpoint aliases matched before and after. Detailed protocol, status and sampled traces are preserved locally in private/architecture-initial-navigation-evidence. The public summary records the existing run rather than rerunning evaluation.

## Remaining work

Diagnose the apartment bathroom route, atrium climb and warehouse aisle timeout from the saved traces before changing the controller. Preserve these original objectives and successful cases as regression checks. Any correction needs its own frozen version and bounded protocol. After retained checks pass, use separately declared held-out designs and varied headings; do not relabel these inspected cases as fresh evidence. Actual-building reconstruction, dynamic obstacles and visual sensing remain future stages. See the [navigation protocol](../ARCHITECTURAL_NAVIGATION.md).
