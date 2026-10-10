# Roadmap

Live status board. Last updated: October 10, 2026, after commit `9e60999` on `navigation-development`. Active runs: none. This file is the single place that says what is done, what is open, and what can start next. The earlier roadmap is kept in [ROADMAP_HISTORY.md](ROADMAP_HISTORY.md).

## 1. Objective

A learned virtual fly that reaches goals in maps it has never trained on. Flight actions come from the learned policy. The full MaleCNS v1.0 connectome (167,184 neurons, 25,583,622 edges) stays in the controller. An explicit planner may be a reference or a teacher. It never chooses the evaluated policy's actions.

"Unseen map" has three levels, reported separately. Details are in [ZERO_SHOT_PLAN.md](docs/ZERO_SHOT_PLAN.md).

| Level | Meaning |
| --- | --- |
| A | New layouts (new seeds) from a family used in training |
| B | Parameter ranges the generator never produced in training |
| C | A map family that never entered training |

Proposed release gate: at least 52 of 64 successes and at most 3 collisions in each of four families (medium, large, maze, architectural), on reserved pools, with Wilson 95% intervals, matched controls (no connectome, planner reference) and at least two seeds. Real buildings and street reconstructions are out of scope until after the first release.

## 2. Where the project stands

| Capability | Status | Evidence |
| --- | --- | --- |
| Historical learned reference (50/64, 48/64, 45/64) | Recovered, hash-verified, replays exactly | [HISTORICAL_REFERENCE.md](docs/HISTORICAL_REFERENCE.md) |
| Medium dense rooms | Retained in every experiment: 21 to 30 of 32 | [TRANSFER_SUMMARY.md](docs/TRANSFER_SUMMARY.md), Phase 1 and 3 results |
| Single and double gates | Solved: 27 to 32 of 32 | Same |
| `passages-wide` | Learned. Stable in one seed (22 to 25 of 32), unstable in another (0 to 18) | [PHASE1_RUN_RESULTS.md](docs/PHASE1_RUN_RESULTS.md) |
| `passages-mid`, `passages` | Mostly 6 to 12 and 0 to 6 of 32. Best single checkpoint: 21 and 5 of 32 | [PHASE1_PILOT_RESULTS.md](docs/PHASE1_PILOT_RESULTS.md) |
| `large`, `maze`, architectural scenes | Not trained in this line. Reference scored 0/16 on `large` | [HISTORICAL_REFERENCE.md](docs/HISTORICAL_REFERENCE.md) |
| Memory (history window) | Not replicated: seed 442 gained, seed 443 lost on one profile | [PHASE3_REPLICATION_RESULTS.md](docs/PHASE3_REPLICATION_RESULTS.md) |
| Unseen-map navigation (levels A, B, C) | No evidence. No held-out set exists yet | This file |
| Release gate | Not met | This file |

Best development candidate so far: `runs/training/phase1-pilot/seed442/stage-3.zip` (medium 25, medium-b 27, gate-two 32, gate-long 32, passages-wide 11, passages-mid 21, passages 5 of 32 on the selection pools). It is a development result from one training run that the recipe did not reproduce.

## 3. What worked, what failed, what we learned

Worked:

- Recovering the reference before training anything new.
- Graded maps with medium rooms kept in the mix. Training only on the hardest map gave no signal.
- Declaring every protocol before training, and keeping selection pools apart from report pools.
- Evaluation is repeatable to within one episode.
- The resource guard (`scripts/resource_guard.py`) keeps the machine usable.

Failed:

- No profile beyond `passages-wide` reaches a useful rate, and none reaches the 81% gate.
- Plain PPO oscillated (Phase 1 control). The stabilization bundle held one seed and not the other.
- Memory did not replicate. A route-progress reward and more steps (experiment 2) gave nothing in their budgets.
- Many comparisons used one training run per condition, with effects smaller than the spread between runs.

Learned:

- The training run is the high-variance part: seeds from the same start differ by up to 18 episodes on one profile, and the same seed with a different decay schedule reversed the outcome.
- The policy often keeps one hard profile at the expense of another. This trade-off appears in all three phases.
- Open hypotheses, not measured: the policy network and short-range sensors limit capacity; the Euclidean-progress reward creates local minima at partitions.

## 4. Progress board

Markers: `[x]` done, `[ ]` open, `[~]` partly done. Each phase links to its design in [ZERO_SHOT_PLAN.md](docs/ZERO_SHOT_PLAN.md).

### Phase 0. Baseline and housekeeping

