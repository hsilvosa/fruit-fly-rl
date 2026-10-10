# Medium-room regression suite

Frozen October 10, 2026 (roadmap action R2). This suite checks that a candidate keeps the skill of the recovered historical reference on the original medium dense-room task. It runs evaluation only. It does not train, and it uses no reserved pool.

## Definition

- Task: `dense-v3` rooms, 32 x 32 x 12 m, 48 obstacles, coordinated dynamics, no map profile, original goals, episode limit 1,200 ticks. This is the task of the 43 to 78% historical results.
- Four fixed pools of 32 episodes each, 128 episodes in total:

| Pool | Seeds | Origin |
| --- | --- | --- |
| A | 100000 to 100031 | Validation pool of the 50/64 policy, where it scored 23/32 |
| B | 840000 to 840031 | Development pool created in transfer experiment 4 |
| C | 860000 to 860031 | Phase 1 selection pool, medium |
| D | 861000 to 861031 | Phase 1 selection pool, medium-b |

- These pools have been inspected. The suite is a regression check, not an independent test. Pools C and D are also selection pools for Phases 1 and 3, so a candidate chosen on them for medium performance would be circular. Future phases must select on other medium pools.
- Pass rule (amended after the baselines, see below): at least 17 of 32 successes in every pool, and at least 88 of 128 in total (68.75%). The rule first declared was 21 of 32 per pool, taken from the floor used in the transfer and Phase 1 work. It failed two historical winners and was relaxed.
- The suite also lists the lost successes: seeds that a reference policy solves and the candidate fails, per pool, and the gained successes. A pass does not hide lost successes.
- Command: `python -s scripts/regression_medium.py <checkpoint.zip> <label> <output-dir> [reference-result.json]`. Evaluation goes through the resource guard.
- Evaluation repeats to within one episode per pool ([PHASE1_PILOT_RESULTS.md](PHASE1_PILOT_RESULTS.md)). A difference of one episode in a pool is not a regression.

## Baselines

| Checkpoint | A | B | C | D | Total of 128 | Original rule (21 per pool) | Amended rule (17 per pool) | Lost / gained against 50/64 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50/64 historical reference (`0a1a6569549a`) | 23 | 23 | 22 | 25 | 93 (72.7%) | pass | pass | reference |
| 48/64 historical (`3b9e8ba41305`) | 20 | 27 | 25 | 26 | 98 (76.6%) | fail (pool A 20) | pass | 15 / 20 |
| 45/64 historical (`92d9c8ba2ff3`) | 26 | 24 | 23 | 17 | 90 (70.3%) | fail (pool D 17) | pass | 25 / 22 |
| Experiment 7 selected (`773dff8d53e2`), start of Phases 1 and 3 | 26 | 29 | 28 | 28 | 111 (86.7%) | pass | pass | 8 / 26 |
| Pilot candidate (`71889c4d752a`) | 24 | 28 | 25 | 27 | 104 (81.3%) | pass | pass | 12 / 23 |

All five evaluations ran with the declared pools and are stored in `runs/verification/regression-medium/` (local, ignored by git). The pool A result for the 50/64 policy, 23/32, equals its recorded validation result.

### Amendment after the baselines

The first rule, 21 of 32 in every pool, failed two of the three historical winners: 48/64 scored 20 in pool A and 45/64 scored 17 in pool D. The rule was too strict for 32-episode pools, because the winners themselves fall below it by chance. The floor per pool was then lowered to 17 of 32, the lowest value a historical winner reached, and the total floor stayed at 88 of 128. This change was made after seeing the baselines, and the table keeps both outcomes so that the change is visible. The script reports `passes` (amended) and `passes_original_rule`.

### What the lost successes mean

Even policies of similar quality lose many of each other's successes: 48/64 loses 15 and gains 20 against 50/64. Different policies solve different episodes, so a count of lost successes is not evidence of regression by itself. The suite uses the totals and the per-pool floors for the verdict, and uses the lost list to point at episodes worth inspecting.

### Reading

- Medium-room skill has not degraded along the transfer work. The experiment 7 start and the pilot candidate score above all three historical winners on these pools (111 and 104 of 128, against 90 to 98).
- These four pools were inspected, and two of them (C and D) are selection pools of Phases 1 and 3. They support a regression check, not a claim of improvement over the historical results.

## Use

Every candidate checkpoint of Phase 2 and later runs this suite before it is called a candidate. A fail stops promotion, whatever the other cells show. The reference for lost successes is the 50/64 policy.
