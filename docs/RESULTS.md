# Results

Navigation performance is separate from implementation correctness and anatomical fidelity. The full fixed MaleCNS v1.0 graph was retained in these experiments; its synapses were not optimized. Outcomes do not establish a biological advantage.

## Latest original-large corrections

| Intervention | Added transitions | Development goals | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Current-feature matched control | 65,536 | 0/8 | 2 | 6 |
| Temporal-feature matched arm | 65,536 | 0/8 | 1 | 7 |
| Obstacle-aware reward pilot | 32,768 | 0/8 | 1 | 7 |
| Guided initialization and PPO | 40,960 | 0/8 | 8 | 0 |
| Visible fan and student-only correction | 65,536 | 0/8 | 4 | 4 |
| Separate critic history | 65,536 | 0/8 | 8 | 0 |
| Full-rollout PPO guard | 32,768 | 0/8 before and after | 8 | 0 |
| Spatial neural readout, post-run verification | 98,304 | 0/8 | 6 | 2 |

These reused development layouts do not constitute an independent final test. The guided teacher's eight optimization goals are not student navigation results. The initial 524,288 cap was exhausted. Subsequently authorized v2, v3 and v4 corrections bring completed substantive use to 688,128. The spatial-neural v5 worker consumed a further 98,304 transitions before a post-save precision assertion failed. Completed substantive training use is 786,432; its separately completed development verification added no training. No new model was promoted, the original six aliases retained their hashes, and no reserved final pool was consumed. [Guided results](evidence/guided-navigation-v1-results.md), [reward-only results](evidence/route-progress-correction-v1-results.md), and [memory results](evidence/brain-memory-comparison-v1-results.md) report the failures without claiming a successful fix.

The [sensors-v5 correction](evidence/visible-fan-v5.md) resolves a measured early-observation ambiguity and is verified through actual full-connectome activity. Its authorized training completed with 0/8 autonomous validation goals, four collisions and four timeouts. The observation correction did not establish successful navigation. [Verified v2 results](evidence/guided-navigation-v2-results.md) retain supervised and autonomous counts separately.

## Geometry comparison

The passage-mastery v2 comparison completed 524,288 added transitions. Validation selected baseline seed 42, round seven (114,688 lifetime transitions). On the single-opening gate-long final pool it reached 61/64 goals (95.3%), zero collisions and three timeouts; Wilson 95% interval 87.1-98.4%. The untrained control reached 0/64. This establishes performance on the simpler single-opening distribution, not the historical large rooms. Original launcher aliases were preserved. See [the verified completion record](evidence/passage-mastery-v2-results.md).

The geometry comparison completed 524,288 added transitions across four fresh runs. Validation selected curriculum, seed 73, with 0 lifetime transitions in the selected checkpoint (initial untrained controller). Its one final assessment on fixed `large` rooms reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0â€“5.7%. The 80% navigation target remains unmet. Original launcher aliases were preserved.

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

Only the validation-selected method/seed/checkpoint and an untrained control were final-tested on the 64 frozen target layouts. The selected checkpoint reached 0/64 (0.0%), with 1 collision and 63 timeouts; Wilson 95% interval 0.0â€“5.7%. The untrained control reached 0/64 (0.0%), with 1 collision and 63 timeouts; interval 0.0â€“5.7%. This pool is now consumed. There was no paired final comparison of both training methods.

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
| Dense adaptation | 43/64 (67.2%) | 15 | 6 | 55.0â€“77.4% |
| Warm-start sensor comparison | 50/64 (78.1%) | 5 | 9 | 66.6â€“86.5% |
| Fresh sensor comparison | 35/64 (54.7%) | 20 | 9 | 42.6â€“66.3% |
| Near-goal curriculum comparison | 45/64 (70.3%) | 15 | 4 | 58.2â€“80.1% |
| Observed-ray risk comparison | 48/64 (75.0%) | 16 | 0 | 63.2â€“84.0% |

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

The [geometry failure diagnosis](GEOMETRY_DIAGNOSIS.md) records a bounded check of retained validation rooms: the unchanged earlier controller reproduced 3/4 original-room goals but reached 0/4 on new large rooms. The legacy world matched its frozen implementation over 480 transitions. The review identifies progression without passage mastery and selection of initialization after all trained target candidates failed. It does not establish a single causal explanation or reuse the final pools.

The 80% target remains unmet. The corrected single-passage tasks and practice-mastery gates are implemented and verified, but improved navigation has not yet been measured. Revised temporal credit and learned output memory remain proposals in [the roadmap](../ROADMAP.md). Any later tuned final assessment requires a new independent pool and declared budget.

[Mathematics](MATHEMATICS.md) specifies formulas and optimizer settings. [Geometry protocol](GEOMETRY_CURRICULUM.md) defines maps, clearance certificates and reset mixtures. [Verification](VERIFICATION.md) describes implementation and publication checks without treating passing tests as learning evidence.