- [x] Recover and hash-verify the historical medium-room winners
- [x] Replay the winners on their recorded pools (per-episode agreement)
- [x] Classify `passages` failures ([PASSAGES_FAILURE_CLASSIFICATION.md](docs/PASSAGES_FAILURE_CLASSIFICATION.md))
- [x] Run and document transfer experiments 1 to 8 ([TRANSFER_SUMMARY.md](docs/TRANSFER_SUMMARY.md))
- [x] Remove regenerable raw datasets from `runs/` ([RUNS_CLEANUP.md](docs/RUNS_CLEANUP.md))
- [x] Write the plan, README and completion-plan updates
- [x] Resource guard for evaluation fan-out
- [x] Measure evaluation repeatability
- [ ] Freeze the medium-room regression suite as a documented, reusable test (action R2)

### Phase 1. Stable trainer: closed as negative for its exit criterion

- [x] Stabilization bundle implemented (pilot and run scripts)
- [x] Separate selection pools introduced (report pools still unopened)
- [x] Two-seed run with four evaluations ([PHASE1_RUN_RESULTS.md](docs/PHASE1_RUN_RESULTS.md))
- [x] Result recorded: seed 442 stable, seed 443 not, hardest profile not raised
- [ ] Measure training variance directly: several runs of one recipe (action R1)

### Phase 2. Randomized map distribution: not started

- [ ] Parameter ranges and adaptive-difficulty rule written and committed
- [ ] Map sampler implemented with tests and a sample gallery (action R3)
- [ ] Level B held-out parameter region and level C held-out family chosen and sealed (action R4, needs a user decision)
- [ ] Training run with at least two seeds (action R5)
- [ ] Level A development gate met on both seeds

### Phase 3. Memory: tested, not established

- [x] No-memory control recorded
- [x] History-window policy trained on two seeds
- [x] Gain decided: not replicated
- [ ] Retest with at least three seeds and 64 episodes per cell, inside the Phase 2 setup (action R6)

### Phase 4. Target families: not started

- [ ] Large rooms, mazes and architectural scenes added to the sampler
- [ ] Sensor decision (current rays or the 24-unit panorama, which needs a versioned transfer)
- [ ] Planner imitation decision (needs an agreed teacher and imitation budget)
- [ ] Development gate in every training family
- [ ] Held-out family result recorded

### Phase 5. Freeze and independent assessment: not started

- [ ] Inventory of inspected pools
- [ ] Reserved pools and final protocol sealed
- [ ] Candidate, sources and hashes frozen
- [ ] Single final run on reserved pools
- [ ] Release gate evaluated per family with intervals
- [ ] No-connectome learned control and planner reference reported

### Phase 6. Release: not started

- [ ] Installation and data distribution verified on a clean machine
- [ ] Learned demo for each supported map family
- [ ] Logging, replay and brain visualization verified with the release checkpoint
- [ ] Formulas, attribution, limitations and results tables published
- [ ] Repository and link audit passed
- [ ] Numbered release tagged

## 5. Actions ready to start

Each action lists what it needs, an estimate with its basis, and what it unlocks. Estimates come from measured timings: one training stage of 32,768 transitions takes 65 to 95 s; one seven-cell evaluation of a checkpoint on one pool set takes 5 to 7 min under the resource guard; a fourteen-cell evaluation takes 8 to 10 min. Code-writing estimates have no measured basis and carry more uncertainty.

| ID | Action | Needs | Estimate | Compute | Unlocks |
| --- | --- | --- | --- | --- | --- |
| R1 | Variance study: 5 trainings of the pilot recipe (98,304 transitions, new seeds), final checkpoint on the seven selection cells | Nothing | About 60 min (5 x (6 min training + 6 min evaluation)) | CPU about 55% in training | A measured spread, a best-of-N candidate, and the minimum effect size any later comparison must exceed |
| R2 | Freeze the medium-room regression suite: script, pools, baseline numbers for the reference checkpoints | Nothing | About 30 min (code 15 min, one evaluation 10 min) | Light | Closes Phase 0. A fixed check for every later candidate |
| R3 | Implement the Phase 2 map sampler with adaptive difficulty, tests and a sample gallery | Nothing | 1.5 to 2 h (no measured basis) | Almost none | R4, R5 |
| R4 | Define and seal the level B region and the level C family | R3 and a user decision on which family to hold out | About 20 min after the decision | None | R5, Phase 5 |
| R5 | Train on the random distribution, two seeds, with selection pools | R3, R4. R1 optional but advised | About 90 min (2 x 7 min training + evaluation) | CPU about 55% | Level A development result, and a first look at levels B and C |
| R6 | Memory retest: 3 seeds x 2 conditions, 64 episodes per cell, final checkpoint only | R3 advised | About 2 h (no measured basis for 64 episodes) | CPU about 55% | A decision on memory |

Recommended order: R2 first (short, closes Phase 0). Run R1 while writing R3, since R3 is mostly editing. Then R4, then R5.

