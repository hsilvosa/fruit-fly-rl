# Results

The latest experimental planner-1.2 preserves contextual mapping while using separate clean neural ranges for braking. In fresh frozen paired development, both planner-1.1 and planner-1.2 reached 15/16 goals with zero collisions and one timeout (Wilson 95% interval 71.7–98.9%). planner-1.2 also resolved retained false stopping and contacts, but did not improve the paired success rate. Learned large-room navigation and the independent-final target remain unresolved. [Complete latest evidence](evidence/planner-dual-v65-results.md) and [per-room outcomes](evidence/planner-v65-development-results.md).

The earlier frozen [paired planner development](evidence/planner-v60-development-results.md) reached **14/16 goals for planner-1.1**, versus **12/16 for planner-1.0**, with no collisions. planner-1.1 had two timeouts and a Wilson 95% interval of 64.0–96.5%. Twelve rooms succeeded in both arms, two only in planner-1.1, and two in neither. The task, initial layouts, graph, and source contracts matched. This separate prospective development check consumed 111,360 physical verification transitions and no training or reserved test. It does not establish the independent-final 80% target or biological benefit.

The [planner-1.1 follow-up](evidence/planner-followup-v57-v60.md) reached all three already inspected planner-1.0 failures without collisions or timeouts. Isolated speed and clearance checks exposed a regression when combined unconditionally; planner-1.1 applies broader clearance recovery only after search saturation. This tuned 3/3 does not revise planner-1.0's historical 13/16 prospective development score. No training or reserved-test evaluation was performed, and planner-1.0 remains the demo default. The earlier [planner-1.0.1-exp.1 correction](evidence/planner-timeouts-v56-results.md) retains its separate 1/3 result.

The observed-map planner-1.0 now navigates `large` rooms: 8/8 arrivals on reused optimization maps and 13/16 in prospective development, without collisions and with three development timeouts. This is explicit planning from full-connectome activity, not a learned movement policy. Student v34 retains its 3/8 result; reliable learning remains unresolved. The [results and limits](evidence/observed-map-v55-results.md) distinguish the two. Original aliases and the reserved test remain intact.

The [resolution history](NAVIGATION_RESOLUTION.md) explains the original problem, learning and perception attempts that were insufficient, corrected blockages, and the final solution. The operational improvement combines observed-map memory, correct reference advancement, and braking in the requested three-dimensional direction; it does not turn the planner's 13/16 into a PPO result.


Navigation performance is separate from implementation correctness and anatomical fidelity. The full fixed MaleCNS v1.0 graph was retained in these experiments; its synapses were not optimized. Outcomes do not establish a biological advantage.

## Latest planner experiments

All rows below use the original `large` profile: 48 x 48 x 16, 112 obstacles and five narrow passages. Every row is a separate frozen paired **development** cohort, not a reserved final test. Compare arms within a row; differences across cohorts do not establish a ranking. [Revision mapping](CONTROLLER_VERSIONS.md) connects these names to the unchanged historical records.

| Cohort | Baseline | Candidate | Baseline goals / collisions / timeouts | Candidate goals / collisions / timeouts | Conclusion |
| --- | --- | --- | --- | --- | --- |
| 9500000–9500015 | planner-1.0 | planner-1.1 | 12 / 0 / 4 | 14 / 0 / 2 | Two added goals, no lost baseline goals. [Evidence](evidence/planner-v60-development-results.md) |
| 10000000–10000015 | planner-1.1 | planner-1.2-exp.1 | 15 / 1 / 0 | 13 / 2 / 1 | Clean ranges alone regressed. [Evidence](evidence/planner-v61-development-results.md) |
| 11000000–11000015 | planner-1.1 | planner-1.2-exp.4 | 15 / 0 / 1 | 12 / 0 / 4 | Momentum braking corrected known contacts but regressed fresh completion. [Evidence](evidence/planner-v64-development-results.md) |
| 13000000–13000015 | planner-1.1 | planner-1.2 | 15 / 0 / 1 | 15 / 0 / 1 | Identical paired outcomes; no success-rate advantage measured. [Evidence](evidence/planner-v65-development-results.md) |

The latest paired cohort used 55,984 physical transitions per arm, 111,968 total, with zero training transitions or optimizer updates. Both 15/16 estimates have Wilson 95% intervals of 71.7–98.9%. These inspected rooms are now design cases for a successor, not untouched evidence for future tuning.

