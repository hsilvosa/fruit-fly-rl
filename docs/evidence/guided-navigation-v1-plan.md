# Guided initialization of a brain-feature movement policy

The reward-only correction added 32,768 original-large transitions but achieved 0/8 development validation goals, with one collision and seven timeouts. Training also finished with no goals. The requested original-large navigation improvement remains unproven. This next intervention addresses the absence of successful long trajectories during exploration, rather than repeating the unchanged objective.

## Training assistance and information boundary

A training-only geometric teacher follows the certified path with coordinated 3D velocity: horizontal and vertical desired velocity are components of the same vector. It waits to turn before accelerating and slows at corners. Physical diagnostic rollouts completed four original-large optimization maps within their normal deadlines, with all 112 boxes retained. This demonstrates the teacher's behavior on these maps; it is not learned-policy performance.

The student uses a 64-unit GRU over 32 sampled historical connectome-feature frames, stride eight, plus current activity. It starts from the preserved round-23 actor and an initially zero temporal residual. Only brain features enter its tensors. Teacher waypoints, map boxes, route indices, absolute pose and teacher actions are supervision or collector state; they are never appended to sensors or inference observations. The geometry and physical ground truth therefore assist training and must be disclosed. This is imitation followed by PPO, not unaided reinforcement learning and not a biological learning claim.

Ordinary evaluation and demo instantiate the standard FlightWorld and the learned policy. They do not construct or call the teacher or route-distance training reward. Successful teacher rollouts must not be counted as student success. Policy checkpoints retain no live teacher or route map.

## Frozen remaining budget

Total added transitions: 40,960, exhausting the remaining original 524,288 cap after 483,328 used. All eight environments use the unchanged original large profile and only the 112 declared optimization layouts, disjoint from 16 withheld practice layouts and all eight development validation seeds.

- Collect 24,576 teacher-controlled transitions continuously in three 8,192-transition chunks. Fit the actor and temporal extractor for exactly 2,048 minibatch updates of 256 records, balancing turn examples and ordinary flight. Critic parameters are excluded from this fit.
- Collect 8,192 further transitions under a per-action mixture: teacher probability 0.8, otherwise the deterministic student. Label all visited states with teacher actions, then fit the actor for 512 further updates. These are guided training observations, not evaluation.
- Fit the critic for 512 updates to discounted guided returns, stopping at terminal boundaries and using zero continuation for the unfinished data suffix. Keep actor/extractor fixed during this critic fit. This is an approximation for initialization, not an exact value guarantee.
- Set initial action standard deviation to exp(-2), reset PPO Adam after supervision and perform 8,192 PPO transitions at learning rate 0.0001, gamma 0.9995 and target KL 0.01. Retain the training-only obstacle-aware progress objective. The live episode/history state continues into this phase. Supervised updates reuse existing records and are counted separately from environment transitions.

The actor minimizes weighted squared action error, with weights (1,1,2,2) for forward, lateral, vertical and yaw commands. The teacher labels are targets, not inference inputs. The critic minimizes squared error to the bounded discounted-return estimate. PPO then uses its ordinary clipped objective. These combined changes are one development intervention; the experiment cannot isolate their individual causal effects.

Measure only the final student checkpoint once on the same eight development validation layouts, without the teacher. These layouts already informed development and are not a reserved independent test. Keep original aliases and source checkpoint unchanged. Freeze all source/configuration and geometry hashes before launch, record actual teacher/student action counts and finished training outcomes, finite losses and checkpoint reload. Stop on completion/error; do not exceed the budget or consume a reserved final pool automatically.
