# Contributing

Start with the [repository map](README.md#repository-map), [architecture](docs/ARCHITECTURE.md) and [mathematical model](docs/MATHEMATICS.md). Keep shared sensor and physics definitions in simulation, checkpoint and evaluation rules in training, and rendering in visualization.

Before changing behavior, identify the affected dataset, sensor version, dynamics and checkpoint contracts. Preserve local experiment files, source snapshots and frozen selections. Keep public launch commands and saved artifacts compatible, or document the migration explicitly.

## Verification

Run checks that exercise the changed behavior. Use the full suite when changing shared geometry, imports or checkpoint handling:

```powershell
.\.conda\python.exe -s -m pytest -q -p no:cacheprovider --basetemp reports/qa-pytest
.\.conda\python.exe -s scripts/verify_repository.py
.\.conda\python.exe -s scripts/verify_publication.py .
```

The repository verifier checks package discovery, documentation links and command parsing. The publication verifier checks tracked files, links available in the publication tree, personal paths and common credential patterns. Neither executes training or policy evaluation. CUDA, renderer and full-data checks are separate and should be run when the change affects them. Automated scans supplement a review of the publication diff; they cannot identify every possible secret.

Map figures can be regenerated with `scripts/render_map_gallery.py`; these are geometry previews without policy evaluation. Public figure provenance belongs in `docs/images/`, not general QA output. See [public release preparation](docs/PUBLICATION.md) for the complete release checks and the distinction between MIT project code and CC BY 4.0 source data.

## Experiments

Give every experiment a new output directory and explicit transition budget. Generic PPO commands can round requests to rollout boundaries; bounded dense training rejects incompatible budgets. Select models using validation only, freeze the winner before final assessment, and treat the final pool as consumed even if evaluation fails. Preserve unsuccessful results and original launcher aliases.

Public results should identify the protocol, source revision, dataset and suite fingerprints, training budget, initialization seeds, validation selection and final uncertainty. Do not claim a matched improvement from experiments evaluated on different rooms, or a biological advantage from navigation alone.

## Public and private records

Detailed journals, decision records, launch records and original machine evidence belong under ignored `private/`. Keep them locally and back them up. Downloaded data, checkpoints, full trajectories and generated QA output remain under ignored `data/`, `runs/` and `reports/`.

Public documentation should explain capabilities, equations, use, protocols, aggregate results and limitations. Write naturally without emotes. Avoid personal paths, conversation transcripts and detailed decision journals. Check that documentation links resolve using only the tracked files, rather than relying on private local artifacts.

Ignoring or untracking a file does not remove it from earlier commits. The local development history may retain previous private records. The `publication` branch has a new root containing the reviewed public files; local `master` retains development ancestors. Use the public branch or the audited source-only ZIP described in [operations](docs/OPERATIONS.md). The ZIP contains no `.git` history. Do not publish the older development history under an assumption that `.gitignore` has erased it.
