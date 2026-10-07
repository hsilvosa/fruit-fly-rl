# Controller versions

Controller names now combine a revision number with a description. `planner-1.2` means the dual-readout planner; it is not a new room generator, a project release, or a claim of better navigation. The default remains `planner-1.0`, the frozen baseline. Both numbered follow-ups, `planner-1.1` and `planner-1.2`, remain experimental.

## Complete mapping

| Public revision | Description | Historical alias | Evidence and status |
| --- | --- | --- | --- |
| `planner-1.0` | Baseline observed-map planner | `v55` | Default; 13/16 on its original prospective development cohort |
| `planner-1.0.1-exp.1` | Goal-margin correction | `v56` | Corrected one of three retained failures; separate patch candidate |
| `planner-1.1-exp.1` | Higher cruise speed | `v57` | Isolated speed experiment |
| `planner-1.1-exp.2` | Known-free margin traversal | `v58` | Isolated clearance experiment |
| `planner-1.1-exp.3` | Combined speed and clearance | `v59` | Unconditional combination regressed a known room |
| `planner-1.1` | Adaptive clearance | `v60` | Conditional recovery; 14/16 versus baseline 12/16 on one fresh paired cohort |
| `planner-1.2-exp.1` | Clean ranges | `v61` | Corrected false stopping but regressed a fresh paired cohort |
| `planner-1.2-exp.2` | Persistent route | `v62` | Retained detour still timed out |
| `planner-1.2-exp.3` | Ray-consistent mapping | `v63` | Retained detour still timed out |
| `planner-1.2-exp.4` | Momentum braking | `v64` | Known contacts corrected; fresh cohort regressed to 12/16 versus adaptive clearance 15/16 |
| `planner-1.2` | Dual readout | `v65` | Contextual mapping plus clean braking ranges; tied adaptive clearance at 15/16 on the latest fresh paired cohort |

