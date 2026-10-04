# Matched temporal-readout comparison

Prepared on 2026-10-04 after measuring rapid fading of the fixed reservoir and confirming the initial action/value equivalence of a zero-residual temporal upgrade on the full connectome.

## Frozen comparison

Two arms start from the same preserved large-continuous-v4 round-23 sensors-v3 movement policy and copied Adam states: current-features and brain-history. This is one paired warm-start comparison with training seed 42, not repeated independent initializations. The temporal arm adds a 64-unit GRU over 32 historical brain-feature samples at stride eight and the current feature. Its initially zero residual preserves actor and critic predictions. Both use the same full annotated graph, flight dynamics, source movement weights, optimization layouts, PPO settings and gamma=0.9995.

The clock channel is excluded from both arms to isolate the temporal readout from the measured clock-transfer disruption. Both retain the original external-truncation learning semantics and timeout penalty; the finite deadline remains partially observed in this interface. Thus this experiment tests added brain-feature memory under matched original sensing, not a complete fix of the deadline objective. Original map and reward semantics remain unchanged.

Each arm has 65,536 added transitions across eight continuous chunks of 8,192, batch eight. Four environments always use the unchanged original large target (48 by 48 by 16, 112 boxes, five partitions, 3.2 by 3.2 openings), guaranteeing 32,768 target transitions per arm. The other four retain the source checkpoint's documented stage four, large-wide, with the existing easier-task mixture. That stage is fixed during this diagnostic comparison, without practice gates or adaptive evaluation.

The total added budget is 131,072. Previous substantive added transitions are 319,488, so planned cumulative use is 450,560 of the existing 524,288 budget, leaving 73,728. Smoke checks are separate verification. The runner stops on completion or error, without extending or restarting training.

## Measurements and isolation

Optimization uses only the previous declared optimization layouts, disjoint from the 16 withheld practice layouts. Eight validation seeds, 430000 through 430007, are disjoint from optimizer layouts and all existing suite seed pools. Their large-map geometry hashes are frozen before launch. The common source is measured once before training. Each arm's final checkpoint is measured once on the same eight validation layouts after its full budget; intermediate checkpoints are not selected by evaluation.

Report success, collision and timeout counts, arrival times, flown distances, final distance, idle fraction, actual target exposure and full training episode outcomes. These eight layouts are validation, not the reserved final test. The result can inform subsequent development and cannot establish the 80 percent independent-test objective or a biological advantage. A single seed and eight layouts limit causal and statistical confidence.

Source files, configuration, source checkpoint and metadata, temporal initial checkpoint and metadata, geometry and original alias hashes are frozen. The original source policy and six launcher aliases are preserved and no checkpoint is promoted. The independent final pools are neither evaluated nor consumed.

Verification before launch: 167 tests passed; full-graph CUDA one-update smoke with 128 transitions had finite losses and compatible reload. The actual full-graph temporal initialization matched source action and critic predictions. Independent history resets and ending terminal histories are tested. The rendered demo was inspected on the original large room.
