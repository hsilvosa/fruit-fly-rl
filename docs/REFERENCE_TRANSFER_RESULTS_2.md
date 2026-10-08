# Reference-preserving transfer experiment 2: results

Completed October 8, 2026 under [REFERENCE_TRANSFER_PROTOCOL_2.md](REFERENCE_TRANSFER_PROTOCOL_2.md), committed before training (`0cdd715`). Both arms started from the retained 48/64 checkpoint `3b9e8ba41305`. The source hash was unchanged after every chunk. No reserved pool was used.

## Outcome

No checkpoint was accepted. Neither change solved `passages`.

| Arm | Added transitions | Medium regression, 32 episodes | Passages development, 32 episodes |
| --- | ---: | --- | --- |
| Source (reference) | 0 | 27/32 | 0/16 earlier |
| route65 (route-progress reward on passages chunks) | 32,768 | 18/32 (3 collisions, 11 timeouts) | 0/32 (8 collisions, 24 timeouts) |
| route65 | 65,536 | 17/32 (2 collisions, 13 timeouts) | 0/32 (2 collisions, 30 timeouts) |
| budget262 (unchanged reward, longer) | 131,072 | 24/32 (7 collisions, 1 timeout) | 0/32 (24 collisions, 8 timeouts) |
| budget262 | 262,144 | 17/32 (5 collisions, 10 timeouts) | 0/32 (11 collisions, 21 timeouts) |

Experiment 1 retained arm for comparison: 24/32 medium and 0/32 passages at 65,536 added transitions.

## Reading

1. More budget with the same reward did not help. Medium performance fell from 27/32 to 24/32 and then to 17/32 as training continued, and passages stayed at zero. Training on partitioned rooms without success degrades the reference.
2. Route-progress reward did not help within 65,536 transitions and cost medium performance (17/32). The route-progress sum per chunk was about 80 to 165 metres over 8,192 transitions, and no training episode on passages succeeded. The reward gave direction but the policy never completed a route to receive the arrival bonus.
3. The result argues against two simple remedies: more steps and a denser reward, each tried alone. It does not show that they cannot work with a different curriculum. A single seed per arm limits every statement.
4. The failure is not one of training length or reward density alone. The gap between the medium task and `passages` is too large for a policy that has never completed a detour.

The next experiment uses easier partitioned maps that the reference partly solves. See [REFERENCE_TRANSFER_PROTOCOL_3.md](REFERENCE_TRANSFER_PROTOCOL_3.md).
