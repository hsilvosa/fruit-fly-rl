# Large-budget test (B1): results

Protocol: [LARGE_BUDGET_PROTOCOL.md](LARGE_BUDGET_PROTOCOL.md), committed (`d3c49c4`) before training. One run, seed 801, 1,015,808 added transitions from the experiment 7 start. Evaluation pool 884000 to 884063 (64 episodes per cell), previously unused.

## Outcome by the frozen rule

**Inconclusive.** At the final checkpoint, deterministic mode, `passages` is 23/64 (threshold for positive: 24) and medium is 59/64. The negative threshold (16 or fewer) is not met either. The result misses the positive rule by one episode, and the rule is not adjusted after the fact.

## Curve (successes / collisions / timeouts, out of 64)

| Added transitions | `passages`, deterministic | `passages`, sampled | Medium, deterministic | Medium, sampled |
| --- | --- | --- | --- | --- |
| 98,304 | 11 / 24 / 29 | 15 / 35 / 14 | 55 / 6 / 3 | 56 / 8 / 0 |
| 294,912 | 12 / 30 / 22 | 13 / 40 / 11 | 51 / 7 / 6 | 54 / 10 / 0 |
| 589,824 | 17 / 18 / 29 | 15 / 34 / 15 | 60 / 3 / 1 | 52 / 12 / 0 |
| 1,015,808 | 23 / 22 / 19 | 25 / 25 / 14 | 59 / 4 / 1 | 58 / 6 / 0 |

Final checkpoint, other cells:

| Cell | Deterministic | Sampled |
| --- | --- | --- |
| `passages-mid` | 48 / 4 / 12 | 52 / 5 / 7 |
| `passages-wide` | 64 / 0 / 0 | 64 / 0 / 0 |
| `gate-two` | 64 / 0 / 0 | 64 / 0 / 0 |

Wilson 95% intervals (percent) for the final deterministic cells: `passages` 25 to 48, medium 83 to 97, `passages-mid` 63 to 84. The interval of `passages` at 23/64 overlaps the interval of the 98k point (10 to 28) only at the edge, and the 589k point (17 to 38) overlaps both.

## What the numbers show

- `passages` rises with the budget in deterministic mode: 11, 12, 17, 23. It is not monotone in sampled mode (15, 13, 15, 25) and the first three points are flat within the interval. The only clear step is the last segment, when the learning rate falls from about 1e-4 to near zero.
- The comparison point is the 262k control mean of 12.3 on `passages` (pool 882000, three seeds). Pools differ, so this is a rough reference. The final value is about 11 episodes above it, and one seed cannot say how much of that is budget and how much is seed luck (the variance study found spreads of up to 11 of 32 on one profile).
- Collisions on `passages` stay between 18 and 30 at every point. The final checkpoint turns timeouts into successes (29 to 19 timeouts) more than it removes collisions (24 to 22). The release gate allows 3.
- Medium is held at 51 to 60 throughout, never below the 48 line. `passages-wide` and `gate-two` are solved (64/64), and `passages-mid` is 48/64, above the earlier best of about 37 on a fresh pool. These extra cells were evaluated at the final point only, so there is no curve for them.
- The sampled and deterministic results agree at the final point (25 and 23), so no hover fixed point is hiding here, unlike the pilot checkpoint on `passages-wide`.

## Limits

- One seed. A repeat could land anywhere in a range of about 10 episodes.
- The learning-rate schedule is tied to the 1M budget, so the early points are not equal to separate short runs.
- The 24/64 threshold and the 16/64 threshold were set before the run and are arbitrary cut points. Reading 23 as nearly positive is an interpretation and not a result.
- Distance to the release gate is large: 23/64 against 52/64 on a partitioned family, with 22 collisions against 3. Level B, level C, `large` and `maze` were not measured.

## What this does and does not support

It supports that the budget is probably a real lever for `passages` (a curve that rises with a medium-room score that does not fall, and a `passages-mid` result above any earlier single run). It does not support that budget alone reaches the gate: even at 1M, `passages` stays below half of the episodes and the collision count is unchanged in order of magnitude. It does not establish unseen-map navigation.

## Artifacts

Run: `runs/training/large-budget/seed801/` (stage checkpoints 1 to 31, `experiment.json`, `summary.json`). Final checkpoint `stage-31.zip`, SHA-256 prefix `0896b5fbe22f9c10`. Source checkpoint unchanged (hash checked after training). Evidence copy in `private/large-budget-evidence/`.

Timing from the clock: training 11:38:56 to 12:20:24 (41 min 28 s, 79 s per stage against 65 s estimated), evaluation 12:20:24 to 12:44:11 (23 min 47 s, against 25 min estimated).
