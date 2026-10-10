# Phase 3 screening (experiment 11): memory

Declared October 10, 2026 before any training. Part of [ZERO_SHOT_PLAN.md](ZERO_SHOT_PLAN.md). The plan lists Phase 3 before Phase 2 in this iteration, at the user's request after [PHASE1_RUN_RESULTS.md](PHASE1_RUN_RESULTS.md).

## Hypothesis

A detour needs memory of where the policy has already looked. The current policy sees one reservoir state and no history, so it hovers at partitions and trades one profile against another. A learned temporal readout over past connectome features should help on the partitioned profiles. This is a hypothesis.

## Design

- Start: `runs/training/reference-transfer-7/mix3e4/stage-2.zip`, as in Phase 1.
- Memory mechanism: the existing history transfer (`fly_rl/training/temporal_policy.py`). A GRU reads the last N connectome feature vectors, one every S simulator ticks (0.05 s), and adds a residual to the current features. The residual is zero at the start, so the transferred policy begins with the exact behavior of the source. The actor and critic weights and their optimizer state are copied. The GRU and residual are new parameters. No raw sensor or map access is added, and the connectome stays in the controller.
- Two memory windows, one change each against the control:

| Arm | History frames N | Stride S (ticks) | Window |
| --- | ---: | ---: | --- |
| short | 8 | 8 | 64 ticks, 3.2 s |
| long | 16 | 32 | 512 ticks, 25.6 s |

- Control: the Phase 1 run, seed 442 (same start, mix, stabilization bundle, budget, seed), already evaluated at all four stages.
- Training: the Phase 1 stabilization bundle (32 simulators with 128 steps, clip range 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, learning rate decaying from 3e-4 to 3e-5, no optimizer restart), the same profile mix, unchanged reward, original goals, coordinated dynamics. 131,072 added transitions in four stages of 32,768. No planner actions, no imitation.
- Screening scope, to keep within time and resources: seed 442 only for both windows. The Phase 3 exit criterion needs two seeds, so a second seed follows only for a promising window.
- Resources: training one process at a time; evaluation through `scripts/resource_guard.py`; no Telegram updates.

## Evaluation

- Stages 2 and 4 (65,536 and 131,072 added transitions) of each arm, on the old pools and the selection pools of Phase 1 (32 episodes per cell). The report pools stay unopened.
- Control numbers at the same stages are in [PHASE1_RUN_RESULTS.md](PHASE1_RUN_RESULTS.md): selection pools, stage 2 [28, 29, 30, 32, 22, 6, 1] and stage 4 [25, 26, 31, 32, 22, 6, 2], in the order medium, medium-b, gate-two, gate-long, passages-wide, passages-mid, passages.

## Decision rule (frozen before running)

- Hard-profile sum: passages-wide plus passages-mid plus passages on the selection pools. Control: 29 at stage 2, 30 at stage 4.
- A window is promising if at stage 2 or stage 4 its hard-profile sum is at least 10 above the control at the same stage, and medium is at least 21/32, medium-b at least 20/32 and gate-two at least 28/32 on the selection pools.
- A promising window earns a second seed with four evaluations. The Phase 3 exit criterion stays as in the plan: a gain of at least 6 episodes of 32 over the no-memory control on a development cell, on two seeds.
- If neither window is promising, the result is recorded as negative for these windows. It does not show that memory cannot help.

## Limits

One seed per window at this stage. Thirty-two episodes per cell, and two seeds from one start differed by up to 18 episodes in Phase 1. A gain of 10 episodes in a sum of three cells is within what one seed can produce, so a promising window is a reason to replicate, not a result.
