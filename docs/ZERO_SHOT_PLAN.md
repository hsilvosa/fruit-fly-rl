# Plan to unseen-map navigation

Written October 8, 2026. This document holds the phase design. The live status is in [ROADMAP.md](../ROADMAP.md). It replaces the open decision in [TRANSFER_SUMMARY.md](TRANSFER_SUMMARY.md) and does not authorize a run. Each phase starts only when the user says so, with its protocol committed before training.

## Final objective

A learned virtual fly that reaches goals in maps it has never trained on. Flight actions come from the learned policy. The full MaleCNS v1.0 connectome (167,184 neurons, 25,583,622 edges) stays in the controller. An explicit planner may serve as a reference or an optional teacher. It never chooses the evaluated policy's actions.

"Unseen map" has three levels. Each is reported separately.

| Level | Meaning | Claim it supports |
| --- | --- | --- |
| A. New layouts | New random seeds from a family used in training | Generalizes across layouts of a known family |
| B. Held-out parameters | A parameter range the generator never produced during training (for example narrower openings, more partitions) | Generalizes beyond the trained difficulty range |
| C. Held-out family | A map family that never entered training (for example the synthetic architectural scenes, or mazes with dead-end branches) | Generalizes to a new kind of map |

Real buildings and streets are out of scope until after the first release. Level C is the strongest claim this project can test.

## Where the project stands

- The historical medium-room winners are recovered and replay exactly ([HISTORICAL_REFERENCE.md](HISTORICAL_REFERENCE.md)).
- Eight bounded transfer experiments gave a partitioned-map signal on trained profiles, and then plain PPO lost it ([TRANSFER_SUMMARY.md](TRANSFER_SUMMARY.md)).
- No result supports level A, B or C yet. The best development numbers are on profiles that were in the training mix.

## Phases

### Phase 1. Stable trainer

Why: performance moved by 20 episodes or more between checkpoints 65,536 transitions apart. Nothing larger can hold until this is fixed.

Changes, all opt-in so earlier experiments stay reproducible:

- 32 parallel simulators per update instead of 8, to reduce gradient variance.
- The existing `GuardedPPO` KL guard, a smaller clip range and fewer epochs per update.
- A learning rate that decays over a run, with no optimizer restart between stages.
- Separate pools: a training pool, a selection pool for choosing checkpoints, and a report pool that selection never sees.
- Evaluation repeatability check (the same checkpoint scored 15, 16 on one pool).

Exit criterion: from the experiment 7 checkpoint, two seeds keep passages-wide within 5 episodes of each other across four evaluations, and medium rooms stay at 21/32 or more. Experiment 8 is the control.

### Phase 2. Randomized map distribution

Why: training on a few fixed profiles teaches those profiles. Unseen-map performance needs a broad distribution.

- A map sampler that draws every episode from parameter ranges: room size, obstacle count, partition count, opening width and height, dead-end branches.
- Adaptive difficulty: ranges widen when the recent success rate is above a threshold and narrow when it falls.
- Pool structure fixed before training: training ranges, a held-out parameter region (level B), and at least one held-out family (level C). Held-out content is never used for selection.
- Keep medium rooms and single gates in every mix to catch forgetting.

Exit criterion: on level A development pools the policy reaches the development gate below, with the Phase 1 stability criterion holding.

### Phase 3. Memory

Why: a detour needs memory of where the policy already looked. The current policy sees one reservoir state and little history.

- Test the existing history frames and the temporal residual transfer. A recurrent policy is an alternative.
- One change per experiment, with the same pools, and a no-memory control.

Exit criterion: memory improves a level B or level C development cell by at least 6 episodes of 32 over the no-memory control, on two seeds. If it does not, record that and keep the simpler policy.

### Phase 4. Scale to the target families

- Add large rooms, mazes and the synthetic architectural scenes to the sampler, keeping at least one family held out.
- Decide whether the 128-ray, 8-unit-range sensors are enough or whether the 24-unit panorama (sensor v6) is needed. Sensor v6 needs a versioned transfer and cannot reuse v2 or v3 weights.
- Optional: planner imitation for hard exploration, with separate teacher and imitation budgets and planner-free evaluation.

Exit criterion: development gate on every family in training, and recorded results on the held-out family.

### Phase 5. Freeze and independent assessment

- Inventory every previously inspected pool. None can return as a test.
- Reserve new layout seeds, held-out parameters and the held-out family before choosing a candidate.
- Freeze the checkpoint, sources, protocol and budget. Run once. Do not tune afterward.
- Release gate (proposed): at least 52 of 64 successes and at most 3 collisions in each of four families (medium, large, maze, architectural), reported with Wilson 95% intervals, per-scene results, path length and flight time. Timeouts count as failures.
- Matched controls: a learned policy without connectome activity and the frozen planner. No claim of biological benefit without evidence.
- At least two training seeds for the final comparison.

### Phase 6. Release

Installation in the project Conda environment, checkpoint and data distribution, learned demos, logs and replay, brain visualization, formulas, attribution, repository audit, numbered release. Opening the viewer never trains.

## Development gate (proposed, to confirm at Phase 2)

For Phases 2 to 4: at least 26/32 successes and at most 3 collisions on each development cell, on two seeds, with medium rooms at 21/32 or more. This allows moving to the next phase. It is not a generalization claim.

## Rules for every experiment

- Commit the protocol (design, pools, acceptance rule, positive result) before training.
- Change one factor per experiment, or run a declared control arm.
- Choose checkpoints on a pool the report never uses.
- Never overwrite aliases, completed runs or controller sources. Record source and checkpoint hashes.
- Report failures and negative results with the same detail as positive ones.
- Keep the first user-visible output a table with counts and denominators, not only percentages.

## Checklist and status

The checklist, the current status and the actions ready to start live in [ROADMAP.md](../ROADMAP.md), so that there is one status board. This document keeps the phase design, the rules and the definitions.
