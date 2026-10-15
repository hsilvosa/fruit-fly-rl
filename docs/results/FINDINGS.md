# Findings

This document consolidates the fly-rl results into one place: what worked, what failed, which configuration was best, and which claims the evidence does and does not support. Every number comes from the linked results documents. [KEY_NUMBERS.md](KEY_NUMBERS.md) lists the headline measurements with denominators, pool status and sources. The live status board is [ROADMAP.md](../../ROADMAP.md), the experiment index is [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md), and the older aggregate is [RESULTS.md](RESULTS.md).

Reading rules used throughout:

- A cell is a set of episodes (for example 36 of 64). A success is a goal reached before the deadline without a collision.
- "Det" means deterministic action selection. "Sampled" means actions drawn from the policy. The roadmap gates use deterministic mode. Both are reported where the source records them.
- Pool status follows the pools registry in the roadmap: development (inspected), selection, consumed final, reserved and unopened, or probe. A pool that has been inspected cannot serve as fresh evidence later.
- A single-seed result is reported as a single-seed result. Seeds are listed.
- Iteration numbers use the project's 16-item list where they help. Experiment IDs (T1 to T8, P9, B1 to B4, C1.0 to C1.P, R1 to R6, D1 to D9) are used otherwise.

## (a) Summary and claims

### Summary

The learned fly is a PPO actor and critic on top of a fixed reservoir: the full MaleCNS v1.0 connectome (167,184 neurons, 25,583,622 directed edges), driven by simulated sensors. It navigates new medium rooms well. It navigates the partitioned rooms of its training family partly, and the best lever found is training budget: at about 2 million added transitions, three seeds reach 36 to 42 of 64 on `passages`, up from 5 of 64 at the start. It transfers only partly to a held-out parameter region (mean 18.3 of 64, below the frozen threshold of 20) and to a held-out family of six synthetic architectural scenes (95 to 108 of 168, against 71 at the start, with one scene regressing). It does not navigate large rooms or mazes: the retained candidate scores 0 to 2 of 32 per cell there. The four-family release gate, at least 52 of 64 with at most 3 collisions in each of four families, is not met in any family. An explicit planner that reads the same connectome activity and chooses actions by search is a reference, not a learned result. It reaches 147 of 168 on the architectural scenes, against about 104 for the learned candidate. The contribution of the connectome's specific wiring is not shown: an edge-shuffled control matches the real connectome within the measured spread.

### Defensible claims

