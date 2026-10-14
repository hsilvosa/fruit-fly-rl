# Light audit before the next experiments (no training, no policy evaluation)

October 11, 2026. Two checks that need no training and no GPU, run after the committee review of the R5 result. Script: `scripts/audit_reward_horizon.py` (details also in `private/reference-recovery-1-evidence/reward-audit.json`).

## 1. Training exposure to hard maps

The training logs do not record episode counts. The only recoverable count is the R5 difficulty controller, which completes one window per 64 finished episodes on the 20 randomized simulators. At the end of each R5 run (98,304 transitions, about 3,070 steps per simulator) it had completed exactly one window (seeds 601, 602, 603). So the randomized simulators finished between 64 and 127 episodes in the whole run, about 3 to 6 episodes each. The success rate in that single window was 67 to 77 percent, at difficulty 0.2 (about 1.3 partitions on average). The controller then moved by one step of 0.05 at most.

Reading: in R5 and in the variance study, a run sees on the order of a hundred episodes in total, and only a few dozen on partitioned maps of any difficulty. The R5 negative result says nothing about training on hard maps, because almost no hard-map experience was collected. An earlier statement of "50 to 150 episodes per run" was an estimate. For the randomized simulators it is now a measured bound (64 to 127).

## 2. Does the reward make hovering look better than following the route?

A committee member proposed that hovering (cost 0.02 per step) is a better local choice than a detour under the real reward (2 x progress in Euclidean distance minus 0.02, plus 20 on arrival, gamma 0.995). I computed the discounted return of an ideal route follower along the certified route of 16 `passages` maps (seeds 870000 to 870015), at constant speeds, and compared it with hovering.

| Speed | Route steps | Return from the start | Minimum return-to-go along the route | Discounted weight of the +20 arrival |
| --- | --- | --- | --- | --- |
| 1 m/s | 1,084 | 7.8 | 2.3 (worst map -0.1) | 0.005 (bonus worth 0.09) |
| 2 m/s | 542 | 17.6 | 12.3 (worst map 9.7) | 0.067 (bonus worth 1.3) |
| 3 m/s | 362 | 26.2 | not computed | 0.164 (bonus worth 3.3) |

Hovering until the timeout returns -4.0 (the cost saturates under the discount). The routes are 54.2 m long against 28.4 m in a straight line, and the largest rise of the Euclidean distance above its running minimum is 1.3 m on average (3.0 m at most).

Reading:

- The hypothesis is **refuted for an ideal follower**. At every point of every route the return-to-go of following the route is above the hover return. The reward ordering favors following the route, even at 1 m/s. Reward design alone does not explain hovering.
- The arrival bonus, however, is almost invisible at low speed (0.09 at 1 m/s). The progress term carries the learning signal. A policy that flies slowly gets little credit from arrival, so the speed the policy actually flies at matters. That has not been measured here.
- The check is for a policy that already knows the route. It does not say how hard the route is to find. Credit assignment, exploration and the lack of information in the observation remain open, so the reward change (timeout as terminal, remaining time) drops in priority.
- Routes for `passages` and `passages-wide` were identical at the same seeds (same length and same episode limit), so the two profiles seem to differ only in the opening width.

## What changed in the plan

- Exposure is the strongest explanation that is now measured: the training that was tried gave almost no hard-map experience. The next experiment should raise exposure at fixed budget and then the budget (steps 3 and 4 of the committee plan).
- The reward step moves to the end of the list.
- Not done yet, because they use the GPU or heavy CPU: the probe of the 256 features, the stochastic evaluation, and the fresh-pool confirmation of run 601 and the pilot.
