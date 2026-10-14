# Planner reference and the four-family picture (C1.P): results

Protocol: [PLANNER_REFERENCE_PROTOCOL.md](PLANNER_REFERENCE_PROTOCOL.md), committed (`e79d275`) before the run. Evaluation only; nothing was trained or selected. The planner is a reference and never chose an action of the learned policy.

## Outcome by the declared statements

- **Level C: the planner exceeds the learned candidate.** Planner-1.4-exp.3 scored 147 of 168 (87.5 percent, Wilson 95% interval 82 to 92 percent), with 4 collisions and 17 timeouts. The retained candidate (stage 61, seeds 801, 851, 901) scored 95, 108 and 108 (mean 103.7) in B4 on the same 168 cases. The planner is 43 episodes above that mean; the declared threshold was 13.
- **`large` and `maze`: the retained candidate does not navigate them.** Zero or near zero in both modes, as expected. The release gate is far.

## Planner on level C (168 episodes, deterministic planner, same headings as the learned evaluation)

| Scene | Planner | Learned retained (B4, deterministic: seeds 801, 851, 901) | Episodes |
| --- | --- | --- | --- |
| office-floor | 20 | 16, 16, 16 | 24 |
| apartment | 12 | 8, 8, 8 | 24 |
| street-block | 38 | 32, 36, 40 | 40 |
| atrium | 21 | 8, 8, 9 | 24 |
| warehouse | 32 | 24, 17, 18 | 32 |
| courtyard | 24 | 7, 23, 17 | 24 |
| Total | **147 (4 collisions, 17 timeouts)** | 95, 108, 108 | 168 |

The planner's failures are concentrated: `study-to-bathroom` (apartment) timed out in all 8 headings, `sofa-to-bedroom` in 4 of 8 and `void-climb-to-top-gallery` (atrium) in 3 of 8; the 4 collisions are spread over `over-the-desks`, `open-plan-to-private-office`, `intersection-turn` and `through-the-passage` (one or two headings each). The learned candidate and the planner both struggle in the apartment (12 and 8 of 24); the planner's gain is mostly the atrium (21 against 8 to 9), the warehouse and the courtyard. Planner timing: 1,676 to 1,832 s per process of 42 episodes, about 41 s per episode with four planner processes and the learned evaluations sharing the machine (the probe alone took 22 s per episode).

## Retained learned candidate on `large` and `maze` (fresh pools 892000 and 893000, 32 episodes per cell; successes / collisions / timeouts)

| Seed | `large`, deterministic | `large`, sampled | `maze`, deterministic | `maze`, sampled |
| --- | --- | --- | --- | --- |
| 801 | 2 / 7 / 23 | 2 / 6 / 24 | 0 / 3 / 29 | 0 / 2 / 30 |
| 851 | 0 / 11 / 21 | 0 / 4 / 28 | 0 / 1 / 31 | 0 / 3 / 29 |
| 901 | 0 / 5 / 27 | 1 / 5 / 26 | 0 / 5 / 27 | 0 / 8 / 24 |

Wilson 95% intervals for a cell: 0 of 32 is 0 to 11 percent, 2 of 32 is 2 to 20 percent. Most failures are timeouts (21 to 31 of 32): the policy flies and does not find the way through the rooms. The old reference scored 0 of 16 on `large`, so nothing here is a gain.

## The four-family picture for the retained candidate (stage 61 of three seeds, deterministic, development pools)

| Family | Retained candidate | Release gate | Planner reference |
| --- | --- | --- | --- |
| Medium rooms (pool 886000, 64 episodes) | 49, 54, 55 of 64 with 11, 7, 5 collisions | 52 of 64, at most 3 collisions | Not applicable |
| `large` (pool 892000, 32 episodes) | 2, 0, 0 of 32 | 52 of 64 (26 of 32), at most 3 collisions | Not run on a matched pool (development: 15/16 for planner-1.2, 8/8 for exp.9, inspected rooms) |
| `maze` (pool 893000, 32 episodes) | 0, 0, 0 of 32 | same | Not run on a matched pool (development: 5/8 fresh rooms for exp.25, 7/8 retained for exp.32) |
| Architectural, level C (168 episodes, development headings) | 95, 108, 108 of 168 (57 to 64 percent) with 45 to 54 collisions | 81 percent and at most 5 percent collisions | 147 of 168 (87.5 percent) with 4 collisions |

The release gate is not met in any family. Medium comes closest on successes (the best seed 55 of 64) and misses on collisions. `large` and `maze` are not in reach of this lineage with 8 m rays and no memory. The architectural family is at 57 to 64 percent against the 81 percent target.

## Limits

- The planner's level C scenes are the ones it was developed on, so 87.5 percent is an optimistic reference and not an independent result.
- 32 episodes per `large` and `maze` cell; the three seeds saw the same rooms, so they are not independent samples. Intervals are wide.
- The planner on `large` and `maze` was not run on the new pools; the development figures are from inspected rooms and small samples.
- The four-family table mixes pools of different size and status (development, inspected). It is a picture of the distance to the gate, not a gate evaluation.

## What this supports

The planner solves most architectural situations that the learned candidate does not, and the learned candidate does not enter `large` or `maze`. Together with C1.1 and C1.2 the claims for the release are: a learned, connectome-in-the-loop policy navigates new medium rooms and, partly, partitioned rooms and a held-out scene family; an explicit planner with the same connectome-driven observations does better on the architectural scenes it was built for; the connectome's own contribution is not shown; large rooms and mazes are open.

## Artifacts

Cells in `runs/training/planner-reference/` (`summary.json`, one file per cell, `planner-levelC-h<first>-<last>.json` with every episode); evidence copy in `private/planner-reference-evidence/`. The planner sources were hashed (navigation modules, in each planner file) before the run.

Timing from the clock: driver log created 16:00:55 on October 14, evaluation finished 17:19:10 (78 min 15 s) against 70 min estimated (range 55 to 100). The planner processes took 28 to 31 min against 25 estimated; the `maze` cells of the learned candidate set the end of the run. Resources: up to 5 processes, VRAM peak 5.7 GiB observed during the run.
