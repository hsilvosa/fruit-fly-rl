# Reproducing the results

This guide shows how to rerun each result in the repository: the environment, the verification commands, and then the drivers and trainers for each experiment series, in order. It also records what each step creates locally, the artifact hashes to check against, and how long the step took when it was run. The results themselves are in [docs/experiments/README.md](../experiments/README.md) and the linked results documents. The command reference for the package CLI is [COMMANDS.md](COMMANDS.md).

Read this before running anything:

- **Local artifacts.** `data/` (the pinned connectome and prepared data), `runs/` (checkpoints, logs, per-episode records) and `private/` (evidence copies) are ignored by git and are not in a fresh clone. Steps that need them are marked **[local artifact]**. Steps that create them say what they write.
- **Resource guard.** Every fan-out of evaluation cells goes through [scripts/resource_guard.py](../../scripts/resource_guard.py) (`run_limited`). Do not start several evaluation processes by hand. Training runs one at a time unless a driver says it runs pairs in parallel. The guard and its `RG_*` variables are described in [scripts/README.md](../../scripts/README.md#resource-guard).
- **Reserved pools.** The drivers below evaluate only pools that have been inspected and selected nothing, or pools that are declared for the series. They never open the reserved report and final pools (Level A report 940000 to 949999, Level B final 960000 to 969999, Level C final headings 970000 to 979999, and the Phase 1 report pools). Do not add a command that evaluates them; see the [pools registry](../experiments/README.md#pools-registry).
- **Hardware used.** The results were produced on Windows with an NVIDIA RTX 3060 (12 GB) and CUDA, as stated in [README.md](../../README.md#install-and-run). The durations below are the measured values quoted in the results documents, so they describe that machine.
- **Paths.** Scripts are run from the repository root with `.conda/python.exe -s` (PowerShell or Git Bash, with forward slashes). Several scripts `os.chdir` to an absolute path (the author's checkout); edit that line if you clone the repository elsewhere.

## Environment and data

The true install steps come from [setup.ps1](../../setup.ps1), [environment.yml](../../environment.yml) and the install section of [README.md](../../README.md#install-and-run). Verified against those files:

1. Install Conda. The environment is created by `setup.ps1` at the repository's `.conda` folder, with Python 3.11 (`environment.yml`).
2. From the repository root:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
   ```

   `setup.ps1` does four things, in this order: creates `.conda` from `environment.yml` if `.conda\python.exe` is missing; installs the locked dependencies from `requirements-lock.txt` (PyTorch 2.7.1 with CUDA 12.8 from the PyTorch index, Stable-Baselines3 2.7.0, Panda3D 1.10.16); installs the package in editable mode (`pip install -e .`); and runs `python -s -m fly_rl prepare-data`.
3. Data preparation. `prepare-data` downloads or prepares the pinned MaleCNS connectome and needs network access if the release files are absent. Its outputs go to `data/` **[local artifact]**; `data/` currently holds `processed` and `raw` folders in this checkout.
4. Check the install:

   ```powershell
   .\.conda\python.exe -s -m fly_rl --help
   .\.conda\python.exe -s -m fly_rl benchmark --seconds 20
   ```

   `benchmark` writes `reports/benchmark.json` (reservoir update timing at batch sizes 1, 4, 8 and 16; it is not a viewer or learning throughput).

The viewing demo (`launchers/current/launch-observed-map.cmd`) needs only the prepared data and no checkpoint. Trained checkpoints are not shipped. Every experiment below either trains its own checkpoint or needs the checkpoint named in its step **[local artifact]**.

## Verification commands

Run these after setup and after any change. None of them trains a policy.

| Command | Purpose | Notes |
| --- | --- | --- |
| `.\.conda\python.exe -s -m pytest -q -p no:cacheprovider` | Unit and integration tests in `tests/` (connectome, navigation, recordings, simulation, training, visualization, and `test_publication.py`) | The command is from [COMMANDS.md](COMMANDS.md). The count of 138 tests and their runtime (58.6 s) are quoted in [VERIFICATION.md](VERIFICATION.md) for the practice-mastery checks. |
| `.\.conda\python.exe -s scripts/verify_repository.py` | Checks documentation links, package discovery and CLI help | Takes no arguments; does not establish navigation performance. |
| `.\.conda\python.exe -s scripts/verify_publication.py .` | Audits the working copies of Git-tracked publication files (positional `root`; optional `--output`, `--archive`) | Reads only; no policy runs. |
| `.\.conda\python.exe -s scripts/check_doc_links.py` | Checks local Markdown links and same-repository anchors in all tracked and untracked Markdown outside `runs/`, `private/`, `data/`, `reports/` | Pass file paths to check only some files. |
| `.\.conda\python.exe -s scripts/verify_geometry.py --data data` | Bounded whole-connectome verification; optimizer smoke only when opted in | Read its argparse help first. |

Verification of an experiment's frozen layouts is built into the loaders: a frozen suite checks its layouts when loaded.

## Series by series

Each series lists its steps in order. Where a step is a driver, it runs everything inside that series; where a step is a single trainer or cell, the command is the one in the script's usage line. The **Artifacts** line gives the run directory and the hash prefixes from [ROADMAP.md, section 9](../../ROADMAP.md#9-artifact-index).

### Start point and reference recovery (transfer 1 to 8)

The chain starts from the 50/64 policy, `runs/training/sensors-v3-v1/selected/selected-policy.zip` (hash `0a1a6569549a958a`) **[local artifact]**. Each later stage starts from the previous selected checkpoint. The Phase 1 and Phase 3 experiments start from the experiment 7 checkpoint `runs/training/reference-transfer-7/mix3e4/stage-2.zip` (hash `773dff8d53e2e115`) **[local artifact]**, which is the start of most later series. Reproducing that checkpoint means running transfer 1 to 7 in order, which needs the earlier historical artifacts.

- **Historical record (read-only).** `scripts/build_reference_manifest.py` builds the manifest of the historical winners from preserved records, and `scripts/replay_reference_validation.py [names]` replays them on their own recorded validation pools (default names `sensors-v3-v1`, `ray-risk-v1`, `approach-v1`). Output goes to `private/` and `runs/verification/reference-recovery-1` **[local artifact]**.
- **Trainers, in order (no driver).** There is no driver for transfer 1 to 8 in `scripts/`. Each experiment's trainer is invoked directly with the arguments in its usage line, and the exact stage order and arguments come from its protocol:
  - T1: `scripts/train_reference_transfer.py <retained|fresh> <output-dir>`, 65,536 transitions.
  - T2: `scripts/train_reference_transfer2.py <route65|budget262> <output-dir>`.
  - T3: `scripts/train_reference_transfer3.py <output-dir>` (source: 50/64 selected policy).
  - T4: `scripts/train_reference_transfer4.py <output-dir>` (from the T3 final checkpoint).
  - T5: `scripts/train_reference_transfer5.py <output-dir>` (from the T4 selected checkpoint).
  - T6: `scripts/train_reference_transfer6.py <output-dir>` (from the T5 selected checkpoint).
  - T7: `scripts/train_reference_transfer7.py <mix3e4|mix1e4> <output-dir>` (from the T6 selected checkpoint).
  - T8: `scripts/train_reference_transfer8.py <seed442|seed443> <output-dir>` (from the T7 selected checkpoint).
- **Evaluation.** Each stage is evaluated on the development pools with `scripts/eval_cell.py <checkpoint> <profile|none> <seed> <episodes> <out.json>` (32 episodes per cell in the early series) or `scripts/eval_checkpoint.py`. Pools are in the protocols (for example `passages` 810000, `passages-mid` 850000, `passages-wide` 830000).
- **Failure classification (T0).** `scripts/classify_failures.py <label> <checkpoint.zip> <profile> <seed> <episodes> <output.json>` and `scripts/profile_edge_ladder.py <checkpoint.zip> <seed> <episodes> <output.json> <profile>...`.

**Resources and timing.** Quoted from the results: each T1 arm about 5.5 minutes of training; T6 about 7.5 minutes; T3 and T4 evaluations of the gate and medium cells on 32 episodes each. The T1 to T8 documents do not give a total wall-clock time for the whole chain.

**Artifacts.** `runs/training/reference-transfer-1` to `reference-transfer-8` **[local artifact, written by the trainers]**; the experiment 7 start `runs/training/reference-transfer-7/mix3e4/stage-2.zip` (`773dff8d53e2e115`).

### Regression suite (medium rooms)

- **Command.** `.\.conda\python.exe -s scripts/regression_medium.py <checkpoint.zip> <label> <output-dir> [reference-result.json]`. It evaluates four frozen medium pools (A 100000, B 840000, C 860000, D 861000; 32 episodes each) through the guard and writes `regression-<label>.json`.
- **Rule.** Per-pool floor 17 of 32, total 88 of 128, and the original-pool floor 21 of 32 (see [MEDIUM_REGRESSION_SUITE.md](../methods/MEDIUM_REGRESSION_SUITE.md)).
- **Artifacts.** Output in the directory you pass **[local artifact]**. The reference checkpoints are in the table of historical winners in [HISTORICAL_REFERENCE.md](../experiments/reference-recovery/HISTORICAL_REFERENCE.md).
- **Resources.** Four cells per checkpoint, run through the guard.

### Variance study (R1)

- **Driver.** `.\.conda\python.exe -s scripts/variance_driver.py` (no arguments). It runs five trainings (seeds 501 to 505) one after another with `NOEVAL=1`, then `eval_checkpoint.py` on each stage 3 checkpoint with pools `select,regab`.
- **Summary.** `.\.conda\python.exe -s scripts/summarize_variance.py`.
- **Confirmation.** `.\.conda\python.exe -s scripts/confirm_variance_best.py` (fresh pool 880000, 64 episodes per cell).
- **Artifacts.** `runs/training/variance-study/seed501` to `seed505` **[local artifact]**. The pilot checkpoint it refers to is `runs/training/phase1-pilot/seed442/stage-3.zip` (`71889c4d752ab6bb`).
- **Resources.** Training runs one at a time; evaluation through the guard. The protocol estimated the series from the measured Phase 1 cost. Use [VARIANCE_STUDY_RESULTS.md](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md) for the outcome.

### Phase 1 pilot and Phase 1 run (stabilized trainer)

- **Pilot (one seed).** `.\.conda\python.exe -s scripts/train_phase1_pilot.py seed442 runs/training/phase1-pilot/seed442` (three stages, 32,768 transitions per stage). Then evaluate stage 3 with `scripts/eval_checkpoint.py runs/training/phase1-pilot/seed442/stage-3.zip <label> runs/training/phase1-pilot/seed442`. The pilot was run once, and an earlier launch with 28 simultaneous evaluations restarted the PC; its results are not used.
- **Run (two seeds).** `.\.conda\python.exe -s scripts/phase1_driver_quiet.py` (no arguments). It trains seeds 442 and 443 with `NOEVAL=1`, then evaluates the four stages of each seed. `scripts/phase1_driver.py` is the same flow with Telegram milestones: it calls the external command `hermes send -t telegram`, so it needs that tool configured. The quiet version does not.
- **Summary.** `.\.conda\python.exe -s scripts/summarize_phase1_run.py`.
- **Artifacts.** `runs/training/phase1-pilot/seed442` (pilot stage 3, `71889c4d752ab6bb`); `runs/training/phase1-run/seed442` and `seed443` **[local artifact]**.
- **Resources.** Quoted: the pilot's first launch was unsafe (28 simultaneous evaluations). The run's training took about 9 minutes for both seeds, and evaluation about 55 minutes for 8 checkpoints and 112 cells (see [PHASE1_RUN_RESULTS.md](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md)).

### Phase 3 memory screening and replication

- **Screening.** `.\.conda\python.exe -s scripts/phase3_driver.py` (no arguments). Trains `short442` and `long442` (four stages each in the trainer, `scripts/train_phase3.py <short442|long442> <output-dir>`), then evaluates stages 2 and 4.
- **Replication.** `.\.conda\python.exe -s scripts/phase3_replication_driver.py`. Trains `long443`, evaluates all four stages.
- **Artifacts.** `runs/training/phase3-screen/long442/stage-4.zip` (`b2ed6a186493c533`) and `runs/training/phase3-screen/long443/stage-4.zip` (`536622b163bc79cd`) **[local artifact]**.
- **Resources.** Replication estimate in its protocol was 45 to 50 minutes; the screening training took 5.5 minutes (short) and 7 minutes (long).

### R5 randomized maps

- **Driver.** `.\.conda\python.exe -s scripts/r5_driver.py` (no arguments). Trains seeds 601 to 603 (`scripts/train_random.py`, 3 stages, the `STAGE_OVERRIDE` environment variable sets the stage size), evaluates each with `eval_checkpoint.py` (`select,regab`), runs randomized cells (`randomA-0.5` pool 890000, `randomA-0.9` pool 891000, `randomB-dev` pool 950000, 64 episodes) through the guard, evaluates the five control runs the same way, and runs the level C baseline of the start checkpoint (168 episodes, seed 900000).
- **Pool note.** Pools 890000 and 891000 are used by R5 cells and are not listed in the [pools registry](../experiments/README.md#pools-registry); check the protocol before citing them.
- **Artifacts.** `runs/training/random-run/seed601` to `seed603`, `control-seed501` to `control-seed505`, `level-c-baseline-start.json` **[local artifact]**.
- **Resources.** Quoted: training 11 minutes in total; evaluation about 2 h 50 min against an estimate of 85 minutes (see [RANDOM_DISTRIBUTION_RESULTS.md](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md)).

### Light audit, committee evaluation, collision anatomy, feature probe, sensing probes

These need no training.

- **Light audit.** `.\.conda\python.exe -s scripts/audit_reward_horizon.py`. No arguments. Writes `private/reference-recovery-1-evidence/reward-audit.json` **[local artifact, under private/]**.
- **Committee evaluation.** `.\.conda\python.exe -s scripts/committee_evals.py` (no arguments): run 601 and the pilot on pool 880000, with stochastic and deterministic cells. Run 601 is `runs/training/random-run/seed601/stage-3.zip`.
- **Collision anatomy.** `.\.conda\python.exe -s scripts/collision_anatomy.py <label> <checkpoint.zip> passages 880000 64 <output.json>`.
- **Feature probe.** `.\.conda\python.exe -s scripts/collect_probe_data.py <checkpoint.zip> passages 881000 64 <output.npz>` (every third step stored; the results document quotes 18,044 samples for run 601 and 22,304 for the pilot), then `.\.conda\python.exe -s scripts/analyze_probe.py <name> ...` (the script reads the collected data for the names given and writes `probe-results.json` in `runs/verification/probe/`).
- **Sensing probes.** `scripts/collect_probe_data_long.py <checkpoint.zip> <profile> <seed> <episodes> <output.npz>`; `scripts/analyze_probe_variants.py history <name>` or `range <name-long>`; `scripts/probe_synthetic.py <maps> <output-prefix>` (synthetic poses, pool 895000 to 895699; no policy).
- **Artifacts.** Probe data and `probe-results.json` in `runs/verification/probe/` **[local artifact]**.
- **Resources.** Quoted: the feature probe's collection took 16 minutes.

### Waypoint diagnostic

- **Driver.** `.\.conda\python.exe -s scripts/waypoint_driver.py` (no arguments). Four trainings in series (`waypoint` and `control`, seeds 701 and 702; each 8 stages of 32,768), then evaluation on pool 880000 (64 episodes per cell).
- **Artifacts.** `runs/training/waypoint-diagnostic/waypoint701` and the other three arm and seed directories **[local artifact]**.
- **Resources.** Quoted: 56 minutes in total (10 minutes per training, 19 minutes of evaluation).

### Auxiliary and privileged-critic students, and pretraining

- **Students.** `.\.conda\python.exe -s scripts/student_driver.py` (no arguments). Trains `aux` and `critic` for seeds 801 to 803 and the control at 703 (`scripts/train_student.py`, and `scripts/train_waypoint.py control` for the control arm), then evaluates all arms on pool 882000 (`passages`, `passages-mid`, `passages-wide`, medium, `passages` with sampled actions) and on the level B development pool 950000. The two earlier controls, 701 and 702, are evaluated too.
- **Pretraining.** `.\.conda\python.exe -s scripts/pretrain_driver.py` (no arguments). Collects data (`scripts/collect_pretrain.py`) on 512 maps (pool 896000 to 896799), pretrains the trunk (`scripts/pretrain_trunk.py`) and gates it at 45 degrees, then runs the `pre` arm (`scripts/train_student.py pre <seed> <output-dir> 8`) for seeds 901 to 903, and evaluates on pool 882000.
- **Artifacts.** `runs/training/student-experiment/` and `runs/training/pretrain/` (`data`, `pre901` to `pre903`) **[local artifact]**.
- **Resources.** Quoted: the pretraining experiment took 1 hour 16 minutes, with collection 13 minutes, pretraining under 1 minute, three PPO trainings 30 minutes, evaluation 34 minutes.

### Large budget B1 (1M added transitions)

- **Driver.** `.\.conda\python.exe -s scripts/large_budget_driver.py` (no arguments). Trains seed 801 for 31 stages with `scripts/train_large_budget.py` if the final stage file is absent, then evaluates the curve at stages 3, 9, 18 and 31 (about 98k, 295k, 590k and 1M transitions) on pool 884000 for `passages` and medium, both modes. The final stage also gets `passages-mid`, `passages-wide` and `gate-two`.
- **Artifacts.** `runs/training/large-budget/seed801/stage-31.zip` (`0896b5fbe22f9c10`) **[local artifact]**.
- **Resources.** Quoted: training 41 min 28 s (79 s per stage), evaluation 23 min 47 s.

### Large budget 2M (B2)

- **Driver.** `.\.conda\python.exe -s scripts/large_budget_2m_driver.py` (no arguments). Trains seed 801 for 61 stages (1,998,848 transitions) and evaluates stages 15, 31, 46 and 61 on pool 885000 for `passages` and medium, both modes; the final stage also gets `passages-mid`, `passages-wide` and `gate-two`, and the B1 final checkpoint is evaluated on the same pool. The driver stops if memory goes above 92 percent during training.
- **Artifacts.** `runs/training/large-budget-2m/seed801/stage-61.zip` (`3a4150b59b5fc894`) **[local artifact]**.
- **Resources.** Quoted: training about 77 min of stage time (65 to 81 s per stage), evaluation 29 min 30 s for 26 cells.

### Replication of the 2M recipe (B3)

- **Driver.** `.\.conda\python.exe -s scripts/replication_2m_driver.py` (no arguments). Trains seeds 851 and 901 in series (`scripts/train_large_budget.py <seed> <output-dir> 61`), then evaluates stages 46 and 61 of all three seeds and the start checkpoint on pool 886000, through the guard (4 processes, 2 threads each).
- **Artifacts.** `runs/training/large-budget-2m/seed851/stage-61.zip` (`fc1b2c69068ac72e`) and `seed901/stage-61.zip` (`29ac1bcf11652646`) **[local artifact]**; B3 evaluation cells in `runs/training/large-budget-2m/b3-eval/`.
- **Resources.** Quoted: each seed about 81 to 82 min of stage time; evaluation 50 min 4 s for 46 cells.

### Level B and level C (B4)

- **Driver.** `.\.conda\python.exe -s scripts/level_bc_driver.py` (no arguments). Evaluates stage 61 of seeds 801, 851 and 901, and the start checkpoint, on level C (`scripts/eval_architecture.py <ck> 8 <out.json> 900000`, deterministic and sampled) and level B (`scripts/eval_random_cell.py <ck> heldout_b 0.8 950000 64 <out.json>`, deterministic and sampled), through the guard.
- **Pool note.** Level B pool 950000 to 950063 and level C headings 900000 are the development pools declared in [LEVEL_BC_PROTOCOL.md](../experiments/large-budget/LEVEL_BC_PROTOCOL.md). The level B final pool (960000 to 969999) and the level C final headings (970000 to 979999) are reserved and must not be run.
- **Artifacts.** `runs/training/large-budget-2m/b4-eval/` **[local artifact]**; checkpoints are the B3 stage 61 files.
- **Resources.** Quoted: 52 min 57 s for the whole evaluation; level C runs 12 to 17 min each.

### Connectome control C1.0, C1.1 and C1.2

Both arms (`real` and `shuffled`, the edge-shuffled reservoir) are trained from random weights. The shuffled checkpoints are evaluated with the shuffled brain injected through `scripts/eval_cell_brain.py` and the `shuffled` argument of `eval_random_cell.py` and `eval_architecture.py`.

- **C1.0 (phase 1, seed 1001).** `.\.conda\python.exe -s scripts/connectome_control_c10_driver.py` (no arguments). Trains both arms (27 stages, 884,736 transitions, medium rooms), in parallel under the raised guard limit, then evaluates medium on pool 887000. If the mean CPU over the first two minutes of overlap is above 93 percent, the shuffled training is stopped and run after the real one.
- **C1.1 (phase 2, seeds 1001 and 1051).** `.\.conda\python.exe -s scripts/connectome_control_c11_driver.py` (no arguments). Runs phase 1 for seed 1051 and phase 2 (61 stages, `scripts/train_fresh_phase2.py <arm> <seed> <source> <output-dir> 61`) for both seeds, in pairs, then evaluates on the retained cells (pool 886000 for `passages`, `passages-mid`, `passages-wide`, medium, and level B and C pools).
- **C1.2 (extension by 61 stages).** `.\.conda\python.exe -s scripts/connectome_control_c12_driver.py` (optional first argument `train-only`, which stops after the trainings). Extends the four C1.1 phase 2 runs by 61 more stages (the driver passes `OFFSET = 100` to `train_fresh_phase2.py`), in two pairs (seed 1001, then 1051), then evaluates on pool 888000 and on level B and C.
- **C1.3 (two more seeds).** `.\.conda\python.exe -s scripts/connectome_control_c13_driver.py` (first argument `train-only` stops after the trainings; `dry-run` prints the pending jobs and exits without starting anything). Trains seeds 1101 and 1151 for both arms through the three phases (27, 61 and 61 stages, the last with layout offset 100), one pair at a time, evaluates on the C1.2 cells and pool 888000, and runs the frozen analysis of `scripts/connectome_control_stats.py` over the four seeds per arm (`c13-eval/analysis.json`). About 7 h 50 min by estimate. Prepared, not yet run.
- **Artifacts.** `runs/training/connectome-control/phase1-real1001` (`05be0cc88b1b7ae3`), `phase1-shuffled1001` (`994d24760718d037`), `phase2-<arm><seed>` (`d1cf2ca4e3c3c535`, `b2e6a0f459ce41b8`, `47ab8dc1c288566f`, `918cbc6fbf0c3464`), and `phase3-<arm><seed>` (`89afcdc35f385c56`, `a7e549d4c9bf8d93`, `b85f2e42c67fea4a`, `9ca7652aa583a5e1`) **[local artifact]**. Evaluation folders `c10-eval/`, `c11-eval/`, `c12-eval/`.
- **Resources.** Quoted: C1.0 training about 38 min with two parallel trainings, evaluation 12 min 20 s; C1.1 phase 2 pairs about 84 min each, training about 3 h 30 in total as planned; C1.2 about 84 min per pair, 4 h 06 in all against 4 h 10 estimated. The three drivers raise the guard to 95 percent CPU and memory, with the fallback described above.
- **Graph check before training.** `.\.conda\python.exe -s scripts/check_shuffled_graph.py` prints statistics of the shuffled and real reservoirs (no policy, no training).

### Planner reference C1.P

- **Driver.** `.\.conda\python.exe -s scripts/planner_reference_driver.py` (no arguments). Runs the explicit planner-1.4-exp.3 on the 168 level C cases in four processes of two headings each (`scripts/eval_planner_architecture.py <out> <first> <last>`), and the retained stage 61 checkpoints of seeds 801, 851 and 901 on the `large` (pool 892000 to 892031) and `maze` (pool 893000 to 893031) profiles, 32 episodes per cell, both modes (`scripts/eval_cell_mode.py`). The driver sets the guard to 95 percent, a start threshold of 85, 5 processes and 15 seconds of stagger, because each planner process uses about 2 GiB of GPU memory.
- **Artifacts.** `runs/training/planner-reference/` (`planner-levelC-h*.json`, `seed*-large-*.json`, `seed*-maze-*.json`) **[local artifact]**; the planner's own sources are hashed in the results document.
- **Resources.** Quoted: estimate of about 70 minutes; actual 78 min 15 s in total, with the planner processes taking 28 to 31 minutes.

### Architectural scenes and the autonomous curriculum

These are smaller series, documented in [docs/evidence](../evidence/README.md) rather than in the experiment catalog.

- **Verification smoke tests.** `.\.conda\python.exe -s scripts/verify_architectural_curriculum.py <output>` and `scripts/verify_autonomous_architecture.py <output>`: 128-transition PPO smoke tests. They check that the pipeline runs and are not navigation experiments.
- **Trainers (argparse; each takes an output path).** `scripts/train_autonomous_architecture.py`, `scripts/train_architectural_curriculum.py`, `scripts/train_architectural_curriculum_balanced.py`, `scripts/train_architectural_curriculum_mixed.py`. Run `--help` on each before use; the output directory must not exist.
- **Planner checks.** `scripts/check_architectural_navigation.py <output> [--controller-version planner-1.4-exp.1|...] [--max-transitions N] [--max-seconds S]`.
- **Evaluation.** `scripts/eval_architecture.py <checkpoint.zip> <headings> <output.json> [seed] [sampled] [shuffled]`.

## Step-by-step for a single result

To reproduce the B2 result as an example:

1. Complete the environment steps and the verification commands.
2. Confirm the start checkpoint `runs/training/reference-transfer-7/mix3e4/stage-2.zip` exists and starts with `773dff8d53e2e115` (for example with `certutil -hashfile <file> SHA256` on Windows or `sha256sum` in Git Bash). **[local artifact]** If it is missing, the chain from transfer 1 is needed.
3. Run `.\.conda\python.exe -s scripts/large_budget_2m_driver.py`. It writes its logs to `runs/training/large-budget-2m/`.
4. Compare `runs/training/large-budget-2m/seed801/stage-61.zip` with `3a4150b59b5fc894` and the cell summaries with [LARGE_BUDGET_2M_RESULTS.md](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md).

## Reading the output

- Trainers write checkpoints as `stage-N.zip` with a sidecar of metadata. Do not overwrite a completed run: the drivers skip finished stages, and a partially finished training restarts from the source (delete its partial directory first, as the driver docstrings say).
- Evaluation cells write one JSON per cell with successes, collisions, timeouts, and the successful seeds. The driver prints a summary line per cell.
- A run's result is the rule in its protocol, not the printed numbers alone. The rule and the decision are in the results document of the series.
