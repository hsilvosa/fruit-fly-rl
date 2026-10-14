# Privileged-waypoint diagnostic: protocol

Declared October 11, 2026, before training. This is a diagnostic of the training pipeline and of the input, not a student. A policy trained here reads the certified route during flight, so it must never be reported as an autonomous result or enter a student comparison.

## Question

The feature probe ([FEATURE_PROBE.md](FEATURE_PROBE.md)) showed that the policy input decodes the direction to the next stretch of the route only to about 50 degrees on hard samples. Is that missing information the reason `passages` stays low? Test: give the same training recipe the missing information, and see whether `passages` rises.

## Design

- Start: `runs/training/reference-transfer-7/mix3e4/stage-2.zip`, the start of the variance study and of R5.
- Change (one): the policy input grows from 256 to 259 values. The three new values are the unit vector, in the body frame, to the point of the certified route 4 m ahead of the fly's progress (`fly_rl/training/waypoint_diagnostic.py`). All source weights are copied and the three new first-layer columns start at zero, so the expanded policy computes exactly what the source computed (a unit test checks the actions and values). Adam moments restart in both arms.
- Control arm: the same network, pipeline and seeds with the three values fixed at zero. It separates the effect of the information from the effect of the expansion and of the training pipeline.
- Recipe otherwise equal to the variance study: 32 simulators with 8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide` and 4 `gate-two` rooms; 128 steps; clip 0.1; 3 epochs; minibatch 256; `target_kl` 0.02; learning rate 3e-4 to 3e-5; gamma 0.995; original reward and goals; no planner actions; no imitation; full connectome.
- Budget: 262,144 added transitions (8 stages of 32,768), because the three new inputs start with zero weights and need room to be used. This is about 2.7 times the variance-study budget, so the control arm is also a budget check at the same recipe. The trained checkpoints at 98,304 transitions are saved as `stage-3.zip` and evaluated only if the final checkpoint is ambiguous.
- Seeds: 701 and 702, in both arms. Four training runs in total, run one after the other.
- Terminal bootstrap: at an episode end the terminal observation reuses the waypoint of the previous step (the fly moves at most about 0.15 m per step).

## Evaluation

Final checkpoint of each run, pool seeds 880000 to 880063 (64 episodes per cell; it was used for confirmations before, never for selection), deterministic actions, with the waypoint input for the waypoint arm and zeros for the control. Cells: `passages`, `passages-mid`, `passages-wide` and medium. Scripts: `scripts/eval_waypoint_cell.py` and `scripts/waypoint_driver.py`. No checkpoint is selected: one final checkpoint per run is reported, with Wilson intervals.

## Decision rules (frozen before running)

- Information is the main limit: the mean of the two waypoint runs on `passages` is at least 40/64, at least 20/64 above the control mean, and each waypoint run is above both control runs. Medium stays at 52/64 or more in every run.
- The trainer or the dynamics are the main limit: the waypoint mean on `passages` is below 20/64, or the gain over the control is below 8/64. A policy that has the route direction in its input and still does not follow it points at the optimizer, the reward or the flight dynamics.
- Anything in between is partial: the information helps, but not enough to explain the gap. It is reported with the numbers and without a conclusion beyond that.
- Also reported: `passages-mid`, `passages-wide` and medium for every run, collisions and timeouts, and the control-versus-start comparison (the control at 262k transitions is a budget check, with the earlier 98k results as reference).

## Limits

Two seeds per arm, which cannot establish reliability (the variance study found seed spreads of 6 to 11 episodes of 32). A large effect would be visible; a small one would not. One look ahead distance (4 m). The waypoint is exact and noise-free, which is the most favorable case: a positive result gives an upper bound on what better sensing could do, and a negative result is strong. The result does not say whether longer sensors or memory could supply the same information to a real student.