These are controller revisions, not certified production releases. Experimental sequence numbers preserve development order within an intended milestone; they do not rank performance. Results from different room cohorts cannot be ranked directly. [Latest experiments and limits](RESULTS.md#latest-planner-experiments).

## Selecting a controller

```powershell
.\launch-observed-map.cmd --controller-version 1.2 --seed 10000005
.\launch-observed-map.cmd --controller-version planner-1.1
.\.conda\python.exe -s -m fly_rl controller-versions
```

The bare number and `planner-` name are equivalent. Every old `v55` through `v65` alias remains accepted, and `--planner-version` remains an alias for `--controller-version`:

```powershell
# Historical command remains valid and selects planner-1.2.
.\launch-observed-map.cmd --planner-version v65 --seed 10000005
```

The catalog command lists every mapping without initializing the graph, opening a viewer, or running training. The viewer shows the public revision and description, and new archives record both alongside the original artifact identifier. Diagnostic preparation, execution, and reporting commands also accept the public numbers. Their frozen protocol arm keys retain historical aliases to avoid changing the interpretation of existing records. A newly prepared protocol adds the public-name mapping and freezes the naming module with other sources.

## What remains unchanged

Frozen controller and readout implementations, original checkpoints, their fingerprints, historical run directories, evidence filenames, and previously recorded source snapshots retain their identifiers. The original archive `version` field is preserved; new `controller_version`, `controller_label`, and `legacy_alias` fields make the mapping explicit. Archived source dependencies include the naming table, so a future table change cannot silently reinterpret a recorded flight. Older archives remain readable without those new fields.

Earlier learned-policy experiment labels such as `v34`, sensor contracts such as `sensors-v6`, map profiles such as `dense-v3`, and MaleCNS v1.0 identify different objects. They are not planner revisions and are not renamed by this migration. Historical evidence continues to use its original IDs; this table translates every currently selectable planner.

## Future numbering

See [Versioning and revision order](VERSIONING.md) for the complete sequence, patch/minor/major branches, and the workflow for assigning the next revision.

Use a new major number for a substantially different controller architecture, a new minor number for a mechanism or input-contract change, and a patch number for a compatible correction. Develop candidates as `planner-1.3-exp.1`, `planner-1.3-exp.2`, and so on. Assign a numbered milestone only after documenting its measured behavior and limitations; that does not automatically promote it to the demo default. Keep old aliases permanent and never reuse a number for different measured code.

Project package/release versions remain separate. Experiment directories should describe the hypothesis and date, such as `dual-readout-large-20261005-seed01`, and record their exact Git commit and source hashes. A controller name alone does not reproduce a run.


## Migration verification

The migration passed 389 regression tests and the 54-test focused compatibility subset. A short full-graph rendered launch displayed planner-1.2 and recorded twenty finite steps; its archive integrity passed, with no completed episode or optimization. Existing frozen results were also reported offline using the public version arguments, reproducing the 15/16 tie. Original protected files retained their hashes. [Verification details](VERIFICATION.md#numbered-controller-naming-migration).


## Room-aware experimental branch

Planner-1.3-exp.1 corrects room decoding and commits local references; exp.2 increases unknown-cell costs and regressed retained large cases; exp.3 adds observed opening references; exp.4 adds sample-aware clustering and completed-plane memory, reaching both retained large failures. Exp.5 considers multiple partially visible wall candidates. Exp.5 subsequently regressed both maze flights and has a recorded diagonal-fit geometry failure. Exp.6 adds a beacon-aligned surface constraint but also regressed both retained flights. Exp.7 returns to strongest-surface selection with a distance-aware vertical span. Exp.7 also timed out in both maze rooms. Exp.8 tests clean-range occupancy with unchanged dual readout and safety. Exp.8 reached one retained maze goal, while the other timed out. Exp.9 raises requested cruise speed within the unchanged physical cap and braking guards and reaches all six retained large rooms plus all eight fresh development rooms, but fails both retained maze flights. Exp.10 adds stalled-reference vetoes, reaching one maze goal. Exp.11 reaches both retained maze goals after refining stronger same-opening center support; its fresh check reached only 5/8 and failed the development rule. Exp.12 reached only 6/8 retained goals and is not selected. Exp.13 reached zero of eight retained goals with a finer 0.4-unit map and its one-voxel buffer. Exp.14 surface fallback reached zero goals and one collision. Exp.15 confined cruising and exp.16 visit pressure each reached four goals without collisions. All four were rejected. Exp.17 clean initial-beacon alignment and exp.18 observed-clearance references each reached five goals with regressions. Exp.19 visible-goal handover reached six goals without collisions and failed its selection rule. Exp.20 stable handover and exp.21 committed handover each reached six goals without collisions. Both failed the selection rule. Exp.22 tests repeatable full-graph execution with a distinct readout fingerprint. All twenty-two support `large` and `maze`; frozen earlier revisions remain large-only. Reliable maze navigation is not yet established; actual retained arrivals and the five-of-eight fresh result are recorded. None changes the default or trains movement weights. [Development evidence](MAZE_NAVIGATION.md) records outcomes and limits.


| New candidate | Artifact alias | Tested change | Current status |
| --- | --- | --- | --- |
| `planner-1.3-exp.14` | `portal-reference-exp12` | Strongly supported alternate surfaces and close goal handover | Rejected: 0/8 goals, 1 collision |
| `planner-1.3-exp.15` | `portal-reference-exp13` | Confined request 1.0 to 1.3, unchanged braking | Rejected: 4/8 goals, 0 collisions |
| `planner-1.3-exp.16` | `portal-reference-exp14` | Bounded visit cost after weak progress | Rejected: 4/8 goals, 0 collisions |
| `planner-1.3-exp.17` | `portal-reference-exp15` | Clean map with initial-beacon surface alignment | Rejected: 5/8 goals, 0 collisions; corridor assumption |
| `planner-1.3-exp.18` | `portal-reference-exp16` | Observed opening clearance reference | Rejected: 5/8 goals, 0 collisions |
| `planner-1.3-exp.19` | `portal-reference-exp17` | Neural-ray visible-goal handover | Rejected: 6/8 goals, 0 collisions |
| `planner-1.3-exp.20` | `portal-reference-exp18` | Sustained distant goal visibility | Rejected: 6/8 goals, 0 collisions |
| `planner-1.3-exp.21` | `portal-reference-exp19` | Committed visible-goal handover | Rejected: 6/8 goals, 0 collisions |
| `planner-1.3-exp.22` | `repeatable-goal-exp1` | Repeatable full-graph visible-goal execution | Replay verified; incomplete at wall limit (five goals, three unfinished) |
| `planner-1.3-exp.23` | `segmented-goal-exp1` | Repeatable segmented full-graph visible-goal execution | Replay verified; 6/8 retained goals, zero collisions; not selected |

Exp.23 completed at 6/8 retained goals, zero collisions and two timeouts and was not selected.

| Candidate | Artifact alias | Change | Status |
| --- | --- | --- | --- |
| planner-1.3-exp.24 | wall-survey-exp1 | Observed blocking-wall opening survey | 6/8 retained goals with two regressions; not selected |

Exp.24 completed at 6/8 retained goals, zero collisions and two regressed timeouts; it was not selected.

| Candidate | Artifact alias | Change | Status |
| --- | --- | --- | --- |
| planner-1.3-exp.25 | clearance-goal-exp1 | Clearance- and crossing-aware goal handover on exp.23 | 7/8 retained, then 5/8 fresh goals; fresh gate failed |

Exp.25 completed at 7/8 retained goals with zero collisions and one timeout, preserving all six exp.23 successes. It passed the retained gate; the same source hashes are frozen for a fresh eight-map check. It is not promoted yet.

Exp.25 completed its fresh suite at 5/8 goals, zero collisions and three timeouts. It failed the 7/8 criterion and is not promoted; work is paused. Its 7/8 retained correction outcome remains separate. No controller or checkpoint alias was replaced.


planner-1.3-exp.26 (`distant-opening-exp1`) follows exp.25. It preserves nearby opening choices and tests a 12-unit fallback detection window when the 6-unit detector finds none. A retained full-connectome check is running; it is not promoted.


Exp.26 completed at 6/8 retained goals with zero collisions and two timeouts; no promotion. Planner-1.3-exp.27 (`progress-wall-scan-exp1`) tests bounded observed-wall recovery after longitudinal nonprogress, preserving the exp.26 range correction. It remains experimental.


Exp.27 completed at 4/8 retained goals, zero collisions and four timeouts; it was rejected after three prior-success regressions. Planner-1.3-exp.28 (`revisit-wall-scan-exp1`) gates the same bounded recovery on sustained revisits rather than longitudinal progress alone; its retained check is running and it is not promoted.


Exp.28 completed at 6/8 retained goals with zero collisions, preserving all six exp.26 arrivals but not fixing the remaining two timeouts. Exp.29 (`coverage-wall-scan-exp1`) tests visit-coverage direction selection within the unchanged bounded recovery; its retained check is running. Neither has been promoted.

Planner-1.3-exp.30 adds bounded release of unreachable crossing references to exp.29. Exp.29 completed at 6/8 retained goals without collisions and was not promoted. A higher experimental number does not imply better results.

Planner-1.3-exp.31 tests completed-surface normal consensus on top of exp.29. It excludes the rejected exp.30 crossing release. It is experimental and has no promotion evidence yet.

Planner-1.3-exp.32 adds terminal-distance gating to exp.31, whose retained check reached 6/8 with a regression and was not promoted. The new candidate has no completed flight evidence yet.

## Architectural controller family

Planner-1.4-exp.1 is the separate architectural adapter, receiving the selected scene dimensions and nine-frame segmented dual neural features. It is available through ArchitecturalPlannerPolicy and the demo architecture-scene selector, separately from the procedural version registry. Its finer grid does not change frozen maze/large contracts. Short CUDA integration and viewer controls are verified; full-route navigation remains pending.
