# Supervised pretraining of the actor trunk, then PPO: protocol

Declared October 11, 2026, before data collection and before any training of the `pre` runs. Follows [AUXILIARY_STUDENT_RESULTS.md](AUXILIARY_STUDENT_RESULTS.md): a head trained with reward-driven PPO data did not turn the route direction into better flight. The synthetic probe had shown that, with many labelled samples from many maps, a network recovers the direction from the sensors. This experiment gives the actor that supervised training first.

## Question

If the actor's trunk is first trained, with supervision on many maps, to encode the route direction (while keeping its flight behavior), does PPO from there improve `passages` over the same recipe without that step?

## Design

1. **Data.** Rollouts of the source policy (`runs/training/reference-transfer-7/mix3e4/stage-2.zip`, no later checkpoint) with sampled actions, on 512 maps: 3 batches of `passages-mid`, 2 of `passages`, 1 of `passages-wide`, 1 of `gate-two` and 1 of medium rooms (64 episodes each, seeds 896000 to 896703, reserved for this purpose). Every third step is stored: the 256 connectome features that the actor reads, and the unit vector (body frame) to the certified-route point 4 m ahead of the fly's progress (the label). The label is used only for training.
2. **Pretraining** (`scripts/pretrain_trunk.py`). The actor trunk (two 128-unit layers), the action layer and a 64-unit auxiliary head are trained on the 256 features with the loss `(1 - cosine(head output, label)) + 1.0 * squared error between the new mean action and the source mean action on the same features`. The second term keeps the flight behavior. Split by map: 70% train, 10% validation (early stopping), 20% test. No flight, reward or PPO is used in this step.
3. **Offline gate** (declared before the data exist). Proceed to PPO only if, on the held-out test maps, the median angular error on the hard subset (straight line to the goal blocked and route more than 40 degrees from the goal direction) is at most **45 degrees**, and the action mean of the pretrained policy matches the source with an R-squared of at least **0.9**. For reference: the goal direction alone gives 63 to 93 degrees on that subset, and probes on the policy features trained with 64 maps gave about 50 degrees. If the gate fails, the experiment stops there and is reported as a negative result on the pretraining itself.
4. **PPO (`pre` arm).** The auxiliary arm of [AUXILIARY_STUDENT_PROTOCOL.md](AUXILIARY_STUDENT_PROTOCOL.md) with the pretrained trunk, action layer and head loaded: the actor and the critic are blind to the route input, the auxiliary head keeps its loss (coefficient 1.0) during PPO, and the rest of the recipe is unchanged (262,144 added transitions, same mix, same learning rate, same evaluation). Seeds 901, 902 and 903.
5. **Comparison.** The controls (701, 702, 703) and the auxiliary arm (801 to 803) of the previous experiment, whose evaluations on the same pool and cells already exist and are reused without change.

## Evaluation

Final checkpoint of each `pre` run, pool 882000 (the pool used for the comparison runs; it selects nothing), 64 episodes per cell, the same six cells as before: `passages`, `passages-mid`, `passages-wide`, medium, `passages` with sampled actions, and level B development maps. No checkpoint is selected.

## Decision rules (frozen before running)

Primary metric: `passages`, deterministic, pool 882000.

- **Positive:** the mean of the three `pre` runs is at least 12/64 above the control mean (12.3), each `pre` run is above each control run, `passages` collisions are lower than the control mean by at least 8, and the means on `passages-mid`, `passages-wide` and medium are not lower than the control means by more than 4.
- **Negative:** the gain over the control mean is below 6/64.
- Anything between is inconclusive and no seeds are added afterward.
- A gain in only one of the deterministic and sampled modes is partial.
- The comparison with the auxiliary arm (14.7 on average) is reported as well. A positive result needs the control comparison, and the auxiliary comparison shows whether the pretraining step is what mattered.

## Interpretation

- Gate fails: the 256 features of the source policy cannot be made to carry the direction with 512 maps of supervision at this capacity (two 128-unit layers), which points to capacity, features or the label, and ends this route.
- Gate passes and PPO is negative: the representation can encode the direction offline, but the actor does not use it to steer. The bottleneck is the use of the information in behavior, which would call for behavior supervision (a different experiment, closer to the imitation work that failed on `large`) or a longer budget.
- Positive: supervised representation learning followed by RL is the way. The next experiment would scale the data and test the held-out families.

## Limits

Poses come from the source policy's own flights, which stay near its habitual paths and rarely visit states far from the route. The label is the direction to a point 4 m ahead on one certified route. 512 maps from one generator, `passages` family only: the experiment does not cover mazes or large rooms. Three seeds, with the same caveats on reliability as before. The pool 882000 was used for the previous comparison and is reused for it here, so the evaluation is a repeat on one pool, not a fresh one; conclusions are screening-level.
