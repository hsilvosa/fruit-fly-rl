# Sensing and memory probes (committee follow-up)

October 11, 2026. Offline analysis, no policy was trained and no checkpoint changed. Scripts: `scripts/analyze_probe_variants.py`, `scripts/collect_probe_data_long.py`, `scripts/probe_synthetic.py`. Continues [FEATURE_PROBE.md](FEATURE_PROBE.md). The third committee review asked for two zero-training checks before choosing between memory, longer sensing and a privileged critic: does feature history help, and does a longer ray range help? Total time about 55 minutes of wall clock against an estimate of 60.

## Probe 1: feature history (rollouts of run 601 and the pilot, 64 maps)

Same targets and splits as the first probe. Median angular error on the hard subset, route point 4 m ahead, MLP:

| Input | Run 601 | Pilot |
| --- | --- | --- |
| 256 features now | 53 | 55 |
| plus lags to 0.6 s | 61 | 59 |
| plus lags to 2.4 s | 66 | 59 |
| plus lags to 4.8 s | 64 | 60 |

Adding history made the error worse in every case, the same for raw sensors. With 40 training episodes, more input values overfit, so this is a limit of the probe and not evidence against memory. It shows no sign of extra information in the history at this data size.

## Probe 2: longer range on the same rollouts

The same 128 ray directions cast to 24 m instead of 8 m, and the 72x25 panorama at 24 m (hard subset, 4 m target, MLP):

| Input | Run 601 | Pilot |
| --- | --- | --- |
| 8 m rays, as the policy | 46.7 | 45.0 |
| same rays at 24 m | 46.3 | 53.7 |
| panorama at 24 m | 50.7 | 53.2 |

No gain, but the same limit applies: 64 maps, and the poses are the ones the policy visited. The result is inconclusive.

## Probe 3: synthetic poses on 700 maps (the decisive one)

No policy involved. For each of 700 `passages` maps (seeds 895000 to 895699, reserved for this probe) 40 poses along the certified route, displaced by up to 3 m horizontally and 1.5 m vertically, with a random heading. Inputs carry the goal direction, goal distance and altitude, and no velocity. Split by map: 500 train, 50 validation, 150 test (6,000 test samples, 57% of them hard). Median angular error in degrees, all test samples / hard subset:

| Input | 4 m target, ridge | 4 m target, MLP | 8 m target, ridge | 8 m target, MLP |
| --- | --- | --- | --- | --- |
| Goal direction only | 46 / 63 | 45 / 63 | 37 / 53 | 37 / 52 |
| 8 m rays (as the policy) | 41 / 59 | 20 / **34** | 35 / 51 | 21 / **35** |
| 24 m rays, same directions | 40 / 57 | 17 / **28** | 31 / 48 | 16 / **27** |
| 24 m panorama | 40 / 57 | 21 / 30 | 31 / 48 | 20 / 29 |
| 8 m and 24 m rays | 40 / 57 | 18 / 27 | 29 / 45 | 17 / 26 |

## Reading

1. **The first probe understated what the 8 m rays contain.** With 500 maps, a nonlinear probe decodes the route direction to 34 degrees on the hard subset from the 8 m rays, against about 50 degrees with 40 episodes. The information is present in the policy's own sensors. It sits in a nonlinear form: a linear readout gets 51 to 59 degrees from the same inputs.
2. **Longer range helps, modestly.** The 24 m rays reduce the error by 6 to 8 degrees on the hard subset (34 to 28 and 35 to 27). The panorama does not beat the plain rays. So range is a lever of limited size, and richer directions are not.
3. **What this changes in the reading of the earlier result.** The diagnostic showed that giving the route direction as an input raises `passages` from 17% to 59%. The synthetic probe shows that a network with enough data can already recover most of that direction from 8 m rays. The gap between what the inputs contain and what the policy uses (it behaves like an input with about 50 degrees of error) is therefore a **learning problem**: the policy has not learned to extract the route direction from its sensors with the data and budget it had, and it was not necessary to have longer sensors to see that direction. This points toward the auxiliary-prediction path (a head trained on the waypoint label, absent at test time) and toward more or better training, ahead of a new sensor contract.
4. **Limits of this reading.**
   - The synthetic poses stay within 3 m of the certified route. The policy's own failures sit 1.5 to 4 m off it, and the probe's error is likely larger there.
   - A probe trained with 20,000 labelled samples is not a policy trained by reward. The auxiliary path is a hypothesis, not a result.
   - The test is on `passages`. Mazes and large rooms, where the opening can be tens of metres away, are not covered: for those, range and memory remain open, and the 8 m result says nothing.
   - The measure is the median error. The tail matters for collisions and was not examined.
   - The history probe could not test memory at all.

## Consequences for the plan

- Rises: **auxiliary waypoint prediction (C)** and a privileged critic, which cost little and keep the student autonomous at test time.
- Falls: a new sensor contract as the first move, and distillation.
- Open: memory and range, for families where the next opening is out of reach.
- Pool 880000 and 881000 should not choose any new checkpoint. A fresh pool must be reserved before any selection. Seeds 895000 to 895699 were used here for the probe.
