# Scripts index

This page lists the 89 Python files in `scripts/` by purpose, plus the `profiles/` folder. Each entry is taken from the file's docstring or its argument handling, and each usage line is copied from the script itself. Commands are shown with the repository interpreter, `.conda/python.exe -s`, from the repository root.

The scripts are research tools, not an installed command set. Most of them set their working directory with an absolute path (the author's checkout), so they run correctly on the machine they were written on and need that path edited elsewhere. The package CLI (`python -m fly_rl`) is documented in [docs/operations/COMMANDS.md](../docs/operations/COMMANDS.md). The experiments these scripts implement are indexed in [docs/experiments/README.md](../docs/experiments/README.md), and the step-by-step commands are in [docs/operations/REPRODUCE.md](../docs/operations/REPRODUCE.md).

## Resource guard

[`resource_guard.py`](resource_guard.py) is the only place where evaluation fan-out is started. Every driver and every multi-cell evaluation goes through its `run_limited(commands)` function, and the rule is in [ROADMAP.md, section 7](../ROADMAP.md#7-rules-for-every-iteration).

- A new process starts only when memory use and CPU load are both below the start threshold. A hard process cap also applies, and starts are staggered.
- Limits and their defaults:

| Variable | Default | Meaning |
| --- | --- | --- |
| `RG_LIMIT` | 90 | Soft ceiling, percent (CPU and memory) |
| `RG_START_BELOW` | 75 | A new process starts only below this, percent |
| `RG_MAX_PARALLEL` | 4 | Maximum number of processes at once |
| `RG_STAGGER` | 20 | Seconds between process starts |
| `RG_THREADS` | 2 | Numerical threads per process (`OMP_NUM_THREADS` and related variables) |

- The defaults are the original limits. The ceiling was later raised by the user to 95 percent. `planner_reference_driver.py` and `connectome_control_c10/c11/c12_driver.py` raise the ceiling in their own code with `os.environ.setdefault`, so a value already set in the shell takes precedence over the driver's value.
- Most training drivers also stop a training process if memory goes above 92 percent (`memory_used_percent() > 92`). `phase1_driver.py` and `phase1_driver_quiet.py` use 88 percent, as their docstring says.
- History: an early pilot launched 28 evaluation processes at once and the PC restarted. The guard was added after that ([PHASE1_PILOT_RESULTS.md](../docs/experiments/variance-and-stability/PHASE1_PILOT_RESULTS.md)).

Windows only: the guard reads memory and CPU through `kernel32` (`GlobalMemoryStatusEx`, `GetSystemTimes`).

## Training

Trainers write checkpoints and logs under `runs/` (see the run directories in [docs/experiments/README.md](../docs/experiments/README.md)). Training runs with `NOEVAL=1` where a driver says so, and the drivers evaluate afterwards.

**Experiment drivers (sequence of trainings and evaluations).** Each driver is resumable where its docstring says so and writes its logs to its run directory.

- `variance_driver.py`: variance study R1, five training seeds (501 to 505) then evaluation.
- `phase1_driver.py`: Phase 1 run, seeds 442 and 443, then evaluation of all checkpoints. Sends Telegram milestones.
- `phase1_driver_quiet.py`: same flow as `phase1_driver.py`, with Telegram off.
- `phase3_driver.py`: Phase 3 screening, both memory windows, then stages 2 and 4. No Telegram.
- `phase3_replication_driver.py`: Phase 3 replication, the long window with seed 443, then all four stages.
- `r5_driver.py`: R5 randomized distribution, seeds 601 to 603, then evaluation and the level C baseline. Resumable.
- `large_budget_driver.py`: B1 (1M budget), one run, then the curve evaluation.
- `large_budget_2m_driver.py`: B2 (2M budget), one run, then evaluation. Resumable.
- `replication_2m_driver.py`: B3, seeds 851 and 901 in series, then evaluation of stages 46 and 61.
- `level_bc_driver.py`: B4, level B and level C evaluation of stage 61 of seeds 801, 851 and 901 and the start checkpoint. Resumable.
- `connectome_control_c10_driver.py`: C1.0, phase 1 of the fresh two-arm chain, then medium-room evaluation on pool 887000.
- `connectome_control_c11_driver.py`: C1.1, phase 2 of both arms, seeds 1001 and 1051, then evaluation.
- `connectome_control_c12_driver.py`: C1.2, extension of the four C1.1 runs by 61 stages, then evaluation on pool 888000. Usage: `connectome_control_c12_driver.py [train-only]`.
- `planner_reference_driver.py`: C1.P, planner on level C (four processes of two headings each) and the retained learned candidate on `large` and `maze`.
- `pretrain_driver.py`: supervised pretraining experiment (data collection, pretraining, three PPO students, evaluation). Resumable.
- `student_driver.py`: auxiliary and privileged-critic students, with controls. Resumable.
- `waypoint_driver.py`: privileged-waypoint diagnostic, four trainings, then evaluation cells. Resumable.

**Individual trainers.**

- `train_phase1_pilot.py <seed442|seed443> <output-dir>`: Phase 1 pilot (three stages). Docstring says it is experiment 9.
- `train_phase1_run.py <seed442|seed443> <output-dir>`: Phase 1 run (four stages). Run with `NOEVAL=1`, then evaluate with `eval_checkpoint.py`.
- `train_variance.py <seed501..505> <output-dir>`: variance study trainer (three stages). Run with `NOEVAL=1`. Its docstring usage line names `train_phase1_pilot.py`.
- `train_phase3.py <short442|long442> <output-dir>`: Phase 3 memory-window trainer (four stages). The replication uses the same script with `long443` (see `phase3_replication_driver.py`).
- `train_random.py <start-without-zip> <seed> <output-dir> <stages>`: R5 randomized-map trainer. `STAGE_OVERRIDE` environment variable sets the stage size (default 32768).
- `train_reference_transfer.py <retained|fresh> <output-dir>`: transfer experiment 1 (T1).
- `train_reference_transfer2.py <route65|budget262> <output-dir>`: transfer experiment 2 (T2).
- `train_reference_transfer3.py <output-dir>`: experiment 3, graded gate maps from the 50/64 policy.
- `train_reference_transfer4.py <output-dir>`: experiment 4, medium-heavy recovery stage.
- `train_reference_transfer5.py <output-dir>`: experiment 5, `passages` in the mix.
- `train_reference_transfer6.py <output-dir>`: experiment 6, `passages-mid` profile.
- `train_reference_transfer7.py <mix3e4|mix1e4> <output-dir>`: experiment 7, profiles mixed in every update.
- `train_reference_transfer8.py <seed442|seed443> <output-dir>`: experiment 8, longer mixed-batch run, two seeds.
- `train_large_budget.py <seed> <output-dir> [stages, default 31]`: B1 and B2 trainer (also used for B3 with 61 stages).
- `train_fresh_chain.py <real|shuffled> <seed> <output-dir> [stages, default 27]`: C1.0 phase 1 from random weights.
- `train_fresh_phase2.py <real|shuffled> <seed> <source> <output-dir> [stages, default 61] [offset]`: C1.1 phase 2 and the C1.2 extension (`offset` shifts the stage numbering).
- `train_waypoint.py <waypoint|control> <seed> <output-dir> <stages>`: privileged-waypoint diagnostic trainer.
- `train_student.py <aux|critic|pre> <seed> <output-dir> <stages>`: autonomous students (`pre` starts from the pretrained trunk).
- `pretrain_trunk.py <data-dir> <output-dir>`: supervised pretraining of the actor trunk on route-direction labels.
- `train_architectural_curriculum.py <output>`: bounded fresh PPO curriculum on the architectural scenes (argparse; original-goal validation, no planner actions).
- `train_architectural_curriculum_balanced.py <output>`: balanced variant of the same curriculum (argparse).
- `train_architectural_curriculum_mixed.py <output>`: PPO continuation mixing lessons and original goals (argparse).
- `train_autonomous_architecture.py <output>`: explicit bounded fresh PPO pilot on the architectural scenes (argparse).

**Smoke and verification trainers.**

- `verify_architectural_curriculum.py <output>`: explicit 128-transition PPO smoke. Not a navigation experiment.
- `verify_autonomous_architecture.py <output>`: explicit 128-transition PPO smoke. Not a navigation experiment.
- `verify_geometry.py [--data DATA]`: bounded whole-connectome verification; the optimizer smoke runs only when opted in (argparse).

## Evaluation cells and drivers

Evaluation never changes weights. The "cell" scripts run one profile, one seed and one episode count in their own process, and the drivers above call them through `run_limited`.

- `eval_checkpoint.py <checkpoint.zip> <label> <output-dir> [pool-list]`: one checkpoint on the Phase 1 selection pools (`select`), the old pools (`old`) and the regression pools (`regab`, a comma-separated list). Runs its cells through the guard.
- `eval_cell.py <checkpoint> <profile|none> <seed> <episodes> <out.json>`: one cell, deterministic unless the environment variable `STOCHASTIC=1` is set.
- `eval_cell_mode.py <checkpoint> <profile|none> <seed> <episodes> <out.json> <det|sampled>`: one cell with an explicit action mode.
- `eval_cell_brain.py <real|shuffled> <checkpoint> <profile|none> <seed> <episodes> <out.json> <det|sampled>`: one cell of a checkpoint trained with a given brain. The shuffled brain is injected at evaluation time, so the frozen source is not modified.
- `eval_random_cell.py <checkpoint.zip> <train|heldout_b> <difficulty> <seed> <episodes> <output.json> [sampled] [shuffled]`: randomized maps at a fixed difficulty (levels A and B).
- `eval_architecture.py <checkpoint.zip> <headings per situation> <output.json> [seed] [sampled] [shuffled]`: level C, the 21 architectural situations.
- `eval_waypoint_cell.py <checkpoint.zip> <profile|none|heldout_b> <seed> <episodes> <out.json> <arm> [stochastic]`: waypoint and student checkpoints; the arm name is `waypoint`, `control`, `aux`, `critic` or `pre`.
- `eval_planner_architecture.py <output> <first> <last> [seed]`: planner-1.4-exp.3 on the architectural situations with headings `first` to `last`. Evaluation only.
- Both level C evaluators default to seed 900000.
- `regression_medium.py <checkpoint.zip> <label> <output-dir> [reference-result.json]`: frozen medium-room regression suite (pools A to D, 32 episodes each).
- `committee_evals.py`: run 601 and stochastic-versus-deterministic checks on pool 880000 (64 episodes), calling `eval_cell.py` with `STOCHASTIC=1`. Its command list is built in code; it takes no arguments in its own handling.
- `confirm_variance_best.py`: confirmation of the best variance-study run and the pilot on pool 880000, 64 episodes per cell. Takes no arguments.
- `profile_edge_ladder.py <checkpoint.zip> <seed> <episodes> <output.json> <profile>...`: how far a frozen policy goes on easier profiles.
- `classify_failures.py <label> <checkpoint.zip> <profile> <seed> <episodes> <output.json>`: records and classifies failures on a profile.
- `collision_anatomy.py <label> <checkpoint.zip> <profile> <seed> <episodes> <output.json>`: where along the certified route each collision happened.

Transfer and reference checks: `replay_reference_validation.py [names]` (default: `sensors-v3-v1`, `ray-risk-v1`, `approach-v1`; replays the historical winners on their own recorded validation pools), and `transfer_ladder_reference.py` (development ladder of the frozen historical winners, seeds 800000 and above, output `runs/verification/reference-recovery-1/transfer-ladder.json`).

## Probes and analysis

Offline analyses of recorded rollouts or synthetic poses. These scripts run no optimizer. Some of them run a frozen policy to collect data first.

- `collect_probe_data.py <checkpoint.zip> <profile> <seed> <episodes> <output.npz>`: rollouts of a frozen policy, with the policy features, raw sensors and route-direction labels.
- `collect_probe_data_long.py <checkpoint.zip> <profile> <seed> <episodes> <output.npz>`: as above, also storing rays and panorama cast to 24 m.
- `collect_pretrain.py <checkpoint.zip> <profile|none> <seed> <episodes> <output.npz>`: pretraining data from sampled-action rollouts, per profile.
- `analyze_probe.py <name> ...`: linear and small nonlinear probes on collected data (split by episode).
- `analyze_probe_variants.py history <name>` or `analyze_probe_variants.py range <name-long>`: probe variants on frozen rollouts.
- `probe_synthetic.py <maps> <output-prefix>`: synthetic sensing probe on many maps, no policy.
- `check_shuffled_graph.py`: statistics of the edge-shuffled reservoir against the real one, with random sensor input, before training. Takes no arguments.
- `audit_reward_horizon.py`: light audit (no training, no policy, no GPU): discounted return of an ideal route follower against hovering. Takes no arguments.
- `audit_architectural_curriculum_goals.py <output>`: availability audit of training goals on the architectural scenes (refuses to overwrite).
- `build_reference_manifest.py`: builds the historical medium reference manifest from preserved records (read-only; writes under `private/`).
- `summarize_variance.py`: summary of the variance study by its protocol. Takes no arguments.
- `summarize_phase1_run.py`: aggregation of the Phase 1 run by its declared rules. Takes no arguments.
- `confirm_variance_best.py` and `committee_evals.py`: see evaluation above.
- `collect_geometry_results.py <root>`: reads a completed geometry run without importing the simulator.
- `cleanup_runs.py [--apply]`: lists raw imitation datasets under `runs/training/*/training-data` and writes a manifest to `private/`. Deletes them only with `--apply`. Keeps every JSON, ZIP and log.
- `check_planner_development.py prepare --output PATH --deadline DEADLINE [--seed-start N]` (argparse subcommands; `prepare` writes the frozen comparison draft): prepares and runs a frozen planner development comparison. Never a final test.
- `check_planner_failures.py --output PATH`: bounded diagnostics on reused v55 failures.
- `check_architectural_navigation.py <output> [--controller-version planner-1.4-exp.1|...] [--max-transitions N] [--max-seconds S]`: bounded full-connectome checks on the architectural objectives.

## Rendering, plots and figures

These scripts write figures or summaries from saved records. They do not run a policy.

- `plot_autonomous_training.py <run> <output>`: plots existing PPO episode logs without loading models.
- `plot_architectural_curriculum.py <run> <output>`: plots recorded lesson rounds and original-goal validation.
- `plot_planner_diagnostics.py <source>`: summarizes saved planner traces without recomputing sensors or actions.
- `report_planner_development.py <baseline> <candidate> --output PATH [--baseline-version ...] [--candidate-version ...]`: report of an already completed, frozen paired development check.
- `report_planner_execution.py <trace> --seed S --output PATH`: sampled planner execution from saved traces (the command is in [COMMANDS.md](../docs/operations/COMMANDS.md#offline-planner-execution-diagnostics)).
- `collect_geometry_results.py` (above) reads a geometry run.
- `render_map_gallery.py [--output DIR]`: documentation map gallery (default `docs/images`), no brain, no policy.
- `make_report_figures.py [maps] [results] [reservoir] [brain]`: the figures in `docs/images/figures/` (partitioned-profile gallery, level B region gallery, architectural scenes, budget curve, connectome control, four-family gate chart, real against edge-shuffled reservoir, one flight with the full connectome in the loop). The result figures read the local `runs/` summaries; the brain figure flies one episode on the GPU.
- `render_random_profile_gallery.py [OUTPUT.png]`: gallery of randomized training and held-out maps (default `docs/images/random-profile-gallery.png`). Preview only.
- `build_architectural_scenes.py [--output DIR]`: CPU-only architectural drafts, meshes, collision records and previews (default `assets/architecture/draft-0.2`).

## Verification and tooling

- `verify_repository.py`: checks repository documentation links, package discovery and CLI help, without training. Takes no arguments.
- `verify_publication.py ROOT [--output PATH] [--archive PATH]`: audits the working copies of Git-tracked publication files (hashes, links, archive contents) without running a policy.
- `check_doc_links.py [file.md ...]`: checks local Markdown links and same-repository heading anchors. Without arguments it checks every tracked and untracked Markdown file outside `runs/`, `private/`, `data/` and `reports/`.
- `profile_viewer.py [--top N] [--sort KEY]`: profiles the spectator viewer offscreen and prints the heaviest functions.

## Planner checks

The planner scripts are listed with their purposes in the sections above: `check_planner_development.py`, `check_planner_failures.py`, `check_architectural_navigation.py` (probes and analysis), `report_planner_development.py`, `report_planner_execution.py`, `plot_planner_diagnostics.py` (figures and reports), and `eval_planner_architecture.py` (evaluation).

## Utilities and data

- `profiles/passages-mid.json`: the `passages-mid` map profile (32 by 32 by 12 m, 36 obstacles, three partitions, aperture 6.0 by 4.4 m). The drivers refer to it as `scripts/profiles/passages-mid.json`.

## Coverage note

Several scripts are mentioned in more than one section, where they serve both a driver role and an analysis role. The section headings are the primary placement; the list of `.py` files in `scripts/` was checked against this page when it was written.
