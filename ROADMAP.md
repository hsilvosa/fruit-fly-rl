# Roadmap

Live status board. Last updated: October 14, 2026, after actions R1 to R5, the diagnostics that followed, B1 to B4, C1.0 to C1.2 (see docs/EXPERIMENT_LOG.md) on `navigation-development`. Active runs: none. This file is the single place that says what is done, what is open, and what can start next. The earlier roadmap is kept in [ROADMAP_HISTORY.md](ROADMAP_HISTORY.md).

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
| Run 601 (R5 seed) on a fresh 64-episode pool | Medium 92%, passages-wide 86%, passages-mid 55%, passages 14%. First checkpoint that keeps medium, wide and mid together | [COMMITTEE_EVAL_RESULTS.md](docs/COMMITTEE_EVAL_RESULTS.md) |
| Why `passages` stays low | Collisions end 1.5 to 3.5 m off the certified route around mid-route. The policy input carries the route direction only to 42 to 53 degrees. Giving the actor the route direction as input lifts `passages` from 17% to 59% (diagnostic, not a student) | [COLLISION_ANATOMY.md](docs/COLLISION_ANATOMY.md), [FEATURE_PROBE.md](docs/FEATURE_PROBE.md), [WAYPOINT_DIAGNOSTIC_RESULTS.md](docs/WAYPOINT_DIAGNOSTIC_RESULTS.md) |
| Route signal used only in training (auxiliary head, privileged critic, supervised pretraining) | Negative: `passages` 13 to 15 of 64 against 12 for the control | [AUXILIARY_STUDENT_RESULTS.md](docs/AUXILIARY_STUDENT_RESULTS.md), [PRETRAIN_RESULTS.md](docs/PRETRAIN_RESULTS.md) |
| Unseen-map navigation (levels A, B, C) | Level B development maps: 1 to 6 of 64 for every run. Level C baseline of the start checkpoint: 71 of 168 (42%), mostly open routes. No gate evidence | [HELD_OUT_SPEC.md](docs/HELD_OUT_SPEC.md), [RANDOM_DISTRIBUTION_RESULTS.md](docs/RANDOM_DISTRIBUTION_RESULTS.md) |
| Large budget (1,015,808 added transitions, one seed) | Inconclusive by the frozen rule: `passages` 11, 12, 17, 23 of 64 along the curve (positive needed 24), medium 55 to 60, `passages-mid` 48, `passages-wide` and `gate-two` 64. Collisions on `passages` stay at 18 to 30 | [LARGE_BUDGET_RESULTS.md](docs/LARGE_BUDGET_RESULTS.md) |
| Large budget, 1,998,848 added transitions (one seed) | Positive by the frozen rule on pool 885000: `passages` 38 of 64 with 6 collisions (the 1M checkpoint scores 27 with 20), `passages-mid` 56, medium 54, `passages-wide` 64. Deterministic curve 16, 26, 48, 38; the drop from 48 to 38 is timeouts. One seed | [LARGE_BUDGET_2M_RESULTS.md](docs/LARGE_BUDGET_2M_RESULTS.md) |
| Three-seed replication of the 2M recipe | Positive by the frozen rule on pool 886000: stage 61 `passages` 42, 36, 39 of 64 (mean 39, start checkpoint 5), `passages-mid` 54 to 57, medium 49, 54, 55, `passages-wide` and `gate-two` 64. Collisions on `passages` 8, 16, 8 against the gate's 3 | [REPLICATION_2M_RESULTS.md](docs/REPLICATION_2M_RESULTS.md) |
| Level B and level C for the 2M checkpoints (stage 61, three seeds) | Level B inconclusive: 26, 17, 12 of 64 (mean 18.3, positive needed 20; earlier runs 1 to 6; start 1). Level C positive by the rule: 95, 108, 108 of 168 deterministic (start 71), but `courtyard` fell from 24/24 to 7 to 23 and `apartment`, `atrium` did not move. Against the sampled start (93) the gain is 12 to 20 episodes | [LEVEL_BC_RESULTS.md](docs/LEVEL_BC_RESULTS.md) |
| No-connectome control (edge-shuffled reservoir, matched fresh chain, 2 seeds per arm) | Chain check failed (fresh real arm 16.0 of 64 on `passages` against 28 needed; retained 36 to 42), so the comparison is a fresh-chain result only. There the shuffled arm is not worse: `passages` 25.5 against 16.0, `passages-mid` 51.0 against 41.5, level B 6.5 against 5.5, level C 86 against 79 of 168. No evidence that the wiring matters; the connectome contribution cannot be claimed | [CONNECTOME_CONTROL_RESULTS_C11.md](docs/CONNECTOME_CONTROL_RESULTS_C11.md) |
| Control at 4.88M transitions (C1.2, 2 seeds per arm) | Chain check fails by half an episode (real mean 27.5 of 64 on `passages`, needed 28; shuffled 21.0; retained 38.0). Comparison inconclusive; no cell shows an advantage of the real connectome (mid 51 vs 47, level B 9.5 vs 12, level C 98 vs 105.5). Seed spread (13 to 16 episodes) is as large as any difference | [CONNECTOME_CONTROL_RESULTS_C12.md](docs/CONNECTOME_CONTROL_RESULTS_C12.md) |
| Release gate | Not met | This file |

