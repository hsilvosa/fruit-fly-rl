# Versioning and revision order

Controller revisions describe the progression of a controller design. Read them as a number followed, when needed, by an experimental candidate number. The description explains what changed; the number explains where that revision belongs. A later number does not guarantee better navigation.

The current default is **planner-1.0**, and the latest numbered milestone is **planner-1.2**. Planner-1.1 and planner-1.2 remain experimental even though their names have no `exp` suffix. Choosing a milestone name, making it the demo default, and demonstrating reliable navigation are separate decisions.

## What each part means

The general form is `planner-MAJOR.MINOR[.PATCH][-exp.CANDIDATE]`.

| Part | When it changes | Example |
| --- | --- | --- |
| Major | A substantial change in controller architecture | A different planning architecture could begin the 2.0 series |
| Minor | A new mechanism or input/readout contract within the same architecture | 1.1 adds adaptive clearance; 1.2 adds the dual readout |
| Patch | A compatible correction to an existing revision | 1.0.1-exp.1 was a goal-margin correction candidate for 1.0 |
| Experimental candidate | Another distinct candidate targeting the same planned revision | 1.2-exp.1, then 1.2-exp.2, then 1.2-exp.3 |

Numbered milestones use the shorter two-part spelling, such as `planner-1.2`. A patch component appears when needed. This is the project's controller naming convention, not a promise of strict semantic-version compatibility for neural inputs or checkpoints. Only registered names are accepted by the CLI; `1.2.0` is not currently an alias for `1.2`.

## What comes first and what comes after

Within a planned minor revision, experimental candidates come before its numbered milestone:

```text
planner-1.1
  -> planner-1.2-exp.1
  -> planner-1.2-exp.2
  -> planner-1.2-exp.3
  -> planner-1.2-exp.4
  -> planner-1.2
```

The candidate sequence records development order. A candidate can fail and still belong in that sequence. Reaching planner-1.2 does not mean all earlier candidates were successful or that their changes were retained.

After planner-1.2, choose the next branch according to the change:

| Intended change | First candidate | Later candidates | Possible numbered milestone |
| --- | --- | --- | --- |
| Compatible correction | planner-1.2.1-exp.1 | planner-1.2.1-exp.2, and so on | planner-1.2.1 |
| New mechanism or input contract | planner-1.3-exp.1 | planner-1.3-exp.2, and so on | planner-1.3 |
| Substantial architectural change | planner-2.0-exp.1 | planner-2.0-exp.2, and so on | planner-2.0 |

The 1.3 branch is now implemented as experimental candidates for room-aware and opening-reference planning. The patch and 2.0 branches in this table remain examples. No planner-1.3 milestone has been selected. A branch may be abandoned without ever receiving a numbered milestone. The historical planner-1.0.1-exp.1 patch candidate, for example, exists without a planner-1.0.1 milestone.

Compare number components numerically: 1.10 comes after 1.9, and exp.10 comes after exp.9. A patch belongs to its minor branch: 1.2.1 follows 1.2 but precedes 1.3 in revision order. Development dates can differ from this order if separate branches are explored concurrently; use the experiment date and Git commit to establish actual chronology.

## Current development sequence

This is the order of the currently registered planner implementations. The historical aliases are retained so earlier evidence remains traceable.

| Order | Public revision | Change | Historical alias |
| ---: | --- | --- | --- |
| 1 | planner-1.0 | Frozen observed-map baseline | v55 |
| 2 | planner-1.0.1-exp.1 | Goal-margin correction candidate | v56 |
| 3 | planner-1.1-exp.1 | Higher cruise speed | v57 |
| 4 | planner-1.1-exp.2 | Known-free margin traversal | v58 |
| 5 | planner-1.1-exp.3 | Unconditional speed and clearance combination | v59 |
| 6 | planner-1.1 | Conditional adaptive clearance | v60 |
| 7 | planner-1.2-exp.1 | Clean distance ranges | v61 |
| 8 | planner-1.2-exp.2 | Route persistence | v62 |
| 9 | planner-1.2-exp.3 | Ray-consistent mapping | v63 |
| 10 | planner-1.2-exp.4 | Actual-motion braking | v64 |
| 11 | planner-1.2 | Contextual mapping plus clean braking ranges | v65 |

| 12 | planner-1.3-exp.1 | Room contract and committed references | room-aware-exp1 |
| 13 | planner-1.3-exp.2 | Higher unknown-cell cost | frontier-cost-exp1 |
| 14 | planner-1.3-exp.3 | Observed opening approach and crossing | portal-reference-exp1 |
| 15 | planner-1.3-exp.4 | Sample-aware opening and completed-plane memory | portal-reference-exp2 |
| 16 | planner-1.3-exp.5 | Multiple partially observed wall candidates | portal-reference-exp3 |
| 17 | planner-1.3-exp.6 | Beacon-aligned surface candidates | portal-reference-exp4 |
| 18 | planner-1.3-exp.7 | Distance-aware wall span | portal-reference-exp5 |
| 19 | planner-1.3-exp.8 | Clean-range occupancy | portal-reference-exp6 |
| 20 | planner-1.3-exp.9 | Bounded faster opening flight | portal-reference-exp7 |
| 21 | planner-1.3-exp.10 | Stalled-reference recovery | portal-reference-exp8 |
| 22 | planner-1.3-exp.11 | Same-opening center refinement | portal-reference-exp9 |
| 23 | planner-1.3-exp.12 | Goal-priority opening planning | portal-reference-exp10 |
| 24 | planner-1.3-exp.13 | Finer occupancy and voxel buffer | portal-reference-exp11 |