# Timeout correction pilot results

The 32,768-transition pilot completed on 2026-10-04T08:34:44.312907+00:00. It included exactly 16,384 transitions on the unchanged original large target. It retained live episodes across four chunks, used gamma=0.9995 in PPO and its rollout buffer, failure-terminal deadline handling and the sensors-v4 clock. The other 16,384 transitions came from the fixed stage-four curriculum mixture. All optimizer losses were finite.

| Development outcome | Before | After |
| --- | --- | --- |
| Goals | 0/4 | 0/4 |
| Collisions | 3/4 | 1/4 |
| Timeouts | 1/4 | 3/4 |
| Mean end distance | 36.82 | 32.54 |
| Mean idle fraction | 0.0267 | 0.0209 |

The same four optimization-layout seeds were measured before and after training. These are development diagnostics, not held-out validation or a final test. The before policy had already been transferred to sensors v4, so this is not a clean comparison with the old sensors-v3 controller. It cannot attribute changes to individual interventions or demonstrate generalization. Fewer collisions and smaller end distance did not produce any arrivals. The navigation issue is unresolved.

The target environments completed five training episodes: zero successes, two collisions and three timeouts. Only three target timeout penalties were observed within this budget. This is actual target exposure but little complete-episode learning experience. Adding exposure and fixing learning semantics alone did not resolve the repeated-turning failure in this pilot.

A subsequent full-graph counterfactual changed only the clock from zero to one in the four initial development worlds. Relative pooled-feature shift was 32.72 percent and mean absolute action change was 0.1395. The clock was added to an already-trained controller through a new projection; preserved archive bytes do not mean preserved flight behavior. This newly measured transfer disruption needs calibrated verification before another pilot. It does not explain the original sensors-v3 zero-success results, which preceded the clock.

The complete frozen source manifest matched after training. All six original alias files and the original source ZIP and metadata retained their initial hashes. No alias was promoted. Detailed before/after episodes, source hashes, losses and exposure counters are in private artifacts and runs/training/timeout-correction-pilot-v1/status.json. The original independent final test remains unused. No training process remains running.

Cumulative substantive added transitions are 319,488 of the earlier 524,288 budget, leaving 204,800. Separate smoke verification remains excluded. The last checkpoint is runs/training/timeout-correction-pilot-v1/round-4/policy.zip; it is not a successful navigation model.


[Verified critic-isolation v3 results](evidence/guided-navigation-v3-results.md) bring cumulative substantive use to 655,360. The subsequent guarded-PPO protocol has a 32,768-transition cap and no navigation result yet.


## Guarded PPO v4

The 32,768-transition correction completed with 0/8 original-large development successes both before and after training, eight collisions and no timeouts. The full-rollout KL guard retained seven updates within its limits; this did not solve navigation. Cumulative substantive transitions: 688,128. No reserved test or alias promotion. See [verified results](evidence/guarded-navigation-v4-results.md).


## Spatial neural v5

The full 98,304-transition training cap was consumed. Student-only optimization rounds reached no goals, with 143 then three collisions; teacher fragments reached 19 goals from privileged training starts. All supervised losses were finite. The worker failed a CPU/CUDA precision assertion after saving the final checkpoint. Saved tensors match exactly, and disabling convolution TF32 brings numerical predictions within the existing tolerance. Its separately completed development validation reached 0/8 goals, with six collisions and two timeouts, using frozen sources and unchanged weights. No final test or promotion. Completed substantive ledger: 786,432. [Evidence](evidence/spatial-neural-v5-results.md).


## Corrección panorámica y resultado de waypoint v6

La tanda waypoint v6 completó 81.920 transiciones nuevas, con pérdidas finitas y recarga compatible, pero su validación autónoma original large siguió en 0/8: ocho colisiones y ningún timeout. El total de entrenamiento sustantivo completado es 868.352 transiciones. Los aliases originales y el checkpoint fuente permanecen intactos. No se utilizó el test reservado y la navegación continúa sin resolverse.

Se conservan los [resultados verificados](evidence/neural-waypoint-v6-results.md) y el [diagnóstico de control y cobertura](evidence/neural-waypoint-v6-diagnostics.md). La siguiente corrección usa visión panorámica medida alrededor del cuerpo y vuelos guiados completos desde los estados originales. Su controlador recibe únicamente actividad neuronal; la ruta oculta solo etiqueta datos durante entrenamiento.
El [protocolo panorámico v7](evidence/panoramic-neural-v7-plan.md) fija un límite de 98.304 transiciones nuevas, 12.288 actualizaciones supervisadas y una única validación de desarrollo. Empieza un controlador nuevo por el cambio de dimensiones, conserva todos los checkpoints anteriores y no consume el test reservado.
