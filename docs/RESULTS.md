# Results

Navigation performance is separate from implementation correctness and anatomical fidelity. The full fixed MaleCNS v1.0 graph was retained in these experiments; its synapses were not optimized. Outcomes do not establish a biological advantage.

## Geometry comparison

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

### Shared target validation

All four runs use the same 32 fixed `large` validation layouts. The experiment budget counts all training transitions, whereas selected lifetime transitions describe only the checkpoint retained by validation.

| Method | Seed | Added transitions | Selected lifetime transitions | Goals / 32 | Collisions | Timeouts |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 42 | 131,072 | 0 | 0 | 1 | 31 |
| baseline | 73 | 131,072 | 0 | 0 | 0 | 32 |
| curriculum | 42 | 131,072 | 131,072 | 0 | 1 | 31 |
| curriculum | 73 | 131,072 | 0 | 0 | 0 | 32 |

All selected validation candidates have zero goals. Selection includes the initial controller, so a zero-transition checkpoint may rank ahead of trained policies that collide more often. This is failure to demonstrate learned navigation in the target rooms, rather than a successful trained policy. Training success in easier profiles does not establish validation generalization. The selected ZIP is byte-identical to its frozen initialization. The method ranking used ending distances 44.2234894709623 (baseline) and 44.2234894695337 (curriculum), with equal success and collision rates. Such a numerical difference is not evidence of a curriculum effect. The declared rule was applied without changing it after observing results.

### One reserved final assessment

Only the validation-selected method/seed/checkpoint and an untrained control were final-tested on the 64 frozen target layouts. The selected checkpoint reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0–5.7%. The untrained control reached 0/64 (0.0%), with 1 collision and 63 timeouts; interval 0.0–5.7%. This pool is now consumed. There was no paired final comparison of both training methods.

The complete comparison, including initialization, training, validation and final assessment, took 206.7 minutes. It is not a pure training throughput measurement. The source revision was `ec7e90193ee60d9b413f05e42058c264306f4ddb`. Both initialization seeds began with zero transitions and empty optimizer state, all eight round loss reports were finite, and the frozen source/configuration/suite hashes passed the completion audit.

### Curriculum exposure and training outcomes

The schedule uses reset mixtures 75/20/5%, 20/60/20% and 10/20/70% for `open`/`passages`/`large`, according to global transition progress. It changes profiles only on episode reset. These are reset probabilities, not guaranteed transition fractions. Counters below describe sampled training episodes; an episode crossing a round boundary can remain incomplete and is not counted as a terminal outcome.

| Seed | Round | Profile | Transitions | Training goals | Collisions | Timeouts |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 42 | 1 | open | 51,217 | 20 | 39 | 17 |
| 42 | 1 | passages | 9,895 | 0 | 41 | 0 |
| 42 | 1 | large | 4,424 | 0 | 13 | 0 |
| 42 | 2 | open | 8,168 | 10 | 2 | 1 |
| 42 | 2 | passages | 16,698 | 0 | 15 | 4 |
| 42 | 2 | large | 40,670 | 0 | 16 | 3 |
| 73 | 1 | open | 47,970 | 17 | 48 | 13 |
| 73 | 1 | passages | 13,620 | 0 | 43 | 0 |
| 73 | 1 | large | 3,946 | 0 | 4 | 0 |
| 73 | 2 | open | 9,553 | 4 | 1 | 4 |
| 73 | 2 | passages | 21,315 | 0 | 21 | 6 |
| 73 | 2 | large | 34,668 | 0 | 38 | 1 |

Full reset counts, stage offsets, original alias hashes and aggregate measurements are preserved in [machine-readable geometry evidence](evidence/geometry-v1-results.json). Detailed source copies, launch records, TensorBoard logs, checkpoints and original evidence remain local and ignored. No launcher alias was promoted.

## Earlier dense-room results

Each row summarizes an already completed, validation-selected final assessment on its own fresh pool. All these pools are consumed. Rooms, initialization and lifetime training differ across experiments; this table is historical context, not a paired ranking of interventions. The profiled geometry comparison is a harder task and is not directly comparable with these dense-room counts.

| Experiment | Final goals | Collisions | Timeouts | Wilson 95% interval |
| --- | --- | ---: | ---: | --- |
| Dense adaptation | 43/64 (67.2%) | 15 | 6 | 55.0–77.4% |
| Warm-start sensor comparison | 50/64 (78.1%) | 5 | 9 | 66.6–86.5% |
| Fresh sensor comparison | 35/64 (54.7%) | 20 | 9 | 42.6–66.3% |
| Near-goal curriculum comparison | 45/64 (70.3%) | 15 | 4 | 58.2–80.1% |
| Observed-ray risk comparison | 48/64 (75.0%) | 16 | 0 | 63.2–84.0% |

The original coordinated dense launcher separately reached 43/64 goals, with 11 collisions and 10 timeouts. Its weights and metadata remain preserved. Later selections were saved separately. The near-goal curriculum and tested risk penalty did not beat their respective normal-training controls under their declared validation rankings; only each winner was final-tested.

## Historical validation selections

Each table uses one shared validation pool within that experiment. Pools differ across experiments. These are selected checkpoint outcomes, not separate final tests. Two initialization seeds do not establish broad seed robustness.

### Warm-start sensor comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| v2 | 42 | 23/32 |
| v2 | 73 | 21/32 |
| v3 | 42 | 19/32 |
| v3 | 73 | 21/32 |
### Fresh sensor comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| v2 | 42 | 17/32 |
| v2 | 73 | 21/32 |
| v3 | 42 | 24/32 |
| v3 | 73 | 21/32 |
### Near-goal curriculum comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| baseline | 42 | 27/32 |
| baseline | 73 | 26/32 |
| curriculum | 42 | 23/32 |
| curriculum | 73 | 26/32 |
### Observed-ray risk comparison

| Method or interface | Seed | Selected validation goals |
| --- | --- | ---: |
| baseline | 42 | 27/32 |
| baseline | 73 | 22/32 |
| risk | 42 | 26/32 |
| risk | 73 | 22/32 |

Warm-start sensor validation selected v2 seed 42, the fresh sensor comparison selected v3 seed 42, and both near-goal and risk comparisons selected baseline seed 42. The chosen final results appear above; alternate methods were not final-tested as a paired comparison.

## Interpretation and next work

The 80% target remains unmet. Use retained validation trajectories to diagnose passage collisions, idle behavior and failed detours before another intervention. Intermediate passage tasks, revised temporal credit or learned output memory are proposals in [the roadmap](../ROADMAP.md), not measured improvements. Any later tuned final assessment requires a new independent pool and declared budget.

[Mathematics](MATHEMATICS.md) specifies formulas and optimizer settings. [Geometry protocol](GEOMETRY_CURRICULUM.md) defines maps, clearance certificates and reset mixtures. [Verification](VERIFICATION.md) describes implementation and publication checks without treating passing tests as learning evidence.
