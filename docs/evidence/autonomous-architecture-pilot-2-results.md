# Autonomous architecture pilot 2 results

The structured PPO policy completed 131,072 training transitions on October 7, 2026. It used the full annotated connectome (167,184 neurons and 25,583,622 edges), with the brain and policy on CUDA. No planner chose its actions.

Deterministic validation improved from zero to one successful goal out of six situations. The final outcomes were:

| Scene | Success | Collision | Timeout | Final goal distance (m) |
| --- | --- | --- | --- | --- |
| Office floor | Yes | No | No | 0.444 |
| Apartment | No | No | Yes | 1.457 |
| Street block | No | No | Yes | 5.770 |
| Atrium | No | No | Yes | 9.033 |
| Warehouse | No | No | Yes | 5.920 |
| Courtyard | No | Yes | No | 17.737 |

These are six held-out situations within existing architectural scenes, using seed 200001. They are validation results, not an independent test of unseen building geometry. Training successes must be reported separately from these deterministic outcomes.

Training took 3,197.703 seconds, excluding validation, with peak allocated GPU memory of 0.772 GiB. All recorded losses were finite. The run completed 256 PPO rollouts and 1,280 optimizer epoch passes. Checkpoint reload reproduced the checked action. Runtime sources and all six protected policy aliases retained their hashes. No reserved test was accessed and no checkpoint was promoted.

The first pilot had zero validation goals, five collisions and one timeout. The second pilot achieved one goal, one collision and four timeouts. This suggests improved obstacle avoidance on this small validation set, while reaching distant goals remains unresolved. A single seed and six situations do not establish a reliable success rate or a connectome advantage.

The next iteration should test the prepared training-only goal curriculum, verify full-connectome episode resets and checkpoint compatibility, and keep final validation goals and geometry unchanged. Advancement must depend on completed training episodes across every training task. Curriculum practice is adaptive training evidence, not independent generalization evidence.

Authoritative local records: `runs/training/autonomous-architecture-pilot-2/protocol.json`, `status.json`, `episodes.jsonl` and `updates.jsonl`.
