# Sensors v3

Version 3 changes three sensor values while preserving the 269-value order, 128 distance rays, 128 approach readings and full connectome. This is an engineered interface change.

## Interface changes

| Value | Existing v2 | New v3 |
| --- | --- | --- |
| Target distance | Distance divided by 18, clipped | Distance divided by the interior room diagonal, norm(room size - 2 body radius) |
| Altitude | Height divided by 6, clipped | Height divided by the current room height |
| Final state value | Previous yaw command repeated | Actual yaw rate divided by 2.6 radians per second |

The final clip to [-1,1] remains. Coordinated yaw rate comes from its filtered rate state. Legacy dynamics have an instantaneous rate of 2.1 times the previous yaw command. The denominator 2.6 covers the coordinated maximum desired rate. Geometry, rewards, sensor rays, seeded neuron projection, and pooling are identical between versions. See [formulas](MATHEMATICS.md).

Each world and brain declares its version. A mismatch is rejected. Metadata and the reservoir fingerprint identify the sensor contract; old metadata without a sensor field resolves to v2 only when its fingerprint agrees. Training, evaluation, demo loading, and archive labels follow the saved checkpoint. No existing default is changed.
## Explicit warm-start transfer

```powershell
.\.conda\python.exe -s -m fly_rl migrate-sensors runs/dense-flight-policy.zip --output runs/NEW-v3-baseline.zip
```

The command creates a new weight/optimizer archive with identical bytes, writes a v3 metadata sidecar, and records the original weight and metadata hashes. It never overwrites the source. This is semantic transfer, not evidence that the old policy already works with the new readings. Ordinary checkpoint loading still rejects different fingerprints.

## Protocol and measured outcomes

Use a new suite, explicit transition budget and independent initialization seeds for each comparison. Select checkpoints and methods using validation only; freeze the winner before one final assessment. Include the initial controller in selection and retain unsuccessful results. A completed optimizer budget does not guarantee improved navigation.

Warm-start adaptation and fresh paired initialization differ in starting weights and inherited sensor semantics. Their final rooms also differ. Comparisons across those experiments are not paired method comparisons.

See [Results](RESULTS.md) for aggregate validation, final counts, uncertainty and limits, [Mathematics](MATHEMATICS.md) for optimization, and [Commands](COMMANDS.md) for execution. Detailed trajectories, decisions, launch records and original machine evidence remain local and private. No biological advantage is inferred from navigation performance.
