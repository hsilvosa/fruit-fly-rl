# Autonomous architectural curriculum 1 results

Completed on October 7, 2026 with 131,072 fresh PPO learning transitions, the full annotated connectome, and no planner assistance. Training took 3,690.579 seconds, excluding validation; peak allocated VRAM was 0.772 GiB. Finite losses, checkpoint reload, frozen sources and protected aliases all passed their checks. No reserved test was accessed and no checkpoint was promoted.

## Training lessons

There were 2,776 completed lesson episodes: 2,429 goals, 286 collisions and 61 timeouts. Every episode used a goal 1 metre from its original start. These adaptive training outcomes do not measure independent generalization or success on the original distant goals.

The first complete mastery round failed. The second passed, with at least six successes in eight episodes for all 15 training tasks. A third complete round was not available before the budget ended. Two consecutive passing rounds were required, so the curriculum never advanced beyond 1 metre. The 2 metre, 4 metre and original-goal training stages were not reached.

The fixed schedule spends 4,096 transitions on each task in turn. Consequently a complete round across all 15 tasks can require an entire schedule cycle even when later tasks complete many short episodes. Early episodes remain in the first round while the policy changes. This is a limitation of this pilot's progression schedule, not proof that longer lessons are unlearnable.

## Original-goal validation

Before training: zero goals and six collisions. After training: one goal, five collisions and zero timeouts.

| Scene | Goal | Collision | Timeout | Final distance (m) |
| --- | --- | --- | --- | --- |
| office-floor | False | True | False | 3.919 |
| apartment | True | False | False | 0.411 |
| street-block | False | True | False | 13.639 |
| atrium | False | True | False | 14.415 |
| warehouse | False | True | False | 4.255 |
| courtyard | False | True | False | 16.378 |

The apartment succeeds. The structured pilot without curriculum also had one goal out of six, but succeeded in the office and had one collision plus four timeouts. The curriculum therefore did not improve the observed overall validation goal count and did not retain that office success. These separate single-seed pilots do not establish a reliable ranking. The six validation situations reuse scene geometry and have now informed development; they are not independent unseen-building evidence.

## Handoff

Work is paused at the user's request. Before any new training, review the schedule so mastery can be checked across all tasks more promptly, preserve exposure to original navigation goals, and agree a bounded comparison. Keep the planner only as a reference or teacher, and evaluate learned actions separately. Do not resume this completed directory, promote this checkpoint, or consume the reserved test to tune these changes.

Local evidence: `runs/training/autonomous-architecture-curriculum-1/`; archived evidence and exact source bytes: `private/autonomous-architecture-curriculum-1-evidence/`. The earlier environment smoke used 128 learning transitions plus one reset probe; the complete runner smoke used 128 learning transitions and one PPO update. Both are separate verification, not part of this budget.
