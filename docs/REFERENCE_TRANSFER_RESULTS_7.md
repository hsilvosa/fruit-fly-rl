# Reference-preserving transfer experiment 7: results

Completed October 8, 2026 under [REFERENCE_TRANSFER_PROTOCOL_7.md](REFERENCE_TRANSFER_PROTOCOL_7.md), committed before training (`c5cbfa8`). Start: the experiment 6 selected checkpoint. The eight parallel simulators of each PPO rollout ran different profiles. 131,072 added transitions per arm in two uninterrupted runs of 65,536, one seed. The starting checkpoint hash was unchanged. No reserved pool was used.

## Outcome

The declared positive result was missed by one episode: the best accepted checkpoint reached 15/32 on passages-mid, and the rule required 16/32. It did exceed the passages requirement (4/32, three above the baseline of 1/32). The selected checkpoint is `runs/training/reference-transfer-7/mix3e4/stage-2.zip`.

| Arm and checkpoint | Medium 100000 | Medium-b 840000 | Gate-two | Gate-long | Passages-wide | Passages-mid | Passages | Accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (experiment 6 selected) | 23 | 29 | 32 | 32 | 20 | 9 | 1 | not applicable |
| mix3e4 after 65,536 | 26 | 25 | 32 | 32 | **0** | 17 | 8 | no (passages-wide below 16) |
| mix3e4 after 131,072 | 26 | 29 | 32 | 29 | 25 | 15 | 4 | yes |
| mix1e4 after 65,536 | 26 | 25 | 32 | 32 | 23 | 11 | 4 | yes |
| mix1e4 after 131,072 | 23 | 28 | 25 | 28 | 17 | 8 | 0 | yes |

All cells have 32 episodes. Selection among accepted checkpoints: highest passages-mid, which is mix3e4 at 131,072 (15/32).

## Reading

1. Mixing profiles inside every update gave the best partitioned-map results so far with medium rooms preserved: passages-mid 15 to 17 of 32 (baseline 9), passages 4 to 8 of 32 (baseline 1), passages-wide 25 of 32, medium 26 of 32 on both pools or close.
2. The instability remains at the learning rate of 3e-4. Passages-wide read 0 of 32 at 65,536 and 25 of 32 at 131,072. The lower rate (1e-4) was steadier (23, then 17) but learned less (passages-mid 11, then 8) and lost gate-two ground at the end (25 of 32).
3. Two evaluations per arm and one seed do not allow a statement on which learning rate is better. The dip to 0 of 32 is a large single event that a checkpoint-selection rule has to guard against.
4. The earlier switching-between-profiles hypothesis is not confirmed: the instability persists with in-batch mixing at 3e-4.

Next: [REFERENCE_TRANSFER_PROTOCOL_8.md](REFERENCE_TRANSFER_PROTOCOL_8.md) runs longer and with two seeds.
