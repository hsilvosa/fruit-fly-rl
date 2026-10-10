# Phase 3 screening (experiment 11): results

Completed October 10, 2026 under [PHASE3_SCREENING_PROTOCOL.md](PHASE3_SCREENING_PROTOCOL.md), committed before training (`7b175b9`). Seed 442 only, two memory windows, 131,072 added transitions each, stages 2 and 4 evaluated on the old and selection pools (32 episodes per cell). The report pools were not opened. Training took 5.5 minutes (short window) and 7 minutes (long window). Each checkpoint evaluation took 8 to 10 minutes under the resource guard.

## Outcome

One window is promising by the declared rule, at its last evaluation only: the long window (16 frames, stride 32, 25.6 s) at 131,072 added transitions. The short window (8 frames, stride 8, 3.2 s) was worse than the no-memory control. A single seed supports a decision to replicate. It does not support a claim that memory helps.

Selection pools, columns medium, medium-b, gate-two, gate-long, passages-wide, passages-mid, passages. The control is the Phase 1 run with seed 442 and no memory.

| Arm | Added | Medium | Medium-b | Gate-two | Gate-long | Wide | Mid | Passages | Hard sum | Control sum | Difference |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| Short | 65,536 | 26 | 28 | 32 | 32 | 13 | 3 | 0 | 16 | 29 | -13 |
| Short | 131,072 | 27 | 28 | 32 | 32 | 4 | 5 | 0 | 9 | 30 | -21 |
| Long | 65,536 | 27 | 26 | 31 | 32 | 11 | 7 | 4 | 22 | 29 | -7 |
| Long | 131,072 | 25 | 28 | 32 | 32 | **28** | **15** | **6** | **49** | 30 | **+19** |

The hard sum is passages-wide plus passages-mid plus passages. The promising rule asked for a difference of at least 10 with medium at least 21, medium-b at least 20 and gate-two at least 28. Only the last row meets it.

Old pools for the long window at 131,072: medium 24, medium-b 30, gate-two 32, gate-long 32, passages-wide 29, passages-mid 23, passages 6. The control at the same stage had passages-wide 22, passages-mid 12, passages 2. For comparison, the earlier unstabilized and stabilized runs never exceeded 17 on passages-mid on these pools in any seed.

## Reading

1. The short window hurt the hard profiles. A 3.2-second memory did not help and passages-wide collapsed to 4 of 32 at the end. Medium rooms and gates stayed at their level.
2. The long window was worse than the control at the middle evaluation (-7) and better at the end (+19), with passages-mid and passages both above everything seen in Phase 1. The path from -7 to +19 shows large movement between two evaluations, as in earlier runs. One seed and two evaluations cannot separate learning from a high draw.
3. A window of 25.6 seconds is long enough to span a detour around a partition at flight speeds of about 1 m/s. The short window is not. This agrees with the hypothesis, and it does not prove it.
4. The result is directional only. The Phase 1 run showed differences of up to 18 episodes between seeds on one profile. The difference here, 19 episodes on a sum of three cells, is of the same size, so replication is required.

## Next step (not started)

Replicate the long window with seed 443, with four evaluations. The Phase 1 run with seed 443 and no memory is the control. Estimated time from measured values: 7 minutes of training plus 4 checkpoints at 8 to 10 minutes each, about 45 to 50 minutes. The Phase 3 exit criterion needs a gain of at least 6 episodes of 32 over the control on a development cell, on two seeds.
