# Passages failure classification

Recorded October 8, 2026 with `scripts/classify_failures.py`. Evaluation only; no training. Two frozen policies ran 16 episodes each on the `passages` profile, seeds 810000-810015 (a development pool). Records are local in `runs/verification/failure-classification-1/`.

| Policy | Collision into obstacle | Timeout, hovering near obstacles | Timeout, repeated motion | Mean route progress | Best route progress |
| --- | ---: | ---: | ---: | ---: | ---: |
| Source (48/64 reference, `3b9e8ba41305`) | 8 | 5 | 3 | 0.30 | 0.71 |
| Retained after experiment 1 (chunk 8) | 3 | 5 | 8 | 0.23 | 0.59 |

Route progress is the fraction of the certified reference route that the trajectory covers, by the closest point on the route. It is an evaluation measure. The policy never sees the route.

Observations:

1. The straight line from start to goal crosses an obstacle in 16 of 16 episodes. The certified route is on average 2.2 times the straight distance (53 to 70 m against 28 m).
2. The source collisions happen at 0.13 to 0.22 m from an obstacle, at speeds of 0.4 to 1.75 m/s, often in the first 300 steps. The policy flies toward the goal until a partition blocks it.
3. Timeouts have a mean speed of 0.14 to 0.56 m/s and a net displacement of at most 19 m in about 1,800 steps. The policy hovers 0.6 to 2 m from obstacles instead of flying the 55 to 70 m detour. Time would not limit a detour: a 60 m route at about 1 m/s needs about 1,200 steps.
4. No episode crossed all partitions. The best trajectory covered 71% of the reference route.
5. Experiment 1 changed the failure mix (fewer collisions, more repeated motion) but not route progress.

The "repeated motion" label means path length above three times net displacement. It is a heuristic, not a diagnosis of an internal mechanism.

Reading: the distance-to-goal progress reward has a local minimum against each partition. A policy that approaches the goal directly is rewarded until it reaches a wall, and gets no signal for moving away from the goal to reach an opening. This fits the hovering and the early collisions. It does not prove the cause.

Next experiment: [REFERENCE_TRANSFER_PROTOCOL_2.md](REFERENCE_TRANSFER_PROTOCOL_2.md).