R1 and R3 can overlap. Two training or evaluation jobs must not run at once, because one training job uses about half of the CPU.

## 6. Decision points

| After | Question | If yes | If no |
| --- | --- | --- | --- |
| R1 | Is the range of passages-mid or passages-wide across runs at least 10 episodes of 32? | Every later comparison needs at least 3 seeds and 64 episodes per cell. Use best-of-N with a separate report pool | Single-run comparisons with a 6-episode threshold are acceptable |
| R5 | On two seeds, does each development cell reach 26 of 32 with at most 3 collisions, and medium stay at 21 or more? | Move to Phase 4 (target families) | Change the representation before more training: decide among a longer-range sensor, a memory retest (R6), or planner imitation. The user decides, because imitation shifts weight from RL |
| R5 | Does any result appear on level B or C? | Report it with intervals. It is the first evidence for the objective | Report that no unseen-map evidence exists yet |
| Phase 4 | Is a held-out family result at or above half the development rate? | Proceed to Phase 5 | Keep training and revisit the representation |

## 7. Rules for every iteration

- Commit the protocol (design, pools, acceptance rule, positive result) before training or evaluation. Report negative results with the same detail as positive ones.
- Change one factor, or run a declared control arm. Use at least two seeds for any claim, and expect between-seed spread of 10 to 18 episodes until R1 says otherwise.
- Choose checkpoints on a selection pool that the report never uses. The report and reserved pools stay unopened until Phase 5.
- Never overwrite aliases, completed runs or controller sources. Record source and checkpoint hashes.
- Resources: the PC must stay usable. Brief CPU peaks are accepted, sustained 100% is not. The GPU has no limit. Evaluation fan-out goes through `scripts/resource_guard.py`. Run one training job at a time.
- Give a time estimate with its basis before each iteration. Update the estimate when a measurement disagrees.
- No planner action in any evaluated policy. Full connectome in every policy.

## 8. Pools registry

| Pool | Seeds | Use | Status |
| --- | --- | --- | --- |
| Historical final pools | Recorded in `runs/suites/consumed` | Earlier final tests, including the 0/64 large-room pool | Consumed. Never a test again |
| Medium regression, validation of the 50/64 policy | 100000 to 100031 | Regression check | Inspected |
| Medium-b | 840000 to 840031 | Regression check | Inspected |
| Gate pools | 830000 to 830031 | Development | Inspected |
| `passages-wide` | 830000 to 830031 | Development | Inspected |
| `passages-mid` | 850000 to 850031 | Development | Inspected |
| `passages` | 810000 to 810031 | Development and failure classification | Inspected |
| Selection pools | 860000 to 865000 (one range per cell) | Choosing checkpoints (Phases 1 and 3) | Used for selection only |
| Report pools | Not yet drawn | Final Phase 1 style reports | Reserved, unopened |
| Level B region, level C family | Not yet defined | Zero-shot evidence | Reserved, to be sealed in R4 |

## 9. Artifact index

All run artifacts are local and ignored by git (`runs/`, `private/`). Hashes are the first 16 hex digits of SHA-256.

| Artifact | Path | Hash |
| --- | --- | --- |
| Reference, 50/64 | `runs/training/sensors-v3-v1/selected/selected-policy.zip` | `0a1a6569549a958a` |
| Reference, 48/64 | `runs/training/ray-risk-v1/selected/selected-policy.zip` | `3b9e8ba41305c035` |
| Reference, 45/64 | `runs/training/approach-v1/selected/selected-policy.zip` | `92d9c8ba2ff308bf` |
| Original dense alias | `runs/dense-flight-policy.zip` | `085963d6e95b2a25` |
| Start of Phase 1 and 3 (experiment 7) | `runs/training/reference-transfer-7/mix3e4/stage-2.zip` | `773dff8d53e2e115` |
| Best development candidate (pilot) | `runs/training/phase1-pilot/seed442/stage-3.zip` | `71889c4d752ab6bb` |
| Phase 3, long window, seed 442, stage 4 | `runs/training/phase3-screen/long442/stage-4.zip` | `b2ed6a186493c533` |
| Phase 3, long window, seed 443, stage 4 | `runs/training/phase3-screen/long443/stage-4.zip` | `536622b163bc79cd` |

Detailed evidence copies live in `private/reference-recovery-1-evidence/`. The experiment index is [docs/EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md).

## 10. How to keep this file current

After every iteration, in the same commit as its results document: update the date and commit in the first line, tick or add items on the board, change the status table in section 2 only if a number changed, add a row to the experiment log, and revise the estimates in section 5 if a timing was off. Keep the protocol and the results in their own documents, and link them from here.
