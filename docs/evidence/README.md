# Evidence index

`docs/evidence/` holds the public record of the development work: planner versions, the maze and architectural checks, the guided and neural-waypoint attempts on large rooms, and the diagnoses that were written between them. There are 60 Markdown documents, one public JSON file and two PNG figures. The controlled experiment series with protocols committed before their runs are indexed in [experiments/README.md](../experiments/README.md), and the chronological log is [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md).

These documents are working records rather than protocols. Many of them are development checks on maps that were inspected while the controller was being built, so they are not independent generalization evidence unless a document says so. Each one states its own scope in its opening lines. The status of the project is in [ROADMAP.md](../../ROADMAP.md).

Local run artifacts referred to in these documents (checkpoints, traces, full flight archives) are not in git. They live in `runs/` and `private/` and are named there as plain text.

## Planner development

Versions of the explicit observed-map planner (planner-1.x), from its first checks to the dual mapping and braking design. The planner is a reference controller and does not use a learned policy.

- [observed-map-v55-results.md](observed-map-v55-results.md): frozen v55 planner, eight reused optimization maps without collisions or timeouts, and a prospective check of new rooms.
- [planner-timeouts-v56-results.md](planner-timeouts-v56-results.md): diagnosis of timeouts on three inspected development failures and a local goal-margin correction.
- [planner-followup-v57-v60.md](planner-followup-v57-v60.md): speed, clearance and conditional recovery checks on three rooms whose v55 failures had been inspected.
- [planner-v60-development-results.md](planner-v60-development-results.md): paired development results of frozen v55 and v60 controllers.
- [planner-readout-v61-v63.md](planner-readout-v61-v63.md): diagnosis of distance readout and two unsuccessful route corrections.
- [planner-v61-development-results.md](planner-v61-development-results.md): paired development results of frozen v60 and v61.
- [planner-momentum-v64-results.md](planner-momentum-v64-results.md): actual-motion braking correction and its effect on collisions in the next room comparison.
- [planner-v64-development-results.md](planner-v64-development-results.md): paired development results of frozen v60 and v64.
- [planner-dual-v65-results.md](planner-dual-v65-results.md): separate neural mapping and safety ranges, and the offline inspection of the remaining timeouts.
- [planner-v65-development-results.md](planner-v65-development-results.md): paired development results of frozen v60 and v65.

## Maze

Room-aware planner work on the `maze` profile. None of these documents is a verified maze solution; the closing summary records the candidate and its limits.

- [maze-navigation-development-results.md](maze-navigation-development-results.md): development results of the room-aware planner on maze tasks, with the full annotated graph and original room geometry.
- [maze-opening-range-results.md](maze-opening-range-results.md): opening detection extended from 6 to 12 units only when the nearby detector finds no candidate, and its effect.
- [maze-clearance-fresh-results.md](maze-clearance-fresh-results.md): fresh-goal result of the frozen planner-1.3 candidate (five of eight, zero collisions, three timeouts).
- [maze-wrap-up.md](maze-wrap-up.md): closing summary of the maze work, the earlier-map regression result and the deferred fresh verification.

## Architectural scenes and planner-1.4

Work on the architectural scenes (level C in the experiment catalog): adapter checks, the full-connectome integration and the planner-1.4 revisions on the original objectives.

- [architectural-adapter-contract-checks.md](architectural-adapter-contract-checks.md): checks that the architectural world prototype matches the six revised scenes and their adapter contract.
- [architectural-fullgraph-integration.md](architectural-fullgraph-integration.md): public flight-world adapter and full-connectome environment for the revised architecture scenes.
- [architectural-initial-navigation-results.md](architectural-initial-navigation-results.md): planner-1.4-exp.1 on the 21 original objectives (18 of 21 goals, zero collisions, three timeouts).
- [architectural-escape-candidate-results.md](architectural-escape-candidate-results.md): planner-1.4-exp.2 on the same objectives (18 of 21, three timeouts), not promoted.
- [architectural-closing-results.md](architectural-closing-results.md): closing record of the architectural work, including the closing revision and the stop of further experiments.

