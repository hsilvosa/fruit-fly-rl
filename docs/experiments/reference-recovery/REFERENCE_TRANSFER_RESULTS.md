# Reference-preserving transfer experiment 1: results

Completed October 8, 2026 under the protocol in [REFERENCE_TRANSFER_PROTOCOL.md](REFERENCE_TRANSFER_PROTOCOL.md). The protocol was committed before training (`468cf39`). Detailed run records are local in `runs/training/reference-transfer-1/` and `private/reference-recovery-1-evidence/`.

## Outcome

No checkpoint was accepted. The retained policy did not learn `passages` in 65,536 added transitions and lost reference performance on the medium regression pool. The fresh control learned neither task. No candidate was promoted. No alias, original run or reserved pool was touched. The source checkpoint hash was unchanged after every chunk in both arms.

## Results

Both arms trained 65,536 added transitions in eight chunks of 8,192 (25% medium rooms), with the full MaleCNS v1.0 connectome, no planner and no imitation. Each arm took about 5.5 minutes of training.

| Arm | Lifetime transitions | Evaluation after | Medium regression, 32 episodes | Passages development, 32 episodes |
| --- | ---: | --- | --- | --- |
| Source checkpoint (reference) | 131,072 | not applicable | 27/32 | 0/16 on a different seed set, earlier ladder |
| Retained | 163,840 | 32,768 added | 24/32 (1 collision, 7 timeouts) | 0/32 (2 collisions, 30 timeouts) |
| Retained | 196,608 | 65,536 added | 24/32 (4 collisions, 4 timeouts) | 0/32 (10 collisions, 22 timeouts) |
| Fresh control | 32,768 | 32,768 added | 5/32 (3 collisions, 24 timeouts) | 0/32 |
| Fresh control | 65,536 | 65,536 added | 11/32 (2 collisions, 19 timeouts) | 0/32 (5 collisions, 27 timeouts) |

Medium pool seeds 240000-240031. Passages pool seeds 810000-810031. The accepted-checkpoint rule required at least 25/32 on the medium pool. Both retained checkpoints reached 24/32, one episode short, so the rule rejects them.

Lost and gained successes against the source's 27 successes on the medium pool:

- After 32,768 added transitions: lost 240007, 240016, 240022, 240026, 240030. Gained 240000, 240005.
- After 65,536 added transitions: lost 240006, 240011, 240016, 240018, 240026. Gained 240000, 240021.

The lost seeds change between checkpoints. Only 240016 and 240026 appear in both lists. This pattern fits ordinary policy variation under PPO updates more than a systematic loss of one situation.

## Interpretation

1. The retained policy kept most of its medium-room skill (24/32 against 27/32) while training. The fresh control reached 11/32 in the same budget. The historical reference therefore remains the stronger starting point, as the user required.
2. Passages did not move. Neither arm had a single success. The retained policy moved from timeouts toward collisions (2 to 10 collisions out of 32), which fits a policy that starts to explore without finding the openings.
3. With zero successes, PPO receives progress shaping and terminal penalties but no success signal on this map. A larger budget alone may or may not change that. This run cannot say.
4. The result separates two earlier confusions. The older curriculum 2 failure came from a changed interface and a fresh policy. This run kept the interface and the retained policy, and passages is still unsolved at 65,536 transitions. The task is hard for this reward and exploration setup, independent of the interface.

## Limits

- One training seed per arm. No claim about the method follows.
- Sixty-five thousand transitions is small next to the 131,072 transitions used by the reference itself.
- Thirty-two episodes per cell. The 24/32 versus 27/32 difference is within pool noise (Wilson 95% intervals overlap widely). The protocol rule is strict, so the checkpoint is rejected, but this does not show a real regression.
- The medium regression pool was inspected before. It is a regression check, not an independent test.
- Failure trajectories on passages were not recorded or classified.

## Next options (not launched)

| Option | Change | Reason | Cost |
| --- | --- | --- | --- |
| A | Same retained arm, 262,144 added transitions, one seed | Tests whether passages needs more budget. Cheapest option. | About 25 minutes |
| B | Easier intermediate map between `open` and `passages` (fewer partitions, wider openings), original goals | Gives PPO a success signal before full partitions | Needs a profile choice and a mastery gate |
| C | Planner imitation on passages with a separate teacher budget, then planner-free student evaluation | Gives a direct signal for opening crossing | Needs separate teacher and imitation budgets |
| D | Record and classify passages failures before further training | Shows whether the policy cannot find openings or cannot cross them | No training, minutes |

D should come first because it is free and decides between A, B and C.
