# Large-budget test (B1): protocol

Declared October 12, 2026, before training. Question: is the training budget the lever that keeps `passages` low? Every earlier comparison used 98k to 262k added transitions. This is the one large hypothesis not yet tested cleanly.

## Design

- Start: `runs/training/reference-transfer-7/mix3e4/stage-2.zip` (retained, hash-verified). Source and sidecar hashes are recorded before and after training.
- Single change: the budget grows to 1,015,808 added transitions (31 stages of 32,768). Nothing else differs from the Phase 1 pilot recipe: 32 simulators (8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two`), 128 steps, clip 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, gamma 0.995, learning rate 3e-4 falling linearly to 3e-5 over the whole budget.
- Policy: the unchanged 256-input network with the full connectome. No privileged input, no auxiliary loss.
- One seed (801). One training run, no restarts.
- Code: `scripts/train_large_budget.py` (copy of the Phase 1 run trainer without in-training evaluation), `scripts/large_budget_driver.py`, `scripts/eval_cell_mode.py`.

## Curve points

Checkpoints are saved at every stage. The curve uses stages 3, 9, 18 and 31, that is 98,304, 294,912, 589,824 and 1,015,808 added transitions (the nominal 100k, 300k, 600k and 1M, rounded to whole stages).

## Evaluation

- New pool: seeds 884000 to 884063 (64 episodes per cell). Not used before for anything. It selects nothing.
- Every curve point: `passages` and medium. The final point also gets `passages-mid`, `passages-wide` and `gate-two`.
- Both action modes are run for every cell: deterministic (argmax) and sampled. **The decision mode is deterministic**, as in all earlier controls (the 262k control mean on `passages` is 12.3 of 64). Sampled results are reported, never used to pick the mode afterwards.
- Evaluation fans out through `scripts/resource_guard.py` (at most 4 processes, 2 threads each).

## Decision rules (frozen)

Applied to the final checkpoint (1,015,808 transitions), deterministic mode:

- **Positive**: `passages` at least 24/64 and medium at least 48/64. Next step: repeat with three seeds and measure level B and C once.
- **Negative**: `passages` at most 16/64. Close the scope with the bounded claim (zero-shot in medium rooms, partial in partitioned rooms), then run C1 and prepare the release with limitations.
- **Inconclusive**: anything else, including `passages` above 16 with medium below 48. Report the curve without a conclusion about budget.

Also reported: collisions and timeouts per cell, the sampled-mode numbers, and the shape of the curve (rising, flat or falling). The curve does not change the rule.

## Limits

- One seed. The variance study found seed spreads of up to 11 episodes of 32 on one profile, so a positive result justifies a repeat and not a claim, and a negative one does not exclude a lucky seed.
- The learning rate schedule is tied to the 1M budget, so the earlier points are not the same as separate shorter runs.
- Medium at 48 only checks that the budget does not destroy it. The final gate needs 52.
- Level B and C are not measured here.
