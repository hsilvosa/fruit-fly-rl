# Historical learned reference

Updated October 7, 2026. This document traces the earlier medium dense-room results to preserved checkpoints. It records read-only checks. No policy was trained. No reserved or consumed final pool was reopened for selection.

Machine-readable record: `private/reference-recovery-1-evidence/historical-reference-manifest.json`, built by `scripts/build_reference_manifest.py`. Detailed evidence stays local and ignored, as for earlier experiments. The scripts rebuild it from the preserved run records.

## Result

All historical winners exist on disk. Each checkpoint and metadata hash matches the hash recorded when its single final test ran. The original aliases are unchanged. The earlier successes were not lost.

| Experiment | Final result | Collisions | Timeouts | Checkpoint SHA-256 (first 12) | Source revision | Sensor interface | Lifetime transitions | Initialization |
| --- | --- | ---: | ---: | --- | --- | --- | ---: | --- |
| Warm-start sensor comparison | 50/64 (78.1%) | 5 | 9 | `0a1a6569549a` | `1b34eda` | v2 | 360,448 | Warm start from `runs/dense-flight-policy.zip` (`085963d6e95b`), plus 32,768 PPO transitions, seed 42 |
| Observed-ray risk comparison, normal-training winner | 48/64 (75.0%) | 16 | 0 | `3b9e8ba41305` | `954dd63` | v3 | 131,072 | Fresh, seed 42 |
| Near-goal curriculum comparison, normal-training winner | 45/64 (70.3%) | 15 | 4 | `92d9c8ba2ff3` | `bb369cb` | v3 | 131,072 | Fresh, seed 42 |
| Original coordinated dense launcher, `dense-flight-policy.zip` | 43/64 (67.2%) | 11 | 10 | `085963d6e95b` | `57e0549` | v2 | 327,680 | Dense coordinated training |
| Fresh sensor comparison | 35/64 (54.7%) | 20 | 9 | `21f1744cc159` | `996b39f` | v3 | 131,072 | Fresh |

All rows share this contract: MaleCNS v1.0 reservoir fingerprint `aff3a08b...`, 256-feature random-pool readout (`random-pool-256-v1`, the default when the key is absent), reward `navigation-v2-progress-timeout`, coordinated dynamics, a 32 x 32 x 12 room with 48 obstacles, a 1,200-tick episode limit and no history frames. Each final pool was separate and is consumed. The table is not a paired ranking.

Two points matter for the next experiment:

- The 75.0% and 70.3% rows used the same configuration (fresh, v3, seed 42, 131,072 transitions). They differ by pool and run, so about 5 points of variation between them is ordinary pool and run variance.
- The 78.1% row is the only one that continued a trained policy. The 43/64 alias is its parent.

## Reproduction check

The three top checkpoints were replayed on their own recorded validation pools with the current repository (`scripts/replay_reference_validation.py`, output copied to `private/reference-recovery-1-evidence/`). This is a reproducibility check on already inspected rooms, not a new test.

| Checkpoint | Validation pool | Recorded | Replayed | Per-episode outcome matches |
| --- | --- | --- | --- | --- |
| Warm-start sensor comparison | seeds 100000-100031 | 23/32 | 23/32 | 32/32 |
| Observed-ray risk comparison | seeds 240000-240031 | 27/32 | 27/32 | 32/32 |
| Near-goal curriculum comparison | seeds 210000-210031 | 27/32 | 27/32 | 32/32 |

Every episode outcome (success, collision, timeout) matched the preserved record. The current simulator, sensors, readout and checkpoint loader still reproduce the historical behavior for sensor v2 and v3 policies.

## Source drift since the winning revisions

For the three top winners, `flight.py`, `planner.py` and `anatomy.py` have no content changes since their revisions. The changes in `sensors.py`, `world.py` and `brain.py` add sensor versions v4 to v6, map profiles and a no-observation step option. They do not alter the v2 or v3 code paths. The replay above confirms this behavior for evaluation.

`learning.py` (about 220 added lines) and `dense_training.py` (about 60 added lines) changed substantially. Evaluation does not depend on the training changes. Continuing PPO from a retained checkpoint does. The next training run must record this and verify optimizer and rollout behavior before relying on it.

The row for `dense-flight-policy.zip` and the 43/64 `priority12-v2` result with 15 collisions and 6 timeouts (the RESULTS.md "Dense adaptation" row) are different checkpoints with the same success count.

