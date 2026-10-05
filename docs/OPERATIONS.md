# Operations and saved information

## Launching

Use the project-local `.conda` interpreter or root launchers from the repository root. The `.cmd` wrappers invoke PowerShell explicitly. An installed environment does not need setup again for every launch. See [Commands](COMMANDS.md).

A source clone contains neither prepared data nor local checkpoints. Small-room launchers support an untrained fallback. The dense launcher tries its existing coordinated, legacy dense and legacy small-room checkpoints, and reports an error if none exists. For an explicit untrained profiled room, use:

```powershell
.\.conda\python.exe -s -m fly_rl demo --map-profile large --dynamics coordinated --brain-view
```

Opening a viewer does not train, modify policy weights or resume an experiment.

## Saved artifacts

| Location | Contents |
| --- | --- |
| `data/` | Source tables, prepared graph, body IDs, attribution, audits and checksums |
| `runs/training/<experiment>/` | Configuration, source snapshot, progress, checkpoints, validation, selection and any final assessment |
| `runs/demo/<UTC-time>-<unique-id>/` | A unique session archive with manifest, transition chunks, events, policy copy and optional full-neuron snapshots |
| `reports/demo.json`, `reports/demo.png` | Latest summary and preview, overwritten by subsequent demos |
| `reports/` | Named figures, diagnostics and QA outputs |
| `private/` | Detailed journal, decisions, original machine evidence and document backups |
| `docs/` | Public guides, equations, protocols and aggregate results |

These local data, model, recording and private folders are ignored by Git. Back them up independently. A compact public result is evidence of the reported measurement; it is not a backup of checkpoints or complete trajectories.

Live archives retain sensors, pooled brain features, commands, world states, geometry, rewards, terminal outcomes and provenance. Active anatomical inspection also records sampled observations, filter and selection events, and selected-neuron traces. Full 167,184-neuron vectors require `--record-brain`; 256 pooled features cannot reconstruct them.

## Timing and integrity

Physics uses 0.05-second simulated decisions. Selected-neuron observations are sampled every five decisions and full-brain snapshots every twenty. Current neural observations are labeled before-action. Read phase and timing metadata when aligning activity and movement, particularly for older archives.

A float32 full-neuron vector occupies approximately 0.638 MiB before compression. One snapshot per simulated second approaches 2.4 GB per simulated hour, plus trajectory data. Accelerated viewing increases storage according to simulated time. Compression depends on the recorded values.

Transition buffers flush in chunks of 128. Graceful shutdown flushes the tail and completes the manifest before optional screenshot capture. Abrupt termination can lose up to 127 buffered decisions. Snapshot or event times can therefore extend beyond the last retained transition. Transition chunks have checksums; snapshots currently have structural and value validation without equivalent per-file manifest checksum coverage.

## Shutdown and recovery

Escape finalizes the main session. Ctrl+C skips optional screenshot capture but still finalizes telemetry. Screenshot errors are warnings rather than a reason to discard the recording. Closing the brain window closes that view; B in the fly window can reopen it.

For an archive left marked `running`, inspect both files and the actual process. Status alone is insufficient. `recover` defaults to a dry run; `recover --apply` can mark validated retained data as interrupted. It cannot reconstruct an unwritten tail. Keep the original evidence.

Saved-state replay restores recorded geometry and motion without executing the brain. Anatomical snapshot replay remains separate proposed work.

## Training and resumption

Weight changes require explicit training commands. Use a new experiment directory and a declared budget. Check the real process together with `status.json`, nested `experiment.json` and `progress.json`, console logs and error logs. A stale `running` file does not justify restarting a live process.

PPO lifetime counters and added transitions are different quantities. Record both. Validation can select the initial controller if training does not beat its ranking; a completed training budget does not guarantee that the selected checkpoint contains those updates. Final outcomes must not select models or promote aliases.

Checkpoint resumption restores policy and optimizer information but starts new episodes. Loading alone does not restore the exact room, recurrent state, random streams or partial episode. Bounded comparison runners pass declared curriculum offsets between rounds; this is not exact mid-episode recovery. Preserve source, configuration, dataset, suite and checkpoint fingerprints for reproducibility.

## Public export

Detailed local records are excluded from the public tree. `.gitignore` and untracking do not remove records from earlier commits, which remain in the local development history. The `publication` branch starts from a new root commit containing the reviewed public tree, without development ancestors. The local `master` branch retains the development history and its original records. Use `publication` for a public Git remote; do not publish all local branches. No remote publication is performed by repository cleanup. An audited source ZIP is also available:

```powershell
New-Item -ItemType Directory -Path dist -Force | Out-Null
git -c core.autocrlf=false archive --format=zip --output=dist/fly-rl-public.zip HEAD
.\.conda\python.exe -s scripts/verify_publication.py . --archive dist/fly-rl-public.zip --output reports/publication-archive-qa.json
```

The export contains committed source and public documentation, without `.git`, private notes, data or models. `.gitattributes` still controls declared line endings even with automatic conversion disabled; the audit compares canonical Git content and accepts that declared conversion while rejecting content changes. Review the publication diff too: automated patterns cannot detect every confidential string. Preserve private backups locally and share the audited public branch or source-only export rather than assuming the development history has been sanitized.

## Temporary Windows file locks

Status files, recording manifests/chunks, preview images, and atomic checkpoint publication use bounded file-replacement retries for Windows errors 5, 32, and 33. The waits total at most 170 ms; persistent errors still propagate. The previous destination remains valid until a rename succeeds, and a failed rename retains its temporary file for diagnosis. This addresses observed transient status-write failures without suppressing genuine permissions or disk errors. Atomic visibility does not guarantee durability after power loss, and this does not permit simultaneous writers to the same status file.
