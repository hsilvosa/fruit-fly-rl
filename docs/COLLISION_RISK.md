# Observed-ray risk

This training-only penalty uses available range and closing-speed sensors. It does not provide hidden obstacle geometry or reference routes to the policy.

## Formula and objective

For ray i, decode observed range d_i = 8 s_i and projected closing speed c_i = 3 s_(128+i). A ray contributes only when d_i < 8 - 0.00001 and c_i > 0.1. Otherwise its risk is zero. For contributing rays:

    tau_i = max(d_i - 0.16, 0) / c_i
    q = max_i max(0, 1 - tau_i / 0.75)
    reward_training = reward_base - 0.05 q

Risk is calculated from the observation before applying the action. The version is `observed-ray-risk-v1`. It uses available engineered range and closing-speed values, with no hidden obstacle map or route reference. The 0.16 radius subtraction is a scalar approximation, not exact swept-box clearance. Occluded obstacles and objects beyond sensor range cannot contribute; future steering is ignored.

This additive penalty changes the training objective. It is not potential-based shaping and carries no guarantee that the optimal policy is preserved. It may induce excessive hesitation. Evaluation and demos retain ordinary rewards, physics, success radius, sensors and starts; loading a checkpoint does not install this training wrapper. Checkpoint metadata records the base reward version and separate shaping version, counters and parameters. There is no change to the connectome or internal synaptic plasticity.

## Protocol and measured outcomes

Use a new suite, explicit transition budget and independent initialization seeds for each comparison. Select checkpoints and methods using validation only; freeze the winner before one final assessment. Include the initial controller in selection and retain unsuccessful results. A completed optimizer budget does not guarantee improved navigation.

The comparison uses matched fresh v3 policies, a normal-training control, seeds 42 and 73, two rounds and 131,072 transitions per method and seed. Only the validation winner and untrained control are final-tested; this is not a paired final comparison of methods.

See [Results](RESULTS.md) for aggregate validation, final counts, uncertainty and limits, [Mathematics](MATHEMATICS.md) for optimization, and [Commands](COMMANDS.md) for execution. Detailed trajectories, decisions, launch records and original machine evidence remain local and private. No biological advantage is inferred from navigation performance.

## View the selected policy

On a machine retaining the completed local run:

```powershell
.\.conda\python.exe -s -m fly_rl demo --room-mode dense --dynamics coordinated --brain-view --checkpoint runs/training/ray-risk-v1/selected/selected-policy.zip
```

This runs live inference in a preview room, without optimization or a new reserved evaluation. A source-only clone does not contain the local checkpoint.

The [retained validation figure](evidence/ray-risk-v1-validation.png) shows both seeds and their selected outcome counts. It summarizes the historical risk experiment, not the later progressive-map comparison.
