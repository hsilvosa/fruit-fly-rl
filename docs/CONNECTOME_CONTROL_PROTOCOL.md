# No-connectome control (C1): protocol, stage C1.0

Declared October 13, 2026, before training. C1 asks whether the connectome contributes to what the learned policy does. The release rules forbid claiming that the biological graph helps unless a matched control says so ([PROJECT_COMPLETION.md](PROJECT_COMPLETION.md)). This document fixes the whole control design and declares stage C1.0 (feasibility) in full. Later stages get their own protocol after C1.0 is read.

## What the control is

The connectome is a fixed reservoir: 167,184 neurons and 25,583,622 edges, no gradients, a fixed random input mapping from the sensors and a fixed pooling to 256 features, followed by a PPO MLP (128 x 128). The control keeps everything and changes who connects to whom.

- **Edge-shuffled reservoir** (`fly_rl/connectome/shuffled.py`, 3 tests): the target of every edge is reassigned by one global random permutation. Each source neuron keeps its out-degree and its weights (so Dale's law holds), each target keeps its in-degree, the weight distribution is unchanged. Duplicate (target, source) pairs created by the shuffle are summed: 25,583,622 edges become 25,496,103 (0.34 percent merged). Input mapping, pooling, leak and scale are the same. One shuffled graph (seed 1) is used for every control run. The graph is rebuilt in 4 s from the seed and never stored; its fingerprint is `shuffled-targets-seed1-ffe7773733e5096a-from-aff3a08b4b50`.
- Pre-training diagnostic (`scripts/check_shuffled_graph.py`, random sensor input, 100 steps, batch 8): features and states of the shuffled reservoir are not dead or saturated and are similar to the real ones (mean absolute feature 0.278 real, 0.280 shuffled; std across features 0.348 and 0.344; state saturation 0 in both). This also warns that statistics alone do not separate the two reservoirs under this input; whether the wiring matters for the policy is what C1 measures.

## Why a fresh chain for both arms

The retained start (experiment 7, 884,736 transitions) came from a historical chain that cannot be reproduced exactly. A control trained from scratch against the retained lineage would confound the connectome with that history. So both arms follow the same declared two-phase chain from random weights: phase 1 of 884,736 transitions on medium rooms (the size of the retained start), then phase 2 with the B2 recipe (2M, 61 stages). The retained B3 seeds stay as a third reference. Fresh policies are declared controls, not replacements of the retained lineage.

## Stage C1.0: feasibility of phase 1 (this protocol)

- Arms: `real` (full connectome) and `shuffled`, same seed (1001), same code (`scripts/train_fresh_chain.py`). Random initial weights. **Amendment, October 13 (before launch):** the user raised the resource ceiling to 95 percent of CPU and RAM, so the two trainings run in parallel (5 threads each) instead of one after the other. They are independent processes with their own seeds and data, so the science is unchanged. If the mean CPU over the first two minutes of overlap is above 93 percent, the shuffled training is stopped and run after the real one. The driver logs CPU and memory every 10 s and stops the trainings if memory exceeds 95 percent.
- Recipe: 32 simulators, all medium dense rooms (profile none, coordinated dynamics, sensor version of the retained start), 128 steps, clip 0.1, 3 epochs, minibatch 256, `target_kl` 0.02, gamma 0.995, learning rate 3e-4 falling linearly to 3e-5 over the phase. This is the B2 recipe with the mix replaced by medium rooms. It is untested from random weights, which is what the stage checks.
- Budget: 27 stages of 32,768 = 884,736 transitions. Checkpoints at every stage; curve at stages 9, 18 and 27 (294,912, 589,824 and 884,736).
- Evaluation: new pool 887000 to 887063 (64 episodes), medium rooms, both modes (decision mode deterministic), for both arms at the three points, and for the retained start checkpoint as reference. Driver `scripts/connectome_control_c10_driver.py`; shuffled checkpoints are evaluated through `scripts/eval_cell_brain.py`, which injects the shuffled brain without touching frozen sources.

### Gate (frozen)

On the final checkpoint (stage 27), deterministic, medium, pool 887000:

- **Chain valid**: the `real` arm reaches at least 40/64. The retained start scores 51 on pool 886000, the historical winners 45 to 50; 40 is a lower bar for a fresh policy and is an arbitrary cut point. Then C1.1 can compare matched arms.
- **Chain not valid**: the `real` arm is below 40/64. A fresh policy does not reach medium-room competence in this budget with this recipe, so a fresh shuffled arm would not be informative. The decision (longer phase 1 or a comparison against the retained lineage only, with that caveat written) goes to the user.
- The `shuffled` arm is reported in both cases. If `real` passes and `shuffled` is 10 or more episodes below it, that is already a first signal that wiring matters; if it is within 5, the reservoir wiring is not visibly needed for medium rooms. Neither reading is a claim, because one seed gives spreads of 10 episodes or more.

## Later stages (declared here, protocols to follow)

- **C1.1**: phase 2 (B2 recipe, 61 stages) for both arms, two seeds each (1001 and 1051), evaluated on the cells of the retained policy: `passages`, `passages-mid`, medium, level B development maps and level C development headings, both modes, with the retained B3 seeds as reference. Estimated 4 x 81 min of training plus about 1 h 30 of evaluation. Own protocol with decision rules before launching.
- **C1.P, planner reference**: the planner supports only the `large` and `maze` profiles and the architectural scenes, with a different sensor interface (nine-frame panorama). It cannot run on medium, `passages` or level B. Planned: level C (168 episodes, about 55 min from the recorded 409 s for 21 episodes), then `large` and `maze` after an 8-episode cost probe. Own protocol.

## Limits

- One shuffled graph realization and, in C1.0, one training seed per arm. A single shuffled reservoir does not represent all random graphs.
- The fresh chain matches the total number of transitions of the retained lineage (2.88M) and not its curriculum or history.
- A negative control result (no difference) forbids the claim that the connectome improves navigation, and does not show that it does not.
- Level C remains inspected and not independent of future decisions; no sealed pool is used in C1.0.

## Estimate

Serial training 2 x 27 stages at about 82 s (B2: 79 s; smoke runs this session: 81 s shuffled, 90 s real with startup) is about 74 min. Evaluation 14 medium cells at about 1 min each under the guard raised to 95 percent (up to 6 processes, 2 threads each), about 8 min. Training in parallel about 45 to 50 min if both arms fit under the ceiling (the 74 min serial figure is the fallback). Total about 1 h to 1 h 30. CPU about 55 percent in training, 50 to 80 percent in evaluation, GPU 30 to 60 percent, one process during training.
