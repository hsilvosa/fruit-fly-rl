# Temporal brain-feature comparison: verified results

Completed on 2026-10-04. Added memory did not demonstrate successful navigation on the original `large` distribution. Neither final controller reached a validation goal. The navigation problem remains unresolved; no checkpoint was promoted and no reserved final test was evaluated.

## Matched validation

Both arms started from the same preserved round-23 movement policy and copied optimizer state, with training seed 42. Both used the full annotated connectome, original sensors-v3, gamma 0.9995, unchanged rewards and external timeout bootstrapping. Four of eight environments trained on the original large map from initialization. The other four used the fixed stage-four mixture. The memory arm added a 64-unit GRU over 32 sampled historical brain features, spanning approximately 12.8 seconds. Its initial residual was zero and initial actor/critic predictions matched the source.

The same eight validation layouts, seeds 430000-430007, were assessed before training and once after each arm's full budget. The shared source achieved 0/8 goals, one collision and seven timeouts. These layouts were excluded from optimization, but are development validation, not the reserved final test.

| Controller | Added transitions | Original-large training transitions | Validation goals | Collisions | Timeouts | Mean final distance |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| current-features | 65,536 | 32,768 | 0/8 | 2 | 6 | 38.02 |
| brain-history | 65,536 | 32,768 | 0/8 | 1 | 7 | 36.62 |

Each 0/8 estimate has a Wilson 95% interval of approximately 0-32.4%. A single warm-start seed and eight layouts do not support a robust ranking. Fewer validation collisions in the memory arm do not establish improvement: its timeout count was higher and neither controller reached a goal.

## Training and integrity audit

The current-feature arm finished 12 original-large training episodes: zero goals, ten collisions and two timeouts. The memory arm finished 23: zero goals, 21 collisions and two timeouts. These stochastic training outcomes differ from deterministic validation and must not be conflated. Unfinished episodes at budget exhaustion are not counted as terminal outcomes.

All 16 saved round loss reports were finite. Live episodes continued across chunks two through eight in both arms. Each arm added exactly 65,536 transitions, including 32,768 on the unchanged original large task. The experiment added 131,072 transitions; cumulative substantive use is 450,560 of 524,288, leaving 73,728. The separate 128-transition smoke checks are verification, outside that experiment budget.

A completion audit recomputed the frozen Python source hashes, source checkpoint and metadata hashes, and all six original launcher alias hashes. All matched. Detailed hashes and outcomes are preserved locally in `private/brain-memory-comparison-v1-audit.json`; checkpoint and status records remain under `runs/training/brain-memory-comparison-v1`. No final-test evaluation or alias replacement occurred.

## Continuation point

This work is stopped for the requested short session. No new training experiment has been launched. Both final checkpoints are retained for diagnosis, without selecting a successful model. The next useful step is to inspect reward components and observed flight traces around necessary detours and partition approaches. The previous continuity, exposure and memory diagnoses identified real limitations, but their corrections have not yet produced original-large navigation success. Avoid spending the remaining budget on an unchanged repeat before identifying a measurable failure mechanism. No biological advantage is established.
