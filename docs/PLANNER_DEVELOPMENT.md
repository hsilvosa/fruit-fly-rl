# Frozen planner development comparison

This protocol compares frozen v55 and v60 on the same sixteen new `large` rooms. It follows the correction of three previously inspected timeouts. Those tuned cases remain design evidence; this prospective check is a separate development measurement, not a reserved final test.

## Predeclared contract

The October 5 comparison uses seeds 9500000 through 9500015, fixed before either arm executes. Preparation checks for overlap against retained suite manifests, plan files, and diagnostic statuses. It records those inventory hashes, source hashes, and original alias hashes in the ignored local protocol. This is a check of the retained records, not proof about unavailable experiments.

Both arms use sixteen parallel instances, full-connectome activity, the original `large` geometry, coordinated dynamics, sensors v6, eight history frames at stride eight, and the stable motion readout. V55 and v60 remain unchanged throughout. V60 is the conditional-recovery candidate described in the [follow-up report](evidence/planner-followup-v57-v60.md).

Each arm has a hard cap of **81,920 physical environment transitions**, for a maximum of 163,840 across both. Vector slots that have finished still step while other slots complete; those physical transitions are counted, but no additional episodes from those slots are scored. No optimization, training collection, checkpoint changes, or final-test access is part of this protocol. A timezone-aware wall-clock cutoff ends a run at the requested stop time even if episodes remain incomplete. Incomplete arms cannot produce the completed paired report.

The source contract covers navigation, connectome, simulation, the environment adapter, and verification runners. It is checked before an arm starts and after it finishes. Initial room fingerprints and the prepared brain fingerprint must match across arms. Audit-only true poses, boxes, and terminal states never enter the controller's action inputs.

## Commands

Use a new protocol filename and new output directories. Do not rerun the documented suite under a new version and describe it as fresh. Preparing or running another check requires its own declared budget and access rules.

```powershell
.\.conda\python.exe -s scripts/check_planner_development.py prepare --output private/planner-v60-development-protocol.json --seed-start 9500000 --deadline 2026-10-05T20:30:00+00:00
.\.conda\python.exe -s scripts/check_planner_development.py run private/planner-v60-development-protocol.json --arm v55 --output runs/diagnostics/planner-v60-development/v55
.\.conda\python.exe -s scripts/check_planner_development.py run private/planner-v60-development-protocol.json --arm v60 --output runs/diagnostics/planner-v60-development/v60
```

The example deadline belongs to the recorded October 5 run and expires. It must not be silently replaced to resume or extend that experiment. The local protocol SHA-256 is `6f7ee07d0bb29530c8862b4a108383a1aa3959565d9c44a67e763039d29b0707`.

Once both arms complete, the offline report validates their contracts before aggregating existing results:

```powershell
.\.conda\python.exe -s scripts/report_planner_development.py runs/diagnostics/planner-v60-development/v55/status.json runs/diagnostics/planner-v60-development/v60/status.json --output reports/planner-v60-development
```

This reporting command performs no environment steps. It refuses incomplete, incompatible, source-modified, budget-exceeded, or final-test results. Each run retains status, initial layouts, sampled traces, final observed maps, and source/alias checks locally. The public evidence report contains aggregate counts and per-room measurements rather than full machine logs.

## Interpretation

The October 5 comparison completed: v55 reached 12/16 and v60 reached 14/16, with zero collisions. There were twelve successes in both arms, two only in v60, and two in neither; both arms used 55,680 physical transitions. All source, alias, graph, and layout checks passed. See [complete per-room results](evidence/planner-v60-development-results.md). The short experimental viewer check separately passed 800 recorded steps, controls, finite activity, rendering, and archive inspection; it did not complete a navigation episode. The full suite passed 326 tests.

Report both frozen arms without retuning either on this suite. Show goals, collisions, timeouts, Wilson 95% intervals, and paired outcomes: both succeed, baseline only, candidate only, and neither succeeds. Distinguish total physical transitions from scored episode steps. Flown distance sums every scored physical displacement; it does not establish route optimality. Wall-clock time and peak allocated VRAM describe these checks, not a general hardware benchmark.

Sixteen rooms from one generator leave substantial uncertainty. A development point estimate above 80% is not the roadmap's independent final-test result. Inspecting these failures afterward makes them known design cases for any subsequent correction. A final claim still needs a frozen selection and an untouched, predeclared final suite.

## Experimental viewing and source preservation

The standard observed-map launcher retains v55. Select v60 explicitly to inspect the candidate:

```powershell
.\launch-observed-map.cmd --planner-version v60 --seed 8500012
```

The viewer labels experimental versions and opens live inference without training. Episode resets clear map, pose, and recovery state. Each experimental flight archive records the controller specification, primary source, viewer adapter, and inherited controller sources with SHA-256 hashes. Archive inspection detects missing or modified controller files. These are provenance copies, not a self-contained executable script; reproduce them in the matching package structure and dependency environment.
