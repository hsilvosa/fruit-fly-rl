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

The initial original-objective check completed at **18/21 goals, zero collisions and three timeouts**, with all cases measured. It used 11,829 full-connectome physical transitions, no training and no reserved test. Protected aliases and frozen sources matched. These inspected synthetic scenes are development evidence, not independent real-world generalization. [Per-scene and per-situation results](evidence/architectural-initial-navigation-results.md). After this initial check, use completed traces to distinguish geometry, sensing, map search and flight-control failures before choosing a correction. Keep objectives and deadlines visible in the evidence. Future independent evaluation needs a separate licensed collection of real-place reconstructions or held-out designs; the current synthetic scenes cannot establish that claim.

## Diagnosis from the completed traces

These observations come from the original check, sampled every 20 physical steps and at termination. They identify symptoms and candidate mechanisms; they do not establish the effect of an untested correction.

| Situation | Observed terminal behavior | Correction question |
| --- | --- | --- |
| Apartment: study-to-bathroom | Steps 1141-1200 stay near (9.46, 6.71, 1.02), 3.81 m from the goal. Route search reports no path after 4,013 expansions. Requested speed is zero, reference generation rises from 1060 to 1119, and recovery count stays at 17 while stall ticks reach 200. | Can local recovery choose a distinct, observed-clear escape reference when the current reference falls inside the same grid cell? |
| Atrium: void-climb-to-top-gallery | The final samples remain near the upper gallery, with 10 recorded portal crossings. A stationary phase at altitude 8.51 m changes into an approach reference pointing downward; final altitude is 7.93 m and goal distance 4.15 m. The minimum sampled distance was 3.71 m. | Is the portal transition selecting a previously traversed passage instead of committing to a feasible upward route? Inspect the observed route before changing altitude control. |
| Warehouse: aisle-run | A path remains available, but the last samples brake near (18.01, 8.10, 7.41), 12.37 m from the goal. Requested speed is zero at the final three samples; seven portal crossings and nine recoveries are recorded. Minimum sampled distance was 12.24 m. | Which sensed surface prevents the reference from being executed, and can an alternative observed-clear reference preserve collision margins? |

The inherited recovery implementation in portal_recovery.py refuses a veto when the reference cell equals the current cell. In the apartment terminal samples, the small reference offsets and rising stall count are consistent with that limitation. The saved traces do not contain the occupancy grid or exact cell identity, so this is a hypothesis to verify with a focused fixture and added diagnostics, not a proven complete root cause.

The next architectural correction should record route availability, reference cell versus current cell, braking clearance and recovery reason. Preserve planner-1.4-exp.1 and the original scene geometry, endpoints and deadlines. Test any new recovery on these three retained failures, then rerun all original situations to check regressions before declaring held-out evaluation. Increasing deadlines or moving goals would not demonstrate that the controller defect was corrected. No maze run is needed for this diagnosis.

Read-only recovery diagnostics are now implemented in architectural_diagnostics.py and included in future runner traces. They record current/reference cells, same-cell status, recovery eligibility and braking clearances. Two focused fixtures verify same-cell deadlock reporting, threshold classification and absence of controller/occupancy mutation. They do not verify a flight correction, and the historical 18/21 trace was not rewritten or re-evaluated.
