# Phase 1: stable-trainer pilot (experiment 9)

Declared October 9, 2026 at about 20:15, before any training. Part of [ZERO_SHOT_PLAN.md](ZERO_SHOT_PLAN.md). The run is a time-bounded pilot (the session ends at 21:00), not the full Phase 1 criterion.

## Hypothesis

Experiment 8 lost its gains with plain PPO at constant learning rate and 8 correlated simulators. A smaller trust region, a decaying learning rate and more decorrelated rollouts should keep the gains. This is a hypothesis, not a measured cause.

## Design

- Initialization: `runs/training/reference-transfer-7/mix3e4/stage-2.zip`, the same start as experiment 8. Experiment 8 is the control.
- Same profile mix as experiments 7 and 8, scaled to 32 parallel simulators (medium 8, passages-mid 12, passages 4, passages-wide 4, gate-two 4). Unchanged reward, original goals, coordinated dynamics, gamma 0.995. No planner actions, no imitation. Full MaleCNS v1.0 connectome.
- Stabilization bundle, applied after loading (no change to `learning.py`): 32 simulators with 128 steps each (4,096 transitions per update, as before, but from four times more distinct episodes); clip range 0.1; 3 epochs per update; minibatch 256; `target_kl` 0.02 (native early stop of epochs); learning rate decaying linearly from 3e-4 to 3e-5 over the run, with no optimizer restart; one uninterrupted run per seed.
- The bundle changes several factors together on purpose. An ablation follows only if the bundle works.
- Budget: 98,304 added transitions per seed, in three stages of 32,768 with an evaluation after each. Seeds 442 and 443, in parallel.

## Pools

- Old pools, for comparison with experiment 8: medium 100000, medium-b 840000, gate-two 830000, gate-long 830000, passages-wide 830000, passages-mid 850000, passages 810000 (32 episodes each).
- New selection pools, never used for reporting: medium 860000, medium-b 861000, gate-two 862000, gate-long 862000, passages-wide 863000, passages-mid 864000, passages 865000 (32 episodes each). Checkpoints are chosen on these.
- Report pools are not opened in this pilot. They are reserved for the full Phase 1 run.

## Acceptance and selection (frozen before running)

- Accept only if, on the selection pools, medium is at least 21/32, medium-b at least 20/32, passages-wide at least 16/32 and gate-two at least 28/32.
- Among accepted checkpoints of both seeds, choose the highest passages-mid on the selection pools, then passages, then the earlier checkpoint.
- Stability measure (reported, not a gate): for each seed, the largest change in passages-wide and passages-mid between consecutive evaluations on the old pools. Experiment 8 reached changes of 24 and 11 episodes.
- Positive pilot result: a seed whose passages-wide stays within 6 episodes across its three evaluations on the old pools, and at least one accepted checkpoint.

## Limits

Two seeds from one start, three evaluations each, 32 episodes per cell. A pilot cannot meet the Phase 1 exit criterion (four evaluations). No reserved or report pool is used.

## Amendment after a resource incident (October 9, 2026, about 20:35)

The first launch started 28 evaluation processes at once (14 cells for each of two seeds). Each process loads the connectome, so memory and CPU reached 100 percent and the user's machine restarted. No result from that launch is used, and no training output of it is kept. This was an error in how the run was launched.

Changes declared before the rerun:

- Every evaluation fan-out goes through `scripts/resource_guard.py`: at most 3 processes at once, a free-memory floor of 8 GB and staggered starts.
- The pilot is reduced to seed 442 only. Seed 443 is not run.
- Only the final stage (98,304 added transitions) is evaluated, and only on the new selection pools. The old pools and the stability measure across evaluations are not collected.
- The acceptance rule, the selection pools and the stabilization bundle are unchanged. With one checkpoint, the selection rule reduces to the acceptance test. The positive pilot result of the stability condition cannot be assessed and is left open.
