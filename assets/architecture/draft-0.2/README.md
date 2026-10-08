# Architectural drafts 0.2

Original project designs released under the repository's [MIT license](../../../LICENSE). No external scans, images or building models are included. These are architectural prototypes, not reconstructions of real locations.

Six scenes: office floor, apartment, street block, atrium, warehouse and courtyard. Open [index.html](index.html) locally to inspect them in 3D, with a cutaway slider for the multi-level scenes. [gallery.png](gallery.png) shows oblique views and [plans.png](plans.png) shows floor plans cut at 2 m. Each named scene has matching `.obj`, `.mtl` and `.json` files; [manifest.json](manifest.json) records hashes, material counts and geometric checks.

The dashed routes are privileged feasibility references, not recorded flights. They must not be supplied to an autonomous controller. Draft assets are inspected development material, not reserved tests. No training or flight evaluation has been run on them.

Regenerate with `python -s scripts/build_architectural_scenes.py` from the repository root. See [the scene guide](../../../docs/ARCHITECTURAL_SCENES.md) for dimensions, controls, coordinate contracts and integration limits. Revision 0.1 is available in git history.
