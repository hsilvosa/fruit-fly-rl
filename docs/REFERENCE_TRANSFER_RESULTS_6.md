# Reference-preserving transfer experiment 6: results

Completed October 8, 2026 under [REFERENCE_TRANSFER_PROTOCOL_6.md](REFERENCE_TRANSFER_PROTOCOL_6.md), committed before training (`38d1508`). Start: the experiment 5 selected checkpoint. 131,072 added transitions, one seed, 7.5 minutes of training. The starting checkpoint hash was unchanged after every chunk. No reserved pool was used.

## Outcome

The declared positive result was not met: passages-mid never reached 16/32. The 65,536 checkpoint failed the acceptance rule (passages-wide fell to 5/32). The 131,072 checkpoint passed it and is the selected checkpoint (`runs/training/reference-transfer-6/mid/chunk-16.zip`).

| Checkpoint | Medium 100000 | Medium-b 840000 | Gate-two | Gate-long | Passages-wide | Passages-mid | Passages |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Baseline (experiment 5 selected) | 22/32 | 24/32 | 32/32 | 31/32 | 26/32 | 11/32 | 2/32 |
| After 65,536 added | 26/32 | 29/32 | 31/32 | 30/32 | 5/32 | 12/32 | 6/32 |
| After 131,072 added | 23/32 | 29/32 | 32/32 | 32/32 | 20/32 | 9/32 | 1/32 |

Passages-mid pool: seeds 850000-850031, a new development profile and pool.

## Reading

1. The intermediate profile did not train. Passages-mid stayed at 9 to 12 of 32 with a 37.5% training share.
2. The policy is unstable between checkpoints. Passages-wide moved 26, 5, 20 of 32, and passages moved 2, 6, 1 of 32, on checkpoints only 65,536 transitions apart. A swing of 21 episodes is larger than 32-episode sampling noise. Whichever profile a checkpoint handles well depends on where training stopped.
3. In each eight-chunk cycle, all 8,192 transitions of a chunk come from one profile, then the policy moves to another. The policy appears to follow the most recent chunks and lose the other profiles. This is consistent with interference between sequential profiles. It is a hypothesis, not a measured cause.
4. Medium rooms and gates stayed at their reference levels throughout.

Next: [REFERENCE_TRANSFER_PROTOCOL_7.md](REFERENCE_TRANSFER_PROTOCOL_7.md) mixes the profiles inside every PPO update.
