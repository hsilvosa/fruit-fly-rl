# Fly RL

The observed-map planner v55 now navigates `large` rooms: 8/8 arrivals on reused optimization maps and 13/16 in prospective development, without collisions and with three development timeouts. This is explicit planning from full-connectome activity, not a learned movement policy. Student v34 retains its 3/8 result; reliable learning remains unresolved. The [results and limits](docs/evidence/observed-map-v55-results.md) distinguish the two. Original aliases and the reserved test remain intact.

The [resolution history](docs/NAVIGATION_RESOLUTION.md) explains the original problem, learning and perception attempts that were insufficient, corrected blockages, and the final solution. The operational improvement combines observed-map memory, correct reference advancement, and braking in the requested three-dimensional direction; it does not turn the planner's 13/16 into a PPO result.

To watch it on Windows:

```powershell
.\launch-observed-map.cmd
```

It also accepts `--speed 4` or `--seed 370001`. Shift accelerates simulation tenfold; R resets, N creates another room, C changes the camera, and F focuses on the fly. The brain window opens separately.

A virtual fruit fly navigates procedural 3D rooms using features from the full annotated MaleCNS v1.0 connectome. A fixed sparse recurrent model converts simulated sensor readings into activity; a PPO actor and critic learn flight commands. Panda3D displays the room and an optional separate anatomical activity window.

This is an engineered navigation experiment. Synthetic distance rays and target direction are available to the controller. The recurrent equations, sensor projection and flight dynamics are project choices, rather than a biological simulation of vision, spiking neurons or wing aerodynamics. Navigation success alone does not establish a benefit from fruit-fly wiring.

## Dataset credit

The MaleCNS reconstruction, annotations and soma coordinates were produced by the FlyEM team at HHMI Janelia Research Campus, the University of Cambridge Department of Zoology, the MRC Laboratory of Molecular Biology, Google Research, and the contributors credited in the original publication. See the [official project](https://male-cns.janelia.org/).

Cite Berg, S., Beckett, I. R., Costa, M., et al. (2026), *Sexual dimorphism in the complete Drosophila male central nervous system connectome*, Cell, 189(18), 5504-5526.e15. [DOI](https://doi.org/10.1016/j.cell.2026.08.015).

The source data is released under CC BY 4.0, as linked by the [official download page](https://male-cns.janelia.org/download/). Fly RL filters and transforms those tables; the original researchers did not produce this controller or its training results. [Credits and references](docs/REFERENCES.md) describes attribution, modifications and reusable citations.

## Model and maps

The audited graph contains 167,184 neurons, 25,583,622 directed edges and 124,176,995 represented synapses. The anatomical view uses 140,033 official soma positions. The remaining 27,151 neurons are simulated but have no supplied soma coordinates.

| Profile | Room dimensions | Collision boxes | Structure |
| --- | --- | --- | --- |
| `gate-near` | 12 x 12 x 10 | 4 | One wide opening and nearby goal |
| `gate-long` | 24 x 12 x 10 | 4 | The same opening with longer travel |
| `open` | 32 x 32 x 12 | 24 | Scattered obstacles |
| `passages` | 32 x 32 x 12 | 64 | Three partitions with openings |
| `large` | 48 x 48 x 16 | 112 | Five partitions and narrower passages |
| `maze` | 64 x 64 x 20 | 192 | Eight partitions and four dead-end branches |

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

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0-5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

Results are selected using validation only. One frozen winner is assessed on each reserved final pool, which is then consumed. Different experiments use different final rooms and do not establish a paired performance improvement. [Results](docs/RESULTS.md) records aggregate outcomes and uncertainty; [verification](docs/VERIFICATION.md) distinguishes correctness checks from learning performance.

The [geometry failure diagnosis](docs/GEOMETRY_DIAGNOSIS.md) confirms that the earlier controller reproduced its outcomes in four retained original validation rooms. The new progression advanced without passage mastery, and the overall selection retained untrained initialization after all trained target candidates failed. Single-opening navigation is the next prerequisite before expanding map complexity further.

The corrected practice-mastery v2 tools start with `gate-near`, withhold 16 training layouts for progression checks, preserve easier examples and leave the final pool unused if no trained candidate succeeds in validation. They passed physical passage checks and a full-graph 128-transition optimizer smoke. The completed 524,288-transition comparison selected baseline seed 42, reaching 61/64 final single-opening goals (95.3%), with zero collisions and three timeouts; Wilson 95% interval 87.1-98.4%. This result applies to the simpler single-opening distribution. The curriculum did not beat baseline in validation. [Completion evidence](docs/evidence/passage-mastery-v2-results.md) includes all seeds, practice rounds and preserved alias hashes. See the [corrected protocol and preparation commands](docs/GEOMETRY_CURRICULUM.md#corrected-practice-mastery-protocol).

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


The earlier [critic-isolation v3 run](docs/evidence/guided-navigation-v3-results.md) and subsequent guarded corrections did not resolve original large-room navigation. Their checkpoints and evidence remain available; those experiments are no longer running.


## Panoramic correction and waypoint v6 result

The waypoint v6 batch completed 81,920 new transitions, with finite losses and compatible reload, but autonomous validation on original `large` rooms remained at 0/8: eight collisions and no timeouts. Completed substantive training totals 868,352 transitions. Original aliases and the source checkpoint remain intact. The reserved test was not used, and navigation remained unresolved at this stage.

The [verified results](docs/evidence/neural-waypoint-v6-results.md) and [control and coverage diagnosis](docs/evidence/neural-waypoint-v6-diagnostics.md) are retained. The next correction uses panoramic vision measured around the body and complete guided flights from original states. Its controller receives only neural activity; the hidden route labels data only during training.
The [panoramic v7 protocol](docs/evidence/panoramic-neural-v7-plan.md) sets a limit of 98,304 new transitions, 12,288 supervised updates, and a single development validation. It starts a new controller because dimensions change, preserves all previous checkpoints, and does not consume the reserved test.

The user set an [additional two-hour window](docs/evidence/two-hour-navigation-plan.md), stopping on October 4 at 22:40:52 Madrid time. The coverage correction extends guided flights and starts on original maps, using CUDA sensors previously checked against NumPy. Autonomous results were still pending at this stage; the time limit did not imply that navigation was resolved.

## Completion of the panoramic corrections

Batches v8, v9, v10, and v12 finished and added 505,856 transitions. The latest autonomous assessment on reused development maps reached 0/8 goals, with one collision and seven timeouts. Completed substantive training totals 1,472,512 transitions. Navigation in the original large maps remained unresolved; the reserved test was not used and original aliases were not promoted. The [two-hour window report](docs/evidence/two-hour-navigation-results.md), its checkpoints, and experimental launcher `launch-panorama.ps1` are retained. Work paused at the requested deadline, October 4 at 22:40:52 Madrid time.
