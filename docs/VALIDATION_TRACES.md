# Validation flight traces

Bounded diagnostic inference records behavior on retained validation failures. It is separate from training and from the reserved final assessment.

## Commands

From the project directory:

```powershell
.\.conda\python.exe -s -m fly_rl trace-validation runs/training/sensors-fresh-v1/v3-seed-42 --output runs/diagnostics/sensors-fresh-v1-v3-42 --count 2 --max-steps 1200
.\.conda\python.exe -s -m fly_rl plot-validation-trace runs/diagnostics/sensors-fresh-v1-v3-42/summary.json --output reports/sensors-fresh-v1-validation-traces.png
```

The first command executes the frozen policy on validation only. It accepts an individual completed experiment, audits its frozen checkpoint, metadata and suite hashes, and verifies that retained episode seeds match the validation split. It rejects final summaries and arbitrary seed selection. Examples are chosen deterministically by alternating a collision and a timeout where available. The output directory must be new; use another name for a future diagnostic.

The cap is one to four cases and at most 1200 decisions per batch. The checked two-case run therefore executed at most 2400 environment transitions. This is inference, not training. A replay stopped by a shorter budget is labeled `budget-truncated`, rather than counted as an episode timeout. Inactive batch slots can advance reset episodes while another slot finishes; only the requested first episode is recorded, and the transition budget includes those inactive slots.

The plot command reads saved arrays and executes neither brain nor policy. It verifies archive checksums before drawing. The JSON summary and compressed NPZ files remain local under `runs/diagnostics/`; plots remain under `reports/`. [Verification](VERIFICATION.md) describes the correctness checks; original measured artifacts and their hashes remain local and ignored.
## What is retained

Each decision stores position before and after the action, terminal velocity, actual action, reward, altitude through position, yaw, measured yaw rate, bank, pitch, target distance, collision clearance, 269 sensor values, and 256 pooled brain features. Features and sensors are recorded before the action; movement is captured after the action and before automatic reset. Pooled features are not full-neuron activity. No anatomical values are fabricated from them.

Geometry includes the room, obstacle boxes, and target. A terminal collision records wall axes and every obstacle intersected by the swept attempted movement. The attempted endpoint is computed from the prior position and terminal velocity using the existing timestep; the displayed position may have been clipped to room bounds. This distinction prevents a wall crossing from disappearing after clipping.

Clearance is a diagnostic signed distance to the existing radius-inflated collision boxes and room boundaries. Positive means outside the inflated obstacle volumes, negative means inside, and zero means a boundary. This value is not injected into the policy and does not change collisions or rewards. Swept contact is checked separately because a segment can cross a box while its endpoint is outside.

## Protocol and measured outcomes

Diagnostics read retained validation outcomes and execute only the declared frozen checkpoint. They make no optimizer updates and do not establish a population-wide cause from a few selected examples.

Trace only the frozen validation configuration under the declared diagnostic decision cap. Plots read saved arrays and execute neither policy nor optimizer. Diagnostic inference must not use the reserved final pool.

See [Results](RESULTS.md) for aggregate validation, final counts, uncertainty and limits, [Mathematics](MATHEMATICS.md) for optimization, and [Commands](COMMANDS.md) for execution. Detailed trajectories, decisions, launch records and original machine evidence remain local and private. No biological advantage is inferred from navigation performance.