## Why the autonomous curriculum did not use this reference

`autonomous-architecture-curriculum-2` used a different interface and a fresh initialization:

| Property | Historical reference | Curriculum 2 |
| --- | --- | --- |
| Sensors | v2 or v3, 128 distance rays | v6, v3 plus 1,800 panorama rays (range 24 m) |
| Readout | `random-pool-256-v1` | `neural-projection-dual-repeatable-segmented-v1` |
| History | none | 8 frames, stride 8 |
| Initialization | warm start or fresh v3 | fresh |
| Task | one dense room, 48 obstacles, no mandatory partitions | architectural scenes, nearby straight-path lessons |

The historical policies cannot load into the curriculum interface. The brain fingerprint check refuses them. A comparison between the two measures an interface change, a readout change, a history change and a task change at once. It does not measure map difficulty alone.

## Development transfer ladder

The frozen historical checkpoints were evaluated without training on new development seeds (800000 and above, 16 episodes per cell). These seeds were created for this check. They are development observations, not tests. Profile runs used the explicit `allow_transfer` flag, which skips only the stored dynamics and map-profile metadata check. Weights and observations are unchanged. See `private/reference-recovery-1-evidence/transfer-ladder.json`.

| Checkpoint | Task | Successes | Collisions | Timeouts |
| --- | --- | ---: | ---: | ---: |
| Observed-ray risk comparison (v3) | Original medium dense room | 12/16 | 3 | 1 |
| Observed-ray risk comparison (v3) | `open` profile, 32 x 32 x 12, 24 obstacles | 12/16 | 3 | 1 |
| Observed-ray risk comparison (v3) | `passages`, 32 x 32 x 12, 64 obstacles, 3 partitions | 0/16 | 7 | 9 |
| Observed-ray risk comparison (v3) | `large`, 48 x 48 x 16, 112 obstacles, 5 partitions | 0/16 | 4 | 12 |

| Warm-start sensor comparison (v2) | Original medium dense room | 11/16 | 1 | 4 |
| Warm-start sensor comparison (v2) | `large`, 48 x 48 x 16, 112 obstacles, 5 partitions | 0/16 | 2 | 14 |

Sixteen episodes give wide intervals. A 12/16 result has a Wilson 95% interval of roughly 51% to 90%. A 0/16 result has an upper bound of about 19%.

## Findings

1. The working reference exists, is traceable and reproduces under the current code. The user's concern was correct: later work started fresh policies and did not use it.
2. On new medium rooms the reference still succeeds at about the historical rate (12/16 on the original task and on the easier `open` profile).
3. The reference fails completely once mandatory partitions appear (0/16 on `passages` and on `large` for the v3 checkpoint, 0/16 on `large` for the v2 checkpoint). Failures are collisions and mostly timeouts with the goal still far away (mean final distance 20 m of 28 m on `passages`, 38 m of 44 m on `large`), so the policy does not find or cross openings. This is a task-capability gap, not a loading, scaling or physics regression.
4. The earlier failure of curriculum 2 therefore combines a changed interface with a task the reference also cannot do. The two causes are not yet separated.

## Limits

- Sixteen episodes per cell. Differences of one or two episodes are not meaningful.
- The ladder covers the observed-ray v3 checkpoint on four tasks and the warm-start v2 checkpoint on two. The near-goal checkpoint and the maze profile were not run.
- Failure classification from recorded trajectories (step 2 exit criterion) is not done. The collision and timeout counts above are outcomes, not diagnoses.
- No medium-room regression suite is frozen yet. The three validation replays above are a candidate for it.

## Candidate next experiment (not launched)

This needs an agreed budget and protocol before any training. It changes one factor from the working reference.

- Initialize from the retained 48/64 v3 checkpoint (`3b9e8ba41305`), keeping the v3 interface and the `random-pool-256-v1` readout.
- Train on the `passages` profile with original goals from the first chunk, and mix in original medium rooms to measure forgetting.
- Gate each stage on the frozen medium-room replay (no lost reference successes) before moving to `large`, maze and architectural scenes.
- Use a matched fresh v3 control with the same budget, declared as a control.
- Treat the sensor-v6 panorama interface as a separate, later experiment, because it needs an explicit versioned transfer and cannot reuse these weights.