## Autonomous learning on architectural scenes

Fresh PPO runs on the architectural scenes with no planner actions, and the completion protocol for large-room navigation.

- [autonomous-architecture-pilot-1-results.md](autonomous-architecture-pilot-1-results.md): first fresh planner-free PPO pilot on 15 situations in six scenes; zero goals in 457 training episodes and 0/6 on post-training validation.
- [autonomous-architecture-pilot-2-results.md](autonomous-architecture-pilot-2-results.md): structured PPO pilot on the full annotated connectome, with its outcome against the planner.
- [autonomous-architecture-curriculum-1-results.md](autonomous-architecture-curriculum-1-results.md): first bounded curriculum run on the architectural lessons, with original-goal validation.
- [autonomous-architecture-curriculum-2-results.md](autonomous-architecture-curriculum-2-results.md): second curriculum run with all annotated neurons and the full edge set, original goals validated, no planner actions.
- [autonomous-large-completion-protocol.md](autonomous-large-completion-protocol.md): what evidence is still needed before large-room autonomous navigation can be called complete; starts no run.

## Guided navigation and large-room learning attempts

Attempts to train a policy on the original `large` rooms, from guided initialization to a two-hour window. Each record reports that the original large-room goal was not met unless its own text says otherwise.

- [guided-navigation-v1-plan.md](guided-navigation-v1-plan.md): protocol for guided initialization of a brain-feature movement policy after a reward-only correction.
- [guided-navigation-v1-results.md](guided-navigation-v1-results.md): result of the guided initialization (zero of eight development goals on the original large rooms).
- [guided-navigation-v2-results.md](guided-navigation-v2-results.md): result of a further bounded guided run with the cumulative substantive budget reported.
- [guided-navigation-v3-plan.md](guided-navigation-v3-plan.md): matched critic-history isolation, the protocol for changing actor and critic history sharing.
- [guided-navigation-v3-results.md](guided-navigation-v3-results.md): result of the critic isolation run on the original large rooms.
- [guarded-navigation-v4-plan.md](guarded-navigation-v4-plan.md): bounded guarded PPO continuation after the failed critic isolation.
- [guarded-navigation-v4-results.md](guarded-navigation-v4-results.md): guarded PPO result, zero of eight development goals with eight collisions.
- [large-goal-v3-plan.md](large-goal-v3-plan.md): an interrupted large-room adaptation run and the persisted transition count at the interruption.
- [large-continuous-v4-plan.md](large-continuous-v4-plan.md): continuous large-room adaptation run, its launch record and its configuration.
- [large-continuous-v4-pause.md](large-continuous-v4-pause.md): record of the pause of the continuous large-room run and the state of the process when it was stopped.
- [route-progress-correction-v1-plan.md](route-progress-correction-v1-plan.md): protocol for an obstacle-aware reward correction, after the temporal readout arms found no validation goals.
- [route-progress-correction-v1-results.md](route-progress-correction-v1-results.md): reward-only correction on unchanged large optimization layouts, zero of eight development goals.
- [timeout-correction-pilot-v1-plan.md](timeout-correction-pilot-v1-plan.md): protocol of a timeout correction pilot, based on the timeout diagnosis (no training exposure to the original target, short discount horizon).
- [timeout-correction-pilot-v1-results.md](timeout-correction-pilot-v1-results.md): result of the 32,768-transition timeout pilot on the original large target.
- [passage-mastery-v2-results.md](passage-mastery-v2-results.md): four fresh runs (two methods, two seeds, 131,072 transitions each) on the single-opening `gate-long` target.
- [two-hour-navigation-plan.md](two-hour-navigation-plan.md): plan for the authorized two-hour window of corrections and training, with its stop rule.
- [two-hour-navigation-results.md](two-hour-navigation-results.md): results of that window, with the batches finished before its deadline.
- [directional-and-lookahead-results.md](directional-and-lookahead-results.md): directional attention and look-ahead correction, its autonomous training transitions and the zero-arrival student fragments.

