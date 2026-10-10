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
- Pass rule, fixed before the baselines were measured: at least 21 of 32 successes in every pool, and at least 88 of 128 in total (68.75%). The numbers come from the 21/32 floor used throughout the transfer and Phase 1 work.
- The suite also lists the lost successes: seeds that a reference policy solves and the candidate fails, per pool, and the gained successes. A pass does not hide lost successes.
- Command: `python -s scripts/regression_medium.py <checkpoint.zip> <label> <output-dir> [reference-result.json]`. Evaluation goes through the resource guard.
- Evaluation repeats to within one episode per pool ([PHASE1_PILOT_RESULTS.md](PHASE1_PILOT_RESULTS.md)). A difference of one episode in a pool is not a regression.

## Baselines

BASELINES_TABLE

## Use

Every candidate checkpoint of Phase 2 and later runs this suite before it is called a candidate. A fail stops promotion, whatever the other cells show. The reference for lost successes is the 50/64 policy.
