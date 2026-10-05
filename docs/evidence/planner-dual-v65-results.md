# Separate neural mapping and safety ranges

V65 addresses two observed problems without replacing the full connectome: contextual range offsets caused false braking, and requested-direction braking did not cover every surface approached by inertia. Cleaning all mapping coordinates in v61/v64 improved known cases but regressed fresh goal attainment. V65 retains v60's mapping features and uses separate clean neural ranges for flight safety.

## Declared interface

[DualActivityBrain](../../fly_rl/connectome/dual_readout.py) advances all 167,184 neurons and 25,583,622 directed aggregated connections once per observation. From previous/current neural states and the known sensory projection, it emits:

| Coordinates | Meaning | Consumer |
| --- | --- | --- |
| 0–3868 | Original motion-stable features, including five percent panoramic context | Target/motion decoding and occupancy mapping |
| 3869–5668 | 1,800 recurrence-cancelled panoramic ranges | Requested-direction and actual-momentum braking |

World sensor count stays 3,869; neural feature count becomes 5,669. No raw sensor values are appended during reconstruction. The controller separates mapping and braking inputs before calling the existing flight rules. Both requested-direction and momentum checks retain the 0.25-unit endpoint tube and 0.27-unit stopping allowance. Physical collision detection, room geometry, and deadlines remain unchanged.

The new readout fingerprint, viewer width check, checkpoint contract, and schema-three development protocol declare this change explicitly. Tests confirm that the original prefix matches its preceding decoder exactly, added ranges match clean reconstruction within numerical tolerance, map evidence uses the original prefix, input features are not modified, and episode reset is independent. This is an engineered information construction, not biological vision or evidence of a wiring advantage.

## Known correction cases

The first four-instance flight declared a 12,000-physical-transition cap. It reached all four known collision/control goals without collisions or timeouts, using 9,040 physical transitions. These cases were previously inspected, so they are design evidence.

| Known room | V65 outcome | Steps | Full flown distance |
| ---: | --- | ---: | ---: |
| 10000005 | Goal | 1,688 | 138.81 |
| 10000006 | Goal | 2,202 | 194.93 |
| 10000007 | Goal | 1,404 | 123.43 |
| 10000008 | Goal | 2,260 | 211.82 |

Two original retained failures were then checked separately under a 4,000-transition cap per room:

| Known room | V65 outcome | Steps | Full flown distance | Ending target distance |
| ---: | --- | ---: | ---: | ---: |
| 9500001 | Goal | 1,782 | 139.71 | 0.45 |
| 9500014 | Timeout | 3,480 | 277.78 | 16.82 |

This adds 5,262 known-case transitions, with zero collisions. The stationary problem is corrected on the retained room, but the detour timeout remains. Shorter flight than another failed variant is not a successful route. No optimizer ran in these flights.

## Frozen fresh paired development

Before either arm ran, the protocol fixed sixteen new rooms, seeds 13000000–13000015, the source snapshot, graph/projection contract, readout widths, unchanged sensor count, original aliases, and a maximum of 81,920 physical transitions per arm. The wall-clock cutoff was 20:30 UTC on October 5. Both completed before it, without retuning.

| Arm | Goals | Collisions | Timeouts | Wilson 95% interval |
| --- | ---: | ---: | ---: | --- |
| Frozen v60 | 15/16 (93.75%) | 0 | 1 | 71.7–98.9% |
| Frozen v65 | 15/16 (93.75%) | 0 | 1 | 71.7–98.9% |

Fifteen rooms succeeded in both arms and room 13000013 timed out in both; neither arm had a unique success. Each used 55,984 physical transitions, totaling 111,968. Readout width differed as declared; initial layouts, graph data, base projection/model, and all source/alias preservation checks passed. Protocol SHA-256: `1f01a244654a24fa2b79222a704e8447ea45dd2a039266eb5b2fc879b481faa7`.

This matches the baseline's success rate on the measured suite while addressing retained false stops and contacts. It does not establish a general performance advantage, independent-final mastery, optimal routes, or biological benefit. The small sample leaves substantial uncertainty. The inspected failures are now design cases for any successor. [Every room, arrival step, and flown distance](planner-v65-development-results.md).

## Verification and viewing

The original distance reader and the dual reader each passed a separate full-graph smoke of exactly 128 physical transitions and one PPO update. Losses were finite, parameters changed, and deterministic CPU reload actions matched exactly. Temporary weights and metadata were deleted. These are pipeline checks, not substantive navigation training; no learned student success is claimed.

The generic residual history extractor now uses its declared feature width while retaining the original 256-feature legacy architecture and transfer behavior. The anatomical inspector also sums both dual-output gradient contributions through the reconstructed-drive inverse. A numerical perturbation test checks that derivative; it is a local sensitivity with previous state/history held fixed, not a causal biological explanation. Explicit planners still report sensitivity unavailable.

