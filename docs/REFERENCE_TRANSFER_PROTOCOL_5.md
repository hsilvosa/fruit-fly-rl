# Reference-preserving transfer experiment 5: full passages in the mix

Declared October 8, 2026 before any training. Experiment 4 met its positive result, which permits this stage.

## Design

- Initialization: `runs/training/reference-transfer-4/recover/chunk-8.zip`. Lineage: 50/64 source, experiment 3, experiment 4, this stage. Hash recorded at launch.
- One change relative to experiment 4: the `passages` profile enters the training mix.
- Plan: sixteen chunks of 8,192 (131,072 added). Cycle of eight, twice: medium, passages, medium, passages-wide, medium, passages, gate-two, passages-wide. Medium rooms are 37.5%. Unchanged reward, original goals, batch 8, gamma 0.995, coordinated dynamics, training seeds 242 plus chunk index. No planner actions, no imitation.
- Evaluation cells run as parallel processes (`scripts/eval_cell.py`). Results are unchanged by this.

## Evaluation and selection (frozen before running)

- Cells: medium seeds 100000-100031, medium-b 840000-840031, gate-two 830000-830031, gate-long 830000-830031, passages-wide 830000-830031, passages 810000-810031 (32 episodes each).
- Baselines: the experiment 4 selected checkpoint on all cells.
- Evaluate after 65,536 and 131,072 added transitions.
- Accept a checkpoint only if medium is at least 21/32 and medium-b is at least 20/32. Among accepted checkpoints, choose the highest passages count, then passages-wide, then the earlier checkpoint.
- Positive result: an accepted checkpoint whose passages count is at least four above the baseline, and whose gate-two is at least 28/32. This permits maze and architectural stages. It is not a generalization claim.

## Limits

One seed. Passages pool 810000 was used for earlier failure classification and for experiments 1 and 2. It is a development pool and has been inspected. No reserved pool is used.
