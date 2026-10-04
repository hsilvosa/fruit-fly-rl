# Guided training and autonomous inference

The [frozen guided-navigation v1 protocol](evidence/guided-navigation-v1-plan.md) uses the remaining 40,960 transitions of the existing budget. It completed with 0/8 autonomous validation goals, all failures by collision; see [verified results](evidence/guided-navigation-v1-results.md). The [sensors-v5 correction and v2 draft](evidence/visible-fan-v5.md) are the next development step, pending a new budget. Navigation remains unresolved.

## What learns

The full annotated MaleCNS recurrent graph remains fixed. Only the movement actor, critic and synthetic temporal feature extractor learn. The actor receives 256 pooled brain features per frame, with 32 historical samples and the current frame. Raw sensors, position, obstacle tables, route indices and waypoint vectors are not extra policy inputs. Independent episode resets clear both fixed brain activity and history.

During collection, a separate teacher can read a training world's geometric certificate and physical pose to produce action labels. It coordinates altitude and horizontal motion as components of one desired 3D velocity, suppresses travel while turning, and slows near route corners. This is privileged supervision. The teacher's arrivals are labeled guided training outcomes, never student evaluation success.

The actor loss is mean over samples and actions of w_j (mu_j(brain_history)-a_teacher,j)^2, with weights w=(1,1,2,2). Half each minibatch is sampled from turn labels with absolute yaw action above 0.25 when available; the other half is uniformly sampled. Gradients update the temporal extractor, actor MLP and action output. They do not update the connectome or critic.

After the first fit, mixed rollouts choose the teacher with probability 0.8 per action and the deterministic student otherwise. All visited states retain teacher labels. The second fit uses the accumulated records. This is a bounded DAgger-style data collection step, following the dataset-aggregation idea of [Ross, Gordon and Bagnell (2011)](https://arxiv.org/abs/1011.0686), rather than an exact implementation of every detail in their algorithm.

The critic is separately initialized against discounted returns from the collected training rewards. Returns stop at recorded terminal boundaries, and the unfinished data suffix uses zero continuation. Its loss is squared prediction error; actor and feature-extractor weights are fixed during this fit. The suffix convention is an approximation for initialization.

Finally, the student performs a short PPO refinement. The action standard deviation starts at exp(-2), learning rate is 0.0001, target KL 0.01 and gamma 0.9995. PPO Adam is reset after supervision. The training-only obstacle-aware progress objective remains enabled. Actual transitions, replay updates and guided/student action counts are separate counters.

## What runs in the demo

The standard FlightWorld supplies synthetic sensor readings to the full fixed brain. The learned movement policy receives the resulting feature history and produces four flight commands. It has no live teacher, geometric path follower or privileged reward field. Viewing never starts training or changes weights. A saved imitation provenance field describes training; it does not provide inference guidance.

Ordinary validation uses exactly this teacher-free path on original large maps. The eight reused development layouts are not an independent final test. A successful guided teacher or a small imitation loss cannot replace this validation.

## Explicit commands and records

From the repository root, start only a reviewed, unused frozen plan:

```powershell
.\.conda\python.exe -s -m fly_rl train-guided --plan private/guided-navigation-v1-plan.json
```

The command refuses an existing run directory status instead of restarting or overwriting it. The plan fixes budgets, source hashes, optimization and validation layouts, aliases, and supervised update counts. Training-data arrays and detailed status remain under runs/training/guided-navigation-v1; plans and launch evidence remain private. No aliases are automatically replaced and no reserved final test is automatically consumed.

An existing final checkpoint can be viewed explicitly:

```powershell
.\.conda\python.exe -s -m fly_rl demo --checkpoint runs/training/guided-navigation-v1/policy.zip --map-profile large --dynamics coordinated --brain-view
```

Until the experiment finishes, that final checkpoint may not exist. Launchers continue to use the original preserved models. Use the final result record to determine whether the new student actually navigated successfully.
