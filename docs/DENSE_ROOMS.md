# Dense rooms

The original dense task uses a 32 × 32 × 12 room with 48 box obstacles, randomized endpoints at least 14 units apart and a randomized initial heading. A hidden collision-clear route certifies reachability; the controller receives neither that route nor the obstacle list. Synthetic sensors provide local rays, approach readings, target direction and state values through the fixed recurrent brain.

The fly has radius 0.16. Arrival requires distance below 0.45, and the original episode allowance is 1,200 decisions, or 60 simulated seconds. Swept collision detection checks the trajectory between positions. Reachability of a layout does not establish that a learned controller can follow its available route.

## Selection and evidence

The original suite separates 256 training, 32 validation and 64 final layouts. Loading regenerates geometry and checks frozen fingerprints. Seed separation alone cannot rule out distribution overfitting or later misuse of final outcomes.

Validation ranks success, then fewer collisions, then lower mean ending distance. It includes the initial controller, so a training run can finish without producing a better selected checkpoint. Final assessment occurs after freezing selection and consumes the reserved pool.

The coordinated dense launcher alias has 327,680 lifetime transitions. Its historical final assessment reached 43/64 goals, with 11 collisions and 10 timeouts. This result does not meet the 80% target or establish robustness beyond the generator. Its final pool is consumed. Later tuned experiments use separate suites; their outcomes are summarized in [Results](RESULTS.md).

## Viewing

```powershell
.\launch-dense.cmd
.\.conda\python.exe -s -m fly_rl plot-dense runs/training/dense-flight-v1
```

The launcher runs a live policy with available local checkpoints. The plot command reads saved records without training or policy evaluation. Default demo seed 10 is a training layout. Inspecting an already evaluated final seed is known-room viewing, rather than a new independent assessment.

New profiles add structured passages, larger rooms and branches with per-layout time allowances. They are separate distributions and require explicit checkpoint transfer or a compatible trained model. See [Progressive maps](GEOMETRY_CURRICULUM.md), [Commands](COMMANDS.md) and [Operations](OPERATIONS.md).
