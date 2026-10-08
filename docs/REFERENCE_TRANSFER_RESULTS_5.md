# Reference-preserving transfer experiment 5: results

Completed October 8, 2026 under [REFERENCE_TRANSFER_PROTOCOL_5.md](REFERENCE_TRANSFER_PROTOCOL_5.md), committed before training (`b40b177`). Start: the experiment 4 selected checkpoint. 131,072 added transitions, `passages` entered the mix (37.5% medium), one seed. Training took 7.8 minutes. The starting checkpoint hash was unchanged after every chunk. No reserved pool was used.

## Outcome

The declared positive result was not met. The `passages` count did not improve by four. Both checkpoints passed the acceptance rule. The selection rule picks the 65,536 checkpoint (`runs/training/reference-transfer-5/passages/chunk-8.zip`) because it has the higher passages count (2 against 1).

| Checkpoint | Medium 100000 | Medium-b 840000 | Gate-two | Gate-long | Passages-wide | Passages |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline (experiment 4 selected) | 24/32 | 23/32 | 32/32 | 32/32 | 6/32 | 1/32 (15 coll, 16 timeout) |
| After 65,536 added | 22/32 | 24/32 | 32/32 | 31/32 | 26/32 | 2/32 (17 coll, 13 timeout) |
| After 131,072 added | 23/32 | 29/32 | 32/32 | 32/32 | 20/32 | 1/32 (12 coll, 19 timeout) |

Seeds: gate and passages-wide pools 830000, passages pool 810000, 32 episodes each.

## Reading

1. Passages-wide, now in the training mix, went from 6/32 to 26/32 and then 20/32. The policy learned to cross partitions on that profile. The 6 to 26 jump took 32,768 passages-wide-and-gate transitions and 16,384 passages transitions. Passages-wide was in the mix, so this is learning on the trained profile, not transfer.
2. Medium rooms stayed at the source's level (22 to 29 of 32 across both pools). Gates stayed at 31 to 32 of 32. The graded mix with 37.5% medium rooms did not cause forgetting.
3. Passages did not move: 1, 2 and 1 successes. The policy now collides more often than it times out (12 to 17 collisions). Passages differs from passages-wide in aperture (4 by 4 m against 8 by 4.8 m) and obstacle count (64 against 12). The jump in difficulty between the two profiles is large, in the same way as the earlier jump from gates to `passages`.
4. The 20/32 at the end against 26/32 at the middle may be noise or drift. One seed and 32 episodes cannot separate them.

Next: a stage between passages-wide and passages. See [REFERENCE_TRANSFER_PROTOCOL_6.md](REFERENCE_TRANSFER_PROTOCOL_6.md).