## Neural waypoint, panorama and spatial sensing

Attempts to give the learned policy a route cue (a neural waypoint input), panoramic sensing and spatial readouts, and their diagnostics. The privileged waypoint diagnostic that uses the same idea in a controlled setting is in [experiments/diagnostics](../experiments/README.md#waypoint-diagnostic).

- [spatial-neural-v5-plan.md](spatial-neural-v5-plan.md): protocol for the spatial neural navigation correction after v4 failed all eight development flights.
- [spatial-neural-v5-data-audit.md](spatial-neural-v5-data-audit.md): audit of completed optimization fragments from the v5 run, with no optimizer step.
- [spatial-neural-v5-results.md](spatial-neural-v5-results.md): v5 training result, including the reload assertion failure after the full transition cap.
- [neural-waypoint-v6-plan.md](neural-waypoint-v6-plan.md): protocol for the neural waypoint correction after v5 reached zero of eight goals.
- [neural-waypoint-v6-results.md](neural-waypoint-v6-results.md): v6 result after 81,920 new transitions (guided and autonomous).
- [neural-waypoint-v6-diagnostics.md](neural-waypoint-v6-diagnostics.md): diagnosis of the v6 optimization data, with no new flight transitions.
- [panoramic-neural-v7-plan.md](panoramic-neural-v7-plan.md): frozen protocol for a panoramic correction after the waypoint run reached zero of eight goals.
- [panoramic-neural-v7-results.md](panoramic-neural-v7-results.md): v7 training result over its authorized physical transitions and supervised updates.
- [panorama-coverage-v8-results.md](panorama-coverage-v8-results.md): broader panoramic coverage correction, with its additional physical transitions and resumed student check.
- [portal-feedback-protocol.md](portal-feedback-protocol.md): protocol for passage perception and flight control through neural activity, written after v12 left original-large navigation unresolved.

## Memory and temporal readout

- [brain-memory-comparison-v1-plan.md](brain-memory-comparison-v1-plan.md): planned matched comparison of a temporal readout against the fixed reservoir, which was measured to fade quickly.
- [brain-memory-comparison-v1-results.md](brain-memory-comparison-v1-results.md): comparison result; added memory did not establish navigation on the original `large` distribution.
- [brain-memory-diagnosis.md](brain-memory-diagnosis.md): diagnosis of short brain memory and the temporal policy correction on the original sensors-v3 interface.

## Diagnoses

Written reviews of why a training or navigation attempt failed. Each one reads retained data or runs bounded checks; none of them is a performance claim.

- [critic-history-diagnosis.md](critic-history-diagnosis.md): diagnosis of the post-v2 controller and critic isolation, from retained optimization observations and checkpoints.
- [input-group-readout-diagnosis.md](input-group-readout-diagnosis.md): input-associated neural readout diagnosis after the guarded-PPO baseline reached zero of eight goals.
- [large-timeout-diagnosis.md](large-timeout-diagnosis.md): why the large-map runs timed out, including the question of treating deadlines as terminal.
- [panoramic-sensor-performance.md](panoramic-sensor-performance.md): measurement of the panoramic sensor cost and of GPU use during guided collection.
- [visible-fan-v5.md](visible-fan-v5.md): perception diagnosis of the original large spawn (nearest partition face and proximity ray range) and a visible-fan correction.

## Sensors and visualization

- [geometry-v1-results.json](geometry-v1-results.json): the one public JSON record, a geometry-v1 run record (protocol, source revision, 524,288 added transitions in total, and per-run validation counts). It is an explicit exception in `.gitignore`.
- [geometry-v1-maps.png](geometry-v1-maps.png): figure accompanying the geometry-v1 results (its contents are not described in a Markdown record).
- [ray-risk-v1-validation.png](ray-risk-v1-validation.png): validation figure for the ray-risk sensor work (no accompanying description in this folder).

## Coverage check

Every Markdown file in this folder is listed once under a topic above, and the JSON and both PNG files are listed under sensors and visualization. A check that each `.md` here appears exactly once is worth running when files are added.