Best development candidate so far: `runs/training/phase1-pilot/seed442/stage-3.zip`. On a fresh pool with 64 episodes per cell: medium 57, passages-wide 14, passages-mid 37 and passages 17 (89%, 22%, 58% and 27%). It is a real policy and an outlier: five repeats of its recipe reached 7 to 13 of 32 on passages-mid. It gives up passages-wide to get the harder profiles.

**Update October 13:** after the three-seed replication, `passages` is 36 to 42 of 64 (about 60 percent) at 2M added transitions, with 8 to 16 collisions; the claim below should be read with this in mind and is revised once levels B and C are measured.

**Defensible claim today:** a learned policy with the full connectome in the loop reaches goals in new medium rooms (86 to 92 percent on fresh 64-episode pools), partly in partitioned rooms (about 20 percent on `passages`, 50 to 90 percent on easier profiles), and has no evidence on `large`, mazes or unseen families. The four-family gate is not met and no tested change moves it.

## 3. What worked, what failed, what we learned

Worked:

- Recovering the reference before training anything new.
- Graded maps with medium rooms kept in the mix. Training only on the hardest map gave no signal.
- Declaring every protocol before training, and keeping selection pools apart from report pools.
- Evaluation is repeatable to within one episode.
- The frozen medium-room regression suite: all three historical winners pass its amended rule, and the later candidates score above them.
- The resource guard (`scripts/resource_guard.py`) keeps the machine usable.

Failed:

- No profile beyond `passages-wide` reaches a useful rate, and none reaches the 81% gate.
- Plain PPO oscillated (Phase 1 control). The stabilization bundle held one seed and not the other.
- Memory did not replicate. A route-progress reward and more steps (experiment 2) gave nothing in their budgets.
- Many comparisons used one training run per condition, with effects smaller than the spread between runs.

Learned:

