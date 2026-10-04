# Progressive maps and the geometry curriculum

The [continuous adaptation correction](evidence/large-continuous-v4-plan.md) retains live training episodes across chunk boundaries. Practice gates update the shared schedule, while ongoing episodes finish on their existing profile. Timeout penalties can now occur across chunks. Model archives still do not recover live worlds after a process restart.

The current [large-room adaptation](evidence/large-goal-v3-plan.md) starts from the trained single-wall controller. Its stages add a second opening, widen multi-wall rooms, increase room size, narrow openings, and finally restore all 112 boxes of the original `large` target. These preparation stages do not change the independent-test acceptance target. The two runs share trained initial weights and optimizer state and should not be described as fresh initializations.

The configurable generator supplies progressive room profiles, geometry measurements and a paired baseline/curriculum comparison. Map complexity and learned navigation are measured separately. The completed comparison and its limitations appear in [Results](RESULTS.md).

## Map profiles

The original `dense-v3` generator remains available with its original random stream, 32 Ã— 32 Ã— 12 room, 48 boxes, and 1200-decision limit. Existing suite fingerprints and launcher aliases are preserved. New profiles use `rooms-v4-profiled-passages`:

| Profile | Room dimensions | Total collision boxes | Partitions | Opening width Ã— height |
| --- | --- | --- | --- | --- |
| `gate-near` | 12 Ã— 12 Ã— 10 | 4 | 1 | 4.5 Ã— 4 |
| `gate-long` | 24 Ã— 12 Ã— 10 | 4 | 1 | 4.5 Ã— 4 |
| `open` | 32 Ã— 32 Ã— 12 | 24 | 0 | No fixed openings |
| `passages` | 32 Ã— 32 Ã— 12 | 64 | 3 | 4 Ã— 4 |
| `large` | 48 Ã— 48 Ã— 16 | 112 | 5 | 3.2 Ã— 3.2 |
| `maze` | 64 Ã— 64 Ã— 20 | 192 | 8, plus 4 dead-end wings | 2.4 Ã— 2.8 |

Each partition consists of four boxes around one opening; partition pieces count toward the total. Openings alternate across the room and in altitude. Endpoints may be reversed and initial heading is randomized. Remaining boxes do not overlap existing boxes or block a reserved route. The `maze` profile adds four side wings whose sole doorway creates a branch and a dead end. Neighboring partitions and the outside room wall close the other sides. Hidden clearance certificates connect the main passage to each wing and keep random boxes from blocking its entrance. This is a chamber-and-wing topology, rather than an arbitrary grid maze or a moving-obstacle task.

Every layout retains a collision-clear polyline through its openings. A segment must avoid each box inflated by body radius 0.16 plus the profile's extra clearance. The room boundaries must also leave that margin. This certificate proves a geometrically feasible center path; it does not prove that the flight dynamics can execute the path at any particular speed. The certificate is available to geometry inspection and evaluation references, never to the policy or its sensory projection.

The policy still receives 128 local distance rays with an 8-unit range, closing-speed projections, direct target direction/distance, and the existing flight-state values through the full fixed connectome. Larger maps do not grant global obstacle access, a longer sensor range, new neuron subsets, or a learned target detector. Sensors v3 scale altitude and target distance to the current room.

## Difficulty measurements and formulas

`geometry-v1-grid32-linf` reports obstacle count, room dimensions, occupancy, endpoint separation, certified-route length and detour, changes of direction, vertical travel, opening dimensions, clearance and episode duration. These are descriptors, not an empirically calibrated difficulty score.

For certificate points q_0 through q_m:

$$
L_{\mathrm{cert}}=\sum_{i=0}^{m-1}\|q_{i+1}-q_i\|_2,\qquad
D_{\mathrm{cert}}=\frac{L_{\mathrm{cert}}}{\|q_m-q_0\|_2}.
$$

Turns count angles greater than 15 degrees between consecutive segments. Vertical travel is the sum of absolute altitude changes. A high certificate detour is not a proof that every feasible route requires that detour; route quality during evaluation still uses the separate approximate visibility-roadmap planner.

Occupancy samples the centers of a 32 Ã— 32 Ã— 16 grid and counts their union membership in boxes. Thin walls can be under- or oversampled. The separate summed box-volume fraction is exact for the new, nonoverlapping profiles. For legacy or externally altered overlapping boxes, that sum can double-count volume; the grid remains a union estimate. A larger obstacle count does not necessarily imply greater occupancy or difficulty.

Clearance is a conservative lower bound obtained by 20 binary-search iterations on box inflation along the certificate, constrained by room boundaries, then subtracting body radius. It uses the infinity norm, not exact Euclidean distance to arbitrary surfaces. See [the generator and measurements](../fly_rl/simulation/map_profiles.py).

