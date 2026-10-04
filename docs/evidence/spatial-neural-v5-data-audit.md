# Spatial neural optimization-data audit

This audit reads completed fragments from the active v5 experiment. It does not advance the environment, optimize a model, alter checkpoints or assess navigation.

The first 36,864 completed fragment rows contain finite teacher labels. A deterministic 4,096-row sample contains finite neural histories and no zero current-feature vectors. Across fan-distance channel groups, the standard deviation ranges from approximately 0.022 to 0.067. Neural inputs therefore vary in these samples; this does not establish that they contain every signal needed for navigation.

Labels span forward commands from -0.301 to 1, vertical commands from -1 to 0.912 and yaw commands from -1 to 1. Lateral commands remain zero because the coordinated teacher does not use lateral thrust. Approximately 5.97% of labels have yaw magnitude above 0.25 and 2.83% have vertical magnitude above 0.25. The imitation sampler already oversamples strong turns; these proportions describe the retained data rather than the sampled optimization batches.

Approximately 7.46% of sampled historical frames are zero, including the initial history at independent fragment starts. Current neural features are nonzero in every sampled row. Detailed measurements remain in private/spatial-neural-v5-data-audit.json. The audit concerns optimization data and makes no independent-generalization or biological claim.