- The training run is the high-variance part: seeds from the same start differ by up to 18 episodes on one profile, and the same seed with a different decay schedule reversed the outcome.
- The policy often keeps one hard profile at the expense of another. This trade-off appears in all three phases.
- Training spread was measured (R1): five runs of one recipe differ by up to 11 episodes of 32 on passages-wide and 6 on passages-mid. A minority of runs land much higher: the pilot checkpoint scores 58% on passages-mid and 27% on passages on a fresh 64-episode pool, and no repeat came close.
- Measured since (October 11, three committee reviews and eight analyses): the reward is not the cause (an ideal route follower beats hovering at every route point); hard-map exposure in the R5 run was almost nil (64 to 127 episodes, controller stayed at 0.2); the 256 pooled features lose nothing compared with raw sensors; the 8 m rays contain the route direction (34 degrees on hard samples with 500 maps; 24 m rays reach 28); a supervised trunk encodes it to 42 degrees on new maps and still does not change flight under PPO.
- Evaluation mode matters: the pilot checkpoint scores 14 of 64 on passages-wide with deterministic actions (50 timeouts, no collisions) and 55 with sampled actions. Future protocols must declare the mode and report both.
- The route direction as an actor input is what works (36 and 39 of 64 on passages against 8 and 14 without it). It is a diagnostic: a student cannot read the certified route.
- Open hypotheses, not measured: a much larger budget (1M transitions or more) with a learning curve; behavior distillation from the route-aware policy (earlier imitation failed on `large`); memory and long-range sensing for `large` and mazes; the 52 of 64 gate looks unreachable on large and maze with 8 m rays and a memoryless policy (opinion of the committee, not a measurement).

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
- [x] Freeze the medium-room regression suite as a documented, reusable test ([MEDIUM_REGRESSION_SUITE.md](docs/MEDIUM_REGRESSION_SUITE.md))

Phase 0 is complete.

### Phase 1. Stable trainer: closed as negative for its exit criterion

- [x] Stabilization bundle implemented (pilot and run scripts)
- [x] Separate selection pools introduced (report pools still unopened)
- [x] Two-seed run with four evaluations ([PHASE1_RUN_RESULTS.md](docs/PHASE1_RUN_RESULTS.md))
- [x] Result recorded: seed 442 stable, seed 443 not, hardest profile not raised
- [x] Measure training variance directly: five runs of one recipe ([VARIANCE_STUDY_RESULTS.md](docs/VARIANCE_STUDY_RESULTS.md), action R1, done October 10)

### Phase 2. Randomized map distribution: not started

- [x] Parameter ranges and adaptive-difficulty rule written and committed ([MAP_SAMPLER.md](docs/MAP_SAMPLER.md))
- [x] Map sampler implemented with tests and a sample gallery (action R3, done October 10)
- [x] Level B region and level C family (synthetic architectural scenes, chosen by the user) defined and sealed in [HELD_OUT_SPEC.md](docs/HELD_OUT_SPEC.md) (action R4, done October 10)
- [x] Training run with three seeds (action R5, done October 11, negative: [results](docs/RANDOM_DISTRIBUTION_RESULTS.md))
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

Each action lists what it needs, an estimate with its basis, and what it unlocks. Estimates come from measured timings: one training stage of 32,768 transitions takes 65 to 95 s; one seven-cell evaluation of a checkpoint on one pool set takes 5 to 7 min under the resource guard; a fourteen-cell evaluation takes 8 to 10 min. Code-writing estimates have no measured basis and carry more uncertainty. The two code actions done so far (R2, R3) took far less than estimated, so code estimates are pessimistic, while training and evaluation estimates have held within 10 to 20 percent.

