# Reference-preserving transfer experiment 3: results

Completed October 8, 2026 under [REFERENCE_TRANSFER_PROTOCOL_3.md](REFERENCE_TRANSFER_PROTOCOL_3.md), committed before training (`83649fb`). Retained 50/64 checkpoint `0a1a6569549a`, 131,072 added transitions, graded gate maps plus 25% medium rooms, one seed. The source hash was unchanged after every chunk. No reserved pool was used. Training took about 6.4 minutes.

## Outcome

Strong learning signal on partitioned maps, with forgetting on medium rooms. No checkpoint met the declared acceptance rule (medium at least 21/32).

| Checkpoint | Medium, seeds 100000-100031 | Gate-two, 32 | Gate-long, 32 | Passages-wide, 16 |
| --- | --- | --- | --- | --- |
| Baseline (source) | 23/32 (4 coll, 5 timeout) | 22/32 (8 coll, 2 timeout) | 23/32 (3 coll, 6 timeout) | 0/16 |
| After 65,536 added | 20/32 (8 coll, 4 timeout) | 26/32 (1 coll, 5 timeout) | 21/32 (0 coll, 11 timeout) | 2/16 |
| After 131,072 added | 19/32 (6 coll, 7 timeout) | 28/32 (4 coll, 0 timeout) | 32/32 (0 coll, 0 timeout) | 4/16 (8 coll, 4 timeout) |

Gate and passages pools use seeds 830000+. Medium baseline replays the recorded 23/32 for this checkpoint, which confirms the setup.

Medium successes lost against the baseline: after 65,536, seeds 100005, 100007, 100012, 100018, 100029, 100031 (gained 100004, 100013, 100027). After 131,072, seeds 100003, 100005, 100007, 100012, 100018, 100021, 100023, 100029, 100031 (gained 100002, 100004, 100006, 100013, 100027). Seeds 100005, 100007, 100012, 100018, 100029 and 100031 are lost at both points, so the loss is partly systematic. The protocol's gain rule (at least 6 more gate-two successes) was met at 131,072 (28 against 22).

## Reading

1. This is the first experiment where training produced a success signal on partitioned maps: gate-long went from 23/32 to 32/32, gate-two from 22/32 to 28/32, and passages-wide from 0/16 to 4/16. Passages-wide is a transfer, because it was never in the training mix.
2. The price is forgetting on medium rooms: 23/32 to 19/32 with a 25% medium share. The protocol rejects the checkpoint. The medium drop is four episodes, with wide intervals, but the same seeds are lost at both evaluations.
3. Earlier experiments (1 and 2) jumped to `passages` and failed. Training where the reference already succeeded works. This supports a graded curriculum with a heavier medium share, as the completion plan requires.
4. Single seed. The 25% medium share was not enough, and the effect of a larger share is untested.

Next: [REFERENCE_TRANSFER_PROTOCOL_4.md](REFERENCE_TRANSFER_PROTOCOL_4.md).