Separately, planner-1.2 reached four retained collision/control goals and corrected the stationary room 9500001 at step 1,782. Retained detour 9500014 and the shared fresh failure 13000013 still timed out. Offline trace inspection found continuing movement, no sampled second-half momentum guards, small pose error, repeated reference-direction reversals, and mostly unknown or ambiguous final route points. These clues support further route/frontier-execution diagnosis, not a proven causal solution. [Detailed report and failure figures](evidence/planner-dual-v65-results.md#offline-inspection-of-the-remaining-timeouts).

Distance and dual readouts each passed an earlier separate 128-transition, one-PPO-update verification smoke with finite losses and compatible reload; those temporary weights were deleted. That verifies the learning pipeline, not learned navigation. The naming migration adds no training, flights, or new performance measurement and leaves the default and original aliases unchanged. Learned large-room navigation and the independent-final objective remain unresolved.

## Latest original-large corrections

The [panoramic v7 report](evidence/panoramic-neural-v7-results.md) records 98,304 additional transitions, a saved compatible checkpoint and a final-report path lookup failure. Its separately recorded recovery development score was 0/8, with eight collisions. The [broader coverage correction](evidence/panorama-coverage-v8-results.md) completed another 301,056 transitions and also recorded 0/8 in reused development, with eight collisions. Neither run consumed a reserved final test or promoted an alias. Completed substantive use through coverage v8 is 1,267,712 transitions. Directional attention and look-ahead guidance are further corrections whose results must be recorded separately.

The [directional and look-ahead records](evidence/directional-and-lookahead-results.md) add 32,768 and 163,840 transitions respectively. Their reused development scores remain 0/8. The final look-ahead checkpoint timed out in all eight rooms; the teacher-only and sparse-pooling diagnostic candidates collided in all eight. Completed substantive use through look-ahead v10 is 1,464,320. Navigation remains unresolved, and the independent final pool remains unconsumed.

| Intervention | Added transitions | Development goals | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Current-feature matched control | 65,536 | 0/8 | 2 | 6 |
| Temporal-feature matched arm | 65,536 | 0/8 | 1 | 7 |
| Obstacle-aware reward pilot | 32,768 | 0/8 | 1 | 7 |
| Guided initialization and PPO | 40,960 | 0/8 | 8 | 0 |
| Visible fan and student-only correction | 65,536 | 0/8 | 4 | 4 |
| Separate critic history | 65,536 | 0/8 | 8 | 0 |
| Full-rollout PPO guard | 32,768 | 0/8 before and after | 8 | 0 |
| Spatial neural readout, post-run verification | 98,304 | 0/8 | 6 | 2 |

These reused development layouts do not constitute an independent final test. The guided teacher's eight optimization goals are not student navigation results. The initial 524,288 cap was exhausted. Subsequently authorized v2, v3 and v4 corrections bring completed substantive use to 688,128. The spatial-neural v5 worker consumed a further 98,304 transitions before a post-save precision assertion failed. Completed substantive training use is 786,432; its separately completed development verification added no training. No new model was promoted, the original six aliases retained their hashes, and no reserved final pool was consumed. [Guided results](evidence/guided-navigation-v1-results.md), [reward-only results](evidence/route-progress-correction-v1-results.md), and [memory results](evidence/brain-memory-comparison-v1-results.md) report the failures without claiming a successful fix.

The [sensors-v5 correction](evidence/visible-fan-v5.md) resolves a measured early-observation ambiguity and is verified through actual full-connectome activity. Its authorized training completed with 0/8 autonomous validation goals, four collisions and four timeouts. The observation correction did not establish successful navigation. [Verified v2 results](evidence/guided-navigation-v2-results.md) retain supervised and autonomous counts separately.

## Geometry comparison

The passage-mastery v2 comparison completed 524,288 added transitions. Validation selected baseline seed 42, round seven (114,688 lifetime transitions). On the single-opening gate-long final pool it reached 61/64 goals (95.3%), zero collisions and three timeouts; Wilson 95% interval 87.1-98.4%. The untrained control reached 0/64. This establishes performance on the simpler single-opening distribution, not the historical large rooms. Original launcher aliases were preserved. See [the verified completion record](evidence/passage-mastery-v2-results.md).

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

### Shared target validation

All four runs use the same 32 fixed `large` validation layouts. The experiment budget counts all training transitions, whereas selected lifetime transitions describe only the checkpoint retained by validation.

| Method | Seed | Added transitions | Selected lifetime transitions | Goals / 32 | Collisions | Timeouts |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 42 | 131,072 | 0 | 0 | 1 | 31 |
| baseline | 73 | 131,072 | 0 | 0 | 0 | 32 |
| curriculum | 42 | 131,072 | 131,072 | 0 | 1 | 31 |
| curriculum | 73 | 131,072 | 0 | 0 | 0 | 32 |

All selected validation candidates have zero goals. Selection includes the initial controller, so a zero-transition checkpoint may rank ahead of trained policies that collide more often. This is failure to demonstrate learned navigation in the target rooms, rather than a successful trained policy. Training success in easier profiles does not establish validation generalization. The selected ZIP is byte-identical to its frozen initialization. The method ranking used ending distances 44.2234894709623 (baseline) and 44.2234894695337 (curriculum), with equal success and collision rates. Such a numerical difference is not evidence of a curriculum effect. The declared rule was applied without changing it after observing results.

### One reserved final assessment

Only the validation-selected method/seed/checkpoint and an untrained control were final-tested on the 64 frozen target layouts. The selected checkpoint reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The untrained control reached 0/64 (0.0%), with 1 collision and 63 timeouts; interval 0.0–5.7%. This pool is now consumed. There was no paired final comparison of both training methods.

The complete comparison, including initialization, training, validation and final assessment, took 206.7 minutes. It is not a pure training throughput measurement. The source revision was `ec7e90193ee60d9b413f05e42058c264306f4ddb`. Both initialization seeds began with zero transitions and empty optimizer state, all eight round loss reports were finite, and the frozen source/configuration/suite hashes passed the completion audit.

### Curriculum exposure and training outcomes

The schedule uses reset mixtures 75/20/5%, 20/60/20% and 10/20/70% for `open`/`passages`/`large`, according to global transition progress. It changes profiles only on episode reset. These are reset probabilities, not guaranteed transition fractions. Counters below describe sampled training episodes; an episode crossing a round boundary can remain incomplete and is not counted as a terminal outcome.

| Seed | Round | Profile | Transitions | Training goals | Collisions | Timeouts |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 42 | 1 | open | 51,217 | 20 | 39 | 17 |
| 42 | 1 | passages | 9,895 | 0 | 41 | 0 |
| 42 | 1 | large | 4,424 | 0 | 13 | 0 |
| 42 | 2 | open | 8,168 | 10 | 2 | 1 |
| 42 | 2 | passages | 16,698 | 0 | 15 | 4 |
| 42 | 2 | large | 40,670 | 0 | 16 | 3 |
| 73 | 1 | open | 47,970 | 17 | 48 | 13 |
| 73 | 1 | passages | 13,620 | 0 | 43 | 0 |
| 73 | 1 | large | 3,946 | 0 | 4 | 0 |
| 73 | 2 | open | 9,553 | 4 | 1 | 4 |
| 73 | 2 | passages | 21,315 | 0 | 21 | 6 |
| 73 | 2 | large | 34,668 | 0 | 38 | 1 |

Full reset counts, stage offsets, original alias hashes and aggregate measurements are preserved in [machine-readable geometry evidence](evidence/geometry-v1-results.json). Detailed source copies, launch records, TensorBoard logs, checkpoints and original evidence remain local and ignored. No launcher alias was promoted.

## Earlier dense-room results

Each row summarizes an already completed, validation-selected final assessment on its own fresh pool. All these pools are consumed. Rooms, initialization and lifetime training differ across experiments; this table is historical context, not a paired ranking of interventions. The profiled geometry comparison is a harder task and is not directly comparable with these dense-room counts.

| Experiment | Final goals | Collisions | Timeouts | Wilson 95% interval |
| --- | --- | ---: | ---: | --- |
| Dense adaptation | 43/64 (67.2%) | 15 | 6 | 55.0–77.4% |
| Warm-start sensor comparison | 50/64 (78.1%) | 5 | 9 | 66.6–86.5% |
| Fresh sensor comparison | 35/64 (54.7%) | 20 | 9 | 42.6–66.3% |
| Near-goal curriculum comparison | 45/64 (70.3%) | 15 | 4 | 58.2–80.1% |
| Observed-ray risk comparison | 48/64 (75.0%) | 16 | 0 | 63.2–84.0% |

The original coordinated dense launcher separately reached 43/64 goals, with 11 collisions and 10 timeouts. Its weights and metadata remain preserved. Later selections were saved separately. The near-goal curriculum and tested risk penalty did not beat their respective normal-training controls under their declared validation rankings; only each winner was final-tested.

## Historical validation selections

Each table uses one shared validation pool within that experiment. Pools differ across experiments. These are selected checkpoint outcomes, not separate final tests. Two initialization seeds do not establish broad seed robustness.

### Warm-start sensor comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| v2 | 42 | 23/32 |
| v2 | 73 | 21/32 |
| v3 | 42 | 19/32 |
| v3 | 73 | 21/32 |
### Fresh sensor comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| v2 | 42 | 17/32 |
| v2 | 73 | 21/32 |
| v3 | 42 | 24/32 |
| v3 | 73 | 21/32 |
### Near-goal curriculum comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| baseline | 42 | 27/32 |
| baseline | 73 | 26/32 |
| curriculum | 42 | 23/32 |
| curriculum | 73 | 26/32 |
### Observed-ray risk comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| baseline | 42 | 27/32 |
| baseline | 73 | 22/32 |
| risk | 42 | 26/32 |
| risk | 73 | 22/32 |

Warm-start sensor validation selected v2 seed 42, the fresh sensor comparison selected v3 seed 42, and both near-goal and risk comparisons selected baseline seed 42. The chosen final results appear above; alternate methods were not final-tested as a paired comparison.

## Interpretation and next work

The [geometry failure diagnosis](GEOMETRY_DIAGNOSIS.md) records a bounded check of retained validation rooms: the unchanged earlier controller reproduced 3/4 original-room goals but reached 0/4 on new large rooms. The legacy world matched its frozen implementation over 480 transitions. The review identifies progression without passage mastery and selection of initialization after all trained target candidates failed. It does not establish a single causal explanation or reuse the final pools.

The independent large-room 80% target remains unmet. Single-opening navigation has since been measured at 61/64 on its final pool, while planner-1.0 reached 13/16 in prospective large-room development. These are different tasks and controller families. Reliable learned large-room navigation remains unresolved; [the roadmap](../ROADMAP.md) orders planner diagnosis, fresh assessment, student learning, and progressive difficulty. Any later tuned final assessment requires a new independent pool and declared budget.

[Mathematics](MATHEMATICS.md) specifies formulas and optimizer settings. [Geometry protocol](GEOMETRY_CURRICULUM.md) defines maps, clearance certificates and reset mixtures. [Verification](VERIFICATION.md) describes implementation and publication checks without treating passing tests as learning evidence.


# Timeout correction pilot results

The 32,768-transition pilot completed on 2026-10-04T08:34:44.312907+00:00. It included exactly 16,384 transitions on the unchanged original large target. It retained live episodes across four chunks, used gamma=0.9995 in PPO and its rollout buffer, failure-terminal deadline handling and the sensors-v4 clock. The other 16,384 transitions came from the fixed stage-four curriculum mixture. All optimizer losses were finite.

| Development outcome | Before | After |
| --- | --- | --- |
| Goals | 0/4 | 0/4 |
| Collisions | 3/4 | 1/4 |
| Timeouts | 1/4 | 3/4 |
| Mean end distance | 36.82 | 32.54 |
| Mean idle fraction | 0.0267 | 0.0209 |

The same four optimization-layout seeds were measured before and after training. These are development diagnostics, not held-out validation or a final test. The before policy had already been transferred to sensors v4, so this is not a clean comparison with the old sensors-v3 controller. It cannot attribute changes to individual interventions or demonstrate generalization. Fewer collisions and smaller end distance did not produce any arrivals. The navigation issue is unresolved.

The target environments completed five training episodes: zero successes, two collisions and three timeouts. Only three target timeout penalties were observed within this budget. This is actual target exposure but little complete-episode learning experience. Adding exposure and fixing learning semantics alone did not resolve the repeated-turning failure in this pilot.

A subsequent full-graph counterfactual changed only the clock from zero to one in the four initial development worlds. Relative pooled-feature shift was 32.72 percent and mean absolute action change was 0.1395. The clock was added to an already-trained controller through a new projection; preserved archive bytes do not mean preserved flight behavior. This newly measured transfer disruption needs calibrated verification before another pilot. It does not explain the original sensors-v3 zero-success results, which preceded the clock.

The complete frozen source manifest matched after training. All six original alias files and the original source ZIP and metadata retained their initial hashes. No alias was promoted. Detailed before/after episodes, source hashes, losses and exposure counters are in private artifacts and runs/training/timeout-correction-pilot-v1/status.json. The original independent final test remains unused. No training process remains running.

Cumulative substantive added transitions are 319,488 of the earlier 524,288 budget, leaving 204,800. Separate smoke verification remains excluded. The last checkpoint is runs/training/timeout-correction-pilot-v1/round-4/policy.zip; it is not a successful navigation model.


[Verified critic-isolation v3 results](evidence/guided-navigation-v3-results.md) bring cumulative substantive use to 655,360. The subsequent guarded-PPO protocol completed its 32,768-transition cap with zero of eight development goals, as recorded below.


## Guarded PPO v4

The 32,768-transition correction completed with 0/8 original-large development successes both before and after training, eight collisions and no timeouts. The full-rollout KL guard retained seven updates within its limits; this did not solve navigation. Cumulative substantive transitions: 688,128. No reserved test or alias promotion. See [verified results](evidence/guarded-navigation-v4-results.md).


## Spatial neural v5

The full 98,304-transition training cap was consumed. Student-only optimization rounds reached no goals, with 143 then three collisions; teacher fragments reached 19 goals from privileged training starts. All supervised losses were finite. The worker failed a CPU/CUDA precision assertion after saving the final checkpoint. Saved tensors match exactly, and disabling convolution TF32 brings numerical predictions within the existing tolerance. Its separately completed development validation reached 0/8 goals, with six collisions and two timeouts, using frozen sources and unchanged weights. No final test or promotion. Completed substantive ledger: 786,432. [Evidence](evidence/spatial-neural-v5-results.md).


## Panoramic correction and waypoint v6 result

The waypoint v6 batch completed 81,920 new transitions, with finite losses and compatible reload, but autonomous validation on original `large` rooms remained at 0/8: eight collisions and no timeouts. Completed substantive training totals 868,352 transitions. Original aliases and the source checkpoint remain intact. The reserved test was not used, and navigation remained unresolved at this stage.

The [verified results](evidence/neural-waypoint-v6-results.md) and [control and coverage diagnosis](evidence/neural-waypoint-v6-diagnostics.md) are retained. The next correction uses panoramic vision measured around the body and complete guided flights from original states. Its controller receives only neural activity; the hidden route labels data only during training.
The [panoramic v7 protocol](evidence/panoramic-neural-v7-plan.md) sets a limit of 98,304 new transitions, 12,288 supervised updates, and a single development validation. It starts a new controller because dimensions change, preserves all previous checkpoints, and does not consume the reserved test.

## Completion of the panoramic corrections

Batches v8, v9, v10, and v12 finished and added 505,856 transitions. The latest autonomous assessment on reused development maps reached 0/8 goals, with one collision and seven timeouts. Completed substantive training totals 1,472,512 transitions. Navigation in the original large maps remained unresolved; the reserved test was not used and original aliases were not promoted. The [two-hour window report](evidence/two-hour-navigation-results.md), its checkpoints, and experimental launcher `launch-panorama.ps1` are retained. Work paused at the requested deadline, October 4 at 22:40:52 Madrid time.

## Distance-stable readout comparison, October 5

A known false-stop correction succeeded on its stationary design room but regressed the subsequent frozen paired development suite. On sixteen new rooms, planner-1.1 reached 15/16 goals with one collision and no timeouts (Wilson 95% interval 71.7–98.9%); planner-1.2-exp.1 reached 13/16 with two collisions and one timeout (57.0–93.4%). Thirteen rooms succeeded in both, two only in planner-1.1, and one in neither. This supports retaining planner-1.1 over planner-1.2-exp.1 on this measured suite, rather than promoting the range correction as a generally improved controller.

The two arms used 105,488 physical transitions in total, zero training transitions, and no reserved-test access. Original aliases, frozen sources, graph-data/projection contracts, and initial layout hashes passed. Different readouts were explicitly declared. The suite is now inspected development evidence and cannot be reused as fresh selection evidence for a tuned successor. See [per-room outcomes](evidence/planner-v61-development-results.md) and [known-case diagnosis](evidence/planner-readout-v61-v63.md).

## planner-1.2-exp.4 regression and planner-1.2 separation

The momentum-only planner-1.2-exp.4 candidate corrected two known collisions but regressed its subsequent development suite: 12/16 goals versus planner-1.1’s 15/16, with no collisions in either arm. planner-1.2 then retained the original contextual mapping features and appended clean neural ranges for braking. On the next frozen suite, both arms reached the same fifteen goals and timed out in room 13000013. There were no lost or added paired successes. The 111,968 physical transitions added no optimization or reserved-test access.

Separate known planner-1.2 checks reached four collision/control goals and resolved the previously stationary room at 1,782; the retained detour room still timed out. Two new-reader optimizer smokes each used 128 transitions and one update, with temporary weights deleted. Those pipeline checks do not train or establish a navigation policy. Original aliases and frozen references were preserved. [Contracts, hashes, limitations, and viewing](evidence/planner-dual-v65-results.md).


## Room-aware large and maze development, October 6

Planner-1.3-exp.4 reached both retained large failures (9500014 at step 3,343; 13000013 at step 2,056), without collisions and within the original deadlines. This is 2/2 reused-case correction, not an independent success-rate estimate. Both maze retries still timed out without collisions. Planner-1.3-exp.5 regressed both retained maze failures; exp.6 also regressed those flights. Exp.7 also timed out. Exp.8 is checking clean-range occupancy; the exp.4 large controller is undergoing retained collision-control checks. The full graph, geometry, deadlines, checkpoint aliases, and reserved-test separation are preserved. See [the detailed development record](MAZE_NAVIGATION.md).

Planner-1.3-exp.8 reached the first retained maze goal: 14000000 at 5,441 steps, no collision. Room 14000001 timed out at 6,352 steps, 11.54 units from the goal. Exp.4 retained large collision controls yielded 3/4 goals and no collisions, so the earlier 2/2 correction alone is insufficient for promotion. The faster clean-map candidate exp.9 is under bounded verification on both profiles.


The frozen exp.9 large-room candidate completed 6/6 retained cases and 8/8 predeclared fresh development cases with zero collisions and timeouts. Its fresh Wilson 95% interval is 67.6–100%; all protected hashes match, with 25, 160 physical transitions and zero optimization. It fails both retained maze cases. Exp.10 recovers the stationary maze case (goal 5,215) but the second times out; exp.11 is under retained verification.

Exp.11 reached both retained maze goals (6,630/6,736 and 6,028/6,352 decisions), without collisions; an eight-layout fresh development check is now frozen and running. Full regression 420 passed, one expected false-fit failure.

The exp.11 fresh maze suite completed at 5/8 goals, zero collisions and three timeouts, failing its 7/8 threshold. Failures: 16000001, 16000004, 16000006. Exp.12 checks goal-relative portal priority on all eight now-retained cases; no successor may reuse them as fresh evidence.

Exp.12 completed at 6/8 retained goals, zero collisions, two timeouts; the 7/8 gate failed. Exp.13 tests a 0.4-unit occupancy grid and associated one-voxel planning buffer on all retained layouts. No fresh successor result is claimed.


### Maze follow-up: rejected fine grid and surface fallback

The retained check for `planner-1.3-exp.12` reached six of eight goals with no collisions. It corrected one previous failure but regressed another layout, so it was not selected. `planner-1.3-exp.13` then returned to the opening-refinement controller and changed the grid from 0.6 to 0.4 units. All eight retained flights timed out without collisions. The change also reduced the physical thickness of the one-cell planning buffer; it is not an isolated resolution ablation. This candidate was rejected.

`planner-1.3-exp.14` keeps the 0.6 unit grid and the existing flight guards. It checks other strongly supported surfaces when the highest-scoring surface has no observed through-rays, and hands over to global goal planning only within three units of the beacon. Its eight-layout retained check is running. It has no verified outcome yet. No optimizer update or reserved final evaluation was performed. Large-room development verification remains eight of eight fresh goals with `planner-1.3-exp.9`.


### Rejected surface fallback and confined-speed check

Exp.14 completed with zero of eight goals, one collision and seven timeouts. Its source and protected-checkpoint hashes remained unchanged. Broadening surface selection did not solve wall search and introduced a collision. It is rejected. Exp.15 returns to the exp.11 surface detector and0.6unit grid, increases the requested confined speed from 1.0 to 1.3 under unchanged range/momentum limits, and restricts goal handover to beacon distances below 3 units. Its retained eight-room check is running; no success claim is made. Four candidate contract tests pass. The previous full focused suite passed 145 tests with one expected failure.


### Confined-speed outcome and search-memory correction

Exp.15 reached four of eight retained maze goals, with zero collisions and four timeouts. It corrected 16000006 but lost prior successes in 16000000 and 16000007. Sources and protected checkpoints were unchanged. It is not selected. Raising a requested speed did not preserve reliable passage search.

Exp.16 retains exp.11 cruise and surface selection. Every tenth decision records a visit to the estimated current cell. After 600 decisions with less than 2 units of reduction in estimated beacon distance, it enables a bounded additive visit cost, `min(0.15 * visits, 4)`, while no portal is active. It never writes this preference into occupancy evidence, never makes blocked cells finite, and disables it during a committed opening approach/crossing. It retains close beacon handover below 3 units. Two tests verify evidence preservation, blocked-cell preservation, inactive portal behavior, and independent memory. Its eight-layout retained flight check is running; no outcome is claimed yet.


### Search-memory outcome and clean alignment check

Exp.16 completed at four of eight goals, zero collisions, four timeouts. It regressed 16000007 and failed all three earlier timeout cases. Visit pressure changed routes but did not establish reliable progress. All source and protected-checkpoint hashes remained unchanged. It is not selected.

Exp.17 combines exp.11 clean occupancy and center refinement with surface normals aligned to the initial observed beacon direction (`normal dot initial_direction >= 0.9`). It retains the original exp.11 cruise, grid, guards and portal planning. The earlier alignment-only candidate used context mapping and did not solve its two cases; this combination must be measured rather than assumed successful. It adds a declared straight-corridor structural assumption appropriate to the present procedural maze and is not a solver for arbitrary wall orientations. The controller receives no hidden heading, partition list, true pose or certified route. Two observed-gap/solid-wall tests pass. The full eight-layout retained check is running.


### Observed-clearance opening reference

Exp.17 reached five of eight retained goals without collisions. It corrected 16000006 but regressed 16000007, and 16000001/16000004 still timed out. It failed the 7/8 rule. Frozen-source and protected-checkpoint hashes matched before/after.

Exp.18 returns to exp.11 surface selection, grid, speed, guards and stronger-support refinement. Let `C` be through-ray intersections belonging to an observed opening cluster, and `W` be observed endpoints on its fitted surface. Both are represented in the wall tangent/height plane. The new reference is `argmax(p in C) min(w in W) ||p - w||`, followed by the existing projection onto the fitted plane. This replaces the median of visible through-rays, which can be biased toward the visible edge of a partially observed opening. It uses no known aperture size or hidden mesh.

The distance to sparse wall endpoints is a reference-selection heuristic, not a guaranteed continuous clearance radius. The actual fly body, collision model, range braking, momentum braking and episode deadlines remain unchanged. Three reference tests pass, including a fixture with the actual maze opening width 2.4 and height 2.8. The selected point lies inside that fixture with body clearance; this does not prove arbitrary sampled surfaces safe. The eight-layout retained full-connectome check is running. No optimizer or reserved final evaluation is involved.


### Neural-ray visible-goal handover

Exp.18 completed at five of eight retained goals, zero collisions and three timeouts. It corrected 16000006 and preserved 16000007, but regressed 16000000; 16000001 and 16000004 still timed out. Sources and protected hashes matched. It failed the 7/8 rule and is not selected.

Exp.19 returns to exp.11 opening inference, grid and cruise. It uses the current decoded local beacon vector and clean neural panorama ranges to recognize a direct goal corridor. For distance `d` below 23, choose the four panorama directions with greatest alignment to the beacon unit vector. Each must have dot product above 0.98 and projected range `r * alignment > d + 0.3`. If these observations pass, the controller relinquishes the opening reference and steers toward the beacon using the existing range/momentum flight guards. Otherwise normal opening planning continues.

This is sampled visibility, not a continuous swept-body clearance proof. No hidden geometry, true pose, certified route or seed enters the action controller. Two tests reject blocked and out-of-range handovers. The full retained eight-layout check is running with unchanged original deadlines and no optimizer or final reserved evaluation.


### Stable distant goal visibility

Exp.19 completed at six of eight retained goals, zero collisions and two timeouts. It corrected 16000006 and kept the other successes, but 16000001 and 16000004 still timed out. Source and protected hashes matched. It still fails the 7/8 rule, so no fresh suite or promotion followed.

Exp.20 retains exp.19 rays, ranges and flight law. A visible beacon below 8 units can hand over immediately. Between 8 and 23 units, all four nearest rays must pass the same visibility check for 20 consecutive decisions (one simulated second). A blocked observation immediately resets that counter and cancels handover. This tests whether brief distant visibility causes premature opening-reference changes. It is not a claim that flicker was proven to be the cause of every failure. Two continuity, cancellation and reset-memory tests pass; the full retained check is running with original deadlines.


## Completed handover checks and numerical repeatability

Planner-1.3-exp.20 and exp.21 each completed at six of eight retained maze goals, zero collisions and two timeouts. Seeds 16000001 and 16000004 remained failures. Both runs preserved their frozen source hashes and protected checkpoint hashes. Neither meets the predeclared seven-of-eight development rule, so no fresh maze suite or promotion followed. The original episode deadlines and physical geometry were preserved.

A separate numerical probe reset the full graph and replayed identical synthetic inputs twice, using eight slots and sixteen steps per replay. It advanced all 167,184 neurons and 25,583,622 directed edges. It performed zero environment transitions and zero optimizer updates. All outputs were finite, but feature values differed by up to 4.76837158203125e-7 and final neuron states by 1.1920928955078125e-7. A second probe with deterministic PyTorch algorithms and `CUBLAS_WORKSPACE_CONFIG=:4096:8` still differed, with maximum feature difference 5.364418029785156e-7. The installed runtime was PyTorch 2.7.1+cu128.

These probes establish small numerical variation for this execution path, not that it causes every navigation failure. Earlier recorded trajectories also diverged before goal handover was possible. The next prepared diagnostic converts the same full matrices to COO storage and checks repeatability; it has not run and has no result. Automatic approval review could not execute it because the account usage limit was reached. This was an unavailable approval review, not a judgment that the operation was unsafe.

Large navigation remains verified on six retained and eight fresh development rooms with planner-1.3-exp.9. Maze reliability remains unresolved. The demo continues to select exp.11, which reached both original retained maze cases and five of eight fresh development layouts. Later six-of-eight outcomes are on reused layouts and must not be presented as independent generalization. No training was initiated during these checks.


## Repeatable full-connectome execution

Execution became available again. The full COO probe still had numerical variation, so storage conversion alone was rejected as a repeatability solution. Ordered CSR accumulation using deterministic `index_add_` produced bit-identical features and final neuron states across both sixteen-step, eight-slot replays. The actual implemented `RepeatableDualActivityBrain` repeated that result on all 167,184 neurons and 25,583,622 edges: zero differing feature values, zero maximum feature/state difference, finite outputs, 32 full-graph steps, and zero environment transitions or optimizer updates. Its probe elapsed 6.477 seconds including initialization.

Planner-1.3-exp.22 keeps exp.19 visible-goal control and selects this explicit experimental readout. Sparse multiplication retains every signed matrix value and edge; it forms weighted presynaptic contributions and accumulates them in deterministic row order. The sensory projection, centering, recurrence, leak, nonlinearity and dual reconstruction formulas remain the same. The discarded pooled output is not computed by the new step method; it never feeds recurrent state or dual reconstruction. Floating-point accumulation order changes and therefore receives a separate readout/fingerprint: `neural-projection-dual-repeatable-index-add-v1`. Historical readouts and checkpoints remain unchanged.

Repeatability here is measured on this installed runtime and device, not guaranteed across hardware or library versions. It is also not a navigation-performance or biological-benefit claim. The eight retained maze layouts are under verification with the same 81,920 physical cap and original episode deadlines. A predeclared 30-minute wall-clock safety bound accommodates slower full-graph execution. All application source files and the runner are frozen by hash for this check. The development rule remains at least 7/8 goals with zero collisions before any new fresh suite. No training or reserved final evaluation is running.

### Segmented execution and incomplete exp.22 flight check

Exp.22 ended at its declared 30-minute wall limit: five goals, zero collisions and three unfinished flights after 47,528 physical transitions. Its source and protected checkpoint hashes matched. The unfinished episodes are not classified as physical timeouts or counted as completed failures; the run cannot support a completed eight-map success rate.

Exp.23 keeps the visible-goal controller and introduces full-graph segmented CSR sums with a separate readout fingerprint. A batch-eight, 32-call probe repeated exactly, with finite features and neuron states, using all 167,184 neurons and 25,583,622 directed edges. Its total elapsed time was 3.51 seconds including initialization, not a warmed throughput measurement. The retained eight-map check is running under the original episode deadlines and 81,920 physical-transition cap, with a predeclared 45-minute wall limit. It performs no optimization or reserved-test evaluation. Both new dual readouts are recognized by the brain inspector; its three-contract regression passes.

An offline trace diagnosis of retained seed 16000001 shows roughly 3,600 decisions spent near the first partition before an opening was found. Several further inferred surface crossings then occurred before timeout. Systematic search along an observed blocking surface is the next correction if the complete flight evidence still misses the selection gate. The proposed geometry checks pass, but the proposal has no measured navigation result yet.

## Completed segmented run and observed-wall correction

Planner-1.3-exp.23 completed all eight retained maze flights: six goals, zero collisions and two physical episode timeouts. Successful decision counts were 4,608 (16000003), 5,053 (16000005), 5,200 (16000000), 5,448 (16000007), 5,496 (16000002) and 6,194 (16000006). Seed 16000001 timed out at 6,562 decisions, 8.75 units from its goal; seed 16000004 timed out at 7,006 decisions, 24.24 units away. The run used 56,048 physical transitions, took 1,268.79 seconds and allocated a peak 1.952 GiB of VRAM. All source and protected checkpoint hashes matched. There were no optimizer updates or reserved-test evaluations. It failed the existing seven-of-eight criterion and was not selected.

Planner-1.3-exp.24 addresses the observed first-partition search delay. If no opening is acquired for 80 decisions, it fits a nearby broad blocking surface from clean neuronal range endpoints, chooses a near-side sweep reference two units from that surface and moves along its tangent in four-unit increments. After 160 decisions without improving distance to the survey target, it reverses direction. Opening acquisition or a ray-supported visible goal cancels the survey. Original route occupancy, body geometry, braking, speed limits and physical deadlines are unchanged. The survey is enabled for the maze contract; it receives no hidden obstacle list, true pose or certified route.

Twelve focused tests passed, covering surface fitting, rejection of distant surfaces, near-side reference geometry, sweep continuation, reversal, independent episode search state and versioned policy selection. All eight retained maze flights are now under a separately frozen diagnostic, with the same 81,920-transition cap, original episode deadlines and a predeclared 45-minute wall limit. The entire 117-file runtime source set is archived byte-for-byte. No navigation improvement is claimed until the flights complete. No fresh maze suite or promotion has occurred.

## Wall survey result and isolated handover correction

Planner-1.3-exp.24 completed at six retained goals, zero collisions and two timeouts. It reached seeds 16000007/06/02/05/01/04 in 4,452/4,492/4,580/4,855/5,588/5,652 decisions. Both previous failures were fixed, but 16000003 and 16000000 regressed to timeouts at 6,535 and 6,885 decisions, ending 24.49 and 36.79 units from the goal. It used 55,080 physical transitions, took 1,321.94 seconds, and peaked at 1.952 GiB allocated VRAM. All source and protected checkpoint hashes matched; no optimization or reserved evaluation occurred. It failed the existing gate and was not selected. Surveying was helpful on several layouts but did not preserve prior successful behavior.

Planner-1.3-exp.25 isolates the visibility/braking correction on exp.23, without the rejected wall survey. It requires no nonsaturated short or panoramic endpoint inside the same 0.25-unit corridor used by braking before direct goal handover. Saturated maximum-range values are not treated as wall hits. An active opening approach/crossing must complete before goal handover. Sensor, connectome, geometry, speed, collision and episode-deadline contracts remain unchanged. Thirteen focused geometry/visibility/version tests passed. The eight retained maps are running with original episode deadlines, the 81,920-transition cap and a separately declared 45-minute wall limit. All 118 runtime source files are frozen and archived. No flight improvement is claimed until the check completes, and no fresh suite or promotion has occurred.

## Clearance-aware handover: retained gate passed

Planner-1.3-exp.25 completed the eight retained maze flights at seven goals, zero collisions and one timeout. Arrival decisions were 4,710 (16000003), 5,051 (16000005), 5,200 (16000000), 5,544 (16000002), 5,614 (16000007), 5,909 (16000001) and 6,357 (16000006). The remaining seed 16000004 timed out at its original 7,006-decision limit, 24.24 units from its goal. The visibility/braking deadlock in 16000001 was corrected, and all six exp.23 successes were preserved.

The check used 56,048 physical transitions and zero optimizer updates, took 1,273.43 seconds, and peaked at 1.952 GiB allocated VRAM. The full 167,184-neuron, 25,583,622-edge graph was retained. All frozen source and protected checkpoint hashes matched. This passes the predeclared seven-of-eight retained gate. It is tuned development evidence, not an independent success-rate estimate or a biological advantage claim.

A separate frozen prospective development suite is now running on seeds 17000000–17000007. An integer-bounded audit of 1,769 archived JSON/Markdown records found no previous occurrences before its seed declaration; undocumented use cannot be ruled out by that audit. No candidate-room geometry was generated or inspected before launch. The fresh run uses exactly the same 118 runtime source hashes as the completed retained run, with an 81,920-transition cap, original physical episode deadlines and a predeclared 45-minute wall limit. At least seven fresh goals and zero collisions are required. The source bytes are archived separately. There is no tuning, optimization, reserved-test access, checkpoint modification or demo promotion during this check. Its outcomes are pending.

## Completed fresh maze check and requested pause

Planner-1.3-exp.25 finished its frozen prospective maze check at **5/8 goals (62.5%)**, zero collisions and three timeouts. The Wilson 95% interval is **30.6–86.3%**. This is a small development sample, not the reserved final test and not an independent paired comparison with exp.11. Its earlier 7/8 retained outcome is tuned correction evidence and must remain separate.

| Fresh seed | Outcome | Decisions | Final goal distance |
| --- | --- | ---: | ---: |
| 17000000 | Goal | 5,916 | 0.439 |
| 17000001 | Goal | 4,090 | 0.443 |
| 17000002 | Timeout | 6,752 | 22.160 |
| 17000003 | Goal | 4,905 | 0.405 |
| 17000004 | Goal | 5,434 | 0.422 |
| 17000005 | Timeout | 6,534 | 20.371 |
| 17000006 | Goal | 5,473 | 0.417 |
| 17000007 | Timeout | 6,666 | 13.211 |

The run completed all eight original episode deadlines with no incomplete flights. It used 54,016 physical transitions, took 1,234.24 seconds and peaked at 1.952 GiB allocated VRAM. Every transition used the full 167,184-neuron, 25,583,622-edge graph. All 118 frozen runtime sources and every protected checkpoint alias matched their before/after hashes. There were zero optimizer updates and no reserved-test access. The process exited normally.

The fresh seven-of-eight criterion was not met, so exp.25 is not promoted. The large launcher remains exp.9, with its six retained and eight fresh goals. The maze launcher remains exp.11. Large-room development criteria are met; reliable maze navigation remains unresolved. The three new timeouts require search/reference diagnosis when work resumes. These newly inspected maps are now correction data for future changes, not reusable fresh evidence.

Navigation, connectome and visualization integration checks passed: 212 passed and one expected failure for a rejected historical candidate. Repository checks passed for 79 documents, 378 links, module imports and CLI help; the public-file audit had no errors. No additional training or navigation experiments followed this check. At the user's request, work pauses after saving and pushing these results; a selected-candidate rendered demo check is deferred until the navigation criterion is met.

## Completed architectural development check

The initial original-objective check completed at **18/21 goals, zero collisions and three timeouts**, with all cases measured. It used 11,829 full-connectome physical transitions, no training and no reserved test. Protected aliases and frozen sources matched. These inspected synthetic scenes are development evidence, not independent real-world generalization. [Detailed results](evidence/architectural-initial-navigation-results.md).

Next: diagnose the three retained timeouts, preserve successful flights, and declare a bounded correction check. Maze experiments remain closed for this iteration.

Architectural exp.2 also reached 18/21 goals without collisions: it fixes the warehouse aisle route but regresses an apartment success, so it is not promoted. The original objectives and deadlines were unchanged. [Candidate results](evidence/architectural-escape-candidate-results.md). Next: constrain recovery using the regression trace before another correction check.

## October 7 closing checkpoint

Architectural planner-1.4-exp.3 reached **19/21 original goals, zero collisions and two timeouts**, preserving every exp.1 success and fixing the warehouse aisle route. Bathroom and atrium climb remain unresolved. These are inspected development scenes, not independent real-world evidence. The demo stays on exp.1 pending further verification. Work pauses at the user's request; no experiment remains running. [Closing results and resume requirements](evidence/architectural-closing-results.md).

## Autonomous learning restart

The planner iteration is closed with defaults retained and unresolved failures recorded. The first planner-free architectural PPO policy passed a 128-transition, one-update CUDA smoke with the complete connectome, finite losses, changed parameters and checkpoint reload. This verifies the learning pipeline, not navigation performance. Substantial training awaits an agreed budget. [Implementation, limits and next experiment](AUTONOMOUS_LEARNING.md).

## First autonomous PPO pilot completed

The 131,072-transition pilot reached 0 goals in 457 training episodes and 0/6 validation goals both before and after; final validation had five collisions and one timeout. The learning pipeline and checkpoint reload passed, but navigation did not. No model was promoted. A structured neural panorama/goal-state encoder is implemented as the next representation candidate; its focused gradient test passes, while full-connectome learning verification and training remain pending. [Results and diagnosis](evidence/autonomous-architecture-pilot-1-results.md).

## Structured autonomous pilot and curriculum verification (October 7, 2026)

The second autonomous PPO pilot completed 131,072 transitions. Deterministic validation improved from 0/6 to 1/6 goals: the office succeeded, the courtyard collided, and apartment, street, atrium and warehouse timed out. This is incomplete navigation, not a successful general solution. Validation shares scene geometry with training; no independent reserved test was used. Losses were finite, reload matched, and protected aliases were unchanged. See docs/evidence/autonomous-architecture-pilot-2-results.md for the recorded outcomes.

The training-only goal curriculum passed a full-connectome verification: one reset probe transition plus 128 PPO learning transitions and one optimizer update. Seeded reset observations matched after intervening activity, the original target was restored at the final stage, learned parameters changed, losses were finite and checkpoint reload matched. The smoke is separate from the pilot budget and makes no navigation-performance claim. The next step is a bounded curriculum experiment with declared stage advancement, task coverage and unchanged original-goal validation.
