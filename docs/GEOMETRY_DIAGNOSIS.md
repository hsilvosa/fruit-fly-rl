# Diagnosis of the zero-success geometry experiment

The geometry experiment failed to learn target navigation. Passing implementation tests and finite optimizer losses did not make its outcome acceptable. This review separates verified failures from possible causes before another training budget is spent.

## What changed

The earlier observed-ray comparison selected a fresh controller that reached 48/64 goals in its own final dense-room pool. The geometry experiment also used fresh initialization, so initialization alone does not explain the difference. It did not continue that successful policy.

The earlier task used a 32 by 32 by 12 room with 48 obstacles and no compulsory partitions. The new target uses a 48 by 48 by 16 room, 112 obstacles and five partitions with alternating 3.2 by 3.2 openings. This changes navigation topology and route length as well as obstacle count. These results measure different tasks; they do not demonstrate that the saved earlier policy lost its original skill.

## Verified checks

On 2026-10-03, a bounded diagnostic used the existing full connectome and deterministic inference without training. It revisited four retained validation rooms from each relevant suite. It did not access either reserved final pool.

| Controller | Retained validation task | Layout seeds | Goals | Collisions | Timeouts |
| --- | --- | --- | ---: | ---: | ---: |
| Earlier ray-risk selected baseline | Original dense | 240000–240003 | 3/4 | 1 | 0 |
| Same unchanged controller, explicit transfer | New large | 290000–290003 | 0/4 | 2 | 2 |

The four original-room outcomes match the stored earlier validation outcomes. These small diagnostic samples are not new estimates of general success or a replacement final assessment.

The legacy dense world was also compared directly with its frozen ray-risk source across 16 layouts and 480 identical action transitions. Geometry, observations, rewards and termination flags matched exactly. The brain source is byte-identical. All eight geometry round reports contain finite losses and changed policy parameters. No general simulator or optimizer failure was found in these checks; they do not rule out every possible issue in the new task.

## Failures visible in the existing records

Every trained geometry checkpoint assessed during validation reached zero goals. Baseline seed 42 at 131,072 transitions collided in 31/32 layouts. Curriculum seed 42 at the same budget collided in 1/32 and timed out in 31/32, spending about 69.9% of decisions below speed 0.1. The trained controllers therefore failed through both collision and near-idle behavior.

The curriculum recorded 51 successful training episodes in `open`, but none in `passages` or `large`. It nevertheless advanced according to transition count. It contained no nearby-goal, single-wall intermediate task or training-practice mastery condition. This was an inadequate progression for the observed outcome.

Selection ranked success, fewer collisions and lower ending distance, and included initialization. With every candidate at zero success, an untrained controller could win by colliding less. The overall selected archive is byte-identical to seed 73 initialization, with zero training transitions. A roughly 1.4e-9 ending-distance difference assigned the curriculum label to equivalent initial weights; this has no practical meaning. The final zero is a real failed assessment, but is not an assessment of a successfully learned curriculum controller.

## Reward and temporal credit need diagnosis

The unchanged reward favors immediate Euclidean progress. With gamma 0.995 and 0.05-second decisions, an arrival bonus 60 seconds ahead is multiplied by about 0.00244; at 100 seconds it is multiplied by about 0.0000443. Bootstrapped value estimates can propagate future value, so this calculation alone does not prove learning cannot succeed. It does show that the objective retained its short temporal scale while the task became longer.

Eight retained geometry-validation layouts have a mean certified route length of about 116 units for `large`, versus 30 units for the original dense generator using the same seeds. Their mean large timeout allowance is about 170 simulated seconds. The certified route is a feasible geometric reference, not an optimal or dynamically verified trajectory. Sensor range remains eight units, and the output policy has no learned recurrent memory. Credit assignment, local sensing and passage discovery are plausible contributors; none has yet been isolated experimentally.

## Correction order

1. Keep the successful old checkpoint as a reference and verify original-room competence alongside every later intervention.
2. Diagnose crossing one wide opening with a nearby goal before introducing multiple alternating walls, greater size or narrower openings. Verify physical traversability through the actual flight controls.
3. Gate progression using a separate training-practice pool and retain easier tasks. Do not advance solely because a step budget elapsed; validation and final pools must not control progression.
4. Report `no successful candidate` when target validation is zero. Keep an initialization control for research, but do not present it as learned navigation or promote it as a working policy. Declare any selection changes before a new experiment.
5. Test reward or temporal-horizon changes separately once the basic passage task works. Comparing continuation of the successful controller with fresh initialization also requires a declared protocol.

No new training, checkpoint modification or final evaluation was performed in this diagnosis. A subsequent tuned experiment needs an agreed bounded budget and a new final pool. See [results](RESULTS.md) and [roadmap](../ROADMAP.md).

## Subsequent corrections

The [practice-mastery v2 implementation](GEOMETRY_CURRICULUM.md#corrected-practice-mastery-protocol) adds `gate-near` and `gate-long`, withholds 16 training layouts for two practice gates, preserves gate state across rounds and retains easier profiles. It excludes initialization from candidate selection and leaves the final pool unused when no trained target candidate succeeds. Existing checkpoints and recorded v1 outcomes are preserved.

All 16 physical oracle examples passed, and a separate full-connectome CUDA smoke completed exactly 128 transitions and one PPO update with finite losses and reload. Its practice inference failed both gates and correctly stayed at stage zero. This is a correctness check, not evidence of improved navigation. Reward and temporal-horizon interventions remain untested proposals.


## Resolución operativa posterior

El [informe del 5 de octubre](NAVIGATION_RESOLUTION.md) conserva esta distinción entre tareas y documenta las correcciones posteriores. El planificador v55 llegó a 8/8 en optimización y 13/16 en desarrollo prospectivo, sin colisiones. El mejor estudiante aprendido de la última tanda quedó en 3/8. La navegación por planificación ya tiene una demostración funcional; el aprendizaje fiable y el objetivo de test independiente siguen pendientes.
