# Command reference

Run commands from the repository root with the project-local interpreter. Global `--data` and `--device` precede the subcommand. Every subcommand supports `--help`.

```powershell
.\.conda\python.exe -s -m fly_rl --help
.\.conda\python.exe -s -m fly_rl --device cpu demo --help
```

Placeholders such as `ARCHIVE`, `LEFT`, and `RIGHT` must be replaced with actual local paths. Viewing never starts an optimizer. Analysis commands may write their named report or figure; “no training” does not mean “no filesystem writes.”

## Viewing and saved flights

`launch-observed-map.cmd` keeps frozen planner-1.0 as its default. Experimental versions require explicit selection, for example `launch-observed-map.cmd --controller-version 1.2 --seed 10000005`. This runs the dual mapping/safety planner live and records its source dependencies; it never trains. Versions refer to controller changes, not different room generators. See [planner development](PLANNER_DEVELOPMENT.md) for the candidate's evidence and limits.

```powershell
.\launch-dense.cmd
.\launch-flight.cmd
.\launch-demo.cmd
.\launch-dense.cmd --speed 10 --seed 10
.\launch-dense.cmd --brain-region T1 --trace-neuron 10069

# Explicitly untrained; no checkpoint argument.
.\.conda\python.exe -s -m fly_rl demo --room-mode dense --dynamics coordinated --brain-view

# Saved states, no connectome or policy execution.
.\.conda\python.exe -s -m fly_rl replay ARCHIVE --speed 2
.\.conda\python.exe -s -m fly_rl replay LEFT --compare RIGHT
```

`demo` defaults to a legacy small room, seed 10, speed 1, and recording enabled. `--checkpoint` loads a policy. `--brain-view` opens the separate anatomical view; `--brain-region`, `--brain-class`, and `--trace-neuron` also request inspection. `--record-brain` adds complete neuron snapshots, while `--no-record` disables archived flight telemetry. `--record-dir` changes the archive parent. `--offscreen --seconds 1 --screenshot reports/check.png` requests a brief rendered check without a visible window.

`replay` reads the archive and uses saved positions, actions, sensors, and features. It creates no new flight archive and performs no optimizer updates. Space pauses; R rewinds; N skips to the next episode; PageUp/PageDown seek by 100 decisions. A comparison overlay is available only for matching room geometry and target. It does not imply matched initial conditions or a controlled learning comparison.

Shift temporarily requests 10 times the base simulation rate. `--speed 10` supplies an alternative that does not require holding a key. These multipliers compose. Compute throughput can prevent the requested wall-clock rate from being reached.

## Archive analysis and recovery

```powershell
.\.conda\python.exe -s -m fly_rl inspect ARCHIVE --output reports/inspection.json
.\.conda\python.exe -s -m fly_rl compare LEFT RIGHT --output reports/comparison.json
.\.conda\python.exe -s -m fly_rl recover ARCHIVE --output reports/recovery.json
# Mutates the archive manifest after checking retained files:
.\.conda\python.exe -s -m fly_rl recover ARCHIVE --apply --output reports/recovery-applied.json
```

Inspection validates retained chunks and reports errors; it exits unsuccessfully when errors exist. Recovery without `--apply` is a dry run. Applying recovery updates an incomplete manifest using files already on disk. It cannot recover unwritten buffered transitions. Back up an important interrupted archive before applying recovery.

## Existing results and correctness

```powershell
.\.conda\python.exe -s -m fly_rl plot-training runs/training/navigation-v2/iteration.json --independent reports/navigation-independent-evaluation.json
.\.conda\python.exe -s -m fly_rl plot-dense runs/training/dense-flight-v1
.\.conda\python.exe -s -m pytest -q -p no:cacheprovider
.\.conda\python.exe -s scripts/verify_repository.py
```

Plots regenerate figures from saved records. They do not rerun training or evaluation. The repository verifier checks documentation links, grouped module discovery, and CLI help; it does not establish navigation performance. Pytest uses temporary fixtures for optimizer/checkpoint logic where applicable, not a substantial learning run.

