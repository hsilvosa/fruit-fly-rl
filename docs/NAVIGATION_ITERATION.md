# Navigation design

The controller must learn both progress toward the target and safe movement around obstacles. Reaching an objective in an open room does not establish the ability to navigate partitions, altitude changes or dead ends.

## Reward and control

The navigation reward supplies distance progress, a terminal goal reward and collision costs. These engineering choices are described in [Mathematics](MATHEMATICS.md). Direct target direction is available through the sensors; it is not discovered through biological vision.

Coordinated flight aligns heading and movement with acceleration, bank, altitude control and inertia. Changing the dynamics or sensor meaning requires a versioned checkpoint contract and explicit retraining or transfer. A visually improved animation does not demonstrate better navigation.

## Diagnosing a failure

Use validation records to distinguish early collisions, altitude errors, stopping, near-goal problems and inefficient detours. [Validation traces](VALIDATION_TRACES.md) retain commands, movement, neural features and contact geometry for bounded diagnostic inspection. Plots of existing arrays do not execute a policy.

Check progress together with success, collisions and timeouts. Fewer collisions obtained by remaining stationary are not successful navigation. Training reward totals across changed tasks are not a fair comparison, and short failed flights are not efficient routes.

## Testing a change

Predeclare a new independent suite, bounded budget, repeated initialization seeds and validation-only selection. Preserve unsuccessful experiments and original launch aliases. Assess the frozen winner once on its reserved final pool and report counts and uncertainty. Do not extend a budget or select a model after seeing that final result.

The project has tested sensor changes, reset curricula and observed-ray risk shaping under separate protocols. These hypotheses and their limits are public; detailed decisions and machine records remain private. See [Results](RESULTS.md), [Progressive maps](GEOMETRY_CURRICULUM.md) and the [Roadmap](../ROADMAP.md).
