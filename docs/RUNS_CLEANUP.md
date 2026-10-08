# Runs directory cleanup

October 8, 2026. The `runs/` directory held 87 GB. About 84.5 GB came from 14 `training-data` folders. They hold raw teacher-collected imitation datasets (binary feature and target arrays) from completed experiments that the transfer work superseded. The experiment code regenerates them (`fly_rl/training/guided_learning.py`, `panorama_navigation.py`, `spatial_navigation.py`, `waypoint_navigation.py`). The cleanup removed those folders. `runs/` now takes about 1.9 GB.

## Kept

- Every checkpoint (`.zip`), its metadata (`.json`), result file, selection record and status file in each experiment.
- `runs/training/*/selected` folders, including the final-test records and the consumed-pool records under `runs/suites/consumed`.
- The historical winners and aliases: `runs/dense-flight-policy.zip`, `runs/dense-policy.zip`, `runs/navigation-policy.zip`, and the 50/64, 48/64 and 45/64 checkpoints. Their hashes were checked after the cleanup.
- Suites, configurations, transfer experiments 1 to 8 and verification records.
- Demo recordings in `runs/demo` and smoke outputs in `runs/smoke`, which are small and referenced by the documentation.

## Removed

| Folder | Size |
| --- | ---: |
| `directional-panorama-v9/training-data` | 19 GB |
| `panorama-coverage-v8/training-data` | 16 GB |
| `panoramic-neural-v7/training-data` | 13 GB |
| `neural-waypoint-v6/training-data` | 8.8 GB |
| `continuous-guidance-v10/training-data` | 7.8 GB |
| `distance-only-perception-v12/training-data` | 6.5 GB |
| `spatial-neural-v5/training-data` | 4.8 GB |
| Seven other `training-data` folders (guided-navigation v1 to v3, dagger-approach-v37, context-portal-v32, centered-portal-v17, whitened-portal-v15) | 1.1 to 1.6 GB each |

The sixteen empty `SB3-*` log folders in the repository root were also removed.

A manifest with every removed file name and size is local in `private/runs-cleanup-manifest.json`. The script is `scripts/cleanup_runs.py`. Completed experiment results and student checkpoints remain, so every reported number stays traceable. A future reproduction of an imitation experiment needs to collect its dataset again.