| ID | Action | Needs | Estimate | Compute | Unlocks |
| --- | --- | --- | --- | --- | --- |
| R1 | Done October 10 (53 min against 60 estimated). Passages-wide ranged over 11 episodes, so the strict rule applies | Not applicable | Measured | Not applicable | Decision D1: at least 3 seeds and 64 episodes per comparison, best-of-N with a report pool |
| R2 | Done October 10 (under 25 min by the clock; estimate was 30 min). Frozen medium-room regression suite, `scripts/regression_medium.py` | Not applicable | Measured: 4 min per checkpoint, 5 checkpoints | Light | Closes Phase 0. Every Phase 2 candidate runs it before promotion |
| R3 | Done October 10. Measured by the machine clock: about 5 minutes between the end of the previous step and the commit, against a 1.5 to 2 h estimate. Sampler, adaptive controller, 14 tests, gallery | Not applicable | Measured | Almost none | R4, R5 |
| R4 | Done October 10. Level C = synthetic architectural scenes, sealed with reserved seeds. Evaluation tool and tests written | Not applicable | Measured: under 15 min | None | R5, Phase 5 |
| R5 | Done October 11. Negative by the frozen rule; the difficulty controller stayed at 0.2 to 0.25, so training saw mostly easy maps ([results](docs/RANDOM_DISTRIBUTION_RESULTS.md)) | Not applicable | Measured: 3 h 10 min against about 2 h estimated | Not applicable | R5b: a version with real difficulty |
| D1 | Done October 11. Committee reviews (three rounds), light audit, 601 confirmation, collision anatomy, feature and synthetic probes. See [EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md) | Not applicable | Measured | Not applicable | Diagnosis: information at decision time, not reward or readout |
| D2 | Done October 11. Privileged-waypoint diagnostic, two seeds per arm: partial by the rule (37.5 against 11 of 64) | Not applicable | Measured: 56 min | Not applicable | Information matters; not a student |
| D3 | Done October 11. Auxiliary head and privileged critic, three seeds: negative (+2.3 and +0.7 of 64) | Not applicable | Measured: 2 h 43 | Not applicable | Closes training-only route signals at 262k |
| D4 | Done October 11. Supervised pretraining of the actor trunk then PPO, three seeds: gate passed, PPO negative (+2.0 of 64) | Not applicable | Measured: 1 h 16 | Not applicable | Representation is not the bottleneck |
| B1 | Done October 12. Inconclusive by the frozen rule: `passages` 23 of 64 (positive needed 24, negative 16 or fewer), medium 59, curve 11, 12, 17, 23 ([results](docs/LARGE_BUDGET_RESULTS.md)) | Not applicable | Measured: 41 min training (79 s per stage, not 65) and 24 min evaluation, 65 min in all | Not applicable | Decision D5: three seeds, or close the scope |
| B2 | Done October 12. Positive by the frozen rule: `passages` 38 of 64 (threshold 28, 11 above the 1M checkpoint on the same pool), medium 54 ([results](docs/LARGE_BUDGET_2M_RESULTS.md)) | Not applicable | Measured: 77 min training (65 to 81 s per stage), 29.5 min evaluation | Not applicable | B3: replicate with three seeds |
| B3 | Done October 13. Positive by the frozen rule: `passages` 42, 36, 39 of 64 on seeds 801, 851, 901 (mean 39, threshold 28; start 5), medium 49, 54, 55 ([results](docs/REPLICATION_2M_RESULTS.md)) | Not applicable | Measured: 3 h 33 against 3 h 25 estimated (82 min per training, 50 min evaluation) | Not applicable | B4: level B and C once |
| B4 | Done October 13. Level B inconclusive (mean 18.3 of 64, one episode under the threshold), level C positive (mean 103.7 of 168, start 71), with a `courtyard` regression ([results](docs/LEVEL_BC_RESULTS.md)) | Not applicable | Measured: 53 min against 1 h 30 estimated (level C runs 12 to 17 min each) | Not applicable | Decision D6: next lever |
| C1.0 | Done October 13. Gate passed: fresh real-connectome arm 61 of 64 on medium after 885k transitions (gate 40); edge-shuffled arm 54, sampled 60 against 59 ([results](docs/CONNECTOME_CONTROL_RESULTS_C10.md)) | Not applicable | Measured: about 38 min training with both arms in parallel (CPU mean 66%, peak 90%) and 12 min evaluation | Not applicable | C1.1 protocol |
| C1.1 | Done October 14. Chain check failed (real arm 16.0 on `passages`, needed 28); no evidence of a wiring effect, shuffled arm nominally higher (25.5) ([results](docs/CONNECTOME_CONTROL_RESULTS_C11.md)) | Not applicable | Measured: training 3 h 28 as estimated, evaluation 1 h 25 against 45 min estimated (eight level C passes under six processes) | Not applicable | Decision D7 |
| C1.2 | Done October 14. Chain check failed by 0.5 episode (real mean 27.5, needed 28); comparison inconclusive; no advantage of the real connectome on any cell ([results](docs/CONNECTOME_CONTROL_RESULTS_C12.md)) | Not applicable | Measured: 4 h 06 against 4 h 10 estimated (training 78 and 81 min per pair, evaluation 87 min) | Not applicable | Decision D8 |
| C1.P | Planner reference on level C (168 episodes, planner-1.4-exp.3, same headings as the learned evaluation) and the retained candidate on `large` and `maze` (pools 892000 and 893000, 32 episodes per cell, both modes), to complete the four-family table. The planner cannot run on medium, `passages` or level B; a planner run on `large` and `maze` needs a runner that this stage does not build (development figures are cited). Protocol committed ([PLANNER_REFERENCE_PROTOCOL.md](docs/PLANNER_REFERENCE_PROTOCOL.md)); **not launched, waiting for the user's go** | Go from the user | About 70 min (range 55 to 100): planner probe of 8 episodes took 176 s (22 s per episode, 168 episodes about 62 process-minutes); learned `large` about 23 s and `maze` about 59 s per episode in 4-episode probes | CPU 70 to 90%, up to 5 processes, VRAM up to about 10 GiB | The reference for the claim and the large and maze rows of the four-family table |
| R6 | Memory retest: 3 seeds x 2 conditions, 64 episodes per cell, final checkpoint only | R3 advised | About 2 h (no measured basis for 64 episodes) | CPU about 55% | A decision on memory |

