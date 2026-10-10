# Phase 3 replication (experiment 12): results

Completed October 10, 2026 under [PHASE3_REPLICATION_PROTOCOL.md](PHASE3_REPLICATION_PROTOCOL.md), committed before training (`3792e5c`). Long memory window (16 frames, stride 32, 25.6 s), training seed 443, 131,072 added transitions in four stages, all four stages evaluated on the old and selection pools (32 episodes per cell). The report pools were not opened. Training took 6 minutes. Each checkpoint evaluation took 9 to 10 minutes.

## Outcome

Not replicated by the declared rule. At stage 4 on the selection pools, the best hard-profile gain over the seed 443 no-memory control was +5 (passages-wide), below the +6 required. Passages-mid was 9 episodes below the control. The Phase 3 exit criterion is not met.

Selection pools, order medium, medium-b, gate-two, gate-long, passages-wide, passages-mid, passages. The control is the Phase 1 run with seed 443.

| Stage (added) | Memory, seed 443 | Control, seed 443 | Difference on wide, mid, passages |
| --- | --- | --- | --- |
| 1 (32,768) | 25, 28, 27, 31, 20, 4, 2 | 27, 27, 27, 30, 1, 7, 1 | +19, -3, +1 |
| 2 (65,536) | 26, 26, 31, 32, 17, 3, 2 | 28, 24, 28, 30, 5, 9, 2 | +12, -6, 0 |
| 3 (98,304) | 25, 30, 27, 31, 9, 1, 0 | 25, 27, 32, 32, 18, 10, 2 | -9, -9, -2 |
| 4 (131,072) | 27, 29, 30, 32, 11, 1, 0 | 28, 27, 32, 32, 6, 10, 0 | +5, -9, 0 |

Old pools at stage 4: memory 29, 23, 32, 32, 11, 1, 0 and control 27, 30, 32, 32, 3, 11, 2. The differences on the old pools are +8, -10 and -2 for passages-wide, passages-mid and passages.

Seed 442 and seed 443 side by side, at stage 4 on the selection pools, difference of memory over the same-seed control:

| Seed | Passages-wide | Passages-mid | Passages |
| --- | --- | --- | --- |
| 442 | +6 | +9 | +4 |
| 443 | +5 | -9 | 0 |

## Reading

1. The seed 442 result did not repeat. With seed 443 the long window raised passages-wide at three of four stages (+19, +12, +5) and lowered passages-mid at every stage (-3, -6, -9, -9). Passages stayed at 0 to 2 of 32.
2. The memory policy seems to shift which profile the policy keeps, not to add ability to all of them. Seed 442 gained on mid and wide. Seed 443 gained on wide and lost on mid. The control runs also showed opposite choices between seeds (Phase 1). Three of the four seed-and-condition combinations traded one profile for another.
3. The seed 442 result was a favorable draw, or the window helps in a way that depends on the seed. Two seeds cannot separate these.
4. No safety loss: medium rooms stayed at 25 to 30 of 32 and gates at 27 to 32 of 32 in all four stages.
5. The training outcome varies up to 18 episodes between seeds in all three conditions measured (no memory, short, long). With 32 episodes per cell and two seeds, effects under about 10 episodes cannot be told apart from seed variance. A decision on memory needs at least three seeds and 64 episodes per cell.

## Consequence

Memory is not established as the missing capacity. It stays a candidate, with a possible interaction with the profile mix. The binding problem, seen in Phase 1 and again here, is that profiles compete inside one training mix. That points to the Phase 2 work: a broad random map distribution, held-out parameters and a held-out family, where competition between a few named profiles cannot dominate. Measurement also needs strengthening (more seeds and episodes) before small differences can be claimed.

The Phase 3 checklist stays open: memory gain decided as "not replicated on two seeds".
