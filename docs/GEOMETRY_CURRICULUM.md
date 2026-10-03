# Progressive maps and the geometry curriculum

The configurable generator supplies progressive room profiles, geometry measurements and a paired baseline/curriculum comparison. Map complexity and learned navigation are measured separately. The completed comparison and its limitations appear in [Results](RESULTS.md).

## Map profiles

The original `dense-v3` generator remains available with its original random stream, 32 × 32 × 12 room, 48 boxes, and 1200-decision limit. Existing suite fingerprints and launcher aliases are preserved. New profiles use `rooms-v4-profiled-passages`:

| Profile | Room dimensions | Total collision boxes | Partitions | Opening width × height |
| --- | --- | --- | --- | --- |
| `open` | 32 × 32 × 12 | 24 | 0 | No fixed openings |
| `passages` | 32 × 32 × 12 | 64 | 3 | 4 × 4 |
| `large` | 48 × 48 × 16 | 112 | 5 | 3.2 × 3.2 |
| `maze` | 64 × 64 × 20 | 192 | 8, plus 4 dead-end wings | 2.4 × 2.8 |

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

Occupancy samples the centers of a 32 × 32 × 16 grid and counts their union membership in boxes. Thin walls can be under- or oversampled. The separate summed box-volume fraction is exact for the new, nonoverlapping profiles. For legacy or externally altered overlapping boxes, that sum can double-count volume; the grid remains a union estimate. A larger obstacle count does not necessarily imply greater occupancy or difficulty.

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

`--map-profile` also accepts a JSON file containing the complete profile. Fields are `name`, `room_size`, `obstacle_count`, `wall_count`, `aperture_width`, `aperture_height`, `route_clearance`, `minimum_separation`, optional `branch_count` and `version`. The version must be `rooms-v4-profiled-passages`. Dimensions are bounded to 10–96 units, boxes to 256, partitions to ten and extra clearance to 0.05–0.35. Each branch requires an interior chamber and four collision boxes; configuration checks its opening width. A missing or zero branch count preserves already-frozen branch-free profiles. Configuration validation rejects apertures that cannot fit the declared clearance. Dense custom configurations can still exhaust the bounded placement attempts and fail explicitly. Frozen suites serialize the actual values, so editing a named preset or JSON file cannot silently change an existing experiment.

## Comparison design

The prepared experiment uses a fresh, audited suite under `runs/suites/geometry-v1.json`. It excludes all six historical suites and reserves these disjoint seeds:

| Split | Seed range | Geometry |
| --- | --- | --- |
| Training | 280000–280255 | Frozen `open`, `passages` and `large` variants for each of 256 seeds |
| Validation | 290000–290031 | 32 fixed `large` layouts |
| Final test | 300000–300063 | 64 fixed `large` layouts, untouched at launch and consumed at completion |

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

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

See [aggregate results](RESULTS.md) and [machine-readable completion evidence](evidence/geometry-v1-results.json).