1. **The historical medium-room reference is recovered and reproduces.** The 50/64 policy's checkpoint hash matches its recorded final test. Replay on three validation pools matched outcome for outcome in 32 of 32 episodes each ([HISTORICAL_REFERENCE](../experiments/reference-recovery/HISTORICAL_REFERENCE.md)).
2. **The learned policy with the full connectome in the loop reaches goals in new medium rooms of the trained family.** At 2M added transitions, three seeds score 49, 54 and 55 of 64 deterministic on development pool 886000 ([REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md)). Run 601 scored 59 of 64 on inspected pool 880000, one training run selected among three ([COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md)).
3. **Training budget is a real lever for `passages` with this recipe, measured on one seed and then replicated on three.** One seed gave 11, 12, 17 and 23 of 64 along a curve to 1,015,808 transitions ([LARGE_BUDGET_RESULTS](../experiments/large-budget/LARGE_BUDGET_RESULTS.md)), then 38 of 64 at 1,998,848 ([LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md)). Two more seeds at the same budget gave 36 and 39 on the replication pool, and seed 801 gave 42 on that pool ([REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md)). The start checkpoint scores 5 of 64 on that replication pool.
4. **Within the trained family, the gain holds on every seed tried.** `passages-wide` and `gate-two` are 64 of 64 on all three seeds, and `passages-mid` is 54 to 57 of 64 ([REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md)).
5. **Partial transfer to a held-out architectural family.** Level C deterministic scores are 95, 108 and 108 of 168, against 71 at the start ([LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md)). The rule for this level was positive, but the gain is uneven: `courtyard` fell from 24 of 24 to 7, 23 and 17, while `apartment` and `atrium` did not move.
6. **The held-out parameter region is partly reachable.** The three 2M seeds score 26, 17 and 12 of 64 on level B development maps, against 1 at the start and 1 to 6 for every earlier run on the same pool. The mean misses the frozen threshold, so the result is inconclusive, not positive ([LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md)).
7. **Route information is a large part of the partitioned-room failure.** A diagnostic policy that receives the route direction as an input, which a student cannot do, reaches 37.5 of 64 on `passages` against 11 for the control (two seeds each, 262,144 transitions). It is not a student ([WAYPOINT_DIAGNOSTIC_RESULTS](../experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md)).
8. **Explicit planning reaches the architectural and development rooms, as a reference.** Planner-1.4-exp.3 reaches 147 of 168 on level C ([PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md)). Planner-1.3-exp.9 reaches 6 of 6 retained and 8 of 8 fresh development rooms on `large` ([MAZE_NAVIGATION](../planner/MAZE_NAVIGATION.md)).
9. **Evaluation is repeatable to about one episode.** Re-evaluating the pilot checkpoint on the same selection pools gave the same results within one episode per cell ([PHASE1_PILOT_RESULTS](../experiments/variance-and-stability/PHASE1_PILOT_RESULTS.md)). Full-graph execution became bit-identical across replays only after the sparse accumulation was made ordered on this installed runtime ([RESULTS](RESULTS.md#repeatable-full-connectome-execution)).

### Claims NOT supported

1. **The four-family release gate.** It requires 52 of 64 and at most 3 collisions in each of four families. It is not met in any family. Best values recorded: medium 55 of 64 with 5 collisions (seed 901), `passages` 42 of 64 with 8 collisions, `large` 2 of 32, `maze` 0 of 32, level C 108 of 168 with 45 to 54 collisions.
2. **Learned navigation in large rooms or mazes.** The retained candidate scores 0 to 2 of 32 per cell, mostly by timeout ([PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md)).
3. **General navigation of unseen maps.** Level B is inconclusive. Level C is one fixed set of 21 situations, each with one start and one goal. Its headings are not independent samples of buildings. No reserved pool has been opened.
4. **That the biological connectome improves or is necessary for navigation.** With four seeds per arm the real connectome is not ahead of the edge-shuffled control in any cell of the matched fresh chain; on `passages` the difference is +3.75 episodes with a 95 percent interval of [-7.6, +15.1], inconclusive by the frozen rule. The chain check failed. It is not a negative proof ([C11](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md), [C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md), [C13](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C13.md)).
5. **That memory helps.** The long history window gained on seed 442 and lost on seed 443 ([PHASE3_REPLICATION_RESULTS](../experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md)).
6. **That reward design, the stabilization bundle, the random-map mix, an auxiliary head, a privileged critic, supervised pretraining or a route-progress reward produce the gains.** Each was tested. None moved `passages` at the tested budget (section (d)).
7. **That the 80 percent large-room target or the 81 percent architectural target is met.** Planner results on development rooms are not an independent success rate.
8. **That the planner has a biological benefit.** It reads simulated connectome activity, but its outcomes say nothing about biology. Its level C scenes were the ones it was developed on, so its 147 of 168 is optimistic.
9. **That maze navigation is reliable.** The best maze candidate passed its retained gate at 7 of 8 and reached 5 of 8 on the fresh suite of 8, which failed the predeclared threshold ([MAZE_NAVIGATION](../planner/MAZE_NAVIGATION.md)).
10. **That hovering explains the `passages` failures.** Collisions dominate on `passages`, and hover fixed points were found only for the pilot checkpoint on `passages-wide` ([COLLISION_ANATOMY](../experiments/diagnostics/COLLISION_ANATOMY.md), [COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md)).

## (b) Best configuration

### Identity

The best learned configuration is the **2M recipe** from the experiment 7 start checkpoint. It was run on seed 801 ([LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md)) and replicated on seeds 851 and 901 ([REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md)).

- **Start:** `runs/training/reference-transfer-7/mix3e4/stage-2.zip` (SHA-256 prefix `773dff8d53e2e115`). It descends from the 50/64 reference (`0a1a6569549a`) through transfer experiments 3 to 7 ([RESULTS](RESULTS.md)). The source hash was unchanged after training.
- **Recipe:** the Phase 1 stabilization bundle. 32 simulators: 8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two`. 128 steps per simulator per update, clip range 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, gamma 0.995. Learning rate falls linearly from 3e-4 to 3e-5 over the whole run. No optimizer restart. Full connectome. No planner, no imitation, no privileged input ([LARGE_BUDGET_2M_PROTOCOL](../experiments/large-budget/LARGE_BUDGET_2M_PROTOCOL.md)).
- **Budget:** 1,998,848 added transitions, 61 stages of 32,768. The schedule is tied to this total.
- **Decision checkpoint:** stage 61. Hashes (first 16 hex): seed 801 `3a4150b59b5fc894`, seed 851 `fc1b2c69068ac72e`, seed 901 `29ac1bcf11652646`.

### Measured performance per family

Stage 61, deterministic, pool 886000 (inspected development) unless marked. Cells are successes of 64 (or of 168 for level C, or 32 for `large` and `maze`).

| Family | Seed 801 | Seed 851 | Seed 901 | Start checkpoint | Release gate |
| --- | ---: | ---: | ---: | ---: | --- |
| Medium rooms, 886000 | 49 (11 collisions) | 54 (7) | 55 (5) | 51 | 52 of 64, at most 3 collisions |
| `passages-mid`, 886000 | 56 (2) | 57 (0) | 54 (2) | not run | same |
| `passages-wide`, 886000 | 64 (0) | 64 (0) | 64 (0) | not run | same |
| `gate-two`, 886000 | 64 (0) | 64 (0) | 64 (0) | not run | same |
| `passages`, 886000 | 42 (8) | 36 (16) | 39 (8) | 5 (27) | same |
| Level B, development pool 950000 | 26 (10) | 17 (14) | 12 (17) | 1 | inconclusive by frozen rule |
| Level C, development headings 900000 | 95 (52) | 108 (45) | 108 (54) | 71 (51) | positive by frozen rule, gate not met |
| `large`, pool 892000, 32 episodes | 2 (7) | 0 (11) | 0 (5) | not run | 52 of 64 (26 of 32 at this size), not met |
| `maze`, pool 893000, 32 episodes | 0 (3) | 0 (1) | 0 (5) | not run | not met |

Sources: [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md), [LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md), [PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md). Sampled-mode values are in [KEY_NUMBERS.md](KEY_NUMBERS.md).

### Caveats on the best label

- Earlier documents ([RESULTS](RESULTS.md), the older README tables) name the Phase 1 pilot checkpoint (`runs/training/phase1-pilot/seed442/stage-3.zip`) as the best development candidate. That predates the 2M results. On `passages`, the 2M seeds score 36 to 42 of 64 on the replication pool, against 17 of 64 for the pilot on pool 880000. The pools differ, so the comparison is indicative. The pilot's 58 percent on `passages-mid` (37 of 64 on pool 880000) is below the 2M seeds' 54 to 57 of 64 on pool 886000, with the same caveat.
- Run 601 is the first checkpoint that keeps medium, `passages-wide` and `passages-mid` together. It has a low `passages` value (9 of 64 on pool 880000, deterministic), below the pilot's 17.
- The 2M result is one recipe on development pools. No reserved final pool has been used.

### Historical lineage (context, not a paired ranking)

Final results from earlier experiments, each on its own pool with 64 episodes, seed 42 for each winner. Modes are not recorded in the source. These are consumed final pools.

| Experiment | Final goals | Collisions | Timeouts | Source |
| --- | ---: | ---: | ---: | --- |
| Warm-start sensor comparison (50/64 reference) | 50 of 64 (78.1%) | 5 | 9 | [RESULTS](RESULTS.md#earlier-dense-room-results) |
| Observed-ray risk comparison | 48 of 64 (75.0%) | 16 | 0 | same |
| Near-goal curriculum comparison | 45 of 64 (70.3%) | 15 | 4 | same |
| Original coordinated dense launcher | 43 of 64 (67.2%) | 11 | 10 | same |
| Fresh sensor comparison | 35 of 64 (54.7%) | 20 | 9 | same |

## (c) Findings by research question

### c1. Can the learned fly navigate medium rooms?

Yes, on the trained family. The historical reference, the 50/64 policy, scores 23 of 32 on its validation pool and replays exactly. Later candidates keep medium competence while training on harder maps: run 601 scores 59 of 64 and the 2M seeds score 49 to 55 of 64 on inspected pools ([COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md), [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md)).

Medium rooms are the easy cell, and they say little about the rest. A random-weight policy trained on medium rooms only reaches 61 of 64 at 884,736 transitions with the real connectome (seed 1001). The edge-shuffled arm reaches 54 of 64 deterministic and 60 sampled ([CONNECTOME_CONTROL_RESULTS_C10](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md)). Medium competence therefore does not require the retained history.

The generalization of the medium result is level A (new layouts of a trained family). The development evidence is in pools that were inspected before use. The reserved level A report pool (940000 to 949999) is unopened.

### c2. Partitioned rooms: what was tried and what made the difference

Passages-type profiles are rooms split by partitions with openings: `passages-wide` (wide openings), `passages-mid` (intermediate), `passages` (4 by 4 m openings plus clutter) ([RESULTS](RESULTS.md), [transfer summary](../experiments/reference-recovery/TRANSFER_SUMMARY.md)).

**Sequence of findings.**

- Training only on `passages` gave 0 of 32 (T1). Adding a route-progress reward or more steps gave 0 of 32 and cost medium competence (T2). The failure classification found collisions into partitions and hovering near them, and no episode crossed all partitions ([PASSAGES_FAILURE_CLASSIFICATION](../experiments/reference-recovery/PASSAGES_FAILURE_CLASSIFICATION.md)).
- Graded maps gave the first partitioned-map signal (T3: `gate-long` 32 of 32, `passages-wide` 4 of 16). Mixing medium rooms at 50 percent restored medium competence (T4). Adding `passages-wide`, `passages-mid` and mixing profiles inside each update (T5 to T7) gave `passages-mid` 15 of 32 and `passages` 4 of 32, one episode short of its positive rule (T7). Continuing for 262,144 transitions over two seeds lost the gains (T8).
- The stabilization bundle (Phase 1) held one seed and not the other. Seed 442 kept `passages-wide` at 22 to 23 across four evaluations. Seed 443 went from 0 to 18 on the same profile. `passages` stayed at 0 to 6 of 32 ([PHASE1_RUN_RESULTS](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md)).
- Budget, with the same recipe, is the difference that held. The one-seed curve reached 23 of 64 at 1M and 38 of 64 at 2M, and three seeds at 2M reached 36 to 42 of 64 ([LARGE_BUDGET_RESULTS](../experiments/large-budget/LARGE_BUDGET_RESULTS.md), [LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md), [REPLICATION_2M_RESULTS](../experiments/large-budget/REPLICATION_2M_RESULTS.md)).

**Caveats on the budget curve.** On pool 885000 the deterministic curve is 16, 26, 48 and 38 of 64 at 0.49M, 1.0M, 1.5M and 2.0M. The fall from 48 to 38 is timeouts (10 to 20), not collisions. Sampled values at the same points are 20, 23, 43 and 45 ([LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md)). Collisions on `passages` fell only at 1.5M and 2M (to 6 on seed 801). They remain above the release limit of 3 on every seed (8, 16 and 8 at stage 61).

**Interventions that did not move `passages`** (details in section (d)):

- Reward changes: route-progress reward (T2) and the obstacle-aware reward pilot. The reward audit found an ideal route follower beats hovering at every route point, so the reward does not favour hovering.
- The stabilization bundle (P9, P10): stable on one seed, not on another.
- Memory windows: short window negative, long window not replicated (M11, M12).
- Random-map training mix (R5): the difficulty controller stayed at 0.20 to 0.25, so training saw 64 to 127 randomized episodes per run ([LIGHT_AUDIT_RESULTS](../experiments/diagnostics/LIGHT_AUDIT_RESULTS.md)).
- Training-only route signals: auxiliary waypoint head (+2.3 of 64 on `passages`), privileged critic (+0.7), supervised pretraining of the actor trunk (+2.0). Each is within the control's range ([AUXILIARY_STUDENT_RESULTS](../experiments/students/AUXILIARY_STUDENT_RESULTS.md), [PRETRAIN_RESULTS](../experiments/students/PRETRAIN_RESULTS.md)).

### c3. Held-out parameter region (level B)

Level B is the region where opening width is below 3.8 m and there are at least four partitions. The training sampler never draws from it ([HELD_OUT_SPEC](../methods/HELD_OUT_SPEC.md)). The development pool is 950000 to 950063. The reserved final pool (960000 to 969999) is unopened.

- Earlier policies scored 1 to 6 of 64 on this pool. The R5 random-map runs reached 5 of 64 at their best ([RANDOM_DISTRIBUTION_RESULTS](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md)).
- The 2M seeds score 26, 17 and 12 of 64 (mean 18.3). The positive rule needed 20, so the result is inconclusive. It missed by 1.7 episodes ([LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md)).
- Sampled results are 23, 16 and 20 of 64.
- Level B failures are mostly timeouts (24 to 35 of 64), then collisions (10 to 24). The policy does not commit through narrow openings.
- The connectome-control arms scored 5.5 to 14.5 of 64 on level B (C1.1 and C1.2, mean and sampled values), so level B is not separated from the control.

### c4. Held-out family (level C)

Level C is six synthetic architectural scenes (`office-floor`, `apartment`, `street-block`, `atrium`, `warehouse`, `courtyard`), 21 situations with 8 headings each (168 episodes). The lineage never trained on them ([HELD_OUT_SPEC](../methods/HELD_OUT_SPEC.md)). The start checkpoint scores 71 of 168 deterministic (42 percent) and 93 sampled. The 2M seeds reach 95, 108 and 108 deterministic and 113, 108 and 105 sampled.

- Gains come from `street-block` (12 to 32, 36 and 40 of 40), `warehouse` (10 to 24, 17 and 18 of 32) and `office-floor` (10 to 16 of 24).
- `apartment` (7 to 8 of 24) and `atrium` (8 to 9 of 24) do not move.
- `courtyard` regressed from 24 of 24 to 7, 23 and 17 of 24.
- Against the sampled start (93), the trained seeds gain 12 to 20 episodes. The deterministic comparison overstates the gain because the start checkpoint hovers in deterministic mode.
- Collisions on level C are 45 to 62 of 168, not lower than the start's 51.
- The planner reaches 147 of 168 on the same headings (section c10).

The level C headings (900000 and above) were used for this baseline and for the 2M checkpoints. They are inspected development headings, not the sealed final pool (970000 to 979999).

### c5. Large rooms and mazes

**Learned policies.** Every learned attempt on `large` has failed to date.

- The historical reference scored 0 of 16 on `large` ([HISTORICAL_REFERENCE](../experiments/reference-recovery/HISTORICAL_REFERENCE.md)). A bounded diagnostic found that the earlier ray-risk baseline reproduced 3 of 4 goals on retained original rooms and 0 of 4 on new large rooms ([GEOMETRY_DIAGNOSIS](../learning/GEOMETRY_DIAGNOSIS.md)).
- The geometry comparison (fresh initialization, baseline and curriculum, two seeds each) reached 0 of 32 on validation and 0 of 64 on its one final assessment, with the untrained control also at 0 of 64 ([RESULTS](RESULTS.md#geometry-comparison)).
- Later correction candidates (guided initialization and PPO, separate critic history, guarded PPO, spatial neural readout, panoramic sensors v5 to v8, directional and look-ahead guidance, waypoint v6) each scored 0 of 8 on the reused development layouts ([RESULTS](RESULTS.md#latest-original-large-corrections)).
- The 2M retained candidate scores 2, 0 and 0 of 32 on `large` and 0, 0 and 0 of 32 on `maze`. Most failures are timeouts (21 to 31 of 32) ([PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md)).
- A single wide opening is different. `gate-long` reached 61 of 64 on a final pool with zero collisions and three timeouts ([passage-mastery-v2](../evidence/passage-mastery-v2-results.md)). This shows that the policy can fly and cross one opening. It is not large-room navigation.

**Explicit planner.** The planner is an observed-map controller. It reads full-connectome activity, builds an occupancy grid, runs weighted search, and chooses actions. It is a reference, not a learned policy.

- `large`: planner-1.0 reached 8 of 8 on reused optimization rooms and 13 of 16 on a frozen prospective suite, with three timeouts and no collisions (Wilson 95%: 57.0 to 93.4) ([README](../../README.md), [observed-map-v55](../evidence/observed-map-v55-results.md)). On a later paired suite, planner-1.1 reached 14 of 16 and planner-1.0 reached 12 of 16 on the same rooms. Planner-1.2 reached 15 of 16 ([planner-v60](../evidence/planner-v60-development-results.md), [planner-v65](../evidence/planner-dual-v65-results.md)).
- `large`, planner-1.3-exp.9: 6 of 6 retained rooms and 8 of 8 fresh rooms, zero collisions (fresh Wilson 95%: 67.6 to 100). The predeclared rule was met ([MAZE_NAVIGATION](../planner/MAZE_NAVIGATION.md)). Caveats: the rooms were inspected during tuning, and this is not an independent final test.
- `maze`: planner-1.3-exp.11 reached 2 of 2 retained and 5 of 8 fresh rooms. Planner-1.3-exp.25 reached 7 of 8 retained and 5 of 8 fresh (Wilson 95%: 30.6 to 86.3), and was not promoted. Many variants regressed earlier successes (section (d)). The maze launcher still selects exp.11 ([maze-wrap-up](../evidence/maze-wrap-up.md)).

### c6. Why failures happen

These are diagnoses. Each is a measured symptom or a probe result, not a proven mechanism.

- **Collision anatomy on `passages`** (64 episodes, pool 880000). Collisions are not edge clips at the opening: only 1 to 3 per checkpoint end within 0.5 m of the route, and most end 1.5 m or more away. Median route progress at collision is 0.29 to 0.48. Timeouts sit about 4 m from the route at under 1.2 m/s ([COLLISION_ANATOMY](../experiments/diagnostics/COLLISION_ANATOMY.md)).
- **Feature probe.** The 256 pooled features lose almost nothing against the raw sensors (within 5 degrees in 16 of 16 pairs). Both decode the route direction only roughly. Median error on the hard subset is 49 to 70 degrees for the probe table entries. The text of the source summarizes these as 45 to 53 degrees ([FEATURE_PROBE](../experiments/diagnostics/FEATURE_PROBE.md)). So the readout is not the lever.
- **Sensing probe on 700 synthetic maps.** An MLP decodes the route direction to 34 degrees on the hard subset from the 8 m rays. The 24 m rays reach 28 degrees. The probes with rollout histories were worse at this data size, which is a probe limit, not a sign against memory ([SENSING_PROBES](../experiments/diagnostics/SENSING_PROBES.md)).
- **Information at decision time.** The privileged waypoint diagnostic raises `passages` from 11 to 37.5 of 64, and `passages-mid` from 33.5 to 57.5, with the same recipe. Exact information still leaves `passages` below the gate ([WAYPOINT_DIAGNOSTIC_RESULTS](../experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md)).
- **The students could not use it.** An auxiliary head, a privileged critic and supervised pretraining of the trunk each left `passages` near the control (13 to 15 of 64 against 12). The pretrained trunk encodes the route direction to 41.6 degrees on held-out maps, yet flight does not change under PPO ([AUXILIARY_STUDENT_RESULTS](../experiments/students/AUXILIARY_STUDENT_RESULTS.md), [PRETRAIN_RESULTS](../experiments/students/PRETRAIN_RESULTS.md)).
- **Exposure.** The R5 runs saw a total of 64 to 127 randomized episodes, a few dozen on partitioned maps. Those runs say little about training on hard maps. The budget curve is the first direct test of more exposure.

### c7. Deterministic versus sampled evaluation, and hover fixed points

Deterministic and sampled results can differ a lot. Every protocol should declare its mode and report both.

- Pilot checkpoint, `passages-wide`: 14 of 64 deterministic (50 timeouts, no collisions) against 55 sampled. This is a hover fixed point ([COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md)).
- Level C start: 71 of 168 deterministic, 93 sampled ([LEVEL_BC_RESULTS](../experiments/large-budget/LEVEL_BC_RESULTS.md)).
- C1.2 shuffled arm, seed 1001, `passages`: 13 of 64 deterministic (44 timeouts) against 27 sampled ([CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md)).
- 2M seed 801, `passages` at 2M: 38 of 64 deterministic against 45 sampled ([LARGE_BUDGET_2M_RESULTS](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md)).
- Run 601 on `passages`: 9 of 64 deterministic and 11 sampled ([COLLISION_ANATOMY](../experiments/diagnostics/COLLISION_ANATOMY.md)).

The effect is not general. For run 601 and for seed 505, the sampled and deterministic numbers agree within a few episodes on `passages`. The roadmap gates use deterministic mode ([ROADMAP](../../ROADMAP.md)).

### c8. Seed variance

Between-seed spread is the dominant noise, and it is larger than most effects that were tested before the protocol rules.

- Five runs of the pilot recipe (R1): `passages-wide` ranged over 11 episodes (12 to 23 of 32), `passages-mid` over 6 and `passages` over 2 on selection pools ([VARIANCE_STUDY_RESULTS](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md)).
- Two seeds from one start (P10): `passages-wide` ranged over 18 episodes on seed 443 ([PHASE1_RUN_RESULTS](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md)).
- Memory (M11, M12): the long window gave +19 on the hard-profile sum for seed 442 at 131k transitions. For seed 443 at the same stage it gave +5 on `passages-wide` and -9 on `passages-mid`.
- Connectome arms (C1.2): real seeds 21 and 34 on `passages`; shuffled seeds 13 and 29. The seed spread equals the arm difference. About eight seeds per arm are needed to detect a 10-episode difference at 80 percent power ([CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md)).
- Connectome arms (C1.3, four seeds each): real 21, 34, 21, 28 and shuffled 13, 29, 22, 25 on `passages`; sample standard deviations 6.3 and 6.8, so the 95 percent interval of the difference narrowed from about +-45 (two seeds) to +-11 ([CONNECTOME_CONTROL_RESULTS_C13](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C13.md)).
- The three 2M seeds agree (36 to 42), a spread of 6. Three seeds do not bound the spread across many seeds.
- The pilot checkpoint: one draw in six of the recipe scored 58 percent on `passages-mid` on a fresh pool, and none of the five repeats came close ([VARIANCE_STUDY_RESULTS](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md)).

### c9. The connectome control

The control replaces the connectome's edges with a degree-preserving shuffle. It keeps degrees, weights and signs, and removes the specific wiring. The fresh chain is trained alongside the real chain with the same budget and seeds.

- **C1.0 (medium, 884,736 transitions, seed 1001):** the gate passed. Real 61 of 64 deterministic (59 sampled), shuffled 54 of 64 (60 sampled). Retained start 55 of 64 on the same pool ([CONNECTOME_CONTROL_RESULTS_C10](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md)).
- **C1.1 (2.88M transitions, seeds 1001 and 1051):** the chain check failed. The real arm reached 16.0 of 64 on `passages` against 28 required. Retained seeds reached 36 to 42. The shuffled arm was higher on `passages` (25.5), `passages-mid` (51.0 against 41.5) and level C (86 against 79), and lower on medium (53.5 against 59.0). No cell showed a 10-episode difference ([CONNECTOME_CONTROL_RESULTS_C11](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md)).
- **C1.2 (4.88M transitions, same seeds):** the chain check failed by half an episode (real 27.5 against 28). Shuffled 21.0 on `passages`. Retained 38.0. `passages-mid` 51.0 against 47.0, level B 9.5 against 12.0, level C 98.0 against 105.5 ([CONNECTOME_CONTROL_RESULTS_C12](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md)).
- **C1.3 (4.88M transitions, four seeds per arm):** `passages` real 26.0 against shuffled 22.25, D +3.75, 95 percent interval [-7.6, +15.1], 90 percent interval [-5.2, +12.7]: inconclusive by the frozen rule (equivalence within 10 needed the 90 percent interval inside +-10). The chain check failed again (26.0 against 28). `passages-mid`, `passages-wide`, medium, level B and level C read equivalent within their margins; none favors the real connectome ([CONNECTOME_CONTROL_RESULTS_C13](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C13.md)).

**What this allows us to say.** The biological connectome is not shown to improve or to be necessary for navigation in this project, and with four seeds per arm its effect on `passages` is bounded to -7.6 to +15.1 episodes of 64 (95 percent). The matched fresh chain did not reach the retained level, so the comparison does not test the retained lineage. This is the bound the release must state. A stronger statement needs many more seeds than the project can afford.

### c10. The explicit planner reference

- **Level C:** planner-1.4-exp.3 scores 147 of 168 deterministic (87.5 percent, Wilson 95%: 82 to 92), with 4 collisions and 17 timeouts. The learned candidate's mean is 103.7 ([PLANNER_REFERENCE_RESULTS](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md)). Failures concentrate in `study-to-bathroom` (timeouts in 8 of 8 headings), `sofa-to-bedroom` and `void-climb-to-top-gallery`. The planner's gain is mostly in `atrium` (21 against 8 to 9), `warehouse` and `courtyard`.
- **Architectural scenes (original objectives, 21 situations):** planner-1.4-exp.1 reached 18 of 21, exp.2 reached 18 of 21 but regressed one success, and exp.3 reached 19 of 21 with no collisions ([architectural-closing-results](../evidence/architectural-closing-results.md)). The demo stays on exp.1.
- **Limits:** the planner's level C scenes are the ones it was developed on. The `large` and `maze` figures are development rooms, not a matched pool. The planner has no learned component and says nothing about PPO's action gradient. Its outputs are not evidence about the connectome.

## (d) What was tried

Verdicts: **Positive** (met its declared rule, still development evidence); **Partial** (positive in part or diagnostic only); **Inconclusive** (rule missed or chain check failed); **Negative** (rule not met or no gain); **Rejected** (not selected or promoted).

| Intervention | Question | Result | Verdict | Link |
| --- | --- | --- | --- | --- |
| Recovery and replay of historical winners | Are the medium winners still there? | 50/64, 48/64, 45/64 replay 32 of 32 episodes each | Positive (verified) | [HISTORICAL_REFERENCE](../experiments/reference-recovery/HISTORICAL_REFERENCE.md) |
| T1, retained policy and fresh control on `passages` | Does the 48/64 policy learn `passages`? | `passages` 0 of 32 for both arms; medium 24 of 32 retained, 11 fresh | Negative | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS.md) |
| T2, route-progress reward; budget 262k | Does a denser reward or more steps help? | `passages` 0 of 32; medium fell to 17 of 32 | Negative | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_2.md) |
| T3, graded gates from 50/64 | Does graded training work? | `gate-long` 32 of 32; `passages-wide` 4 of 16; medium 19 of 32 | Rejected (forgetting), first signal | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_3.md) |
| T4, 50% medium share | Does medium share recover medium? | medium 24 of 32; `passages-wide` 6 of 32 | Positive | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_4.md) |
| T5, `passages` in mix | Does `passages` train? | `passages-wide` 26 of 32, then 20; `passages` 1 to 2 of 32 | Negative | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_5.md) |
| T6, `passages-mid` profile | Does an intermediate profile help? | `passages-mid` 9 to 12 of 32; swings of 21 episodes | Negative | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_6.md) |
| T7, profiles mixed inside every update | Does in-batch mixing help? | `passages-mid` 15 of 32; `passages` 4 of 32; one episode short | Inconclusive (selected on reported pools) | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_7.md) |
| T8, 262k transitions, two seeds | Do the gains persist? | Gains lost; medium dropped at times | Negative | [results](../experiments/reference-recovery/REFERENCE_TRANSFER_RESULTS_8.md) |
| Reward-hover audit (no training) | Does the reward favour hovering? | Ideal route follower beats hovering at every route point | Refuted for ideal follower | [LIGHT_AUDIT_RESULTS](../experiments/diagnostics/LIGHT_AUDIT_RESULTS.md) |
| Stabilization bundle, P9 and P10 | Does a stable trainer keep the gains? | Seed 442 stable (`passages-wide` 22 to 23); seed 443 range 18 | Negative for the criterion | [results](../experiments/variance-and-stability/PHASE1_RUN_RESULTS.md) |
| Run 601 confirmation | Is 601 a real candidate? | medium 59, `passages-wide` 55, `passages-mid` 35, `passages` 9 of 64 | Partial (first to keep three profiles) | [COMMITTEE_EVAL_RESULTS](../experiments/diagnostics/COMMITTEE_EVAL_RESULTS.md) |
| M11, short memory window (8 frames) | Does history help? | hard-profile sum 9 against 30 control at 131k | Negative | [results](../experiments/variance-and-stability/PHASE3_SCREENING_RESULTS.md) |
| M11, long memory window (16 frames), seed 442 | Does the long window help? | +19 on hard-profile sum at 131k | Promising, not replicated | same |
| M12, long window, seed 443 | Does it replicate? | +5 `passages-wide`, -9 `passages-mid`, 0 `passages` | Not replicated | [results](../experiments/variance-and-stability/PHASE3_REPLICATION_RESULTS.md) |
| R5, random-map mix (three seeds) | Does random training help? | margins +1.1 (d=0.9) and +0.6 (level B) of 64; controller 0.20 to 0.25 | Negative by rule | [results](../experiments/random-distribution/RANDOM_DISTRIBUTION_RESULTS.md) |
| Auxiliary waypoint head (three seeds) | Does a training-only route signal help? | `passages` 14.7 against 12.3 (+2.3); sampled +6.3 | Negative by rule | [results](../experiments/students/AUXILIARY_STUDENT_RESULTS.md) |
| Privileged critic (three seeds) | Same question | `passages` 13.0 against 12.3 (+0.7) | Negative | same |
| Supervised pretraining, then PPO (three seeds) | Does a pretrained trunk help PPO? | offline gate passed (41.6 degrees); `passages` 14.3 against 12.3 (+2.0) | Negative (PPO) | [results](../experiments/students/PRETRAIN_RESULTS.md) |
| Privileged waypoint input (diagnostic, not student) | Is missing route information the limit? | `passages` 37.5 mean (two seeds) against 11 control | Partial, diagnostic | [results](../experiments/diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md) |
| B1, 1,015,808 transitions (one seed) | Is budget the lever? | `passages` 23 of 64 (threshold 24) | Inconclusive | [results](../experiments/large-budget/LARGE_BUDGET_RESULTS.md) |
| B2, 1,998,848 transitions (one seed) | Does 2M keep raising `passages`? | `passages` 38 of 64; collisions 6 | Positive (one seed) | [results](../experiments/large-budget/LARGE_BUDGET_2M_RESULTS.md) |
| B3, 2M replication (three seeds) | Does the 2M effect replicate? | `passages` 42, 36, 39 of 64 | Positive, replicated | [results](../experiments/large-budget/REPLICATION_2M_RESULTS.md) |
| B4, level B and C for the 2M checkpoints | Does the effect reach unseen cells? | level B mean 18.3 (threshold 20); level C mean 103.7 (threshold 88) | Inconclusive (B), positive by rule (C), uneven | [results](../experiments/large-budget/LEVEL_BC_RESULTS.md) |
| C1.0, fresh medium chain | Is the chain valid? | real 61 of 64 (gate 40); shuffled 54 | Positive (chain valid) | [results](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C10.md) |
| C1.1, fresh two-phase chain, two seeds | Does the real connectome beat the shuffled control? | chain check failed (16.0 against 28); shuffled not worse | Inconclusive (chain failed) | [results](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C11.md) |
| C1.2, four extended runs | Does more budget settle it? | chain check failed by 0.5 (27.5 against 28); no cell favours real | Inconclusive | [results](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C12.md) |
| C1.3, four seeds per arm | Is there a real-versus-shuffled difference? | `passages` D +3.75, 95 percent interval [-7.6, +15.1]; chain check 26.0 against 28; secondary cells equivalent | Inconclusive | [results](../experiments/connectome-control/CONNECTOME_CONTROL_RESULTS_C13.md) |
| C1.P, planner reference | Where does the planner stand? | level C 147 of 168; learned `large` 0 to 2 of 32; `maze` 0 of 32 | Reference result | [results](../experiments/connectome-control/PLANNER_REFERENCE_RESULTS.md) |
| Geometry comparison, fresh initialization | Does a curriculum learn large rooms? | validation 0 of 32 for all runs; final 0 of 64; control 0 of 64 | Negative | [RESULTS](RESULTS.md#geometry-comparison) |
| Passage mastery v2 (single wide opening) | Does the policy learn one wide opening? | `gate-long` 61 of 64 (Wilson 95%: 87.1 to 98.4); control 0 of 64 | Positive on a simpler task | [passage-mastery-v2](../evidence/passage-mastery-v2-results.md) |
| Guided init, critic history, guarded PPO, spatial readout, panoramic v5 to v8, directional and look-ahead, waypoint v6 (`large`) | Do these fix large-room learning? | 0 of 8 each on reused development layouts | Negative | [RESULTS](RESULTS.md#latest-original-large-corrections) |
| Autonomous architecture PPO, pilots 1 and 2, curricula 1 and 2 | Does autonomous PPO learn the architectural scenes? | validation 0 of 6, then 1 of 6, 1 of 6 and 0 of 6 | Negative | [pilot 1](../evidence/autonomous-architecture-pilot-1-results.md), [pilot 2](../evidence/autonomous-architecture-pilot-2-results.md), [curriculum 1](../evidence/autonomous-architecture-curriculum-1-results.md), [curriculum 2](../evidence/autonomous-architecture-curriculum-2-results.md) |
| Timeout correction pilot (`large`) | Do more exposure and fixed semantics help? | 0 of 4 before and after | Negative | [RESULTS](RESULTS.md#timeout-correction-pilot-results) |
| Sensing: history lags, longer rays (offline probes) | Does history or range carry the direction? | history worse at this size; 24 m rays 34 to 28 degrees | Inconclusive for history; modest for range | [results](../experiments/diagnostics/SENSING_PROBES.md) |
| Deterministic full-graph readout (planner) | Is full-connectome execution repeatable? | ordered accumulation gives bit-identical replays on 167,184 neurons | Positive (engineering, this runtime) | [RESULTS](RESULTS.md#repeatable-full-connectome-execution) |

### Planner iteration outcomes (explicit controller, development rooms)

These are not learned results. Rejected entries were not selected.

| Candidate | Rooms | Outcome | Verdict |
| --- | --- | --- | --- |
| planner-1.1 versus 1.0, cohort 9500000 | `large`, 16 | 14 of 16 against 12 of 16, no collisions | Candidate; planner-1.0 remains the default |
| planner-1.2-exp.1, cohort 10000000 | `large`, 16 | 13 of 16 against 15 of 16 for 1.1 | Rejected |
| planner-1.2-exp.4 (momentum braking), cohort 11000000 | `large`, 16 | 12 of 16 against 15 of 16 | Rejected |
| planner-1.2, cohort 13000000 | `large`, 16 | 15 of 16, tied with 1.1 | Not selected (no success-rate advantage) |
| planner-1.3-exp.4 | `large` and `maze` retained | 2 of 2 large retained fixed; maze timeouts | Partial |
| planner-1.3-exp.9 | `large` | 6 of 6 retained, 8 of 8 fresh | Positive on development rule |
| planner-1.3-exp.11 | `maze` | 2 of 2 retained, 5 of 8 fresh | Fresh result missed its 7 of 8 rule; launcher still selects it |
| planner-1.3-exp.13 (0.4 grid) | `maze` retained | 0 of 8 (all timeouts) | Rejected |
| planner-1.3-exp.14 (surface fallback) | `maze` retained | 0 of 8, one collision | Rejected |
| planner-1.3-exp.15 (speed 1.3) | `maze` retained | 4 of 8 | Rejected |
| planner-1.3-exp.16 (visit pressure) | `maze` retained | 4 of 8 | Rejected |
| planner-1.3-exp.17 (alignment) | `maze` retained | 5 of 8 | Rejected |
| planner-1.3-exp.18 (observed-clearance reference) | `maze` retained | 5 of 8 | Rejected |
| planner-1.3-exp.19 (neural-ray handover) | `maze` retained | 6 of 8 | Rejected (fails 7 of 8) |
| planner-1.3-exp.20 and exp.21 | `maze` retained | 6 of 8 each | Rejected |
| planner-1.3-exp.22 (repeatable readout) | `maze` retained | incomplete at the wall limit (5 goals, 3 unfinished) | Inconclusive |
| planner-1.3-exp.23 (segmented readout) | `maze` retained | 6 of 8 | Rejected |
| planner-1.3-exp.24 (wall survey) | `maze` retained | 6 of 8 | Rejected (regressed two) |
| planner-1.3-exp.25 (clearance-aware handover) | `maze` retained, then fresh | 7 of 8 retained; 5 of 8 fresh | Retained gate passed, fresh gate failed; not promoted |
| planner-1.4-exp.2 (broad escape) | architectural, 21 | 18 of 21, regressed apartment | Rejected |
| planner-1.4-exp.3 (portal escape) | architectural, 21 | 19 of 21, no collisions | Candidate, not promoted |

## (e) Methodological lessons

- **Pool discipline matters more than any single number.** Several pools were used for selection and then reported. The experiment 7 gains were selected on reported pools and did not persist in the next experiment. The lesson is to separate selection pools from report pools, as the roadmap now requires ([RESULTS](RESULTS.md), [TRANSFER_SUMMARY](../experiments/reference-recovery/TRANSFER_SUMMARY.md)).
- **Single seeds and 32-episode cells are too noisy for the claims that were made early.** Five runs of one recipe differed by 11 episodes on `passages-wide`. The rule adopted after R1 is at least three seeds and 64 episodes per cell, and a difference under about 10 episodes of 32 is not a result ([VARIANCE_STUDY_RESULTS](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md)).
- **Winner's curse.** Best-of-N selection inflates numbers. The pilot checkpoint scored 21 of 32 on `passages-mid` on its selection pool, and 37 of 64 (58 percent) on a fresh pool. None of the five repeats of its recipe reached more than 13 of 32 on that profile. Experiment 7 numbers are optimistic for the same reason ([VARIANCE_STUDY_RESULTS](../experiments/variance-and-stability/VARIANCE_STUDY_RESULTS.md), [TRANSFER_SUMMARY](../experiments/reference-recovery/TRANSFER_SUMMARY.md)).
- **Frozen rules were applied without adjustment.** B1 missed its positive rule by one episode and was reported as inconclusive. B4 missed level B by 1.7 episodes and was reported as inconclusive. C1.1 and C1.2 failed their chain checks by about a half-episode and were reported as failed. The same discipline applied to failures and to positives.
- **Pre-declared checks that fail are failures.** Several checks failed narrowly. The chain check in C1.2 was missed by half an episode and the result was not reinterpreted.
- **Model-written diagnoses are hypotheses.** The sensor, memory and wiring explanations were each proposed and then tested. The reward-hover explanation was refuted. The "same-cell deadlock" was confirmed for the apartment case by trace inspection, while the atrium and warehouse failures had different causes ([architectural recovery diagnostic](../evidence/architectural-initial-navigation-results.md)).
- **Declare the evaluation mode.** A deterministic-only result can invent or hide a trade-off. The pilot's `passages-wide` result changed from 14 to 55 of 64 with the mode alone.
- **Tests, finite losses and reload checks are not navigation evidence.** Many documents state this explicitly. Smoke tests of 128 transitions verify pipelines only.
- **Keep failed corrections.** The planner iteration rejected about twenty variants, each with its outcome. Rejected variants are the record that prevents retuning on the same retained rooms.
- **Inspected pools become correction data.** Maze retained rooms, `large` development rooms and the level C headings are now inspected. Results on them cannot be presented as fresh.
- **Operational limits.** A first evaluation launch started 28 processes at once and restarted the machine. A resource guard was added to every fan-out ([PHASE1_PILOT_PROTOCOL](../experiments/variance-and-stability/PHASE1_PILOT_PROTOCOL.md)).

## (f) Open problems

- **Release gate.** Not met in any family. The 2M recipe is close on `passages` (36 to 42 of 64) and on medium (49 to 55 of 64), but collisions are 8 to 16 against the limit of 3 on `passages` and 5 to 11 on medium.
- **Large rooms and mazes.** No learned policy has navigated them. The best learned value is 2 of 32. The explicit planner works on development rooms, but maze reliability is 5 of 8 on the fresh suite, and the large planner's fresh result (8 of 8) was not reached on an independent pool.
- **Level B.** Inconclusive: mean 18.3 of 64 against a threshold of 20. More seeds or more budget are the open lever. The reserved final pool (960000 to 969999) is unopened.
- **Level C.** Positive by rule, but uneven. `courtyard` regressed, `apartment` and `atrium` did not move, and collisions are unchanged at 27 to 37 percent.
- **Memory.** The R6 retest with three seeds and 64 episodes per cell has not been run ([ROADMAP](../../ROADMAP.md)).
- **Connectome contribution.** Unresolved. The matched chain did not reach the retained level; with four seeds per arm the `passages` difference is bounded to -7.6 to +15.1 episodes of 64, and an equivalence verdict within 10 would take about seven seeds per arm if the true difference is near the observed +3.75.
- **Reserved pools.** Level A report (940000 to 949999), level B final (960000 to 969999), level C final headings (970000 to 979999) and the Phase 5 report pools have not been opened.
- **Next training step.** The decision was to consolidate the repository and write up first. One more training step aimed at collisions and at `large` and `maze` stays open ([ROADMAP](../../ROADMAP.md)).
