# Collision anatomy on passages

October 11, 2026. Evaluation only, no training. Script: `scripts/collision_anatomy.py`. Pool seeds 880000 to 880063 (64 episodes of `passages`, the same pool as [COMMITTEE_EVAL_RESULTS.md](COMMITTEE_EVAL_RESULTS.md)), deterministic unless stated. Each episode records its final position relative to the certified route, the obstacle that was hit, the speed, and the angle of the velocity against the route 4 m ahead and against the goal. It took 28 minutes in total (one process, two threads), against an estimate of 25 to 30. Success counts differ by one episode from the earlier evaluation of the pilot (18 against 17) and of seed 505 (3 against 2): the batch composition differs and the floating-point behavior of the batch is not bit-identical. Run 601 gives 9 in both.

## Results

| Checkpoint | Success | Collisions | Timeouts | Hit a partition piece | Hit a box | Collision at 0 to 1.5 m from the route | 1.5 to 3 m | Over 3 m | Median route progress at collision | Median speed at impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Run 601 | 9 | 33 | 22 | 23 | 10 | 11 | 7 | 15 | 0.48 | 1.23 m/s |
| Pilot | 18 | 20 | 26 | 8 | 12 | 6 | 5 | 9 | 0.46 | 1.49 m/s |
| Seed 505 | 3 | 19 | 42 | 8 | 11 | 3 | 8 | 8 | 0.29 | 1.48 m/s |
| Run 601, sampled actions | 11 | 42 | 11 | 32 | 10 | 10 | 9 | 23 | 0.35 | 1.25 m/s |

Timeouts (all checkpoints): median route progress 0.27 to 0.48, median distance from the route 4.1 to 4.3 m, median speed 0.65 to 1.2 m/s.

## Reading

1. **Collisions are not edge clips at the opening.** Only 1 to 3 collisions per checkpoint end within 0.5 m of the certified route, and at most 11 within 1.5 m. Most end 1.5 to 3.5 m or more from the route. The policy does not fail by touching the frame of an opening it is crossing. It leaves the route corridor before.
2. **The flies die about halfway.** The median route progress at collision is 0.3 to 0.5, and no checkpoint has a majority of collisions in the last third. Reaching the first partition is common. Getting through the later ones is not.
3. **Timeouts are far from the route and slow.** They sit about 4 m from the route at under 1.2 m/s, which is wandering or hovering away from the openings, and not hovering at the right opening.
4. **Run 601 hits partition pieces more often (23 of 33) than the pilot (8 of 20).** The pilot's failures are mostly boxes (12 of 20), meaning general obstacle avoidance in the clutter. The sampled version of 601 trades timeouts for collisions (timeouts 22 to 11, collisions 33 to 42, successes 9 to 11): sampling makes it more aggressive, and not better at finding the opening.
5. At impact the velocity is about 60 to 80 degrees from both the route direction and the goal direction. The angle is measured in 3D, with the vertical component included, so a lateral or vertical slide dominates, and it does not show the heading of the fly. I did not measure what the sensors saw at that point.

## What this does and does not say

- It rules out a clearance problem at the opening (the policy knows where to put its body when it is there) as the main failure.
- It does not separate missing exposure from missing information. Both give a policy that leaves the corridor between partitions. The probe of the 256 pooled features, which was in the plan, is still the discriminating measurement: if the features encode the direction to the next opening, more exposure can help, and if they do not, it cannot.
- It is one pool of 64 episodes per checkpoint, without confidence intervals on the shares above.
