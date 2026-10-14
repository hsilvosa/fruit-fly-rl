# Autonomous students with a training-only route signal: results

Run October 11, 2026 under [AUXILIARY_STUDENT_PROTOCOL.md](AUXILIARY_STUDENT_PROTOCOL.md), committed before training (`296b74c`). Seven new trainings of 262,144 added transitions from the experiment 7 start (aux 801 to 803, privileged critic 801 to 803, control 703), plus the two earlier controls (701 and 702) re-evaluated with them. All nine final checkpoints were evaluated on the new pool 882000 (64 episodes per cell). The actor of every student is blind to the route input (verified by unit tests, and the route columns are zeros at test time). Duration: 2 hours 43 minutes against an estimate of 2 hours 20 (training 68 minutes as estimated; evaluation 95 minutes against 65, because the sampled-action and level B cells are slower than the others).

## Results

Successes / collisions / timeouts out of 64.

| Run | Passages | Passages-mid | Passages-wide | Medium | Passages, sampled | Level B dev |
| --- | --- | --- | --- | --- | --- | --- |
| Control 701 | 11/28/25 | 39/9/16 | 53/3/8 | 54/8/2 | 11/35/18 | 2/29/33 |
| Control 702 | 11/35/18 | 30/18/16 | 49/5/10 | 52/10/2 | 10/42/12 | 1/31/32 |
| Control 703 | 15/24/25 | 30/12/22 | 43/2/19 | 57/4/3 | 11/36/17 | 2/29/33 |
| **Control mean** | **12.3** | 33.0 | 48.3 | 54.3 | 10.7 | 1.7 |
| Aux 801 | 18/24/22 | 41/7/16 | 49/0/15 | 54/7/3 | 19/33/12 | 6/22/36 |
| Aux 802 | 14/22/28 | 27/8/29 | 40/0/24 | 60/3/1 | 19/23/22 | 4/20/40 |
| Aux 803 | 12/25/27 | 28/8/28 | 47/3/14 | 52/6/6 | 13/30/21 | 1/20/43 |
| **Aux mean** | **14.7** | 32.0 | 45.3 | 55.3 | 17.0 | 3.7 |
| Critic 801 | 17/23/24 | 35/12/17 | 58/0/6 | 50/7/7 | 11/45/8 | 2/29/33 |
| Critic 802 | 10/23/31 | 27/13/24 | 33/3/28 | 52/5/7 | 13/35/16 | 2/27/35 |
| Critic 803 | 12/21/31 | 36/7/21 | 62/1/1 | 49/8/7 | 15/33/16 | 1/21/42 |
| **Critic mean** | **13.0** | 32.7 | 51.0 | 50.3 | 13.0 | 1.7 |

## Outcome by the frozen rule: negative for both arms

On the primary metric (`passages`, deterministic), the gain over the control mean is +2.3/64 for the auxiliary arm and +0.7/64 for the privileged critic. Both are below the 6/64 line for a negative result, and far from the 12/64 needed for a positive one. In both arms, runs fall inside the control range (aux 18, 14, 12 against controls 11, 11, 15; critic 17, 10, 12).

For reference, the actor-reads-the-route diagnostic reached 36 and 39 on a different pool. The students did not move toward it.

## Secondary observations (not decisions)

- **Auxiliary arm with sampled actions:** `passages` 19, 19 and 13 against 11, 10 and 11 for the controls (+6.3 on average, all three above all three controls). This crosses neither threshold of the rule for a decision, because the primary metric is the deterministic one, and the protocol says that a gain in one mode only is partial. The size is small and rests on three seeds.
- **Collisions on `passages`:** lower in both arms (aux 23.7 and critic 22.3 against 29.0), by 5 to 7 on average. Short of the 8 required, and most of the drop turns into timeouts.
- **Level B development maps:** 3.7/64 for the auxiliary arm against 1.7 for the controls and the critic arm. All are in the range of 1 to 6 of 64, which is a floor.
- **Other cells:** no consistent effect. The critic arm has lower medium (50.3 against 54.3, a loss of 4.0, at the edge of the tolerance). Passages-wide varies by 29 episodes between critic runs (33 to 62).

## Reading

1. **Neither route signal improves what the actor can do on `passages` at this budget.** The auxiliary head learned to predict the direction (its loss fell during training), but the behavior did not change in a way that the deterministic metric detects. A privileged critic does not help either.
2. **The gap to the diagnostic stays open.** The diagnostic's actor read the route direction as an input and reached about 59%. The students, who can only use their own sensors, are at about 20%. Whatever made the diagnostic work was the actor having the information at decision time. Using it as a training signal for the representation or for the value estimate is not enough in this form.
3. **The earlier synthetic probe said that the 8 m rays contain the route direction, recoverable with a network and many labelled poses.** This experiment does not contradict that: a prediction head trained with reward-driven data from the policy's own trajectories, at this budget and with a single coefficient, did not turn that information into better flight. The probe had 20,000 supervised samples from poses within 3 m of the route, and the policy visits poses that are further away.
4. The variation between seeds remains of the same order as the effects. For example, the critic arm's `passages-wide` goes from 33 to 62 between seeds.
5. The sampled-action result of the auxiliary arm is the only signal. It is small, and it would need its own pre-declared test before it counts.

## What this does not show

One head design, one coefficient (1.0), one label (direction to a point 4 m ahead), one budget (262k). A larger coefficient, a longer budget, a different label, or a dedicated pretraining of the head on supervised data (like the synthetic probe) may behave differently. Three seeds per arm cannot establish small effects. The experiment does not cover mazes or large rooms.

## Consequences for the plan

- Cross out, for now: training-only route signals (auxiliary head and privileged critic) as the main lever at this budget.
- Still open: supervised pretraining of the representation on many labelled poses (the data of the synthetic probe), then PPO; a larger budget; longer range sensing; memory.
- The claim stays at medium rooms (86 to 92% on fresh pools), and partitioned rooms remain partial. The release gate for the four families is not within reach with the current approach, and there is no new evidence that changes that.
