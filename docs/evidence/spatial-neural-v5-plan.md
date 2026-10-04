# Spatial neural navigation v5 protocol

The original-large navigation goal remains unmet. The v4 source and trained controller both failed all eight development flights. The next bounded correction tests a structured neural readout and fresh spatial policy, without PPO refinement.

Every annotated neuron and edge remains simulated. Neural activity is grouped using the existing seeded input assignments. Each output is the signed mean activity of neurons assigned to that input channel. These are artificial channel groups, not identified biological cell types. The actor receives 1,447 neural outputs, never raw sensors, world pose, hidden routes or complete obstacle maps. Two 19 by 31 neural fan planes pass through a convolutional encoder; the remaining channel groups pass through a learned linear encoder. A GRU consumes nine frames at stride eight. New fingerprints reject incompatible legacy readouts.

The experiment adds at most 98,304 world transitions: 65,536 teacher-controlled transitions across 16 fragments, followed by two 16,384-transition student-only rounds. Training fragments sample from the 112 optimization layouts and their hidden route vertices. The existing world reset samples a layout using the requested reset seed: the 128 planned fragment starts cover 74 distinct actual layouts, with further automatic resets able to sample more. Status fragment_seeds records requested sampler seeds; the actual initial layouts are reconstructed in private/spatial-neural-v5-layout-audit.json. The experiment does not guarantee a fragment in every pool layout. Room dimensions, obstacles, openings, collisions and physics remain the original large profile. The first four fragments start at original endpoints. Fragment successes must not be reported as original-start autonomous successes.

The teacher provides privileged training labels and actions during teacher fragments. During student rounds it only provides labels; the policy determines all executed actions from brain activity. Supervision uses 3,072 initial updates and 1,536 further updates on retained optimization examples. These replay updates do not count as additional world transitions. There is no PPO phase or critic fitting in this experiment.

The final checkpoint is fixed in advance and evaluated on development seeds 430000 through 430007, from original endpoints without a teacher. This suite has been reused and cannot demonstrate independent generalization. No final test is consumed, no launcher alias is promoted, and no biological advantage is claimed. Original alias hashes are checked before and after. Substantive cumulative cap: 786,432. The full-graph 128-transition smoke is separate verification.

The static counterfactual readout diagnosis motivates the representation but does not show learned navigation. The existing eight-map controller failure remains the baseline; this is a bundled engineering correction rather than a controlled causal comparison.

Explicit command:

```powershell
.\.conda\python.exe -s -m fly_rl train-spatial --plan private/spatial-neural-v5-plan.json
```

The plan freezes runtime sources and refuses an existing experiment status. Progress is written atomically to runs/training/spatial-neural-v5/status.json. Opening a demo never invokes training.
