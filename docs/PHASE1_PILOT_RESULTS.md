# Phase 1 pilot (experiment 9): results

Completed October 9, 2026 under [PHASE1_PILOT_PROTOCOL.md](PHASE1_PILOT_PROTOCOL.md), committed before training (`2627f2a`) and amended after a resource incident (`7642f06`). One seed (442), 98,304 added transitions with the stabilization bundle, one evaluation of the final checkpoint on the new selection pools. The starting checkpoint hash was unchanged. No report or reserved pool was used.

## Resource incident

The first launch started 28 evaluation processes at once. Memory and CPU reached 100 percent and the user's machine restarted. None of that launch's results is used. The fix, in `scripts/resource_guard.py`: new processes start only below 65 percent of CPU and memory, with staggered starts, at most 8 processes and 2 numerical threads each. The user's limit is 80 percent for CPU and memory, with no limit on the GPU. The rerun stayed at 50 to 57 percent memory and 7 to 57 percent CPU. An intermediate attempt with only a process cap (3) and a memory floor reached 100 percent CPU for a short time and was stopped, so the CPU check and the thread limit were added.

## Outcome

Not accepted under the declared rule: passages-wide fell below 16/32. The pilot did not meet its positive condition, and the stability part could not be assessed with one evaluation.

Selection pools (new seeds, 32 episodes per cell):

| Checkpoint | Medium 860000 | Medium-b 861000 | Gate-two | Gate-long | Passages-wide | Passages-mid | Passages |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Start (experiment 7 selected) | 28 | 28 | 31 | 27 | 23 | 10 | 0 |
| After 98,304 added, stabilized | 25 (5 coll, 2 timeout) | 27 (3, 2) | 32 | 32 | **12** (0 coll, 20 timeout) | **21** (4, 7) | **5** (8, 19) |

## Reading

1. Training moved well on the harder profiles that were in the mix: passages-mid 10 to 21 of 32, passages 0 to 5 of 32, gate-long 27 to 32 of 32. Medium rooms stayed at 25 to 27 of 32.
2. Passages-wide fell from 23 to 12 of 32, with no collisions and 20 timeouts. The policy gained on the harder profile and lost on the easier one, so one profile still trades against another.
3. The training log shows small, controlled updates: approximate KL about 0.001 to 0.003, and the learning rate decayed from 3e-4 to 3e-5. These are consistent with the stabilization bundle, and they do not show that the bundle prevents oscillation. One checkpoint gives no stability measurement.
4. Single seed. The result is a development number. The start values on the new selection pools differ from the old pools (passages-wide 23 here, 25 before), which shows the spread between pools.

## Next

Phase 1 stays open. Needed: the second seed, evaluations after each stage (four in the full criterion) under the resource guard, and an ablation of the bundle if it holds. The checklist in [ZERO_SHOT_PLAN.md](ZERO_SHOT_PLAN.md) is updated. No run is active.
