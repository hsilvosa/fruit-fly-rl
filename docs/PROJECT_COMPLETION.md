# Project completion plan

Updated October 7, 2026. This is the current order of work and supersedes earlier next-step lists. It does not authorize new training or consume a held-out test. Each substantial experiment needs an agreed additional budget before launch.

## What completion means

The deliverable is a learned virtual fly that reaches goals autonomously in 3D rooms, large rooms, mazes and the current synthetic architectural scenes. The evaluated student's flight actions must come from the learned policy. An explicit planner may be a reference or an optional imitation teacher, but cannot choose the student's evaluation actions. The full annotated MaleCNS v1.0 graph remains in the connectome controller.

A planner demonstration, successful nearby lessons, finite losses or a compatible checkpoint alone do not complete this goal. Historical medium-room success remains valid on its original distribution; it is not evidence for architectural navigation. Current architectural learned validation is 0/6. The mixed curriculum is implemented and smoke-tested, but not selected as the next run: first recover the working learned reference.

## 1. Recover the successful learned reference

Identify which exact checkpoints produced the historical medium dense-room results, including 50/64 (78.1%), 45/64 (70.3%) and 48/64 (75.0%). Trace each result to its checkpoint hash, source revision, observation contract, connectome/readout fingerprint, dynamics, reward, training budget, initialization and evaluation pool. Verify the result records rather than assuming a current alias still points to the winner.

Create a reference manifest and a documented launcher for the selected policy. Preserve the original files and source bytes. Replays on previously evaluated rooms are reproducibility checks, not new independent tests. Use a bounded development suite to establish current behavior on the original task. Select the reference using existing evidence and development data, not a new reserved test.

Exit criterion: a loadable, traced learned policy reproduces its documented input and physics contract, its preserved result records are auditable, and its current development behavior is recorded. If the checkpoint or historical runtime cannot be recovered, document that explicitly and reconstruct the same experiment before attributing the failure to map difficulty.

## 2. Transfer the reference and locate the regression

Compare the original medium task, structured large rooms and architectural tasks using frozen checkpoints and a declared development protocol. Preserve the reference on its original interface. Audit sensor scaling and range, goal coordinates, action meaning, steering, reset/history state, collision geometry, reward and episode deadlines.

If interfaces differ, either keep the original compatible observation adapter or introduce a versioned transfer method with explicit retained and newly initialized parameters. Never call an incompatible checkpoint load a successful continuation. Record the difference between a retained policy, a transferred policy and fresh initialization. Use a matched fresh policy only as a declared control, not an unannounced replacement for the working reference.

Exit criterion: observed failures are classified with recorded trajectories and reproducible checks; an adaptation path is demonstrated without modifying protected sources or aliases. Maintain a frozen medium-room regression suite. Report every lost reference success and do not promote a candidate that regresses the agreed reference gate.

## 3. Learn complete routes progressively

Start the next substantial experiment only after steps 1 and 2 determine the initialization and interface. Keep exposure to original navigation goals from the start. Nearby straight-path lessons can help flight control but must not replace obstacle detours, doorway crossings and full routes. Increase map complexity after demonstrated task mastery; retain simpler tasks to check forgetting.

The implemented mixed runner is one candidate, not a proven fix. Optional imitation must have separate teacher collection and imitation budgets, followed by planner-free student evaluation. Prefer one justified change per bounded experiment. Record training transitions, optimizer updates, lesson stage, original-task outcomes, initialization and all interrupted episodes. Declare training seeds, validation cases, selection rule and budget in advance. Use at least two training seeds for the final candidate comparison, subject to an agreed budget.

Exit criterion: the frozen selected learned candidate meets the declared development gates on medium rooms, large rooms, mazes and architectural routes, and retains the medium reference's accepted regression performance. Development success is permission to proceed to final assessment, not a final generalization claim.

## 4. Freeze and independently assess

