# Architectural navigation development

The architectural stage uses the user's six architecture-0.2 designs and 21 original situations. These are realistic synthetic interiors and streets, not reconstructions of real locations. The maze experiments are closed for this iteration; this stage does not reopen them.

## Controller and inputs

Planner-1.4-exp.1 is an explicit observed-map controller. Simulated v6 observations enter the complete MaleCNS recurrent graph; segmented dual neural features provide its mapping and braking inputs. The controller receives known scene dimensions and decoded target direction/distance. It does not receive the connecting reference polyline, true pose, collision boxes or doorway coordinates. The environment retains geometry for physical simulation and logging.

The separate architectural grid has 0.25-meter cells. Room dimensions determine altitude and distance decoding and grid extent. Coordinated flight, inertia, a 0.16-meter body radius and swept collision checks remain active. Transparent glass is physically solid. Scene and situation changes clear neural state, controller memory and history. This is an engineered navigation experiment, not a biological flight model.

## Initial original-objective check

The initial check covers all 21 documented situations in scene order, with seed 42 for each heading. It preserves the original starts, goals, collision geometry and per-situation physical deadlines. It runs at most 32,768 physical transitions and 600 seconds after initialization. No optimizer, training, checkpoint promotion or reserved final test is involved. The complete runtime and geometry fingerprints are recorded before flights, and protected checkpoint aliases are compared before and after.

A goal requires reaching within the existing target tolerance before the physical deadline without colliding. Collision and timeout are failures. If the overall budget expires, the active case is incomplete and unattempted cases remain unmeasured; neither is counted as a timeout. Source changes abort the check. Existing output directories cannot be overwritten or restarted.

The current run is stored in runs/diagnostics/architecture-initial-navigation. Its protocol, status and sampled controller/flight traces distinguish actual neural execution from asset geometry checks. These inspected designs are development data; success on them is not independent generalization evidence.

The bounded runner is scripts/check_architectural_navigation.py. Running it is an explicit verification action, separate from opening the viewer. Its output must use a new directory; it never trains.

## Demonstration and remaining work

Use launch-architecture.cmd for live flight and the separate activity window. N changes situation, G changes scene, R resets, C changes camera and Shift boosts simulation speed. [Launcher and controls](ARCHITECTURAL_SCENES.md#interactive-architectural-demo) document scene selection.

Full-objective results are pending. After this initial check, use completed traces to distinguish geometry, sensing, map search and flight-control failures before choosing a correction. Keep objectives and deadlines visible in the evidence. Future independent evaluation needs a separate licensed collection of real-place reconstructions or held-out designs; the current synthetic scenes cannot establish that claim.
