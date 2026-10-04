# Neural waypoint v6 protocol

Original-large navigation remains unresolved after v5 development verification reached 0/8 goals, six collisions and two timeouts. This engineering correction adds an explicit learned waypoint auxiliary, natural training-start headings, maneuver/start sampling and continuous autonomous student episodes. It is not a controlled causal comparison of those changes.

The experiment adds at most 81,920 world transitions: 16,384 teacher-controlled transitions in eight fragments, then four 16,384-transition student-only chunks. The student starts once from the original environment state and retains physical episodes, full brain activity and neural histories between fitting chunks. Only physical termination triggers automatic reset. This removes the earlier 102-second manual cuts from student training; individual rooms retain their original episode limits and physics.

Teacher fragments select exact optimization layouts 370000 through 370063, starting at the environment-generated position and heading. They do not replace yaw with a route-aligned heading or place the fly at later route vertices. The complete optimization pool remains 370000 through 370111 for automatic episode resets and student flights. Room geometry remains the original 48 by 48 by 16 large profile with 112 boxes, five partitions and 3.2 by 3.2 openings.

The declared source is the unchanged v5 final checkpoint. Explicit transfer adds a zero-initialized residual, initially preserving its motor output. The entire audited MaleCNS v1.0 graph remains simulated: 167,184 neurons and 25,583,622 edges. The runtime actor receives only nine frames of 1,447 input-associated neural outputs. It receives no world pose, reference route, teacher state or full map.

The new auxiliary predicts the local unit vector and clipped distance to the teacher's current waypoint. The teacher provides these privileged training labels, which supervise a predictor whose inputs are neural histories. Its estimated vector can affect motor commands through a learned residual. This is not a runtime path follower, an optimal-path claim or a biological visual circuit.

Training retains 98,304 old v5 optimization rows for action supervision. Their unavailable waypoint labels are masked out of auxiliary loss. They add no new world transitions. New collection adds pose, velocity, actual layout seed, executed actions, teacher-use flags and waypoint labels to the retained neural/action arrays. The trace schema identifies the valid new-trace offset; it does not invent old trajectories.

Initial supervision uses 2,048 updates, followed by 1,024 updates after each student chunk. Every update samples a quarter strong turns, a quarter strong vertical commands, a quarter empty recent neural histories and a quarter uniform examples, with uniform fallback for missing groups. The loss is weighted action MSE plus twice the waypoint MSE on valid labels. These 6,144 replay updates are separate from world-transition accounting. There is no PPO refinement in this experiment.

The fixed final checkpoint receives one development validation on reused seeds 430000 through 430007, with original starts and no teacher. This cannot demonstrate independent generalization. No reserved final test, automatic alias promotion or checkpoint selection is performed. The original six launcher aliases and source checkpoint are hashed before and after. Completed substantive training use before v6 is 786,432; the new cumulative cap is 868,352. The source checkpoint lifetime count is 98,304 and the proposed final lifetime count is 180,224; lifetime and project accounting are different.

Verification before launch includes the earlier zero-transition full-graph auxiliary smoke and a separate 128-transition full-graph student collector smoke with three supervised updates. It verified continuity, finite labels, unchanged source weights and CPU/CUDA reload error 1.70e-6. Focused runner and transfer tests passed. These are interface checks, not navigation evidence.

The frozen plan refuses an existing experiment status. Progress and fitting-loss samples are retained in runs/training/neural-waypoint-v6/progress.jsonl, with atomic status in status.json. Opening a demonstration never invokes training.

```powershell
.\.conda\python.exe -s -m fly_rl train-waypoint --plan private/neural-waypoint-v6-plan.json
```