New layouts use a route-dependent allowance:

$$
T_{\max}=0.05\left\lceil\frac{\max(60,\;2L_{\mathrm{cert}}/1.5+15)}{0.05}\right\rceil.
$$

The nominal 1.5 units/s and factor two are engineering allowances, not measured optimal speeds. This avoids giving a 240-unit certificate the original 60-second budget. The reward formula, 0.45 goal radius, collision geometry and fixed 0.05-second dynamics remain unchanged. Per-layout limits are recorded; batched evaluation waits for the largest initial limit rather than assuming every episode has the same duration.

## View and inspect maps

From the repository root, open a new profile without training:

```powershell
.\.conda\python.exe -s -m fly_rl demo --map-profile large --dynamics coordinated --brain-view
```

This fresh controller is untrained. To inspect the existing v3 policy on the new distribution, explicitly allow transfer:

```powershell
.\.conda\python.exe -s -m fly_rl demo --map-profile large --dynamics coordinated --checkpoint runs/training/ray-risk-v1/selected/selected-policy.zip --transfer --brain-view
```

This command does not demonstrate that the old policy was trained for these passages. Use preview seeds, not reserved final-test seeds, for exploratory viewing. Reset and new-room controls retain the chosen profile. The HUD identifies the profile and box count. Archives record the complete profile, actual room geometry, episode limit and difficulty descriptors; saved-state replay restores the recorded room and flight state without running a brain.

Generate a geometry-only report and illustration:

```powershell
.\.conda\python.exe -s -m fly_rl map-report --output reports/geometry-preview.json --figure reports/geometry-preview.png --count 8
```

The figure shows the hidden certificate for human inspection. Its route is not passed to the controller. [The saved preview](evidence/geometry-v1-maps.png) uses seed 10 and includes all four new profiles.

`--map-profile` also accepts a JSON file containing the complete profile. Fields are `name`, `room_size`, `obstacle_count`, `wall_count`, `aperture_width`, `aperture_height`, `route_clearance`, `minimum_separation`, optional `branch_count` and `version`. The version must be `rooms-v4-profiled-passages`. Dimensions are bounded to 10â€“96 units, boxes to 256, partitions to ten and extra clearance to 0.05â€“0.35. Each branch requires an interior chamber and four collision boxes; configuration checks its opening width. A missing or zero branch count preserves already-frozen branch-free profiles. Configuration validation rejects apertures that cannot fit the declared clearance. Dense custom configurations can still exhaust the bounded placement attempts and fail explicitly. Frozen suites serialize the actual values, so editing a named preset or JSON file cannot silently change an existing experiment.

## Corrected practice-mastery protocol

`prepare-geometry-comparison` now prepares `geometry-v2-practice-mastery`. It starts with the frozen `gate-near` profile: one wide opening, no additional random boxes, and endpoints eight units apart longitudinally. `gate-long` changes longitudinal room size and endpoint separation while keeping the same opening, height, lateral size and box count. A first comparison should target `gate-long`; multiple partitions and `large` remain later tasks.

Preparation freezes at least 32 contiguous training seeds. The last 16, including their already-frozen profile variants, become a separate training-practice pool; both arms exclude them from optimizer rollouts. Validation and final seeds remain disjoint and never drive the curriculum. This adaptive use of practice is part of training, not independent generalization evidence.

At each round boundary, the curriculum checkpoint runs deterministic inference on two distinct batches of eight practice layouts at its current stage. Both batches must reach at least seven goals. If either fails, the stage stays unchanged regardless of transition count or stochastic training success. If both pass, the next round can advance one stage. Profiles change only on episode reset: stage zero uses only `gate-near`; later stages sample the current profile with probability 0.8 and distribute the remaining 0.2 uniformly over previous stages. A fixed budget can finish without advancing. Practice decisions and compute are recorded separately from optimizer transitions.

The updated gate state, outcomes, exposure and practice checks are saved in each new round checkpoint's metadata and restored for the next round. This preserves mastery across round boundaries, but still starts fresh episodes; it is not exact mid-episode resumption.

Selection considers trained rounds only, retaining initialization as a comparison control. Ending distances are rounded to six decimals for ranking, with stable input-order ties and baseline first for method ties. If no trained candidate reaches any validation goal, the run finishes with `no_successful_candidate`, without a winner directory, alias promotion or final assessment. A positive validation result is only a minimum eligibility condition, not achievement of the 80% target.

Prepare a fresh suite and an inert draft from the repository root:

```powershell
.\.conda\python.exe -s -m fly_rl prepare-suite --output runs/suites/passage-mastery-v2.json --map-profile gate-long --training-profiles gate-near gate-long --train-start 310000 --validation-start 320000 --test-start 330000 --train-count 64 --validation-count 32 --test-count 64
.\.conda\python.exe -s -m fly_rl prepare-geometry-comparison --suite runs/suites/passage-mastery-v2.json --output runs/configs/passage-mastery-v2-draft.json --rounds 8
```

Use a new path and new seeds, and add `--exclude-suite` for each local historical suite when freezing real experiments. No budget is supplied above, so the draft cannot train. An agreed budget, a newly configured plan with complete PPO rollouts per round, and explicit `run-geometry-comparison` are required to change weights. Frozen source changes require preparing a new configuration. Old launchers and checkpoints remain preserved.

Both new passage profiles were traversed with the actual coordinated flight controls on eight preview layouts each, using an oracle that follows the hidden certificate solely for physical QA. All 16 reached the goal without collision. This is evidence of dynamic feasibility for those examples, not learned-policy success or a universal reachability proof. The oracle is not wired into training, rewards, sensors or the demo.

The corrected pipeline passed a full-connectome CUDA smoke with exactly 128 transitions, one PPO update, finite losses and checkpoint reload. These checks establish operation, not successful learned navigation. The ordinary reward, discount and connectome equations are unchanged; reward and memory interventions still require separate evidence.

## Completed v2 single-opening comparison

The corrected experiment completed 524,288 transitions in 60.4 minutes, including initialization, training, practice, validation and final assessment. Target validation selected baseline seed 42, round seven, at 114,688 lifetime transitions. Selected validation goals were baseline 42: 30/32, baseline 73: 25/32, curriculum 42: 29/32, curriculum 73: 1/32.

The curriculum seed 42 passed both gate-near practice batches at round five (7/8 and 7/8) and entered gate-long; seed 73 never advanced. Later seed 42 gate-long practice checks failed, ending with 0/8 and 4/8. Practice controls progression and is not independent evidence of generalization. The gate prevented seed 73 from being moved to a harder training stage merely because time elapsed.

The frozen baseline winner's only final assessment reached 61/64 goals (95.3%), zero collisions and three timeouts, with Wilson 95% interval 87.1-98.4%. The untrained control reached zero goals, zero collisions and 64 timeouts, interval 0.0-5.7%. This demonstrates single-opening performance and does not establish success in the earlier large maps, a curriculum advantage, biological benefits or a paired final comparison. The final pool is consumed. All six original launcher aliases retained their before/after hashes. [Full aggregate evidence](evidence/passage-mastery-v2-results.md) records every practice round and selected validation checkpoint.

## Historical v1 comparison design

The prepared experiment uses a fresh, audited suite under `runs/suites/geometry-v1.json`. It excludes all six historical suites and reserves these disjoint seeds:

| Split | Seed range | Geometry |
| --- | --- | --- |
| Training | 280000â€“280255 | Frozen `open`, `passages` and `large` variants for each of 256 seeds |
| Validation | 290000â€“290031 | 32 fixed `large` layouts |
| Final test | 300000â€“300063 | 64 fixed `large` layouts, untouched at launch and consumed at completion |

Schema 3 freezes each variant's configuration, layout and geometry hashes, metrics, and the final-pool fingerprint. Loading audits all variants. Structural inspection of the reserved geometry is not a policy assessment, but exploratory policy viewing on those final seeds would consume their independence.

Baseline always trains on `large`. The intervention samples one of the three training profiles at episode reset. Both arms use the same fresh v3 archive for each initialization seed, empty optimizer state, full annotated graph, PPO settings, ordinary rewards, train seed pool, validation layouts and declared transition budget. Their geometry exposure and compute time can differ; equal transitions do not imply equal wall time.

Let n be globally added transitions, including the offset from prior rounds, and N the declared per-seed budget. The stage is min(2, floor(3n/N)):

| Budget progress at reset | `open` probability | `passages` probability | `large` probability |
| --- | --- | --- | --- |
| First third | 75% | 20% | 5% |
| Middle third | 20% | 60% | 20% |
| Final third | 10% | 20% | 70% |

An episode retains its chosen profile until termination. These are reset probabilities, not promised proportions of transitions: longer episodes contribute more steps. Checkpoints and progress records retain actual transitions, reset counts, and success/collision/timeout counts by profile. Round offsets preserve the declared schedule; resumption still starts fresh episodes and is not an exact mid-episode replay. Validation and final outcomes do not control stage progression. Combining this intervention with risk shaping is rejected.

