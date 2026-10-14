# Two-million-transition test (B2): protocol

Declared October 12, 2026, before training. Follows [LARGE_BUDGET_RESULTS.md](LARGE_BUDGET_RESULTS.md): at 1,015,808 added transitions `passages` reached 23/64 (deterministic), one episode below the positive rule, with a curve that was still rising (11, 12, 17, 23) and collisions unchanged (22). Question: does doubling the budget again keep raising `passages`, or does the curve flatten?

## Design

- Start: `runs/training/reference-transfer-7/mix3e4/stage-2.zip`, hash-checked before and after training.
- Single change from B1: the budget doubles to 1,998,848 added transitions (61 stages of 32,768). The learning rate schedule is the same shape, 3e-4 falling linearly to 3e-5 over the new total. Everything else is the B1 recipe (32 simulators: 8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two`; 128 steps; clip 0.1; 3 epochs; minibatch 256; `target_kl` 0.02; gamma 0.995).
- Seed 801, the seed of B1, so that B1 is the matched reference with the same start and recipe at half the budget. The two runs share the first rollouts only; because the schedule differs, trajectories diverge, so this is a budget comparison and not a continuation.
- One training run, no restarts. Code: `scripts/train_large_budget.py` (now takes an optional stage count), `scripts/large_budget_2m_driver.py`, `scripts/eval_cell_mode.py`.

## Curve points

Stages 15, 31, 46 and 61: 491,520, 1,015,808, 1,507,328 and 1,998,848 added transitions.

## Evaluation

- New pool: seeds 885000 to 885063 (64 episodes per cell). Unused before; it selects nothing.
- Every curve point: `passages` and medium. The final point also gets `passages-mid`, `passages-wide` and `gate-two`.
- The B1 final checkpoint (`runs/training/large-budget/seed801/stage-31.zip`) is evaluated on `passages` and medium on the same pool, so that the comparison between 1M and 2M does not depend on pool difficulty.
- Both modes are run for every cell. **The decision mode is deterministic**, as in B1. Evaluation fans out through `scripts/resource_guard.py`.

## Decision rules (frozen)

Applied to the final checkpoint (1,998,848 transitions), deterministic mode, on pool 885000:

- **Positive**: `passages` at least 28/64 and medium at least 48/64, and `passages` at least 4 episodes above the B1 final checkpoint on the same pool. Next step: repeat the better budget with three seeds, then measure level B and C once.
- **Negative**: `passages` at most 20/64, or not above the B1 final checkpoint on the same pool. The budget stops helping at this recipe. Close the scope with the bounded claim and run C1.
- **Inconclusive**: anything else. Report the curve without a conclusion and decide with the user.

The 28 threshold is about one binomial standard deviation (3.5 episodes at 40 percent) above the B1 value of 23 and is an arbitrary cut point, set before the run. The 20 threshold sits just below B1 and allows for pool difference. Also reported: collisions and timeouts, the sampled numbers, and the shape of the curve.

## Limits

- One seed. The variance study found seed spreads of up to 11 episodes of 32 on one profile, so even a positive result is a reason to replicate and not a claim.
- The schedule is tied to the total, so the early points of this run are not the same as the B1 points of equal size.
- Medium at 48 only checks that the budget does not destroy it. The release gate needs 52 and, on `passages`, 52 successes with 3 collisions; this run does not measure level B, level C, `large` or `maze`.
- Collisions stayed at 18 to 30 across the whole B1 curve. If they stay there at 2M, more budget alone does not meet the gate even if successes rise.
