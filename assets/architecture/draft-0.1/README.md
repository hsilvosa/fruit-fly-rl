# Architectural drafts 0.1

Original project designs released under the repository's [MIT license](../../../LICENSE). No external scans, images or building models are included. These are architectural prototypes, not reconstructions of real locations.

Open [index.html](index.html) locally to inspect office, apartment and street layouts. [gallery.png](gallery.png) shows static views. Each named scene has matching `.obj`, `.mtl` and `.json` files; [manifest.json](manifest.json) records hashes and geometric checks.

The dashed route is a privileged feasibility reference, not a recorded flight. It must not be supplied to an autonomous controller. Draft assets are inspected development material, not reserved tests. No training or flight evaluation has been run on them.

Regenerate with `python -s scripts/build_architectural_scenes.py` from the repository root. See [the scene guide](../../../docs/ARCHITECTURAL_SCENES.md) for dimensions, controls, coordinate contracts and integration limits.
