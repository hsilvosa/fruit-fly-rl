# Architectural escape candidate results

Planner-1.4-exp.2 completed the original 21 inspected objectives at **18/21 goals, zero collisions and three timeouts**. It is not promoted: it fixes the warehouse aisle run but loses the previously successful apartment sofa-to-bedroom route. This is retained development evidence, not an independent sample or training result.

| Scene | Situation | Exp.1 outcome / steps | Exp.2 outcome / steps |
| --- | --- | --- | --- |
| office-floor | reception-to-meeting-room | Goal / 175 | Goal / 175 |
| office-floor | open-plan-to-private-office | Goal / 405 | Goal / 405 |
| office-floor | over-the-desks | Goal / 76 | Goal / 76 |
| apartment | sofa-to-bedroom | Goal / 1091 | Timeout / 1200 |
| apartment | study-to-bathroom | Timeout / 1200 | Timeout / 1200 |
| apartment | kitchen-low-to-high | Goal / 40 | Goal / 40 |
| street-block | street-traverse | Goal / 869 | Goal / 869 |
| street-block | intersection-turn | Goal / 1130 | Goal / 1232 |
| street-block | under-the-skybridge | Goal / 776 | Goal / 776 |
| street-block | through-the-passage | Goal / 920 | Goal / 920 |
| street-block | over-the-bus | Goal / 406 | Goal / 406 |
| atrium | lobby-to-first-gallery | Goal / 246 | Goal / 246 |
| atrium | void-climb-to-top-gallery | Timeout / 1200 | Timeout / 1200 |
| atrium | bridge-crossing | Goal / 252 | Goal / 252 |
| warehouse | aisle-run | Timeout / 1200 | Goal / 523 |
| warehouse | aisle-switch | Goal / 194 | Goal / 194 |
| warehouse | over-the-racks | Goal / 503 | Goal / 503 |
| warehouse | under-mezzanine-and-up | Goal / 167 | Goal / 167 |
| courtyard | gate-over-fountain | Goal / 221 | Goal / 221 |
| courtyard | arcade-walk | Goal / 443 | Goal / 308 |
| courtyard | courtyard-to-lobby | Goal / 315 | Goal / 315 |

The apartment bathroom and atrium climb remain timeouts. The street intersection still reaches its goal but takes 1,232 rather than 1,130 steps; the courtyard arcade reaches its goal in 308 rather than 443 steps. Unchanged cases retain their original step counts.

The complete graph executed 11,228 physical transitions in 382.59 seconds after initialization; peak allocated VRAM was 0.592 GiB. All original endpoints, scene geometry and deadlines were preserved. Source and protected-alias hashes matched. No training, optimizer update or reserved test occurred. Protocol SHA-256: `c8ffc2ad0be031784fffafce7c2ae103263554270afe64ec5c8647cc35b80bca`.

The broad stationary escape trigger is not sufficient for promotion. Next: inspect where the apartment regression activates and constrain escape commitment using observed execution evidence. Preserve the warehouse fix and all prior successes in the next bounded correction check. Exp.1 remains the demo default. Detailed artifacts are stored locally in private/architecture-escape-candidate.