The v65 rendered check recorded 200 physical steps, finite activity, zero collisions, programmatically exercised reset/new-room/pause/camera handlers, and a separate brain window. Archive inspection passed all transitions and controller/readout source hashes. It ended before completing an episode. The [screenshot](../images/planner-v65-scene.png) therefore verifies rendering rather than navigation performance. Physical keyboard focus and extended interactive use remain broader QA tasks.

Use the explicit experimental version:

```powershell
.\launch-observed-map.cmd --planner-version v65 --seed 10000005
```

The standard launcher retains frozen v55 by default. Opening either version never trains or changes weights. Original learned-policy aliases were preserved, and no reserved final test was opened. Peak PyTorch allocated VRAM for these sixteen-instance checks was approximately 0.552 GiB; this excludes driver/renderer allocation and is not total GPU memory. Elapsed times are not a controlled throughput comparison.

## Remaining work

Diagnose the retained room 9500014 and shared fresh timeout 13000013 from their saved routes and maps. Freeze any narrow correction before measuring new layouts, and distinguish search/frontier choice from physical route execution. A larger independent final assessment needs its own predeclared access rule; the 80% independent-final objective remains open. Complete-route student learning, harder map profiles, and tests of connectome contribution remain separate roadmap work.

## Preserved original aliases

The following SHA-256 values matched before and after every recorded v65 flight. They are local artifact identifiers; the public repository does not ship these model binaries.

| Alias | Unchanged SHA-256 |
| --- | --- |
| `runs/dense-flight-policy.json` | `0ca02c89a6e17d16cfd949a56d46909cdf8638758a4536953e3e3d8ecef5e2db` |
| `runs/dense-flight-policy.zip` | `085963d6e95b2a25647e3e6dd7ad2dc61f8f3c61bbfaaf3ce0db2c067a287d66` |
| `runs/dense-policy.json` | `88c3e01eb7926dedfc1679f23b4a92c3783384782ad4203013afa8d38fe4e3c3` |
| `runs/dense-policy.zip` | `db0839a921ae8775bbad9dbea62c28ab3752d33dad0e8edcfa72c7dc1318cab6` |
| `runs/navigation-policy.json` | `aa47f7ef830c491958a16bd121497c703d689b2a9717c566ad9888de5815460f` |
| `runs/navigation-policy.zip` | `2aa3469b6c56fa7f29c56399a7737b29c1870432e005714782d8efe23bf6be01` |

The frozen v55 working source also retained SHA-256 `faec0e96a8fb6e26a88675a25c7fb4468593aca481e70a4e50d463c621053dd2`. Detailed statuses, traces, layouts, source copies, and journals remain local under ignored directories.


## Offline inspection of the remaining timeouts

After the frozen comparison completed, existing traces were inspected without new flights, optimization, or reserved-test access. The traces record every twenty physical steps, so these statements concern sampled frames rather than every intervening action.

| Room | Samples in the second half | Samples reporting a found grid route | Active momentum guards | Maximum estimated pose error |
| ---: | ---: | ---: | ---: | ---: |
| 9500014 | 87 | 86 | 0 | 0.00104 room units |
| 13000013 | 88 | 87 | 0 | 0.000553 room units |

Both flights continued moving: sampled second-half speeds ranged from approximately 0.145 to 2.60 units per second. Their positions covered more than 33 units along one horizontal coordinate. These are not the stationary false-stop behavior that motivated the clean-distance reader. A reported grid route is not evidence that the physical fly executes it efficiently. Late route-reference directions changed substantially, while some searches reached the 12,000-expansion cap.

The next hypothesis is an interaction between repeated replanning, route-reference selection, and inertial flight through detours. It remains a hypothesis: sampled traces do not isolate causality, and the earlier simple route-persistence variant failed. A successor should log route identity and progress, turn cost, and swept clearance, then check a narrow correction on retained cases before freezing new development rooms. Extending the deadline alone would conceal rather than explain this inefficiency.


The offline execution reporter makes these counts reproducible from retained traces. Room 9500014 had 24 reference-direction changes greater than 90 degrees across 173 eligible consecutive sampled pairs, including 13/86 in its second half. Room 13000013 had 15/174 overall and 8/87 in its second half. Each reached the search cap in one recorded frame. A reference can change because the fly moved, reached a waypoint, or changed its observed map; these counts do not identify erroneous replanning by themselves. The report hashes the input and preserves missing-field coverage. Eight synthetic reporter tests passed separately from the preceding 359-test full suite. [Command](../COMMANDS.md#offline-planner-execution-diagnostics).