Recommended order: R1 to R5, D1 to D4, B1 to B4 and C1.0 to C1.2 are done. The connectome-contribution claim is not supported and cannot be settled cheaply (about 8 seeds per arm would be needed to detect a 10-episode difference). Next (D8, section 6): the planner reference C1.P (level C, `large`, `maze` only), then the release with limitations (Phase 6).

R1 and R3 can overlap. Two training or evaluation jobs must not run at once, because one training job uses about half of the CPU.

## 6. Decision points

| After | Question | If yes | If no |
| --- | --- | --- | --- |
| R1 (decided October 10) | Is the range of passages-mid or passages-wide across runs at least 10 episodes of 32? | Yes (passages-wide 11). Every later comparison needs at least 3 seeds and 64 episodes per cell. Use best-of-N with a separate report pool | Not applicable |
| R5 | On two seeds, does each development cell reach 26 of 32 with at most 3 collisions, and medium stay at 21 or more? | Move to Phase 4 (target families) | Change the representation before more training: decide among a longer-range sensor, a memory retest (R6), or planner imitation. The user decides, because imitation shifts weight from RL |
| R5 | Does any result appear on level B or C? | Report it with intervals. It is the first evidence for the objective | Report that no unseen-map evidence exists yet |
| B1 | Does `passages` reach 24 of 64 (twice the 262k control) with medium at 48 or more after 1M transitions? | Repeat with three seeds, then level B and C once | At 16 or less: close the scope. Bounded claim: zero-shot in medium rooms, partial in partitioned rooms. Run C1 and prepare the release with limitations |
| B1 (October 12), D5 | Did the 1M run reach the rule? | Not applicable: `passages` 23 of 64 against 24, medium 59. Inconclusive. Rising curve, collisions unchanged (22). Open decision D5: repeat with three seeds before closing the scope, or close it now | Not applicable |
| B2 (October 12) | Did the 2M run reach the rule? | Yes: `passages` 38 of 64, medium 54, 11 above the 1M checkpoint on the same pool. Open: collisions 6 against the 3 allowed; one seed. Next: B3, three-seed replication | Not applicable |
| B3 (October 13) | Does the 2M effect replicate on other seeds? | Yes: mean `passages` 39 of 64, every seed 36 or more, medium 49 or more. Next: B4, level B and C once | Not applicable |
| B4 (October 13), D6 | Does the 2M effect reach level B and C? | Level B inconclusive (18.3 of 64 against 20), level C positive (103.7 of 168 against 88) with uneven scenes. Open decision D6: the next lever | Not applicable |
| C1.1 (October 14), D7 | Does the real connectome beat the edge-shuffled control? | No evidence: the shuffled arm is at least as good in every cell (differences below 10 episodes, inside seed spread). The fresh chain reaches only 16 to 26 of 64 on `passages` against 36 to 42 retained, so the check on the chain failed. Open: C1.P and the release, or strengthen the control | Not applicable |
| C1.2 (October 14), D8 | Does a larger budget let the control settle the connectome question? | No: the fresh real arm reaches 27.5 of 64 on `passages` (needed 28), shuffled 21.0; seed spread equals the differences; no cell favors the real connectome. Settling it would take about 8 seeds per arm. Open: C1.P and the release, or stop the control here | Not applicable |
| Phase 4 | Is a held-out family result at or above half the development rate? | Proceed to Phase 5 | Keep training and revisit the representation |

