# Phase 1 run (experiment 10): stable trainer, two seeds, four evaluations

Declared October 10, 2026 before any training. Part of [ZERO_SHOT_PLAN.md](ZERO_SHOT_PLAN.md). It follows the pilot ([PHASE1_PILOT_RESULTS.md](PHASE1_PILOT_RESULTS.md)), which had one seed and one evaluation.

## Design

- Initialization: `runs/training/reference-transfer-7/mix3e4/stage-2.zip`, the same start as experiment 8 (control) and the pilot.
- Same 32-simulator profile mix, stabilization bundle and settings as the pilot: clip range 0.1, 3 epochs, minibatch 256, 128 steps per simulator, `target_kl` 0.02, learning rate decaying linearly from 3e-4 to 3e-5 over the run, no optimizer restart, unchanged reward, original goals, no planner actions, no imitation, full MaleCNS v1.0 connectome.
- Budget: 131,072 added transitions per seed, in four stages of 32,768. Seeds 442 and 443.
- Resource limits: CPU and memory stay below 80 percent, with no GPU limit. Training of the two seeds runs one after the other, because one training process uses about half of the CPU. Evaluation cells go through `scripts/resource_guard.py`. Training finishes before the evaluation of its checkpoints starts.

## Pools

- Old pools, for comparison with experiment 8: medium 100000, medium-b 840000, gate-two 830000, gate-long 830000, passages-wide 830000, passages-mid 850000, passages 810000.
- Selection pools, used to choose checkpoints: medium 860000, medium-b 861000, gate-two 862000, gate-long 862000, passages-wide 863000, passages-mid 864000, passages 865000.
- Report pools stay unopened. They are reserved for the final Phase 1 report after the candidate is selected and frozen.
- 32 episodes per cell.

## Acceptance and selection (frozen before running)

- Accept a checkpoint only if, on the selection pools, medium is at least 21/32, medium-b at least 20/32, passages-wide at least 16/32 and gate-two at least 28/32.
- Among accepted checkpoints of both seeds, choose the highest passages-mid, then passages, then the earlier checkpoint.
- Stability measure, on the old pools: for each seed, the range (largest minus smallest count) of passages-wide and of passages-mid across the four evaluations. Experiment 8 ranges over its four evaluations, from its results table: passages-wide 16 (seed 442) and 9 (seed 443); passages-mid 4 and 5. Including its starting checkpoint, passages-wide ranged 24 and 23.
- Phase 1 exit criterion (from the plan, made exact here): for both seeds, the range of passages-wide on the old pools is at most 6 episodes, medium stays at or above 21/32 on the selection pools at all four evaluations, and each seed has at least one accepted checkpoint. Otherwise the result is recorded as negative.

## Limits

Two seeds from one start. They measure training-seed variance, not variance of the whole lineage. Thirty-two episodes per cell. Old and selection pools have been seen by the analysis. No report or reserved pool is used.
