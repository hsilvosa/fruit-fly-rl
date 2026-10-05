# Fly RL

El planificador de mapa observado v55 ya recorre habitaciones `large`: 8/8 llegadas en optimización reutilizada y 13/16 en desarrollo prospectivo, sin colisiones y con tres timeouts en desarrollo. Es planificación explícita desde actividad del conectoma completo, no una política de movimiento aprendida. El estudiante v34 conserva su resultado de 3/8; el aprendizaje fiable sigue pendiente. Los [resultados y límites](docs/evidence/observed-map-v55-results.md) separan ambas cosas. Los aliases y el test reservado permanecen intactos.

La [historia de resolución](docs/NAVIGATION_RESOLUTION.md) explica el problema inicial, los intentos de aprendizaje y percepción que no bastaron, los bloqueos corregidos y la solución final. La mejora operativa combina memoria de mapa observado, avance correcto de referencias y frenado en la dirección tridimensional solicitada; no convierte el 13/16 del planificador en un resultado de PPO.

Para verlo en Windows:

```powershell
.\launch-observed-map.cmd
```

También acepta `--speed 4` o `--seed 370001`. Shift acelera la simulación 10 veces; R reinicia, N crea otra sala y C cambia la cámara y F enfoca la mosca. La ventana cerebral se abre por separado.

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


## Corrección panorámica y resultado de waypoint v6

La tanda waypoint v6 completó 81.920 transiciones nuevas, con pérdidas finitas y recarga compatible, pero su validación autónoma original large siguió en 0/8: ocho colisiones y ningún timeout. El total de entrenamiento sustantivo completado es 868.352 transiciones. Los aliases originales y el checkpoint fuente permanecen intactos. No se utilizó el test reservado y la navegación continúa sin resolverse.

Se conservan los [resultados verificados](docs/evidence/neural-waypoint-v6-results.md) y el [diagnóstico de control y cobertura](docs/evidence/neural-waypoint-v6-diagnostics.md). La siguiente corrección usa visión panorámica medida alrededor del cuerpo y vuelos guiados completos desde los estados originales. Su controlador recibe únicamente actividad neuronal; la ruta oculta solo etiqueta datos durante entrenamiento.
El [protocolo panorámico v7](docs/evidence/panoramic-neural-v7-plan.md) fija un límite de 98.304 transiciones nuevas, 12.288 actualizaciones supervisadas y una única validación de desarrollo. Empieza un controlador nuevo por el cambio de dimensiones, conserva todos los checkpoints anteriores y no consume el test reservado.

El usuario ha fijado una [ventana adicional de dos horas](docs/evidence/two-hour-navigation-plan.md), con parada el 4 de octubre a las 22:40:52 de Madrid. La corrección de cobertura amplía los vuelos guiados y los arranques en mapas originales, y utiliza sensores CUDA previamente contrastados con NumPy. Sus resultados autónomos todavía están pendientes; el límite de tiempo no implica que la navegación esté resuelta.

## Cierre de las correcciones panorámicas

Las tandas v8, v9, v10 y v12 terminaron y añadieron 505.856 transiciones. La última evaluación autónoma en desarrollo reutilizado alcanzó 0/8 objetivos, con una colisión y siete timeouts. El total sustantivo completado es 1.472.512 transiciones. La navegación en los mapas grandes originales sigue pendiente; no se usó el test reservado ni se promovieron los aliases originales. Se conserva el [informe de la ventana de dos horas](docs/evidence/two-hour-navigation-results.md), sus checkpoints y el lanzador experimental `launch-panorama.ps1`. El trabajo se pausa al cumplirse el plazo solicitado, el 4 de octubre a las 22:40:52 de Madrid.
