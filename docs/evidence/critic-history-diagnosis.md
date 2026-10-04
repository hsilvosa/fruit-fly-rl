# Post-v2 controller diagnosis and critic isolation

Original-large navigation remains unresolved. This diagnosis uses only retained optimization observations, labels and checkpoints; it adds no environment transitions, executes no reserved-test evaluation and changes no existing model weights.

## Offline evidence

The 32,768 teacher transitions covered 15 distinct optimization layouts from the declared 112-layout pool. On a fixed sampled subset, initial imitation action mean absolute errors were 0.02723 forward acceleration, 0.01455 altitude and 0.02570 yaw. On first student-round states those errors were 0.41130, 0.41948 and 0.38701. Supervised fit quality on teacher trajectories did not establish robust closed-loop recovery.

The pre-PPO guided checkpoint reduced first-round errors to 0.23083, 0.10190 and 0.16819. The final PPO checkpoint increased them to 0.43392, 0.19387 and 0.28688. These are descriptive comparisons on retained optimization samples, not new flight evaluations or independent generalization evidence. The final PPO approximate KL was 0.159238 against target 0.01; this target is an early-stop threshold, not a hard bound on each optimizer step.

## Shared gradient path

The current history policy shares its learned GRU feature extractor between actor and critic. Value loss therefore updates actor memory as well as the critic. On one saved optimization minibatch, teacher-label actor MSE was 0.057212 with memory-gradient norm 0.51856. An illustrative zero-return value target produced loss 733.17822 and memory-gradient norm 22,214.61523. The zero target is a diagnostic, not a reconstruction of the actual PPO returns. These measurements establish a coupling mechanism; they do not establish the sole cause of the observed navigation failures.

## Explicit correction

New policies can opt into separate actor and critic history extractors through `share_history=False`; future guided plans select `isolate_critic_history=true`. Before critic initialization, a one-time copy synchronizes critic memory from the fitted actor. Subsequent value gradients cannot update actor memory. Actor policy gradients still train actor memory. Existing policy defaults and checkpoints retain their original sharing behavior; completed experiments are not retroactively changed.

Sixteen temporal-policy and guided-learning tests passed. A meaningful optimizer test verifies that a critic-only update changes critic parameters while leaving actor memory and deterministic actions exactly unchanged, then verifies checkpoint reload. Warm transfer still preserves actor actions and value predictions. Small graph fixtures in these unit tests are not substitutes for the full graph in experiments.

No isolated-memory navigation training has started. The completed v2 transition cap is exhausted. A further experiment requires its own explicit budget and frozen protocol. GPU utilization is a separate issue: the fixed brain uses CUDA, while the current PPO policy is intentionally constructed on CPU; separating gradient paths does not move the policy to CUDA.
