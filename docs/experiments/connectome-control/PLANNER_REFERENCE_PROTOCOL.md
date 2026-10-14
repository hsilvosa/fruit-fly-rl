# Planner reference and the four-family picture (C1.P): protocol

Declared October 14, 2026, before any run of this stage. The release rules ask for the explicit planner as a reference next to the learned policy ([PROJECT_COMPLETION.md](../../overview/PROJECT_COMPLETION.md)), and the gate has four families (medium, large, maze, architectural). The learned candidate has been measured on medium rooms, partitioned rooms and level C, and never on `large` or `maze` (the old reference scored 0/16 on `large`). The planner is a reference only: it never chooses the actions of the learned policy.

## What the planner can and cannot do

The planner controllers support the `large` and `maze` profiles and the architectural scenes, with a nine-frame panoramic observation and a different brain readout. They do not run on medium dense rooms, `passages` or the level B maps. So the reference exists for level C, `large` and `maze` only, and the other cells are reported as not applicable. The planner was developed by inspecting maps of these families, so its numbers are development results.

## Parts

**C1.P-a. Planner on level C.** `scripts/eval_planner_architecture.py` (new, evaluation only) runs planner-1.4-exp.3, the closing architectural revision (19/21 on one heading, zero collisions, in the October 7 check), on the same 21 situations and the same 8 initial headings as the learned evaluation: heading h uses seed 900000 + h. A check on all 168 cases showed identical start pose, goal and yaw in `ArchitecturalWorld` (planner) and `ArchitecturalSceneWorld` (learned). Episode limits are the physical deadlines of each situation. Four processes of two headings each (42 episodes per process). Full connectome in the loop. A cost probe on 8 episodes was run (7 successes, 1 timeout, 176 s, 22 s per episode, about 32 steps per second; the output was discarded).

**C1.P-b. Retained learned candidate on `large` and `maze`.** Stage 61 of seeds 801, 851 and 901 (B3 checkpoints), fresh pools 892000 to 892031 (`large`) and 893000 to 893031 (`maze`), 32 episodes per cell, both modes (`scripts/eval_cell_mode.py`). 32 episodes and not 64 because the expected result is near zero (4-episode probes on seed 801 gave 0 of 4 on `large` and 0 of 4 on `maze`) and the cells are long: about 23 s per episode on `large` and 59 s on `maze`. The sealed final assessment will use 64.

**Not run:** the planner on `large` and `maze` fresh pools. It needs a runner built from the viewer's environment code and per-version readout widths, and this stage does not build one. Context only, from the repository records: planner-1.2 reached 15/16 on `large` (paired development comparison, zero collisions), planner-1.3-exp.9 reached 8/8 on fresh `large` development rooms, and the `maze` planner reached 5/8 on fresh development rooms (planner-1.3-exp.25; planner-1.3-exp.32 reached 7/8 on retained rooms and 7/8 on the earlier set, not promoted). These are inspected development figures with small samples and are not matched to our pools.

## Pools and rules

- `large`: 892000 to 892031. `maze`: 893000 to 893031. Both unused before. Level C uses the development headings (seed 900000), as in B4 and C1.1; the sealed final headings (970000 to 979999) stay closed. Nothing is chosen from these numbers.
- This stage has no pass or fail rule: it fills the reference table. The statements it allows are descriptive:
  - On level C, "the planner exceeds the learned candidate" only if the planner total is at least 13 episodes above the learned mean (103.7 of 168 in B4, the same proportion cut as the earlier level C comparisons).
  - On `large` and `maze`, the learned candidate is reported with Wilson intervals. It is below the release gate (52 of 64 with at most 3 collisions) unless a cell reaches 26 of 32 with at most 1 collision, which is not expected.
- The four-family table in the results combines: medium (B3 stage 61 on pool 886000), `large` and `maze` (this stage), architectural (level C, B4), for the retained candidate, and the planner reference where it exists.

## Limits

- The planner's level C numbers come from scenes it was developed on. They are an upper-leaning reference, not an independent result.
- 32 episodes per `large` and `maze` cell: intervals are wide (a score of 0 of 32 still allows up to about 11 percent).
- No planner reference for medium rooms, partitioned rooms, level B, `large` or `maze` on matched pools.
- The learned candidate has never trained on `large` or `maze`; near-zero results are expected and are not a failure of the evaluation.

## Estimate

Planner level C: 168 episodes at about 22 s each is about 62 min of process time, in four processes about 16 min plus about 1 min of connectome load; with GPU and CPU sharing, about 25 min. Retained candidate on `large` and `maze`: 12 cells, 32 episodes each; about 12 min per `large` cell and 31 min per `maze` cell in one process, 264 process-minutes, spread over the other slots. At most 5 processes at a time (the GPU has 12 GiB, about 2.2 GiB in use by the system, and each planner process peaked at 1.95 GiB in the repository records; six processes could run out of VRAM, and a failed cell is simply repeated by the resumable driver). Total wall time about 70 min (344 process-minutes over 5 slots; range 55 to 100), CPU 70 to 90 percent, memory about 70 percent. Nothing runs until the user says so.
