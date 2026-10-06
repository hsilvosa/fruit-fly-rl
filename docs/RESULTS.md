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

Planner-1.3-exp.4 reached both retained large failures (9500014 at step 3,343; 13000013 at step 2,056), without collisions and within the original deadlines. This is 2/2 reused-case correction, not an independent success-rate estimate. Both maze retries still timed out without collisions. Planner-1.3-exp.5 regressed both retained maze failures; exp.6 also regressed those flights. Exp.7 tests a distance-aware surface-span requirement. The full graph, geometry, deadlines, checkpoint aliases, and reserved-test separation are preserved. See [the detailed development record](MAZE_NAVIGATION.md).
