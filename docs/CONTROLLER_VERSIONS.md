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

Planner-1.3-exp.1 corrects room decoding and commits local references; exp.2 increases unknown-cell costs and regressed retained large cases; exp.3 adds observed opening references; exp.4 adds sample-aware clustering and completed-plane memory, reaching both retained large failures. Exp.5 considers multiple partially visible wall candidates. Exp.5 subsequently regressed both maze flights and has a recorded diagonal-fit geometry failure. Exp.6 adds a beacon-aligned surface constraint but also regressed both retained flights. Exp.7 returns to strongest-surface selection with a distance-aware vertical span. Exp.7 also timed out in both maze rooms. Exp.8 tests clean-range occupancy with unchanged dual readout and safety. Exp.8 reached one retained maze goal, while the other timed out. Exp.9 raises requested cruise speed within the unchanged physical cap and braking guards and reaches all six retained large rooms plus all eight fresh development rooms, but fails both retained maze flights. Exp.10 adds stalled-reference vetoes, reaching one maze goal. Exp.11 reaches both retained maze goals after refining stronger same-opening center support; its fresh check reached only 5/8 and failed the development rule. Exp.12 reached only 6/8 retained goals and is not selected. Exp.13 checks a finer 0.4-unit map and its one-voxel buffer on all retained cases. All thirteen support `large` and `maze`; frozen earlier revisions remain large-only. Maze success is not yet established. None changes the default or trains movement weights. [Development evidence](MAZE_NAVIGATION.md) records outcomes and limits.