The [controller catalog](CONTROLLER_VERSIONS.md#complete-mapping) describes the status and evidence of each revision. The [results](RESULTS.md#latest-planner-experiments) explain why several intermediate candidates regressed and why the latest 15/16 result is a tie with its paired baseline, not proof of improvement.

## Choosing and recording the next revision

1. State the proposed change and whether it is a compatible correction, a new mechanism/input contract, or a new architecture.
2. Choose the corresponding patch, minor, or major branch. Use the next unused experimental candidate number on that branch.
3. Add a distinct implementation and register its public name, description, and permanent internal alias in [the naming table](../fly_rl/navigation/versions.py). Update [controller dispatch](../fly_rl/navigation/registry.py) without changing existing measured implementations or reassigning their names.
4. Verify selection, input contracts, independent resets, and recording provenance. A naming change alone does not require another training experiment.
5. Before navigation measurements, declare the baseline, layouts, budget, selection rule, and final-test access rule. Freeze sources and checkpoint hashes. Preserve failures as well as successes.
6. Record results and limitations before deciding whether to give the candidate a numbered milestone. Leave the default unchanged unless its promotion is separately justified and documented.

Do not rename an unsuccessful candidate to conceal its result. Do not reuse a revision number for different measured code. Implementation, a numbered milestone, default selection, and independent performance evidence should each be visible in the documentation.

## Other version numbers in the repository

| Object | Example | What it identifies |
| --- | --- | --- |
| Controller revision | planner-1.2 | A specific controller design |
| Project release | A separately assigned package/release number | The repository as a whole, including viewer and tools |
| Sensor or readout contract | sensors-v6, a readout fingerprint | The neural input/output interface and checkpoint compatibility |
| Room generator | dense-v3, rooms-v4-profiled-passages | A task or geometry contract |
| Dataset release | MaleCNS v1.0 | The source connectome data |
| Historical learned experiment | v34 | An earlier experiment, outside the planner numbering series |
| Experiment run | dual-readout-large-20261005-seed01 | One recorded execution, with its own budget, configuration, and source hashes |

These numbers do not advance together. Updating camera controls does not necessarily create a new controller revision. Selecting planner-1.2 does not change the room profile or prove compatibility with a learned-policy checkpoint. A controller name should be accompanied by its exact source hashes and experiment configuration when reproducing results.

## Commands and historical compatibility

```powershell
# List implemented revisions and their historical aliases.
.\.conda\python.exe -s -m fly_rl controller-versions

# Select the latest implemented numbered milestone explicitly.
.\launch-observed-map.cmd --controller-version 1.2
```

The prefixed name `planner-1.2` also works. Old arguments such as `--planner-version v65` remain accepted aliases. Historical run directories, checkpoint fingerprints, evidence filenames, and frozen source snapshots keep their original identifiers; new archives record the public revision alongside them. See [controller compatibility](CONTROLLER_VERSIONS.md#what-remains-unchanged).


## Exact source bytes

Frozen controller and connectome source archives are checked by SHA-256 over their exact bytes. Git preserves their original line endings through path-specific attributes, rather than converting them during staging or checkout. The bounded diagnostic runner follows the same rule. This makes the committed source match the measured source and archived hash; Python supports these preserved line endings. Other source and documentation keep the repository's normal line-ending rules. Do not reformat a measured implementation to normalize its endings or EOF: create a new revision when changing its bytes.

`planner-1.3-exp.14` follows exp.13 and tests supported-surface fallback plus close beacon handover. Its higher revision number denotes implementation order, not a measured improvement.

`planner-1.3-exp.15` follows exp.14 and tests bounded confined cruising with close goal handover. It remains experimental pending full-flight evidence.

`planner-1.3-exp.16` follows exp.15 and tests a bounded visit cost after weak beacon-distance progress. Higher numbering does not imply better navigation.

`planner-1.3-exp.17` follows exp.16 and combines clean mapping with initial-beacon-aligned surface inference. Its corridor assumption and measured outcomes must accompany any result.

`planner-1.3-exp.18` follows exp.17 and tests an opening reference selected by distance from observed wall endpoints. It does not guarantee physical clearance.

`planner-1.3-exp.19` follows exp.18 and tests direct goal handover through a corridor supported by current neural range rays. It remains experimental.

`planner-1.3-exp.20` follows exp.19 and tests sustained distant goal visibility before handover. Nearby handover retains the same sampled-ray condition.

`planner-1.3-exp.21` follows exp.20 and tests bounded persistence after visible-goal handover. Both completed at 6/8 retained goals and remain unselected. The COO numerical probe is not a registered controller revision or a measured navigation result.

`planner-1.3-exp.22` follows exp.21 and pairs visible-goal control with an explicitly fingerprinted repeatable full-connectome readout. Numerical repeatability does not establish navigation improvement.

planner-1.3-exp.23 follows exp.22 and uses segmented CSR sums with a separate readout fingerprint. Exp.22 ended incomplete at its declared wall limit. Higher numbering does not imply better navigation; exp.23 requires completed flight evidence.
