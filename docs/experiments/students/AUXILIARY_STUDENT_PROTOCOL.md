# Autonomous students with a training-only route signal: protocol

Declared October 11, 2026, before training. Follows the third committee review ([SENSING_PROBES.md](../diagnostics/SENSING_PROBES.md), [WAYPOINT_DIAGNOSTIC_RESULTS.md](../diagnostics/WAYPOINT_DIAGNOSTIC_RESULTS.md)).

## Question

The privileged-waypoint diagnostic showed that giving the route direction to the policy lifts `passages` from 17% to 59%. The synthetic probe showed that a network with enough data recovers most of that direction from the policy's own 8 m rays (34 degrees on hard samples), so the gap looks like a learning problem. Can the route direction help training without ever reaching the actor at test time? Two ways to test it, in separate arms:

- **Auxiliary arm (`aux`):** a head on the actor's last hidden layer is trained to predict the route direction (cosine loss, coefficient 1.0). Actor and critic are both blind to the route input. The direction is a label only. It shapes the actor's representation.
- **Privileged-critic arm (`critic`):** the critic reads the route direction, the actor does not. The critic is not used at test time. It can only change the value estimates and therefore the advantages during training.

## Design

- Start: `runs/training/reference-transfer-7/mix3e4/stage-2.zip`.
- Network and recipe equal to the waypoint diagnostic: input 259 values (256 features and the 3 route columns), all source weights copied, new columns at zero; 32 simulators (8 medium, 12 `passages-mid`, 4 `passages`, 4 `passages-wide`, 4 `gate-two`); 128 steps; clip 0.1; 3 epochs; minibatch 256; `target_kl` 0.02; learning rate 3e-4 to 3e-5; gamma 0.995; original reward and goals; no planner actions; no imitation; full connectome. Budget: 262,144 added transitions (8 stages).
- Blindness is enforced in `fly_rl/training/waypoint_students.py`: the actor's first-layer weights for the route columns are zero and their gradient is masked (also the critic's in the `aux` arm). Unit tests check that the actor output does not change with those inputs at the start, after training and after a save and load, that the critic columns do learn in the `critic` arm, and that the auxiliary head reduces its loss. At test time the route columns are zeros.
- Seeds: 801, 802 and 803 for each student arm.
- Control: the same pipeline with the route columns at zero, seeds 701, 702 (already trained in the diagnostic) and 703 (new). The three controls are evaluated again on the new pool, together with the students, so that all runs share the same cells.
- Order: aux 801, critic 801, control 703, aux 802, critic 802, aux 803, critic 803. Runs are in series.

## Evaluation

Final checkpoint of every run, 64 episodes per cell, deterministic actions unless stated. New pool, reserved for this experiment: seeds 882000 to 882063 (never opened before). Cells: `passages`, `passages-mid`, `passages-wide`, medium; `passages` with sampled actions (action sampling by the policy only); level B development maps (held-out sampler, difficulty 0.8, seeds 950000 to 950063, inspected, not used to decide anything). Wilson 95% intervals are reported. No checkpoint is selected: one final checkpoint per run.

The primary metric is `passages` with deterministic actions on pool 882000. Sampled actions are reported alongside, and a conclusion that holds in only one of the two modes is stated as such.

## Decision rules (frozen before running)

For each student arm against the three controls:

- **Positive:** the arm mean on the primary metric is at least 12/64 above the control mean, and each of the three arm runs is above each of the three control runs. In addition, the arm mean of `passages` collisions is lower than the control mean by at least 8/64, and the arm means on `passages-mid`, `passages-wide` and medium are not lower than the control means by more than 4/64.
- **Negative:** the gain on the primary metric is below 6/64 (the spread of the control seeds in the diagnostic was 6/64 on `passages`).
- Anything between is **inconclusive**, and no seeds are added afterward.
- A positive result in the sampled mode only, or in the deterministic mode only, is reported as partial.
- Reference only, never a comparison: the diagnostic runs with the route as an actor input (39 and 36 of 64 on `passages` in pool 880000) give the order of magnitude of what exact information achieves.

## Interpretation

- `critic` positive and `aux` not: credit assignment during training matters, and the actor can use it without extra information.
- `aux` positive and `critic` not: shaping the representation is what matters.
- Both positive: both help, and a combination is the natural next experiment.
- Neither: the route direction as a training signal is not enough at this budget. The gap to the diagnostic then comes from the actor reading the route at test time, which a student cannot do. Longer range or memory would be the remaining paths for `passages`, and the claim would stay at medium rooms.

## Limits

Three seeds per arm, with a variance between seeds that earlier studies found large; the thresholds are screening rules and no guarantee of reliability. One auxiliary coefficient and one head, with no tuning. The label is the direction to a point 4 m ahead on the certified route, which can change abruptly near route projections and can penalize other valid paths. The probes were run on `passages` only: mazes and large rooms are not covered by this experiment, and the level B development cell is the only evidence outside the trained profiles. The controls and the students use different seeds. The controls 701 and 702 were trained earlier in the same way as 703. The pool for the new evaluation was not used for any selection.
