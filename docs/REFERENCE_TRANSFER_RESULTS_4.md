# Reference-preserving transfer experiment 4: results

Completed October 8, 2026 under [REFERENCE_TRANSFER_PROTOCOL_4.md](REFERENCE_TRANSFER_PROTOCOL_4.md), committed before training (`a5383ea`). Start: the experiment 3 final checkpoint. 65,536 added transitions, 50% medium rooms, one seed. Training took 3.4 minutes. The experiment 3 checkpoint hash was unchanged after every chunk. No reserved pool was used.

## Outcome

The protocol's positive result was met. Both checkpoints passed the acceptance rule. The selected checkpoint is `runs/training/reference-transfer-4/recover/chunk-8.zip` (131,072 + 65,536 = 196,608 added transitions over the 50/64 source).

| Checkpoint | Medium 100000-100031 | Medium-b 840000-840031 | Gate-two, 32 | Gate-long, 32 | Passages-wide, 32 |
| --- | --- | --- | --- | --- | --- |
| 50/64 source | 23/32 (recorded) | 23/32 | 22/32 | 23/32 | 0/16 |
| Experiment 3 final (baseline) | 19/32 | 26/32 | 28/32 | 32/32 | 4/32 |
| After 32,768 added | 22/32 (6 coll, 4 timeout) | 28/32 | 32/32 | 32/32 | 4/32 (0 coll, 28 timeout) |
| After 65,536 added (selected) | 24/32 (3 coll, 5 timeout) | 23/32 (3 coll, 6 timeout) | 32/32 | 32/32 | 6/32 (0 coll, 26 timeout) |

Acceptance rule: medium at least 21/32, and medium-b at most three below the source (20/32 or more). Both checkpoints pass. The selection rule picks the higher passages-wide count, which is the 65,536 checkpoint.

At the selected checkpoint, medium lost 2 of the experiment 3 baseline's 19 successes (seeds 100017 and 100027) and gained 7. Against the 50/64 source, it scores 24/32 against 23/32.

## Reading

1. A mixed curriculum of single gates, passages-wide and 50% medium rooms restored medium-room performance (24/32 and 23/32) to the source's level while keeping perfect gate scores. The earlier forgetting came from the mix, not from learning partitions.
2. Passages-wide improved only from 4 to 6 of 32. The policy never collides there (0 collisions) and times out in 26 of 32 episodes. It avoids obstacles but does not commit to a long detour.
3. Medium-b fell from 28/32 to 23/32 between the two checkpoints, while medium rose from 22/32 to 24/32. Differences of this size between pools are within the noise at 32 episodes. The acceptance rule is met on both.
4. This is a development result on one seed. It is not a generalization claim and not a release result.

Next: [REFERENCE_TRANSFER_PROTOCOL_5.md](REFERENCE_TRANSFER_PROTOCOL_5.md).
