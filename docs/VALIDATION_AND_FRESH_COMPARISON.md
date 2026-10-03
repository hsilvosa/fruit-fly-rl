# Fresh initialization comparisons

Matched fresh initialization separates an interface change from transferring previously trained weights. Warm-start and fresh experiments answer different questions.

## Fresh comparison protocol

The new suite, `runs/suites/sensors-fresh-v1.json`, has 256 training rooms with seeds 130000–130255, 32 validation rooms with seeds 140000–140031, and 64 reserved final rooms with seeds 150000–150063. Seed and geometry overlap are checked against all three historical suites. At preparation, final outcomes remained untouched; the completed assessment consumed this pool; its aggregate outcomes appear in [Results](RESULTS.md). Novelty is relative to those supplied historical suites and this room generator.

For each initialization seed, construct a new PPO policy with zero timesteps, zero optimizer updates, and an empty Adam state. Save its v2 checkpoint, then copy the archive byte for byte for v3 and change only the sensor-contract metadata. Although the implementation reuses the explicit migration utility, these copies contain no pretrained weights or optimizer history. The full fixed brain, sensory projection, and feature pooling are shared; sensor normalization and measured yaw rate differ by interface.

The training runner uses seeds 42 and 73, coordinated flight, batch 8, and two rounds by default. Each interface receives the same declared per-seed transition budget. Validation chooses a checkpoint within each seed, then a seed within each interface, then one interface. Ranking is success rate, fewer collisions, then lower ending distance; an exact interface tie selects v2. Only the frozen winner and a fresh untrained control using its interface reach the final test. This design does not estimate a paired v2-versus-v3 final-test effect, and two initialization seeds provide limited evidence about variation.

Policy files, metadata, paired-weight hashes, source snapshots, declared configuration, suite checksum, dataset fingerprint, stage/status, per-round losses, validation results, selection records, and final evidence are saved under a new experiment directory. Existing launcher aliases are preserved. A failed run records its error and stops; the tool does not silently extend a budget or restart it.

## Protocol and measured outcomes

Use a new suite, explicit transition budget and independent initialization seeds for each comparison. Select checkpoints and methods using validation only; freeze the winner before one final assessment. Include the initial controller in selection and retain unsuccessful results. A completed optimizer budget does not guarantee improved navigation.

Warm-start adaptation and fresh paired initialization differ in starting weights and inherited sensor semantics. Their final rooms also differ. Comparisons across those experiments are not paired method comparisons.

See [Results](RESULTS.md) for aggregate validation, final counts, uncertainty and limits, [Mathematics](MATHEMATICS.md) for optimization, and [Commands](COMMANDS.md) for execution. Detailed trajectories, decisions, launch records and original machine evidence remain local and private. No biological advantage is inferred from navigation performance.
