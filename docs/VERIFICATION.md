# Verification

Correctness, navigation performance and publication privacy are separate checks. [Results](RESULTS.md) records learning outcomes; this guide describes what the implementation checks cover. Complete local logs and original evidence are retained privately.

## Simulation and connectome

The progressive geometry implementation passed 117 tests before repository cleanup. Coverage includes deterministic layouts, clearance certificates, passage and branch geometry, scalar/vector ray agreement, swept collisions, flight controls, hidden-route independence, episode resets, frozen variants, curriculum transition accounting, checkpoint contracts and profile-aware replay. Historical suites regenerated their original 2,112 fingerprints.

Whole-graph CUDA checks retained all 167,184 neurons and 25,583,622 directed edges. The disposable optimizer smoke used exactly 128 transitions and one PPO update, reported finite losses and reloaded its checkpoint. Its sampled episodes remained in `open`; it does not demonstrate learning across curriculum stages. Other profiles and stage switching were checked separately through reset tests and inference.

The final 12-second, batch-one inference checks measured approximately 247, 204, 149 and 101 transitions/s for `open`, `passages`, `large` and `maze`, respectively. Peak CUDA allocation after initialization was approximately 0.298 GiB. These measurements include sensors, physics, brain and policy, but exclude rendering, data initialization and optimization. They are not training speed estimates.

## Viewer and recordings

The large-room fly view, separate anatomical window and saved-state replay were rendered and inspected. Reset, new-room and camera handlers were exercised; the anatomical view retained 140,033 official soma positions. Missing coordinates remain missing.

Unique demo archives retain trajectories and optional full-neuron snapshots. Saved-state replay restores recorded geometry and motion without running a brain. Pooled features cannot reconstruct the full neuron vectors. Shift scaling computes additional fixed-timestep decisions; achievable speed depends on load. Broader physical keyboard, focus, monitor scaling and extended multiple-window checks remain useful.

The post-cleanup viewer check loaded both a zero-transition checkpoint and the original trained dense policy. Labels and archive metadata correctly distinguished them, all displayed brain activity was finite, and no optimizer ran. Saved-state replay retained the recorded untrained label and executed no brain. Short rendered checks used preview seed 10, not reserved evaluation layouts.

Initial graphics captures in the restricted process were empty. The permitted driver execution produced valid decoded images of both flight views, both anatomical windows and replay; these were inspected. Capture failure remains optional and does not discard flight logs. Its warning now states that the preview was not updated, without claiming that an image was retained.

## Bounded comparison audit

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

The completion audit reads existing records only. It checks the four method/seed budgets, finite round losses, fresh paired initialization, frozen source snapshot, suite and configuration hashes, final-pool claim, selected checkpoint provenance and original aliases. It does not retrain or rerun final evaluation. Only the validation-selected winner and untrained control are final-tested.

## Publication QA

The final repository suite passed 126 tests, including nine publication regressions. Repository verification passed for 22 documents, 134 local links, 46 modules and 35 CLI help commands. All 46 original documentation/evidence backups matched their recorded SHA-256 checksums, and the private journal retained its original contents.

The publication guard rejects private or generated tracked files, detailed evidence outside the explicit public summary, unfinished result placeholders, personal absolute paths, common credential patterns and links to files unavailable in the tracked tree. Its regression cases cover private files, sensitive content, local-only links and an archive with an unexpected private entry.

The source-only ZIP is audited against committed Git blobs with newline conversion disabled during export. It contains no `.git` history. Detailed records remain locally backed up and ignored. The local `master` development history retains older private records. The separate `publication` branch starts from the reviewed tree without development ancestors; the release checks verify its root and current files.

Automated checks do not establish biological fidelity, global route optimality, arbitrary-distribution generalization or the absence of every possible sensitive string. Test counts establish covered correctness properties, rather than a learning-performance claim.
