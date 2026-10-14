# Variance study (action R1): results

Completed October 10, 2026 under [VARIANCE_STUDY_PROTOCOL.md](VARIANCE_STUDY_PROTOCOL.md), committed before training (`da55a04`). Five training runs of the Phase 1 pilot recipe, seeds 501 to 505, 98,304 added transitions each, from the experiment 7 checkpoint. Each final checkpoint was evaluated on the seven selection cells and on the medium regression pools A and B (32 episodes per cell). The report pools stayed unopened. The study took 53 minutes against an estimate of 60. One evaluation was interrupted by the driver's memory limit (another program on the machine was using memory too) and was rerun without loss.

## Outcome

Training variance is large. By the declared rule, every later comparison now needs at least three seeds and 64 episodes per cell, and candidates are chosen by best-of-N on a selection pool with a separate report pool.

Selection pools, 32 episodes per cell:

| Run | Medium | Medium-b | Gate-two | Gate-long | Wide | Mid | Passages | Hard sum | Regression total of 128 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 501 | 23 | 27 | 32 | 32 | 13 | 10 | 2 | 25 | 102 |
| 502 | 25 | 28 | 32 | 32 | 23 | 7 | 1 | 31 | 100 |
| 503 | 27 | 25 | 32 | 32 | 18 | 12 | 3 | 33 | 106 |
| 504 | 24 | 26 | 32 | 32 | 12 | 13 | 3 | 28 | 98 |
| 505 | 26 | 28 | 31 | 31 | 23 | 9 | 2 | 34 | 107 |
| Mean (standard deviation, range) | 25.0 (1.6, 4) | 26.8 (1.3, 3) | 31.8 (0.4, 1) | 31.8 (0.4, 1) | 17.8 (5.3, **11**) | 10.2 (2.4, 6) | 2.2 (0.8, 2) | 30.2 (range 9) | 98 to 107 |

- All five runs pass the amended medium regression suite and keep gate-two at 28/32 or more.
- Passages-wide ranges over 11 episodes (12 to 23). That meets the decision rule's threshold of 10. Passages-mid ranges over 6 and passages over 2.
- None of the five reached passages-mid of 20/32. The pilot checkpoint, from the same recipe, scored 21/32.
- Best eligible run by the hard-profile sum: seed 505 (34).

## Confirmation on a fresh pool

The best run and the pilot checkpoint were then evaluated on a pool that selection never used: seeds 880000 to 880063, 64 episodes per cell, with Wilson 95% intervals.

| Checkpoint | Passages-wide | Passages-mid | Passages | Medium |
| --- | --- | --- | --- | --- |
| Seed 505, best of five | 41/64 (64%, 52 to 75%) | 17/64 (27%, 17 to 38%) | 2/64 (3%, 1 to 11%) | 55/64 (86%, 75 to 92%) |
| Pilot candidate | 14/64 (22%, 14 to 33%) | 37/64 (58%, 46 to 69%) | 17/64 (27%, 17 to 38%) | 57/64 (89%, 79 to 95%) |

This confirmation was added after seeing the five results and is labeled as such. It does not change the decision rule.

## Reading

1. The pilot checkpoint is a real, better policy on the harder profiles, not a measurement fluke. On a fresh pool with 64 episodes it scores 58% on passages-mid and 27% on passages, well above every run of the recipe (passages-mid 22 to 41% and passages 3 to 9% on the selection pools). It does this at the cost of passages-wide (22%, against 64% for seed 505).
2. The recipe reaches that region rarely: the pilot was one draw in six, and none of the five repeats came close on passages-mid. Training outcomes are spread widely, and a minority of runs land in a much better place. This is the case for best-of-N with held-out selection.
3. The two checkpoints show the same trade-off as before. Seed 505 keeps passages-wide and gives up the harder profiles, and the pilot does the opposite. No checkpoint holds both.
4. Medium rooms stay high for all runs (regression 98 to 107 of 128; fresh pool 86% and 89%).
5. Evaluation noise is about one episode per 32. The spread between runs is 6 to 11 episodes on the middle profiles. Training variance is therefore the dominant source, as already suspected.

## Consequences

- Rule adopted: every comparison needs at least three seeds and 64 episodes per cell. A difference under about 10 episodes of 32 (or 20 points of 64) between single runs is not a result.
- Candidate selection becomes best-of-N on a selection pool with a separate report pool. R5 is planned with that structure.
- The pilot checkpoint stays the best development candidate. It is confirmed on one fresh pool. It remains a development result: it is still far from the 81% gate on `passages` (27%), and it was chosen among several runs.
