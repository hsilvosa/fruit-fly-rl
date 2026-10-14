# Supervised pretraining of the actor trunk, then PPO: results

Run October 11, 2026 under [PRETRAIN_PROTOCOL.md](PRETRAIN_PROTOCOL.md), committed before data collection (`8bf628f`). The whole experiment took 1 hour 16 minutes against an estimate of 1 hour 45: collection took 13 minutes (estimated 30), pretraining under 1 minute, three PPO trainings 30 minutes, and evaluation 34 minutes.

## Step 1: offline pretraining (gate passed)

Data: 512 maps, 151,046 samples of the 256 features the actor reads, from sampled-action flights of the source policy. Split by map: 103,924 train, 14,517 validation, 32,605 test (65% of the samples are hard). Held-out maps:

| Measure | Before pretraining | After (test maps) |
| --- | --- | --- |
| Median angular error to the route direction, hard subset | 104 degrees (random head) | **41.6 degrees** |
| Median angular error, all samples | 100 degrees | 37.0 degrees |
| R-squared of the mean action against the source policy | 1.0 | 0.996 |

The gate (hard-subset error at most 45 degrees and action R-squared at least 0.9) passed. The 256 features of the source policy, through the actor's two 128-unit layers, encode the route direction to about 42 degrees on maps never seen in the supervision, and the flight behavior is preserved. This is better than the roughly 50 degrees of the probes with 64 maps and close to what the synthetic probe got from raw rays (34 degrees).

## Step 2: PPO from the pretrained trunk (negative)

Successes / collisions / timeouts of 64, pool 882000. Controls and the auxiliary arm come unchanged from [AUXILIARY_STUDENT_RESULTS.md](AUXILIARY_STUDENT_RESULTS.md).

| Run | Passages | Passages-mid | Passages-wide | Medium | Passages, sampled | Level B dev |
| --- | --- | --- | --- | --- | --- | --- |
| Pre 901 | 20/28/16 | 35/10/19 | 52/0/12 | 56/6/2 | 14/46/4 | 4/39/21 |
| Pre 902 | 14/22/28 | 43/5/16 | 60/0/4 | 48/8/8 | 23/27/14 | 3/19/42 |
| Pre 903 | 9/39/16 | 28/19/17 | 45/11/8 | 58/4/2 | 11/38/15 | 3/32/29 |
| **Pre mean** | **14.3** | 35.3 | 52.3 | 54.0 | 16.0 | 3.3 |
| Control mean (701 to 703) | 12.3 | 33.0 | 48.3 | 54.3 | 10.7 | 1.7 |
| Auxiliary arm mean (801 to 803) | 14.7 | 32.0 | 45.3 | 55.3 | 17.0 | 3.7 |

On the primary metric (`passages`, deterministic) the gain over the control is **+2.0/64**, below the 6/64 line for a negative result. Collisions on `passages` are 29.7 against 29.0 for the controls: no reduction. The positive rule is not met on any clause.

Secondary, not decisions: `passages-wide` is 4.0 above the control (52.3 against 48.3, with a spread of 15 between runs), and `passages` with sampled actions is 5.3 above (the auxiliary arm is at 6.3). The pretraining arm is level with the plain auxiliary arm everywhere: `passages` −0.3, medium −1.3, sampled −1.0.

## Reading

1. **The representation can carry the information, and the policy still does not use it.** The offline step shows that the direction is encoded to about 42 degrees from the policy's own features, on new maps, with the flight behavior unchanged. After PPO, the flight results are the same as without that step. This separates the two possible failures that the plan had left open: the lack of a usable representation is not the bottleneck, whereas turning the representation into steering is.
2. **The training-only route signals are now closed at this budget.** The auxiliary head with PPO data, the privileged critic and the supervised pretraining all give `passages` between 13 and 15 of 64, against 12 for the control. Only the actor reading the route at decision time (the diagnostic) reaches 36 to 39 on a different pool.
3. **What the diagnostic had that the students lack** is the route direction as an input to the policy's steering layers at each step. A representation inside the trunk, even when it encodes the direction, did not change what the action layers do under PPO at 262k transitions with the small learning rate of the recipe. The pretrained trunk keeps the old behavior (that was the objective of the preservation term), which may also keep the action layers from changing. This is a hypothesis; it was not tested.

## What this does not show

One preservation weight (1.0), one trunk size, one label, 512 maps from the `passages` family and the source policy's own flights. The action layers were frozen in function by the preservation term, so a different design that lets the actor's steering depend on the encoded direction (for example supervised behavior from a teacher that sees the route) is not excluded. Teachers of that type were tried on `large` earlier and failed (0/8), with other policies. Three seeds, with large seed variation. `passages` only: mazes and large rooms are not covered. Pool 882000 was reused for this comparison and selected nothing.

## Consequences for the plan

- The route-information line for the autonomous student is exhausted in the forms tested: representation, value and pretraining all failed to move `passages` at this budget.
- Open, and none cheap: a much larger budget (1M transitions or more) with a single seed and a learning curve; behavior distillation from the route-aware policy (risky given earlier failures); memory or long-range sensing for `large` and mazes.
- The defensible claim stays: zero-shot navigation in medium rooms (86 to 92% on fresh pools), partial results on partitioned rooms (about 20% on `passages`, 50 to 80% on the easier partitioned profiles), and no evidence that the four-family gate is within reach with this approach.
