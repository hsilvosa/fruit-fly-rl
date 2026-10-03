# Fly RL

A virtual fruit fly navigates procedural 3D rooms using features from the full annotated MaleCNS v1.0 connectome. A fixed sparse recurrent model converts simulated sensor readings into activity; a PPO actor and critic learn flight commands. Panda3D displays the room and an optional separate anatomical activity window.

This is an engineered navigation experiment. Synthetic distance rays and target direction are available to the controller. The recurrent equations, sensor projection and flight dynamics are project choices, rather than a biological simulation of vision, spiking neurons or wing aerodynamics. Navigation success alone does not establish a benefit from fruit-fly wiring.

## Dataset credit

The MaleCNS reconstruction, annotations and soma coordinates were produced by the FlyEM team at HHMI Janelia Research Campus, the University of Cambridge Department of Zoology, the MRC Laboratory of Molecular Biology, Google Research, and the contributors credited in the original publication. See the [official project](https://male-cns.janelia.org/).

Cite Berg, S., Beckett, I. R., Costa, M., et al. (2026), *Sexual dimorphism in the complete Drosophila male central nervous system connectome*, Cell, 189(18), 5504–5526.e15. [DOI](https://doi.org/10.1016/j.cell.2026.08.015).

The source data is released under CC BY 4.0, as linked by the [official download page](https://male-cns.janelia.org/download/). Fly RL filters and transforms those tables; the original researchers did not produce this controller or its training results. [Credits and references](docs/REFERENCES.md) describes attribution, modifications and reusable citations.

## Model and maps

The audited graph contains 167,184 neurons, 25,583,622 directed edges and 124,176,995 represented synapses. The anatomical view uses 140,033 official soma positions. The remaining 27,151 neurons are simulated but have no supplied soma coordinates.

| Profile | Room dimensions | Collision boxes | Structure |
| --- | --- | --- | --- |
| `open` | 32 × 32 × 12 | 24 | Scattered obstacles |
| `passages` | 32 × 32 × 12 | 64 | Three partitions with openings |
| `large` | 48 × 48 × 16 | 112 | Five partitions and narrower passages |
| `maze` | 64 × 64 × 20 | 192 | Eight partitions and four dead-end branches |

The original dense generator remains available. Each new profiled layout has a hidden clearance certificate and a route-dependent time allowance. The controller receives neither the certificate nor the complete obstacle map. [Progressive maps](docs/GEOMETRY_CURRICULUM.md) explains generation, difficulty measurements and the curriculum.

## Install

Commands assume PowerShell in the repository root, with Conda already installed:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
.\.conda\python.exe -s -m fly_rl --help
```

Setup creates the local `.conda` environment, installs dependencies and downloads the pinned public dataset. It requires network access and substantial storage. The tested environment uses Python 3.11, CUDA-enabled PyTorch 2.7.1+cu128, Stable-Baselines3 2.7.0 and Panda3D 1.10.16. Tested versions are recorded in `requirements-lock.txt`.

## Watch a fly

A fresh clone contains no local checkpoint. Open an untrained full-connectome simulation:

```powershell
.\.conda\python.exe -s -m fly_rl demo --map-profile large --dynamics coordinated --brain-view
```

Viewing never starts an optimizer or modifies weights. Loading a checkpoint runs live sensor, brain and policy calculations; it does not replay a recorded flight. Checkpoint contracts prevent silently changing the sensor, dynamics or map interface. Explicit `--transfer` allows a deliberate distribution transfer and does not establish trained performance in the new room.

On a machine with the original local models, `launch-dense.cmd` opens the coordinated dense policy with its brain window. The `.cmd` wrappers run PowerShell explicitly, avoiding `.ps1` file associations opening a text editor. `launch-flight.cmd` and `launch-demo.cmd` also remain available. The original dense launcher reports a missing-model error when none of its candidate checkpoints exists.

| Control | Action |
| --- | --- |
| Space | Pause or resume |
| Shift | Temporarily request ten times the simulation rate |
| R / N | Reset this room / generate the next room |
| C | Cycle orbit, chase and free cameras |
| Mouse drag / wheel | Rotate, pan, look or zoom |
| WASD and Q/E | Move the free camera, including altitude |
| V | Toggle sensor rays |
| B | Open or restore the separate brain window |
| Escape | Exit and finalize the recording |

Achievable speed depends on compute and rendering load. Physics keeps its fixed 0.05-second timestep. Neural colors display modeled signed activity; they do not identify biological excitation, inhibition or movement causation. [Flight and neuron inspection](docs/FLIGHT_AND_NEURONS.md) covers the complete controls and their interpretation.

## Results and verification

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

Results are selected using validation only. One frozen winner is assessed on each reserved final pool, which is then consumed. Different experiments use different final rooms and do not establish a paired performance improvement. [Results](docs/RESULTS.md) records aggregate outcomes and uncertainty; [verification](docs/VERIFICATION.md) distinguishes correctness checks from learning performance.

[Mathematical model and optimization](docs/MATHEMATICS.md) explains the recurrent update, sensory projection, pooling, flight, reward, PPO, GAE and Adam equations. PPO updates the actor and critic, while connectome weights remain fixed.

## Repository map

```text
fly_rl/connectome/    Source tables, audits, recurrent brain and anatomy
fly_rl/simulation/    Sensors, rooms, collisions and flight dynamics
fly_rl/training/      PPO, checkpoint contracts, curriculum and evaluation
fly_rl/visualization/ Live windows, cameras, neural traces and plots
fly_rl/recordings/    Telemetry, integrity checks, archive recovery and replay
tests/               Checks grouped by responsibility
scripts/             Verification and publication tools
docs/                Public guides, formulas, protocols and result summaries
private/             Local detailed notes and original evidence; ignored
data/                Downloaded and prepared data; ignored
runs/                Checkpoints, experiments and recordings; ignored
reports/             Generated figures and QA output; ignored
.conda/              Local dependencies; ignored
```

Each demo retains a unique archive under `runs/demo/`; its latest preview and summary may be overwritten. Full-neuron snapshots require `--record-brain`: pooled features cannot reconstruct them. Saved-state flight replay does not execute a live brain. Back up local artifacts separately.

[Documentation index](docs/README.md), [command reference](docs/COMMANDS.md), [operations](docs/OPERATIONS.md), [contribution workflow](CONTRIBUTING.md) and [roadmap](ROADMAP.md) cover use and further work. Training requires an explicit command and budget.