## 7. Rules for every iteration

- Commit the protocol (design, pools, acceptance rule, positive result) before training or evaluation. Report negative results with the same detail as positive ones.
- Change one factor, or run a declared control arm. Use at least two seeds for any claim, and expect between-seed spread of 10 to 18 episodes until R1 says otherwise.
- Choose checkpoints on a selection pool that the report never uses. The report and reserved pools stay unopened until Phase 5.
- Never overwrite aliases, completed runs or controller sources. Record source and checkpoint hashes.
- Resources: the PC must stay usable. Brief CPU peaks are accepted, sustained 100% is not. The GPU has no limit. Evaluation fan-out goes through `scripts/resource_guard.py`. Run one training job at a time. **Since October 13 the user allows up to 95 percent of CPU and RAM** (never above), so trainings may run in parallel and evaluation may use up to 6 processes; the guard defaults stay at the old limits and are raised per run with the `RG_*` environment variables (`scripts/resource_guard.py`).
- Give a time estimate with its basis before each iteration. Update the estimate when a measurement disagrees.
- No planner action in any evaluated policy. Full connectome in every policy.

## 8. Pools registry

| Pool | Seeds | Use | Status |
| --- | --- | --- | --- |
| Historical final pools | Recorded in `runs/suites/consumed` | Earlier final tests, including the 0/64 large-room pool | Consumed. Never a test again |
| Medium regression pool A (validation of the 50/64 policy) | 100000 to 100031 | Frozen regression suite | Inspected |
| Medium regression pool B | 840000 to 840031 | Frozen regression suite | Inspected |
| Medium regression pools C and D | 860000 to 860031 and 861000 to 861031 | Frozen regression suite. Also Phase 1 and 3 selection pools for medium | Inspected. Do not select on them for medium performance |
| Gate pools | 830000 to 830031 | Development | Inspected |
| `passages-wide` | 830000 to 830031 | Development | Inspected |
| `passages-mid` | 850000 to 850031 | Development | Inspected |
| `passages` | 810000 to 810031 | Development and failure classification | Inspected |
| Selection pools | 860000 to 865000 (one range per cell) | Choosing checkpoints (Phases 1 and 3) | Used for selection only |
| Report pools | Not yet drawn | Final Phase 1 style reports | Reserved, unopened |
| Level A report | 940000 to 949999 | Report pool | Reserved, unopened |
| Confirmation and comparison pools | 880000 to 880063; 882000 to 882063 | Fresh-pool confirmations, student comparisons (882000 reused for the pretraining comparison). Selected nothing | Inspected. 880000 also drove the committee analyses: not a selection set from now on |
| Probe pools | 881000 to 881063 (rollouts), 895000 to 895699 (synthetic poses), 896000 to 896799 (pretraining data) | Offline probes and supervised pretraining | Used. Never evaluation pools |
| Large-budget test pool (B1) | 884000 to 884063 | Curve evaluation of the 1M run, `passages` and medium, both modes ([protocol](docs/LARGE_BUDGET_PROTOCOL.md)) | Inspected October 12 (B1 results). Selects nothing |
| 2M test pool (B2) | 885000 to 885063 | Curve evaluation of the 2M run and of the B1 final checkpoint, `passages` and medium ([protocol](docs/LARGE_BUDGET_2M_PROTOCOL.md)) | Inspected October 12 (B2 results). Selects nothing |
| 2M replication pool (B3) | 886000 to 886063 | Stages 46 and 61 of seeds 801, 851, 901 and the start checkpoint, `passages` and medium (final stage also mid, wide, gates) | Inspected October 13 (B3 results). Selects nothing |
| C1.2 pool | 888000 to 888063 | `passages`, `passages-mid`, `passages-wide`, medium for the four extended control runs and the three retained seeds | Inspected October 14 (C1.2 results). Selects nothing |
| C1.P pools | `large` 892000 to 892031, `maze` 893000 to 893031 | Retained candidate on large and maze rooms; level C development headings for the planner | Declared October 14, unopened. Selects nothing |
| C1.0 pool | 887000 to 887063 | Medium rooms: retained start and the two fresh phase 1 arms | Inspected October 13 (C1.0 results). Selects nothing |
| Level B region, development | Held-out sampler, 950000 to 959999 | Look at progress, not for selection | Drawn: 950000 to 950063 inspected for every R5 and student run |
| Level B region, final | Held-out sampler, 960000 to 969999 | Final assessment | Reserved, unopened |
| Level C scenes, development headings | 900000 and above | Baseline measurements only before Phase 5, with one declared exception (B4) | Used twice: baseline of the start checkpoint (71 of 168) and the three 2M checkpoints in B4 (LEVEL_BC_PROTOCOL.md, results in LEVEL_BC_RESULTS.md) |
| Level C scenes, final headings | 970000 to 979999 | Final assessment | Reserved, unopened |

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
| B1 final checkpoint (1M added transitions, seed 801) | `runs/training/large-budget/seed801/stage-31.zip` | `0896b5fbe22f9c10` |
| B2 final checkpoint (2M added transitions, seed 801) | `runs/training/large-budget-2m/seed801/stage-61.zip` | `3a4150b59b5fc894` |
| B3 final checkpoint, seed 851 | `runs/training/large-budget-2m/seed851/stage-61.zip` | `fc1b2c69068ac72e` |
| B3 final checkpoint, seed 901 | `runs/training/large-budget-2m/seed901/stage-61.zip` | `29ac1bcf11652646` |
| C1.0 fresh phase 1, real connectome, seed 1001 | `runs/training/connectome-control/phase1-real1001/stage-27.zip` | `05be0cc88b1b7ae3` |
| C1.0 fresh phase 1, edge-shuffled, seed 1001 | `runs/training/connectome-control/phase1-shuffled1001/stage-27.zip` | `994d24760718d037` |
| C1.1 phase 2 checkpoints (stage 61): real 1001, real 1051, shuffled 1001, shuffled 1051 | `runs/training/connectome-control/phase2-<arm><seed>/stage-61.zip` | `d1cf2ca4e3c3c535`, `b2e6a0f459ce41b8`, `47ab8dc1c288566f`, `918cbc6fbf0c3464` |
| C1.2 phase 3 checkpoints (stage 61): real 1001, real 1051, shuffled 1001, shuffled 1051 | `runs/training/connectome-control/phase3-<arm><seed>/stage-61.zip` | `89afcdc35f385c56`, `a7e549d4c9bf8d93`, `b85f2e42c67fea4a`, `9ca7652aa583a5e1` |

Detailed evidence copies live in `private/reference-recovery-1-evidence/`. The experiment index is [docs/EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md).

## 10. How to keep this file current

After every iteration, in the same commit as its results document: update the date and commit in the first line, tick or add items on the board, change the status table in section 2 only if a number changed, add a row to the experiment log, and revise the estimates in section 5 if a timing was off. Keep the protocol and the results in their own documents, and link them from here.
