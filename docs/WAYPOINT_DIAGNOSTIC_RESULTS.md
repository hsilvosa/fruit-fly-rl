# Privileged-waypoint diagnostic: results

Run October 11, 2026 under [WAYPOINT_DIAGNOSTIC_PROTOCOL.md](WAYPOINT_DIAGNOSTIC_PROTOCOL.md), committed before training (`c121b26`). Four trainings of 262,144 added transitions from the experiment 7 start (waypoint arm and zero-input control arm, seeds 701 and 702), final checkpoint of each evaluated on pool 880000 with 64 episodes per cell. The policies in the waypoint arm read the certified route during flight: they are a diagnostic of the input, and not an autonomous student.

The run took 56 minutes in total (10 minutes per training, 19 minutes of evaluation), against an estimate of 75.

## Results

Successes of 64 (Wilson 95% interval in parentheses); collisions and timeouts in the last column.

| Run | Passages | Passages-mid | Passages-wide | Medium | Passages collisions / timeouts |
| --- | --- | --- | --- | --- | --- |
| Waypoint 701 | 39 (61%, 49 to 72) | 58 (91%, 81 to 96) | 64 (100%, 94 to 100) | 59 (92%, 83 to 97) | 16 / 9 |
| Waypoint 702 | 36 (56%, 44 to 68) | 57 (89%, 79 to 95) | 64 (100%, 94 to 100) | 58 (91%, 81 to 96) | 19 / 9 |
| Control 701 | 14 (22%, 14 to 33) | 42 (66%, 53 to 76) | 59 (92%, 83 to 97) | 47 (73%, 62 to 83) | 31 / 19 |
| Control 702 | 8 (12%, 6 to 23) | 25 (39%, 28 to 51) | 53 (83%, 72 to 90) | 52 (81%, 70 to 89) | 38 / 18 |
| Waypoint mean | **37.5 (59%)** | 57.5 | 64 | 58.5 | |
| Control mean | 11 (17%) | 33.5 | 56 | 49.5 | |

## Outcome by the frozen rule: partial

- Waypoint mean on `passages`: 37.5/64, below the 40/64 required for "information is the main limit". It is 26.5/64 above the control mean (the rule asked for at least 20), and both waypoint runs are above both control runs.
- The medium clause of the information rule (52/64 or more in every run) fails for control 701 (47). That run is a control, so the clause does not concern the waypoint arm, whose medium scores are 58 and 59.
- The "trainer or dynamics are the limit" outcome does not apply: the waypoint mean is far above 20/64 and the gain is far above 8/64.

So the result is in the partial band, near its upper edge. The mean misses the 40/64 line by 2.5 episodes with two seeds and an interval of about plus or minus 12 per run, so it cannot separate "mostly information" from "information plus something else".

## Reading

1. **The information matters a lot.** With the route direction in the input, the same recipe moves `passages` from 17% to 59%, `passages-mid` from 52% to 90% and `passages-wide` from 88% to 100%, while medium improves too (77% to 91%). Collisions on `passages` fall from 31 to 38 of 64 down to 16 to 19. The training pipeline, the reward and the flight dynamics can therefore produce route-following behavior when the information is there.
2. **It does not reach the gate.** Even with an exact route direction 4 m ahead, `passages` is at 56 to 61%, below the 81% target, with 16 to 19 collisions. A gate-level student would need the information and better execution.
3. **The control arm at 262k transitions is also informative.** Without the waypoint, 2.7 times the variance-study budget gives `passages` 12 to 22% and `passages-mid` 39 to 66%. The variance study's runs at 98k scored 2 to 3 of 32 on `passages` and 7 to 13 of 32 on `passages-mid`. The extra budget helps somewhat on its own, and the exposure experiment (more `passages` simulators) remains open. This comparison mixes three differences (budget, the expanded network, seeds) and is only suggestive.
4. This closes the main question of the committee review. The missing route information, which the feature probe found in the input, is a large part of the plateau. Exposure and budget are secondary.

## What this does not show

- A student cannot read the certified route. The result is an upper bound on what better sensing or memory could provide, using an exact waypoint at one look-ahead distance. A real student must get the information from its own sensors or memory, and the probe found the sensors give it to about 50 degrees.
- Two seeds per arm. The ranges between seeds in this experiment are small compared with the effect (the two waypoint runs are within 3 episodes on `passages`), but two seeds do not establish reliability.
- It does not say which route information matters (direction, distance, the opening position) or how far ahead. Those were not varied.

## Consequences for the plan

- Information is confirmed as a major limit. The next work should give the student that information from its own inputs, in one of two ways:
  - **Memory:** the Phase 3 work revisited with the exposure that a stronger recipe provides, since a fly that has seen the opening can remember where it was.
  - **Longer or richer sensing:** a sensor contract with a longer range or a coarse map of free space.
- A cheap bridge test is available: train a student that predicts the waypoint direction from its own inputs as an auxiliary task (the waypoint is a training label only and is absent at test time, which keeps the student autonomous). The feature probe suggests the sensors alone limit this to about 50 degrees, so the auxiliary task alone is unlikely to be enough. It is a possible comparison, not a plan.
- The exposure experiment from the committee plan moves down: the control shows budget helps, and the larger question is now information.