Validation alone selects a checkpoint round, initialization seed and method, ranked by success, then fewer collisions, then lower mean ending distance. Baseline wins an exact method tie. One frozen winner and one untrained controller are assessed once on the reserved final pool. This is not a paired final comparison of both methods. Original launcher aliases are never promoted by this runner; hashes before and after are recorded.

The completed configured comparison used `runs/configs/geometry-v1-approved.json`: 524,288 total added transitions, 131,072 per method and initialization seed, seeds 42 and 73, batch eight and two rounds. The earlier budget-required drafts remain inert preparation artifacts. The recorded source snapshot identifies the implementation used; later documentation and viewer labeling changes do not reinterpret its learning results.

Do not rerun the completed configuration or its consumed final pool. A later comparison needs a new versioned suite, declared budget and frozen source. Preparation without `--steps-per-seed` creates a nontraining draft. `run-geometry-comparison` is an explicit weight-changing command.

## Verification and interpretation

The unit suite checks deterministic layouts, clear certified paths, opening collision geometry, scalar/vector ray agreement, profile bounds, hidden-route independence, curriculum reset boundaries, global transition accounting, frozen variants, strict map checkpoint contracts, matching evaluation geometry, heterogeneous time limits and saved-state replay. Whole-graph CUDA verification is separate; its opt-in optimizer smoke is exactly 128 transitions and one PPO update, with finite losses and checkpoint reload.

The geometry implementation passed 117 tests before publication cleanup; [Verification](VERIFICATION.md) records the final repository checks. The final 12-second, batch-one whole-environment inference benchmark measured about 247 transitions/s for `open`, 204 for `passages`, 149 for `large` and 101 for the four-branch `maze`, with 0.298 GiB peak CUDA allocated memory after initialization. This excludes rendering, initial data auditing and optimizer work; it is not a measured training speed or an exact experiment-duration estimate. All 167184 neurons and 25583622 directed edges were retained. The only optimizer smoke passed with finite losses and checkpoint reload; its 128 transitions happened to remain in `open` episodes, so it does not establish learned performance across stages. Stage switching and the other profiles are covered by separate reset tests and full-graph inference checks. The final whole-graph verification matched the current source hashes and added no optimizer updates.

```powershell
.\.conda\python.exe -s scripts/verify_geometry.py --suite runs/suites/geometry-v1.json --output runs/verification/NEW-DIRECTORY --benchmark-seconds 12 --optimizer-smoke
```

This verifier audits historical geometry without rerunning historical policy tests, proves paired fresh initialization, benchmarks sensors/physics/brain/policy together, and checks unchanged aliases and an unconsumed pool before launch. It does not execute the substantive comparison; the completed final pool is now consumed. Measured local results are recorded in [public verification](VERIFICATION.md).

Procedural diversity is motivated by [Cobbe and colleagues' Procgen study](https://proceedings.mlr.press/v119/cobbe20a.html); staged task distributions are a hypothesis informed by [Klink and colleagues' curriculum research](https://www.jmlr.org/beta/papers/v22/21-0112.html). Neither paper establishes that these presets or this schedule improve our fly controller. The existing near-goal curriculum and ray-risk penalty did not beat their respective normal-training controls on the declared validation ranking. A new geometry curriculum needs its own evidence.

## Completed comparison

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0â€“5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

See [aggregate results](RESULTS.md) and [machine-readable completion evidence](evidence/geometry-v1-results.json).


## Guaranteed target exposure

The opt-in target_envs setting reserves environment indices 0 through target_envs-1 for the final profile from initialization. Each continues to use that profile after natural resets. Other environments follow the original practice-mastery schedule. The count must be an integer smaller than batch size so at least one environment remains in the curriculum. With fixed batch size B, K dedicated environments and N transitions, dedicated target exposure is N*K/B; completed rollouts make this exact. Other curriculum environments may add further target exposure after reaching its stage.

The lane allocation is part of the saved protocol and continuous-session contract. Changing it on resume is rejected. Zero retains earlier protocols. Practice success still controls the non-target curriculum; validation and test never control it. [The correction pilot](evidence/timeout-correction-pilot-v1-plan.md) keeps its current stage fixed to diagnose the combined changes.

## Temporal comparison completion and continuation

The [matched memory comparison](evidence/brain-memory-comparison-v1-results.md) completed with 0/8 original-large validation goals in both arms. Dedicated target lanes delivered exactly 32,768 target transitions per arm, so this result is not attributable to zero target exposure. The stage-four mixture was fixed, with no practice-based advancement. Temporal features did not resolve navigation within this budget. Cumulative substantive use is 450,560; 73,728 transitions remain. No reserved final test was consumed. Work stops here for later diagnosis of reward components and detour behavior before a new intervention.
