# Feature probe on passages

October 11, 2026. Offline analysis of frozen data, no training of any policy. Scripts: `scripts/collect_probe_data.py` (rollouts) and `scripts/analyze_probe.py` (probes). Rollouts: 64 episodes of `passages`, seeds 881000 to 881063, deterministic actions, every third step stored (run 601: 18,044 samples; pilot: 22,304). Raw data in `runs/verification/probe/` (ignored by git). Collection took 16 minutes and the analysis about 6, against an estimate of 1.5 hours for everything.

## Question

Committee review, step 6: do the 256 pooled connectome features that the policy reads carry the direction to the next stretch of the certified route (the way through the next partition)? If they do not, more exposure or budget cannot fix `passages`, and the bottleneck is the representation.

## Method

- Target: the unit vector, in the body frame, from the fly to the route point 4 m (and 8 m) ahead of its progress along the certified route.
- Inputs: the goal direction alone (3 numbers), the raw sensors (rays, goal direction, velocity and so on, as the world produces them), the 256 pooled features, and the features plus the goal direction.
- Probes: ridge regression and a small MLP (two hidden layers, early stopping on validation). Episodes are split 40 train, 8 validation, 16 test, so steps of one episode never cross the split.
- Metric: median angular error in degrees on the test episodes, overall and on the hard subset, defined as the straight line to the goal being blocked and the route direction differing from the goal direction by more than 40 degrees (64% of the test samples for run 601 and 51% for the pilot). Reference: two random directions differ by 90 degrees at the median.

## Results (route point 4 m ahead; all test samples / hard subset)

| Input | Run 601, ridge | Run 601, MLP | Pilot, ridge | Pilot, MLP |
| --- | --- | --- | --- | --- |
| Predict the goal direction, no model | 74 / 89 | same | 43 / 93 | same |
| Goal direction only | 59 / 75 | 53 / 64 | 45 / 79 | 49 / 76 |
| Raw sensors | 45 / 57 | 35 / 51 | 53 / 70 | 40 / 49 |
| 256 connectome features | 45 / 57 | 37 / 53 | 52 / 70 | 41 / 49 |
| Features plus goal direction | 45 / 56 | 38 / 52 | 51 / 69 | 39 / 49 |

The 8 m target gives the same picture (run 601 MLP: raw 34 / 47, features 34 / 45; pilot MLP: raw 41 / 48, features 38 / 50).

## Reading

1. **The 256-feature readout loses almost nothing compared with the raw sensors.** In 16 of 16 pairs the features and the raw sensors are within 5 degrees of each other, with no consistent winner. Whatever information the sensors contain about the route direction, the pooled connectome features pass it on. A change of readout (the segmented-dual option in the plan) is therefore unlikely to be the lever for this problem.
2. **Neither input decodes the route direction well where it matters.** On the hard subset the best error is 45 to 53 degrees, against 90 degrees for guessing and 76 to 93 degrees for the goal direction. The inputs know something (the error is roughly halved), but not enough to point at an opening. A policy that needs to turn toward an opening 4 m ahead is working with a direction known to about 50 degrees.
3. **This points at the sensors or at memory, not at the pooling.** The rays reach 8 m and the rooms are 28 to 48 m wide. The opening of the next partition is often outside the rays' range. A memoryless policy then cannot know where the opening is, with any readout.
4. The two checkpoints differ in how much the goal direction explains (pilot: 43 degrees when it predicts the route direction, run 601: 74). That follows from where their episodes spend time, and I did not examine it further.

## Limits

- The probes are small and trained on 40 episodes from the policy's own trajectories. A larger probe or more data may decode more, so 45 to 53 degrees is an upper bound on the error, not a floor.
- The label is noisy where the route turns sharply, which inflates every error equally.
- A decoder limit shows what the input contains linearly or through a small network. It does not show what a trained policy could extract with a long training.
- Both checkpoints share the same sensor contract and readout. The result says nothing about other readouts or about longer sensors.
- It does not prove that exposure does not help. It says that if the exposure experiment helps, it has to do so with inputs that decode the route direction to about 50 degrees at best.

## Consequences for the plan

- The readout-change step (committee plan, step 6) drops in priority.
- The sensor and memory directions rise: the diagnostic of the committee plan that adds the next route waypoint to the input (never reported as the student), and the Phase 3 memory work revisited with more exposure to hard maps.
- The exposure experiment is still worth running, but a null result there now has a likely explanation: the inputs lack the information.
