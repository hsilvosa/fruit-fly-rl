# Short brain memory and temporal policy correction

Measured on 2026-10-04 using the original sensors-v3 interface and the full annotated MaleCNS graph. This diagnosis concerns the original controller, before adding a clock.

The graph has maximum absolute row sum 0.900000274. The recurrence is h_next = 0.5 h + 0.5 tanh(W h + sensory). Since tanh is 1-Lipschitz, differences between states under the same subsequent input contract by at most 0.5 + 0.5 norm_inf(W), approximately 0.95 per 50 ms decision. The corresponding worst-case e-folding time is 0.975 seconds. This is a mathematical bound under identical subsequent inputs, not a biological memory claim.

A full-graph pulse test changed target_y once in one of two otherwise identical streams, then supplied identical sensors. Relative maximum neuron-state difference fell to 0.159 after 0.25 seconds, 0.0441 after 0.5 seconds, 0.00295 after one second and approximately 9.53e-6 after 2.5 seconds. Later values reach floating-point precision limits. Evidence is in private/full-connectome-memory-diagnosis.json. The movement policy was a feed-forward MLP, so it had no separate learned history. These facts identify a short-memory limitation relevant to multi-wall search; they do not prove that every reactive controller must fail or establish this as the sole cause of timeouts.

## Implemented correction

BrainEnv can provide history_frames sampled every history_stride decisions, followed by the current 256 connectome features. With 32 frames and stride eight, retained samples cover approximately 12.8 seconds at 50 ms per decision. The precise sample ages vary with the sampling phase. No raw sensors, positions, obstacles, hidden opening locations or certified routes are supplied to the temporal readout.

A 64-unit GRU processes the feature sequence. A linear residual maps its final output back to 256 dimensions and is added to the current feature vector. Its weight and bias start at zero. Thus the initial readout equals the previous current-feature interface for all histories. The actor and critic weights, exploration scale and Adam states for copied parameters are transferred explicitly from the original controller. Temporal-module optimizer states begin fresh. This preserves initial action and value predictions; it is not exact resumption of the old policy architecture.

This uses [SB3 custom feature extractors](https://stable-baselines3.readthedocs.io/en/master/guide/custom_policy.html), with orthogonal reinitialization disabled to preserve the zero residual. Older policies keep their original feature shape and behavior. Metadata records history dimensions, sampling stride and transfer provenance. Loading for evaluation and the viewer constructs the declared history interface automatically. Ordinary flight recordings continue to store the instantaneous 256 brain features.

Each natural episode reset clears only that fly's history. Terminal value observations retain the ending history rather than the next episode's cleared history. Continuing episodes and histories survive live training chunks. A full environment reset clears all histories. Saved policy archives do not preserve live world/history buffers for an exact process restart.

## Verification and limits

The full suite passed 167 tests. Tests verify sampled feature order, independent reset and terminal histories, exact initial action/value equivalence, copied optimizer states and the temporal branch's ability to distinguish different histories with identical current features after its output weights are enabled.

A full-graph CUDA smoke used 128 added transitions and one PPO update, starting from the original round-23 sensors-v3 controller with 32 history frames and stride eight. Losses were finite, checkpoint reload reproduced actions and the original source ZIP retained its hash. Evidence is in private/brain-history-smoke.json. This is verification, not navigation training evidence. A two-second offscreen demo executed 40 transitions with finite activity and no training invocation on the unchanged 112-box large profile.

The previous clock/exposure pilot still reached zero goals. The new temporal policy has not yet been assessed in a bounded navigation experiment. The independent final pool remains unused; no 80 percent claim is justified. The next experiment should preserve the original sensor semantics to isolate temporal memory from the measured clock-transfer disruption, report actual full-episode and target-exposure counts, and compare on development layouts before consuming independent evidence.
