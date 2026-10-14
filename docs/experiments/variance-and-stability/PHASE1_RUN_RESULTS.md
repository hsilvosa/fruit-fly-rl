# Phase 1 run (experiment 10): results

Completed October 10, 2026 under [PHASE1_RUN_PROTOCOL.md](PHASE1_RUN_PROTOCOL.md), committed before training (`60baad7`). Two seeds, four stages of 32,768 added transitions each, four evaluations per seed on the old pools and on the selection pools (32 episodes per cell). Start: the experiment 7 selected checkpoint. The report pools were not opened. Training took about 9 minutes for both seeds. Evaluation ran under the CPU and memory guard.

## Outcome

The Phase 1 exit criterion was not met. Seed 443 let passages-wide swing by 18 episodes (the limit was 6) and had only one accepted checkpoint of four. Seed 442 met the criterion by itself. The result is recorded as negative for the criterion, with a useful partial finding.

Old pools (comparable with experiment 8). Columns: medium, medium-b, gate-two, gate-long, passages-wide, passages-mid, passages.

| Seed | Added | Medium | Medium-b | Gate-two | Gate-long | Wide | Mid | Passages |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| 442 | 32,768 | 26 | 27 | 32 | 32 | 22 | 12 | 6 |
| 442 | 65,536 | 24 | 26 | 32 | 32 | 23 | 10 | 3 |
| 442 | 98,304 | 24 | 27 | 32 | 32 | 23 | 11 | 3 |
| 442 | 131,072 | 21 | 27 | 32 | 32 | 22 | 12 | 2 |
| 443 | 32,768 | 23 | 29 | 28 | 27 | 0 | 17 | 6 |
| 443 | 65,536 | 25 | 28 | 30 | 29 | 2 | 14 | 4 |
| 443 | 98,304 | 24 | 29 | 32 | 32 | 18 | 13 | 1 |
| 443 | 131,072 | 27 | 30 | 32 | 32 | 3 | 11 | 2 |

Selection pools (new seeds), with the acceptance rule applied (medium at least 21, medium-b at least 20, passages-wide at least 16, gate-two at least 28).

| Seed | Added | Medium | Medium-b | Gate-two | Gate-long | Wide | Mid | Passages | Accepted |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| Start | 0 | 28 | 28 | 31 | 27 | 23 | 10 | 0 | not applicable |
| 442 | 32,768 | 25 | 29 | 31 | 32 | 25 | 11 | 2 | yes |
| 442 | 65,536 | 28 | 29 | 30 | 32 | 22 | 6 | 1 | yes |
| 442 | 98,304 | 25 | 28 | 31 | 32 | 24 | 6 | 2 | yes |
| 442 | 131,072 | 25 | 26 | 31 | 32 | 22 | 6 | 2 | yes |
| 443 | 32,768 | 27 | 27 | 27 | 30 | 1 | 7 | 1 | no |
| 443 | 65,536 | 28 | 24 | 28 | 30 | 5 | 9 | 2 | no |
| 443 | 98,304 | 25 | 27 | 32 | 32 | 18 | 10 | 2 | yes |
| 443 | 131,072 | 28 | 27 | 32 | 32 | 6 | 10 | 0 | no |

Selected by the declared rule: seed 442 at 32,768 added transitions (passages-mid 11 on the selection pools, passages 2). It is only one episode above the start on passages-mid, and two above on passages. It is not a useful improvement over the start.

Stability on the old pools, range across the four evaluations:

| Seed | Passages-wide | Passages-mid | Medium (selection) minimum |
| --- | --- | --- | --- |
| 442 | 1 episode (22 to 23) | 2 episodes | 25 |
| 443 | 18 episodes (0 to 18) | 6 episodes | 25 |
| Experiment 8 (control, unstabilized) | 16 and 9 | 4 and 5 | not applicable |

## Reading

1. The stabilization bundle did what it targeted on seed 442. Passages-wide stayed at 22 to 23 of 32 across four evaluations, medium rooms stayed at 24 to 26, and gates stayed at 32. Experiment 8 oscillated by 16 episodes on the same quantity.
2. The same bundle did not stabilize seed 443. Passages-wide went 0, 2, 18, 3 while passages-mid went 17, 14, 13, 11. The two seeds from the same start settled on opposite profiles: seed 442 kept the easier one (passages-wide) and let passages-mid slip to 6 on the selection pools, while seed 443 kept passages-mid at 10 to 17 and lost passages-wide.
3. Neither seed raised the hardest profile. Passages stayed at 0 to 6 of 32.
4. The profiles still compete for the same capacity. Stable training holds what the policy has, but it did not gain both. The pilot's passages-mid of 21 on the selection pools did not return in either seed: 6 to 11 here. The pilot was one seed and one evaluation, so that number was a high draw.
5. Two seeds from one start differ by up to 18 episodes on a profile. Any single-seed result in the earlier experiments should be read with that spread in mind.

## Consequence

Stabilizing the optimizer alone does not give a policy that handles every profile in the mix. The capacity or representation looks like the limit: the policy is a small network over reservoir features, with almost no memory. This agrees with the plan's reason for Phase 3 (memory) and with the earlier failure analysis, where the policy hovered at partitions. Phase 1 stays open and is closed as negative for the exit criterion. The seed 442 recipe is kept as the stable baseline for Phase 2 and Phase 3.

## Resource use

The first driver started too many processes at once and the CPU touched 91 percent. After that, the guard allowed at most 4 and then 6 processes, starting new ones below 75 percent. Evaluation took about 55 minutes for 8 checkpoints and 112 cells.
