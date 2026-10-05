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
