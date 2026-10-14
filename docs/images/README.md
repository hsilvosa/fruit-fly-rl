# Map-image provenance

The three PNG galleries render twelve configurations directly from `FlightWorld` and the versioned map profiles. They use preview seed 10, not a selected success or final-test seed. No brain, learned policy, optimizer, or flight trajectory is executed to make them.

| Image | Configurations |
| --- | --- |
| [Compact rooms](maps-small.png) | Original three-obstacle room, gate-near, gate-long, gate-two |
| [Medium rooms](maps-medium.png) | dense-v3, open, passages-wide, passages |
| [Large rooms](maps-large.png) | large-wide, large-narrow, large, maze |

Blue is the start and amber is the goal. Transparent collision boxes expose interior geometry; physical boxes are solid. Coordinates and aspect ratios use the actual room dimensions. The same preview seed does not mean different profiles are identical layouts or matched navigation experiments. No hidden certificate is drawn as if it were a flown route.

[maps-manifest.json](maps-manifest.json) records profile names, dimensions, collision-box counts, and geometry checksums. This is public figure provenance, not machine launch evidence or a navigation result. All figures are original project renders of synthetic rooms; they contain no downloaded dataset images.

Regenerate from the repository root after installing dependencies:

```powershell
.\.conda\python.exe -s scripts/render_map_gallery.py
```

The script intentionally replaces these named public figure files. It does not overwrite demo archives, train weights, or evaluate a policy. See the [README gallery](../../README.md#the-maps) for task descriptions and measured results.

## Experimental planner render

[planner-v60-scene.png](planner-v60-scene.png) is a Panda3D screenshot from the actual v60 viewer in the original `large` profile, seed 8500012. It is separate from the geometry-only galleries. The verification ran 800 physical steps with full-connectome activity, zero collisions, and no training. It ended before completing an episode, so the image is not a navigation result or a selected-success claim. The separate brain window was also exercised; this image shows the room window.

Recorded command:

```powershell
.\.conda\python.exe -s -m fly_rl demo --controller observed-map --planner-version v60 --seed 8500012 --offscreen --seconds 10 --speed 4 --brain-view --record-dir runs/verification/planner-v60-viewer --screenshot reports/planner-v60-viewer.png
```

The named public image is copied from that output after visual inspection. Its flight archive and QA reports remain ignored local artifacts. No downloaded anatomical or dataset image is included in this screenshot.

## Momentum correction diagnostic figure

[planner-momentum-v64.png](planner-momentum-v64.png) plots saved known-case flights in rooms 10000005 and 10000008, sampled every twenty decisions. It was generated with `scripts/plot_planner_diagnostics.py` from the retained v64 trace, then visually inspected. XY paths hide altitude, sampled lengths undercount full flight, and sampled guard events are not every braking decision. This is design evidence, not independent performance. [Counts and protocol](../evidence/planner-momentum-v64-results.md).

## Dual mapping/safety render

[planner-v65-scene.png](planner-v65-scene.png) is the actual Panda3D v65 viewer on the original `large` profile, requested seed 10000005. The controls check restores that seed after exercising new-room/reset handlers. The 200-step recording had finite activity and zero collisions, with a separately inspected brain window; no episode completed. It verifies rendering and archive compatibility rather than performance. Recorded command: `python -s -m fly_rl demo --controller observed-map --planner-version v65 --seed 10000005 --offscreen --seconds 5 --speed 2 --brain-view --record-dir runs/verification/planner-v65-viewer --screenshot reports/planner-v65-viewer.png`. The public image was copied after visual inspection; detailed flight records remain local.


## Remaining timeout diagnostics

[planner-v65-timeout.png](planner-v65-timeout.png) and [planner-v65-timeout-map.png](planner-v65-timeout-map.png) were generated from the retained v65 fresh-development room 13000013 after its frozen comparison ended. This room timed out in both v60 and v65. They show sampled physical positions and a final observed-grid slice, respectively; they are neither new flights nor selected-success examples. The route is an XY projection across altitudes, and the grid slice uses goal altitude. Unknown cells remain visible rather than being presented as measured free space. Both figures were visually inspected.

```powershell
.\.conda\python.exe -s scripts/plot_planner_diagnostics.py runs/diagnostics/planner-v65-development/v65 --seeds 13000013 --output reports/planner-v65-shared-timeout-plot
```

The local input trace SHA-256 is `8229f67bea1d3a10e7b1301c4a5e57da6be8e3e0a4d5274e179d92e52f5c1c54`. Its every-twenty-step sampling does not show all intervening actions. The public figures were copied from the generated output; the underlying trace and maps remain ignored local records. [Interpretation and limits](../evidence/planner-dual-v65-results.md#offline-inspection-of-the-remaining-timeouts).


`maze-first-arrival.png` shows completed planner-1.3-exp.8 diagnostic traces in retained maze rooms 14000000 and 14000001. The left flight reached the goal; the right timed out. It samples every twentieth position, shows true geometry only as an offline audit, and is not a geometry preview or independent test. Original layouts, telemetry, figure hashes, and plotting provenance remain in private/maze-first-arrival-figure.json.

## Report figures (`docs/images/figures/`)

Generated by `scripts/make_report_figures.py` (run `.conda/python.exe -s scripts/make_report_figures.py [maps] [results] [reservoir] [brain]` from the repository root). Map figures use only the geometry code. Result figures read the JSON summaries under `runs/training/` (local, not versioned; the numbers are tabulated in the [key numbers](../results/KEY_NUMBERS.md)). The reservoir figure loads the processed connectome and the edge-shuffled control. The brain figure flies one episode of the retained policy with the real connectome in the loop.

| File | Content | Source of the data |
| --- | --- | --- |
| `map-profiles-partitioned.png` | `gate-two`, `passages-wide`, `passages-mid`, `passages`, two seeds each, top-down with the certified route | geometry code, seeds 10 and 11 |
| `level-b-region-gallery.png` | eight maps of the level B held-out region (opening below 3.8 m, at least four partitions) | held-out sampler, seeds 950000 to 950007, difficulty 0.8 |
| `architectural-scenes-gallery.png` | the six synthetic architectural scenes with the route of each of the 21 situations | architectural scene builders |
| `budget-curve.png` | `passages` successes against added training transitions: B1, B2 and the three B3 seeds, with the start checkpoint and the release gate as references | B1, B2 and B3 evaluation summaries (pools 884000, 885000, 886000) |
| `connectome-control.png` | `passages` for the retained lineage and the fresh real and edge-shuffled arms at 2.88M and 4.88M transitions | C1.1 and C1.2 summaries |
| `four-family-gate.png` | success rate of the retained candidate in the four release families against the gate, with the planner on level C | B3, B4 and C1.P summaries |
| `shuffled-vs-real-reservoir.png` | in-degree, out-degree and weight histograms of the real connectome and of the edge-shuffled control | processed graph, shuffle seed 1 |
| `brain-activity-example.png` | one flight in a medium room, soma-position maps of neuron activity at three steps, the 256 pooled features over time and the population activity | retained policy stage 61, seed 801, pool 886000 seed 886003, deterministic |

All figures describe development pools and single evaluations; they are not final results.
