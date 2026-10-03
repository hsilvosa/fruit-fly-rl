# Architecture

The project separates the biological dataset from the engineered controller, the physical environment, and the tools used to observe a run. This separation makes it possible to change rendering without changing learning, or audit a saved flight without loading the connectome.

## From a room to a movement

```text
World state
  -> 269 engineered sensor values
  -> seeded sensory projection
  -> full fixed recurrent connectome activity
  -> 256 pooled features
  -> PPO actor: four movement commands
  -> fixed-timestep flight and collision update
  -> next world state
```

The policy receives pooled brain features. It does not receive a second direct sensor input, the obstacle list, or the generator's reference route. The sensory interface does include target direction and distance even when the target is occluded. This is a navigation task with engineered sensing, not image-based target recognition.

## Code ownership

| Area | Files and responsibilities |
| --- | --- |
| [Connectome](../fly_rl/connectome/__init__.py) | `data.py` downloads, joins, prepares, and audits official tables; `brain.py` checks prepared-file integrity and runs recurrence; `anatomy.py` joins body IDs with real soma positions and labels |
| [Simulation](../fly_rl/simulation/__init__.py) | `world.py` generates rooms, observations, rewards, and episode outcomes; `sensors.py` defines ray directions and the versioned sensor contract; `flight.py` implements the coordinated movement rules |
| [Training](../fly_rl/training/__init__.py) | `learning.py` provides the vector environment, PPO, and model compatibility; `iteration.py` handles small-room curriculum; `dense_training.py` runs bounded rounds; `evaluation.py` measures episodes; `selection.py`, `suites.py`, and `generalization.py` handle selection, frozen layouts, and final testing |
| [Visualization](../fly_rl/visualization/__init__.py) | `viewer.py` runs live viewing and archived playback; `camera.py` controls the camera; `brain_map.py`, `neural_view.py`, and `neural_trace.py` support anatomical inspection; `playback.py` defines speed scaling; plotting modules render existing results |
| [Recordings](../fly_rl/recordings/__init__.py) | `recording.py` writes telemetry; `archive.py` inspects, compares, and recovers archives; `replay.py` presents saved states; `shutdown.py` finalizes records independently of optional screenshots |
| [CLI](../fly_rl/cli.py) | Parses explicit commands and dispatches to these areas; importing the package does not download data or begin learning |

Tests follow the same five areas under `tests/`. The root Windows scripts are intentionally kept near the README so a person can find and launch the demo easily. Large local artifacts keep their existing `data/`, `runs/`, and `reports/` paths.

## Brain and policy

The graph has one modeled state per retained neuron. Its sparse matrix uses postsynaptic rows and presynaptic columns. Incoming absolute weights are normalized and scaled to 0.9. Predicted GABA neurons contribute negative outgoing signs; other modeled transmitters use positive signs. The state update mixes half of the previous state with half of the new hyperbolic-tangent response. Two seeded sensory indices per neuron supply signed input, and signed bucket pooling produces 256 features.

These numerical choices are engineering assumptions. They are neither calibrated membrane dynamics nor a validated interpretation of the biological neurons. The graph and sensory projection are fixed during PPO training. PPO learns the actor and critic, each with two 128-unit hidden layers; it does not change synapses inside the connectome. CUDA runs the sparse recurrent graph, while the present PPO policy runs on CPU.

`BrainEnv` maintains separate room and recurrent states for vectorized episodes. A terminal observation is preserved for logging before the environment starts a fresh episode. Reset clears the corresponding recurrent state. Checkpoint metadata binds the graph fingerprint, reservoir/sensor specification, and flight dynamics. Explicit transfer can permit a dynamics mismatch, but it is an experiment rather than proof of compatibility.

## Rendering and inspection

The fly and brain windows share one simulation, graph, and policy. The anatomical window is an additional Panda3D output rather than a second training process. It shows official soma coordinates and labels. The selected-neuron history is bounded, and sampled observations are aligned with the activity used to choose the action. Details and interpretation limits are in [Flight and neurons](FLIGHT_AND_NEURONS.md).

Simulation speed changes how many fixed 0.05-second decisions advance. It does not change the physics timestep. The displayed multiplier is requested speed; rendering, full-graph inference, and logging can limit wall-clock throughput.

Saved-state replay replaces the live environment and policy with archive readers. It does not reconstruct recurrent activity from pooled features, train a model, or require the graph. Full-brain snapshot playback in the anatomical viewer remains future work.

## Persistence boundaries

Source, tests, technical documentation and aggregate evidence are tracked in Git. Detailed journals, machine-specific launch records and original evidence are preserved under the ignored `private/` directory. Downloaded data, Conda packages, checkpoints, archives, figures, and full experiment logs are ignored. Git history alone cannot reproduce a trained local checkpoint; those artifacts need their own backup.

Every live recording gets a unique directory. The latest preview and summary may be overwritten. Shutdown finalizes telemetry before attempting a screenshot. See [Operations](OPERATIONS.md) for recovery and storage guarantees, and [Data and model](DATA_AND_MODEL.md) for the dataset selection and version contracts.

## Equations and optimization

Versioned map configurations and geometry descriptors live in `simulation/map_profiles.py`. The original world generator remains the default, while profiled suites serialize their complete target and training variants. `training/geometry_curriculum.py` changes only the training reset distribution; `training/geometry_comparison.py` freezes the source, paired initialization, budgets and shared target evaluation. Checkpoint metadata distinguishes the evaluation target from the currently active training profile. Explicit map transfer is required when those contracts differ. Viewer archives and saved-state replay retain the actual room profile and episode allowance. See [progressive maps](GEOMETRY_CURRICULUM.md).

See [Mathematical model and optimization](MATHEMATICS.md) for the exact recurrent, sensory, flight, reward, PPO/GAE, optimizer, and metric formulas, including source links and current parameter values.
