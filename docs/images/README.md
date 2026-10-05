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

The script intentionally replaces these named public figure files. It does not overwrite demo archives, train weights, or evaluate a policy. See the [README gallery](../../README.md#map-gallery) for task descriptions and measured results.

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