Inventory previous pools first. Previously inspected rooms and the consumed large-room 0/64 final pool cannot be renamed as new held-out evidence. Reserve new scene/layout seeds, task situations and, where supported, architectural geometry variants before candidate selection. Keep their geometry and outcomes hidden until the candidate and protocol are frozen. The current architectural scenes are synthetic designs, not reconstructions of real buildings.

Proposed release gate: at least 52 successes in 64 completed episodes (81.25%, satisfying the 80% point-estimate target) in each of four separately reported families: historical medium dense rooms, structured large rooms, mazes and synthetic architectural scenes. Balance the architectural sample across all six scene types with at least eight episodes per type. This last family tests new situations/layouts only to the extent the generator supports them; shared inspected geometry cannot establish unseen-building generalization. Declare a maximum collision rate of 5% per family, allowing at most three collisions out of 64. Timeouts count as failures. Report the Wilson 95% interval, per-scene outcomes, path length and flight time. An 80% observed rate does not mean the confidence interval's lower bound is 80%.

Before evaluation, finalize these proposed gates, sampling rules, physical/evaluation budget and source hashes. Run the selected candidate once on its reserved final pools. Do not select another checkpoint or tune after seeing them. A failed final gate means the release objective remains open; any later independent assessment requires a separately reserved pool and protocol. The small introductory room remains a functional demonstration and regression check, not a substitute for these gates.

Also report a matched learned control without connectome activity and the frozen planner reference. Match information, dynamics, tasks, seeds and learning budget as far as possible; record differences and uncertainty. Lack of connectome advantage does not invalidate a working project, but forbids claiming that the biological graph improves or is necessary for navigation. Keep comparison and navigation acceptance distinct.

## 5. Prepare the release

Choose a numbered release and immutable selected checkpoint. Provide explicit launch commands for each supported map family and label learned, planner and untrained modes clearly. Opening the viewer must never train. Verify reset, new-room controls, free camera, simulation speed, brain visualization, logging/replay and clean shutdown with the release checkpoint.

Document installation in the project Conda environment, tested dependency versions, hardware expectations, full-connectome data download/checksums, source licenses and original publisher attribution. Publish concise results tables, representative success and failure videos/images, formulas and optimization details, reproduction commands and honest limitations. Store large data and model artifacts through a declared distribution method rather than accidentally committing them. Audit Git ignore rules, tracked files and public links. Tag the release only after the functional and performance gates pass. Work remains on navigation-development; push commits for the user's GitHub PR, without creating the PR automatically.

Exit criterion: a fresh installation can retrieve the specified data and checkpoint, open an autonomous learned demo, reproduce the reported evidence and inspect all limitations. The project is complete only when this release checklist and the navigation gates are met.

## Deferred scope

Real building scans, reconstructed streets, moving obstacles, wind, sensor noise and sim-to-real deployment follow the first learned-navigation release. Existing architectural map designs remain useful development assets. Real-world geometry requires provenance, suitable licenses, unit/scale checks, traversability validation and a new generalization protocol; it is not achieved by labeling current box geometry realistic.

## Immediate next action

Recover the historical successful learned checkpoints and create the reference manifest. Do not launch the pending mixed experiment merely because its runner is ready. First agree the reference-preserving transfer experiment and its additional budget.

## Status update, October 7, 2026

Step 1 is complete for evaluation. The historical winners are recovered, hash-verified and replayed with exact per-episode agreement on their recorded validation pools. See [HISTORICAL_REFERENCE.md](HISTORICAL_REFERENCE.md). Frozen historical policies succeed on medium dense rooms and fail on partitioned `passages` and `large` rooms in a 16-episode development ladder. Step 2 (failure classification from trajectories, regression suite, transfer adaptation) is open. No training has been launched.

Reference-preserving transfer experiment 1 (65,536 added transitions per arm) accepted no candidate: the retained policy stayed at 24/32 on the medium regression pool and scored 0/32 on `passages`, and the fresh control reached 11/32 and 0/32. See [REFERENCE_TRANSFER_RESULTS.md](REFERENCE_TRANSFER_RESULTS.md). The next step is to record and classify `passages` failures before choosing a larger budget, an intermediate map or a planner-imitation stage.