## Data preparation and performance measurement

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
.\.conda\python.exe -s -m fly_rl prepare-data
.\.conda\python.exe -s -m fly_rl benchmark --seconds 20
```

Setup creates/updates the `.conda` environment, installs the editable package, and prepares data. Data preparation needs network access if release files are absent. Benchmark measures the full graph at batches 1, 4, 8, and 16, with the requested duration capped at 120 seconds after initialization. It writes `reports/benchmark.json`; it measures reservoir updates, not full viewer or learning throughput.

## Evaluation and frozen suites

The current `runs/suites/dense-v1.json` test split has already been evaluated. Do not use it for further tuning and present the result as untouched generalization evidence.

```powershell
# Existing validation pool only; no weight updates.
.\.conda\python.exe -s -m fly_rl evaluate --checkpoint runs/dense-flight-policy.zip --dynamics coordinated --suite runs/suites/dense-v1.json --split validation --episodes 32 --output reports/validation-check.json
# Creates fresh ranges; exclude all relevant historical suites.
.\.conda\python.exe -s -m fly_rl prepare-suite --output runs/suites/NEW-SUITE.json --train-start 30000 --validation-start 40000 --test-start 50000 --exclude-suite runs/suites/dense-v1.json
```

Generic evaluation defaults to 16 legacy obstacle-room episodes starting at seed 10000. `--mode`, `--seed`, `--dynamics`, `--episodes`, and `--goal-probe` customize it. `--suite` uses its validation or test seed pool and validates geometry. `--transfer` explicitly permits a checkpoint dynamics mismatch. Generic validation evaluation can be repeated and overwrite its output. Suite test evaluation requires `--expose-test` and claims the local exposure record for versioned suites; use guarded `final-test` for final assessment.

The default suite ranges are now 30000–30255, 40000–40031, and 50000–50063; each start/count is configurable. Repeat `--exclude-suite` to certify novelty against prior pools. Every frozen layout is checked when loading. Reusing the same ranges at a different filename does not establish independence. See [Generalization and routes](GENERALIZATION_AND_ROUTES.md) for bounded repeated-seed commands and route-quality reporting.

`final-test EXPERIMENT-DIRECTORY` requires a completed dense experiment and its frozen selection, verifies checkpoint/metadata/suite fingerprints, and evaluates the reserved 64 layouts against selected and untrained policies. Its result is exclusive and cannot overwrite a previous final test. It is an evaluation command, not training. A new suite is still needed once results have informed subsequent development.

## Commands that update weights

These are references for a future explicit training decision. They were not run during repository organization. Choose budgets, output paths, versions, and an evaluation protocol before invoking them.

| Command | Purpose and budget behavior |
| --- | --- |
| `train --steps N --batch B --output PATH` | General PPO run; may round to complete rollout boundaries; `--resume` restores a checkpoint, `--mode`, `--dynamics`, and optional `--suite` specify the task |
| `iterate --baseline PATH --output DIRECTORY` | Fresh small-room curriculum, evaluated against a baseline; defaults to three 65,536-transition rounds and batch 16; the baseline is evaluated rather than used as fresh curriculum initialization |
| `train-dense --suite PATH --output DIRECTORY --baseline PATH` | Budgeted adaptation on training layouts only; defaults to 131,072 added transitions, one round, batch 16; supports `--rounds` and `--dynamics` |
| `migrate-sensors SOURCE --output PATH` | Explicit v2-to-v3 warm-start copy; preserves archive bytes and source, changes metadata with provenance; no optimizer |
| `compare-sensors --suite PATH --baseline PATH --output DIRECTORY` | Four matched adaptations: two seeds per interface, 65,536 transitions each, batch 8; validation selects one winner before one fresh final test; never promotes the launcher alias |
| `smoke-test --dynamics coordinated` | Temporary 128-transition, one-update PPO pipeline check, saved under `runs/smoke`; this does change a test policy |
| `select-policy ITERATION-JSON --output PATH` | Copies a selected curriculum policy and metadata; no optimizer, but changes the selected checkpoint destination |

Dense budgets must fit complete 512-step rollouts per environment and divide across requested rounds. New experiment directories must not already exist. `train-dense` also supports `--training-seed`, `--no-promote`, and `--route-metrics`. `select-experiment` compares completed distinct-seed adaptations on the same suite using validation only. `diagnose-validation` reads retained outcomes; `plot-generalization` plots a completed multi-seed experiment without rerunning it. Dense selection ranks validation success, collision rate, and end distance, including the baseline; the last round is not automatically selected. Default aliases differ by dynamics. Check [Dense rooms](DENSE_ROOMS.md) and [Operations](OPERATIONS.md) before creating a run.

Training and evaluation resolve the saved checkpoint sensor version. Fresh policies keep the original v2 default. The `train` Python API accepts `sensor_version` for fresh v3 construction; CLI v3 warm starts use explicit migration or resume a v3 checkpoint. The completed comparison suite is consumed, so its command cannot be reused for another untouched final claim. See [sensor protocol and results](SENSORS_V3.md).

## Validation plots and fresh initialization

`plot-validation-failures EXPERIMENTS --output FIGURE.png` reads existing shared validation records only. `prepare-fresh-comparison --suite SUITE --output CONFIGURATION` creates a nontraining draft; `--steps-per-seed N` declares a configured budget. `run-fresh-comparison CONFIGURATION --output DIRECTORY` explicitly trains four fresh paired runs by default, selects on validation, and assesses one frozen winner once. Drafts are rejected. See [the full protocol](VALIDATION_AND_FRESH_COMPARISON.md).

## Detailed validation diagnostics

`trace-validation EXPERIMENT --output NEW_DIRECTORY --count 2 --max-steps 1200` executes the frozen policy on retained validation failures only. Counts are limited to four and budgets to 1200 decisions per batch. It does not train. `plot-validation-trace SUMMARY.json --output FIGURE.png` reads saved arrays without brain/policy execution. Both are documented in [Validation traces](VALIDATION_TRACES.md).

## Approach curriculum comparison

`prepare-approach-comparison --suite SUITE --output CONFIGURATION` creates a budget-required draft. Add `--steps-per-seed N` only for an agreed bounded comparison. `run-approach-comparison CONFIGURATION --output NEW_DIRECTORY` explicitly runs equal-budget normal-training and curriculum arms using fresh v3 weights, selects on ordinary validation, and assesses one frozen winner. Drafts are refused. See [protocol](APPROACH_CURRICULUM.md).

## Collision diagnosis and risk comparison

`trace-validation --kind collision` selects only retained validation collisions. `diagnose-collisions` summarizes saved version-2 validation arrays without inference. `prepare-risk-comparison` prepares an inert draft without a budget; `run-risk-comparison` requires an explicitly configured budget and unchanged source/suite hashes. See [protocol and examples](COLLISION_RISK.md).

The completed risk-comparison winner is stored separately from launcher aliases. See [the viewing command](COLLISION_RISK.md#view-the-selected-policy) for inference with the dense coordinated room and anatomical window.

## Progressive geometry

`demo --map-profile NAME` implies dense mode and accepts `dense-v3`, `open`, `passages`, `large`, `maze` or a complete profile JSON file. A fresh profiled demo uses sensors v3. Checkpoints trained for another profile require explicit `--transfer`; using transfer is not evidence of trained performance on the new distribution. Demo never updates weights.

`map-report --output REPORT.json --figure FIGURE.png` inspects up to four profiles and 1–32 preview seeds without a brain or policy. `prepare-suite --map-profile large --training-profiles open passages large` freezes the target and training-only variants in schema 3. With `--suite`, training and evaluation use the serialized profile and reject conflicting profile arguments. `train-dense` requires `--no-promote` for profiled suites to preserve original launcher aliases.

`prepare-geometry-comparison --suite SUITE --output CONFIGURATION` now creates an inert practice-mastery v2 draft. Freeze profiles starting with `gate-near`, for example `prepare-suite --map-profile gate-long --training-profiles gate-near gate-long`, with at least 32 training layouts and fresh split seeds. The last 16 training layouts are withheld from optimizer rollouts and used for practice gates. `--steps-per-seed N` declares a bounded configured comparison; `run-geometry-comparison CONFIGURATION --output NEW_DIRECTORY` is the explicit weight-changing command. Both arms start fresh. Progression requires two practice batches with at least seven goals out of eight each. Only trained candidates enter selection; a final assessment requires positive target validation success. Otherwise it records `no_successful_candidate` and preserves the final pool. Drafts and changed source/suite fingerprints are rejected. See [the formulas and versioned protocol](GEOMETRY_CURRICULUM.md).


The explicit `train` command supports `--gamma` (default 0.995) and `--timeout-as-terminal` (default off). These controls are recorded in checkpoint metadata. Treating task deadlines as terminal requires a remaining-time observation for a Markov finite-horizon task; see [timeout diagnosis](evidence/large-timeout-diagnosis.md). No new large training experiment was launched during this diagnosis.


Use `train --sensor-version sensors-v4-128-distance-128-approach-14-state-deadline` to opt into the deadline interface. An existing v3 checkpoint requires an explicit copied migration through `migrate-sensors SOURCE --output NEW_PATH --target sensors-v4-128-distance-128-approach-14-state-deadline`. Migration preserves policy weights and does not train. A changed interface requires new verification and a newly frozen training protocol.


The explicit train command accepts `--history-frames 32 --history-stride 8`. Upgrading a current-feature checkpoint also requires `--transfer-history` and an explicit `--resume` source. This creates a learned temporal readout of connectome features with an initially zero residual; the original movement weights and their optimizer states are preserved. Evaluation and demo infer the history contract from checkpoint metadata. See [memory diagnosis](evidence/brain-memory-diagnosis.md).


## Offline planner execution diagnostics

Saved planner traces can be inspected without a brain, controller execution, training, or evaluation:

```powershell
.\.conda\python.exe -s scripts/report_planner_execution.py runs/diagnostics/planner-v65-development/v65/trace.json --seed 13000013 --output reports/planner-v65-timeout-execution.json
```

The local trace is not shipped in a fresh clone. Supply an existing diagnostic trace and a new output path. The report preserves its SHA-256 and counts sampled route availability, search-cap hits, momentum braking, and reference-direction reversals greater than 90 degrees. It records missing fields separately from observed zero counts and rejects nonfinite vectors or nonincreasing room steps. These indicators do not establish causality or behavior between samples. [Interpretation](evidence/planner-dual-v65-results.md#offline-inspection-of-the-remaining-timeouts).


## Room-aware maze development

Only planner-1.3 experimental candidates support the maze contract. For example, `launch-observed-map.cmd --controller-version 1.3-exp.4 --map-profile maze --seed 14000000`. This is a live autonomous development demo; it currently has two recorded maze timeouts and is not a verified maze solution. See [maze navigation](MAZE_NAVIGATION.md). Older controllers reject this profile before graph initialization.


The latest verified large development candidate is `launch-observed-map.cmd --controller-version 1.3-exp.9 --map-profile large` (6/6 retained and 8/8 fresh goals, zero collisions). It fails both retained maze flights. For the first recorded maze-arrival controller, use `--controller-version 1.3-exp.8 --map-profile maze --seed 14000000`; that is a retained-case demonstration, not reliable maze navigation.


`launch-large.cmd` selects the verified large development candidate and a recorded successful development seed. `launch-maze.cmd` selects the opening-refinement candidate and a retained successful maze seed, with fresh verification pending. Both open live flight and the separate brain window, save telemetry, and never start training. Extra arguments are forwarded to the demo CLI.
