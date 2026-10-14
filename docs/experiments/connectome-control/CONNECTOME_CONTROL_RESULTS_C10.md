# No-connectome control, stage C1.0: results

Protocol: [CONNECTOME_CONTROL_PROTOCOL.md](CONNECTOME_CONTROL_PROTOCOL.md), committed before training (`3b57215`, amended in `2b8f50f` to run the two arms in parallel). Phase 1 of the fresh chain: random initial weights, 884,736 transitions, 32 simulators of medium dense rooms, seed 1001, real connectome against the edge-shuffled reservoir (shuffle seed 1). Evaluation on pool 887000 to 887063, 64 episodes per cell.

## Outcome by the frozen gate

**Chain valid.** The `real` arm reaches 61/64 deterministic on medium (gate: at least 40). A fresh policy trained for the same number of transitions as the retained start reaches medium-room competence with this recipe. C1.1 can compare matched arms.

## Results (medium rooms, successes / collisions / timeouts, out of 64)

| Checkpoint | Transitions | Deterministic | Sampled |
| --- | --- | --- | --- |
| Retained start (experiment 7), reference | 884,736 (different chain) | 55 / 5 / 4 | 59 / 4 / 1 |
| Real connectome, fresh | 294,912 | 52 / 7 / 5 | 50 / 13 / 1 |
| Real connectome, fresh | 589,824 | 57 / 5 / 2 | 62 / 2 / 0 |
| Real connectome, fresh | 884,736 | **61 / 2 / 1** | 59 / 5 / 0 |
| Edge-shuffled, fresh | 294,912 | 52 / 4 / 8 | 56 / 6 / 2 |
| Edge-shuffled, fresh | 589,824 | 54 / 5 / 5 | 57 / 7 / 0 |
| Edge-shuffled, fresh | 884,736 | **54 / 6 / 4** | 60 / 3 / 1 |

## What the numbers show

- Competence in medium rooms does not need the retained history. A random-weight policy with this recipe reaches 52 of 64 by 295k transitions and 61 by 885k with the real connectome, which is above the retained start on this pool (55). The historical winners scored 45 to 50 of 64 on other pools, so the pools are not directly comparable.
- The edge-shuffled reservoir learns medium rooms too. After 885k it scores 54 deterministic and 60 sampled, against 61 and 59 for the real connectome. The final deterministic gap is 7 episodes, which falls between the protocol's two readings (10 or more would be a first signal that wiring matters, 5 or less that it is not visibly needed). The sampled results are 60 and 59, with the shuffled arm higher.
- With one seed per arm and a pool of 64 episodes, a gap of 7 does not separate the arms: the variance study found spreads of 10 episodes and more between seeds on one profile (on harder cells), and no medium-room spread was measured for this recipe from random weights. The curves cross (real 52, 57, 61; shuffled 52, 54, 54; sampled 50, 62, 59 against 56, 57, 60).
- Medium rooms are the easy cell. They say that the control is a competent learner and that the pipeline is not broken for the shuffled brain. Whether the connectome wiring matters shows up, if at all, in the harder cells of C1.1 (`passages`, `passages-mid`, level B and level C).
- The retained start is not worse than the fresh arms because of its history: it is within the range of both fresh arms (55 against 54 and 61).

## Resources

Both trainings ran in parallel at the raised ceiling. Resource log: CPU mean 66 percent, peak 90 percent, memory peak 66 percent, no process was killed. Each arm took 37.0 min (real, 27 stages, 2,222 s) and 37.6 min (shuffled, 2,258 s) of stage time, 82 to 84 s per stage, against 82 s when alone, so parallel running cost almost nothing per arm.

## Limits

- One seed per arm, one shuffled graph, medium rooms only. No conclusion about the connectome follows from this stage.
- The retained start is a reference on the same pool and was trained by a different chain.
- Pool 887000 is inspected now and selects nothing.

## Artifacts

Runs: `runs/training/connectome-control/phase1-real1001` and `phase1-shuffled1001` (stages 1 to 27 each, `experiment.json`), cells in `c10-eval/` with `summary.json`, resource log `c10-resources.log`. Evidence copy in `private/connectome-control-c10-evidence/`. Fingerprint of the shuffled brain: `shuffled-targets-seed1-ffe7773733e5096a-from-aff3a08b4b50`.

Timing from the clock: launch about 16:14, both trainings finished by 16:52:06 (about 38 min), evaluation finished at 17:04:26 (12 min 20 s for 14 cells with up to 6 processes). Estimates were 45 to 50 min and 8 min.
