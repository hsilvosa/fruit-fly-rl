# Data and model contract

## Pinned biological release

This project uses **MaleCNS v1.0**, from the [official MaleCNS downloads](https://male-cns.janelia.org/download/). It remains pinned for reproducibility. This document does not claim that it is the newest release available at every future date.

The downloader uses the official Google Cloud release directory:

```text
https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/
```

Required tables:

- `body-annotations-male-cns-v1.0-minconf-0.5.feather`
- `body-neurotransmitters-male-cns-v1.0.feather`
- `connectome-weights-male-cns-v1.0-minconf-0.5.feather`

The local audit records source URLs, attribution, checksums, selection counts, and prepared-file hashes. Attribution recorded by the project includes HHMI Janelia FlyEM, University of Cambridge, MRC Laboratory of Molecular Biology, and Google Research, under CC BY 4.0. Retain the release attribution when redistributing derived data.

## Original creators and scientific citation

Credit for the connectome reconstruction and biological annotations belongs to the MaleCNS authors and contributing teams, including FlyEM at HHMI Janelia, the University of Cambridge Department of Zoology, the MRC Laboratory of Molecular Biology, and Google Research. The [official project page](https://male-cns.janelia.org/) identifies the collaboration.

The primary published reference is **Berg, S., Beckett, I. R., Costa, M., et al. (2026). _Sexual dimorphism in the complete Drosophila male central nervous system connectome._ Cell, 189(18), 5504–5526.e15.** [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015).

See [Credits and references](REFERENCES.md) for the source-data license, the changes made by this project, the earlier preprint, and [BibTeX entries](references.bib). The research citation attributes the dataset; it does not validate this project's engineered dynamics or learning results.

## What “full annotated graph” means here

A body is retained when its status is `Traced` or it has an assigned superclass, except statuses `Glia`, `Orphan`, and `Unimportant`. Every connection in the downloaded table whose endpoints both satisfy this rule is retained. The release's `minconf-0.5` table defines the input boundary; the project does not apply a further minimum synapse count to shrink the retained graph.

| Audit quantity | Recorded value |
| --- | ---: |
| Annotation rows | 211,577 |
| Retained neurons | 167,184 |
| Excluded annotation rows | 44,393 |
| Source connection rows | 151,856,684 |
| Retained directed connections | 25,583,622 |
| Excluded connections involving other endpoints | 126,273,062 |
| Represented synapses | 124,176,995 |
| Isolated retained neurons | 548 |
| Neurons assigned a GABA sign | 20,228 |
| Retained neurons with usable soma coordinates | 140,033 |
| Retained neurons without usable soma coordinates | 27,151 |

Missing coordinates affect display, not graph coverage. Isolated neurons are also preserved. The prepared dataset fingerprint is:

```text
aff3a08b4b506711ea87109a21d5a3face06599183046ec9d9eba560d9d39d85
```

The release tables, raw/processed checksums, and audit live under `data/`; the folder is local and ignored. `prepare-data` prepares and audits data. The brain checks the recorded integrity of prepared files before use. Do not edit a prepared matrix while retaining old metadata or reuse a checkpoint with a silently changed graph.

## Sensors and dynamics

The original default sensor version is `sensors-v2-128-distance-128-approach-13-state`. It contains 128 distance readings, 128 approach-speed readings, and 13 state values. The state values encode relative target direction, normalized target distance, local velocity, previous actions, altitude, and the previous yaw command repeated as the final value. Actual yaw rate is logged for inspection but is not that sensor value. Rays combine axis/diagonal directions with spherical coverage and have range 8 units.

The v2 normalization divides target distance by 18 and altitude by the original room height of 6, then clips observations to [-1, 1]. Dense rooms can therefore saturate these two readings. This is the existing trained interface; changing it requires a new sensor version and model evaluation, rather than a silent refactoring fix.

Target direction is directly provided through this engineered sensor interface. There is no camera-image encoder, learned target detector, or mapping from each ray to an identified biological sensory cell. Sensory projection is seeded rather than anatomically validated.

Movement commands are normalized forward, bank/lateral, vertical, and yaw controls. Legacy dynamics allow stronger independent lateral motion. Coordinated dynamics reduce lateral acceleration, favor forward movement, smooth yaw, and derive visible bank and pitch from motion. Both use inertia, drag, bounded altitude, and swept collision tests with a body radius of 0.16. They remain simplified flight mechanics.

The recurrent specification and sensor version are encoded in model metadata. The navigation reward version is `navigation-v2-progress-timeout`: distance progress is rewarded, each step has a cost, and arrival, collision, and timeout have explicit terminal values. Changing these rules must create an identifiable experiment version.

## Local policies and provenance

| Local file | Role | Lifetime training transitions |
| --- | --- | ---: |
| `runs/navigation-policy.zip` | Selected legacy small-room policy | 196,608 |
| `runs/training/flight-v1/selected-policy.zip` | Selected coordinated small-room policy | 196,608 |
| `runs/dense-policy.zip` | Legacy dense adaptation | 327,680 |
| `runs/dense-flight-policy.zip` | Original coordinated dense launcher alias | 327,680 |
| `runs/training/priority12-v2/selected/selected-policy.zip` | October 1 fresh-suite adaptation | 393,216 |
| `runs/training/sensors-v3-v1/selected/selected-policy.zip` | October 2 validation winner, v2 | 360,448 |
| `runs/training/sensors-v3-v1/v3-selected/selected-policy.zip` | Validation-selected v3 candidate | 393,216 |

The coordinated curriculum trained a fresh policy; its 196,608 transitions are not continuations of the earlier legacy small-room policy. Each dense adaptation added 131,072 transitions to its corresponding small-room baseline. Do not sum cumulative checkpoint counters as if each were a separate round budget.

The original coordinated dense experiment froze `runs/training/dense-flight-v1/selected-policy.zip` and its metadata before final testing. The convenience alias has the same weights; its metadata can include additional selection information. Load compatibility relies on the saved graph/specification/dynamics contract, not the filename alone. A field such as `trained_navigation` is not a substitute for measured experiment results.

The historical two-seed dense adaptation started from the original dense alias. Two seeds each added 65,536 transitions, totaling 131,072 compute transitions; the selected trajectory added only its own 65,536, giving 393,216 lifetime transitions. The original alias was not promoted. See [latest experiment](GENERALIZATION_AND_ROUTES.md).

## Reproducibility limits

Stored source versions, hashes, seeds, and fixed layouts establish provenance. They do not guarantee bitwise CUDA repeatability. During the repository move, short trajectories differed by less than 0.000001 across the three existing profiles; repeated runs of unchanged CUDA code also differed at that scale. Checkpoint files were unchanged and the algorithm ASTs, excluding imports, matched.

PPO resume restores a saved policy and optimizer but starts new environment episodes. Exact continuation of random generators, partial episodes, room states, and recurrent activity is not currently guaranteed. New releases, sensors, flight rules, or recurrence assumptions need explicit compatibility and evaluation decisions.

## Equations and optimization

See [Mathematical model and optimization](MATHEMATICS.md) for the exact recurrent, sensory, flight, reward, PPO/GAE, optimizer, and metric formulas, including source links and current parameter values.

The versioned [v3 interface](SENSORS_V3.md) uses room-scale distance/altitude and measured yaw rate. Loading resolves the saved sensor contract; explicit migration is required to reinterpret a warm start.

Later experiments used fresh initialization and versioned v3 inputs. [Results](RESULTS.md) distinguishes aggregate experiment budgets from selected checkpoint lifetime counters. A saved checkpoint can have zero training transitions when the selection rule retains the initial controller.
