# Resolving navigation in large maps

This history retains original experiment IDs and measured source snapshots. Current public names are listed in [Controller versions](CONTROLLER_VERSIONS.md): planner-1.0 is historical v55, planner-1.1 is v60, and planner-1.2 is v65. The naming migration does not change their recorded results. [Latest paired experiments](RESULTS.md#latest-planner-experiments).

Date: October 5, 2026. Operational version: `observed-neuronal-map-v55`, integrated in commit `972ceb4`.

This document reconstructs the problem, the hypotheses tested, the failed attempts, and the available solution. The working result is an explicit planner that consumes activity from the full connectome. The learned policy still does not reproduce that performance. The [v55 report](evidence/observed-map-v55-results.md) contains the figures, prospective protocol, and preservation hashes; the [attempt protocol](evidence/portal-feedback-protocol.md) records the experimental development.

Sections 1 through 6 explain the problem and its resolution. Sections 7 through 20 detail the background, experiments, data, contracts, formulas, results for each room, resources, and reproduction. The figures describe the verified state on October 5, 2026; hypotheses and contributions that were not isolated are identified explicitly.

## Contents

- [1. The problem](#1-the-problem)
- [2. Investigation](#2-investigation)
- [3. Attempted solutions and results](#3-attempted-solutions-and-results)
- [4. The final operational solution](#4-the-final-operational-solution)
- [5. Verification](#5-verification)
- [6. Running it and remaining work](#6-running-it-and-remaining-work)
- [7. Background and development of the problem](#7-background-and-development-of-the-problem)
- [8. Record of all resumed pilots](#8-record-of-all-resumed-pilots)
- [9. Data, connectome, and exact transformations](#9-data-connectome-and-exact-transformations)
- [10. Sensor contract, memory, and input separation](#10-sensor-contract-memory-and-input-separation)
- [11. Odometry and knowledge of the goal](#11-odometry-and-knowledge-of-the-goal)
- [12. Exact map construction](#12-exact-map-construction)
- [13. Route search and following](#13-route-search-and-following)
- [14. Three-dimensional braking, flight, and reward](#14-three-dimensional-braking-flight-and-reward)
- [15. Results for each room and timeout diagnosis](#15-results-for-each-room-and-timeout-diagnosis)
- [16. Resources, timing, and GPU use](#16-resources-timing-and-gpu-use)
- [17. What the tests and checks established](#17-what-the-tests-and-checks-established)
- [18. Recording, reproduction, and preservation](#18-recording-reproduction-and-preservation)
- [19. Data separation and scientific limits](#19-data-separation-and-scientific-limits)
- [20. Completed criteria and remaining work](#20-completed-criteria-and-remaining-work)

## 1. The problem

The fly needed to navigate a three-dimensional room, pass through gaps between obstacles, and reach the goal. In the `large` profile, the room measures 48 x 48 x 16 units and contains 112 collision boxes, including five partitions with alternating openings. Coordinated flight dynamics remain in use, with decisions every 0.05 seconds. Reaching the goal requires being within 0.45 units without a collision; running out of time is a failure.

Controllers could collide, approach a wall without crossing its opening, or become almost motionless. Finite losses, compatible checkpoints, and implementation tests did not establish that they could complete the route.

The earlier 75% represented 48/64 arrivals in a different task: a 32 x 32 x 12 room with 48 obstacles and none of the mandatory partitions in `large`. The new comparison started from fresh initialization rather than continuing that successful policy. Checking the earlier checkpoint in four original rooms reproduced 3/4 arrivals, whereas transfer to four large rooms yielded 0/4. The records therefore do not establish a loss of the earlier behavior on the same task. They do establish that navigation in the new problem failed. See the [initial diagnosis](GEOMETRY_DIAGNOSIS.md).

## 2. Investigation

Neural readout, reference estimation, route search, and physical control were separated. This made it possible to check whether a good prediction became useful motion and whether an available route ended in an actual arrival.

Earlier checkpoints were preserved. Each batch recorded its sources, budget, physical transitions, updates, and results for each episode. Teacher flights, student flights, and geometric checks were counted separately. Layouts repeatedly used to tune variants are optimization maps, not an independent test.

The first two map variants, v41 and v42, performed a second generator reset. Although they retained seed labels, their layouts differed from the earlier canonical layouts. The explicit reset was corrected in v43, and initial geometry was saved to audit that identity. The affected batches are not compared by seed.

## 3. Attempted solutions and results

### Learning, coverage, and perception

Early changes tested curriculum, rewards, guided supervision, temporal memory, critic isolation, and controls on PPO updates. Vision was also expanded to a panorama around the body, and complete guided flights were collected. Several guides reached the goal, but their students continued to fail in `large`. The teacher's privileged references serve only as training supervision; teacher arrivals are not autonomous model results.

The v13–v19 portal-perception batch tested new heading distributions, projection readout, local attention, context, and braking. Its seven candidates finished at 0/8 on optimization maps. Greater coverage or fewer collisions was insufficient to cross the walls.

V32 added global context. Its angular fit on training data looked good, but flight remained at 0/8. V34 learned a wall normal and separated approach from crossing: first align the fly in front of the opening, then aim beyond it. It reached 3/8, with one collision and four timeouts. This is the best learned student in this batch.

Later attempts isolated distance, collected student states with teacher recovery, changed lateral protection, and aligned panoramas during turns. They did not improve on v34. In particular, a different readout or temporal alignment cannot be presented as a sufficient cause of the final success.

Geometry-derived center references were also found not to guarantee visibility. A center could be hidden in the image used to label it. The retained audit uses the nearest panoramic ray and is an angular approximation, not an exact visibility test. This limitation helps interpret perception failures; it does not establish their complete cause by itself.

### Neural readout and the observed map

A motion reconstruction with a small bias could accumulate drift when integrating position and turning. A reader with its own contract and fingerprint was introduced: it cancels the projected recurrent contribution in the 269 base channels and retains 5% in the 3,600 panoramic channels. It reconstructs those channels from previous and current neural states and the fixed projection; it does not add raw sensors to the controller.

The full graph continues to advance, with 167,184 neurons and 25,583,622 directed connections. This transformation is an engineering choice, not an established biological mechanism. A short diagnostic measured turning error of approximately 0.00000472 rad/s. The formula and its check are in [mathematics](MATHEMATICS.md).

Explicit planning from an observed map separated a poor learned reference from a mechanical route failure. V43 and v44 reached 5/8 without collisions. V44 used the stable reader and achieved the same arrival count as v43; stabilizing the readout did not resolve every blockage.

### Specific blockages and corrections

| Verified problem | Correction | What it showed |
| --- | --- | --- |
| The map's safety margin left a single accessible cell near the start | Allow escape through local margin cells at high cost, while keeping observed surfaces impassable | A conservative margin can enclose a physically free position |
| Smoothing a route through a margin allowed a corner to be cut | Reduce lookahead and speed in narrow areas and check the segment | Relaxing the entire margin caused a collision and was insufficient |
| A predicted reference fell outside the grid | Validate its bounds before converting it to indices | V49 failed with an index error; fixing it prevented that failure, but v50 reached only 1/8 |
| A group of boxes could resemble a complete wall to geometric fitting | Require surface coverage before accepting a wall | Synthetic geometry improved, but v51–v53 remained at 0/8 |
| Search accepted an endpoint up to 0.96 units before its reference | Search for the exact final cell and append the continuous goal | A search marked complete did not guarantee that the fly crossed the reference |
| Route following could retain an already reached cell | Advance to the next reference when the current one is sufficiently close | Avoids requesting zero speed while a route remains |
| Braking checked the front even when the next movement was vertical | Measure clearance around the requested three-dimensional direction | A frontal wall no longer blocked a clear ascent or descent |
| Horizontal turning also reduced vertical movement | Apply heading reduction only to horizontal speed | The fly can adjust altitude while turning |

Not every correction belongs to the final algorithm. Wall fitting, stored openings, and learned proposals were tested, but v55 retains only the observed map and neural goal. This simplification avoided dependence on potentially incorrect opening references.

| Representative variant | Optimization arrivals | Collisions | Timeouts |
| --- | ---: | ---: | ---: |
| v13–v19, seven perception candidates | 0/8 each | See protocol | See protocol |
| v31, local geometry with reduced recurrence | 4/8 | 0 | 4 |
| v34, best learned student | 3/8 | 1 | 4 |
| v43 and v44, observed map | 5/8 each | 0 | 3 |
| v48, more conservative protection | 1/8 | 0 | 7 |
| v51–v53, observed wall and opening | 0/8 each | 0 | 8 |
| v54, global map without a learned proposal | 3/8 | 0 | 5 |
| v55, corrected route following and three-dimensional control | 8/8 | 0 | 0 |

These figures show the development of optimization. They are not an independent final comparison and do not establish which isolated contribution explains each arrival. The change from v54 to v55 combined route-following and control corrections; no independent ablation of each was performed.

## 4. The final operational solution

V55 reconstructs distances, the goal, velocity, and turning from neural activity. These allow it to estimate relative position and build an occupancy grid with 0.6-unit cells. A weighted search selects a route through observed or still unknown space. Route following selects a nearby reference, and acceleration, altitude, and turning controls execute the movement. Subsequent observations update the map and correct the trajectory.

Search is limited to 12,000 expansions. If it does not reach the final cell, it selects an open frontier to continue exploring. Its weighted cost and limit do not guarantee the shortest route. Rays and the grid likewise do not guarantee absolute safety.

The controller does not receive the world object, true poses, boxes, seeds, or certified routes. It does know the contracted room size and receives a synthetic goal as an observation. Saving true geometry to audit a flight does not mean supplying it to the controller. It would therefore be incorrect to describe this as a biological fly that independently discovers which goal to seek.

The planner works without learned movement weights. Earlier phases did involve training: the resumed batch added 131,072 physical transitions, bringing cumulative substantive use to 1,603,584. V55 checks added zero training transitions and zero updates. Fits on existing records, temporary PPO verification, and verification flights remain separate.

## 5. Verification

V55 was frozen after completing eight optimization maps and before opening 16 new development rooms. It was not adjusted between these flights.

| Check | Physical transitions | Arrivals | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Eight reused optimization maps | 25,168 | 8/8 | 0 | 0 |
| Sixteen new development rooms | 56,544 | 13/16 | 0 | 3 |

The prospective result is 81.25%, with a 95% Wilson interval of 57.0% to 93.4%. The three rooms that timed out are 8500011, 8500012, and 8500013. The sample is small and belongs to the same generator; it does not establish robustness in arbitrary maps. The reserved test was not consumed. If these three failures are now used to tune a new version, subsequent results on them would no longer be a prospective check of that new version.

The public version reproduced the prototype's actions and map over 60 synthetic steps. This is an implementation-equivalence check without physical transitions. The complete suite passed 265 tests. In the viewer, the fly completed known map 370000 in 2,857 decisions: 142.85 simulated seconds without a collision. The session closed after 3,200 decisions and verified automatic reset with fresh memory. That repetition is not added to the prospective arrivals.

Room and brain screenshots were inspected. Neural inspection with history required a gradient correction, and screenshot saving was corrected to avoid an empty brain capture. The anatomical map displays actual modeled activity; gradient sensitivity is marked unavailable for the planner. Flight archives closed and passed their audit without errors or warnings.

Protected checkpoint and alias hashes match before and after. Original models were not overwritten, and planner arrivals were not attributed to the student.

## 6. Running it and remaining work

From the project folder:

```powershell
.\launch-observed-map.cmd
```

The launcher opens the room and a separate brain window. Shift accelerates simulated time tenfold; R resets, N changes rooms, C changes the camera, and F focuses on the fly. Sessions archive states, actions, metadata, and controller code. The demo does not start training.

The available solution completes many large routes through explicit planning. Three timeouts remain in the prospective sample, along with autonomous student learning and broader independent evaluation. Before increasing difficulty to `maze`, the new size, sensor contracts, and navigation must be checked. A reliable learned policy remains an open objective; planner performance must not mark it complete.

Next steps are to diagnose detours that exhaust the time limit, measure a corrected version on new maps, and then investigate whether the student can learn from planner trajectories. That stage must declare its budget and again separate teacher and student performance.


## 7. Background and development of the problem

### 7.1. Changes to the task, selection, and reward

The `large` partitions require temporarily moving away from the goal, finding an opening, adjusting altitude, and discovering the next passage. Reducing Euclidean distance can lead into a wall. The initial diagnosis measured mean certified routes of approximately 116 units in eight retained large layouts versus 30 in the earlier generator with the same seeds. These routes are feasible geometric references, not optimal or dynamically verified flights. The episode limit was around 170 simulated seconds in that sample.

The earlier curriculum recorded 51 successful episodes in `open`, none in `passages` or `large`, and advanced through step consumption. Selection could retain initialization when every candidate had zero success. A winning-method label therefore did not establish that a trained policy had learned. That interpretation was corrected, and the original failure results were retained.

With gamma 0.995 and decisions every 0.05 seconds, a reward 60 seconds away is multiplied by approximately 0.00244; at 100 seconds, by 0.0000443. The critic can propagate value through bootstrapping; this calculation does not establish that learning is impossible. It justified investigating horizon and exploration, but did not identify a single cause.

### 7.2. Corrections before the portal experiments

| Attempt | New physical training | Autonomous development result | Evidence |
| --- | ---: | --- | --- |
| Guided initialization v1 | 40,960 | 0/8, eight collisions | [Report](evidence/guided-navigation-v1-results.md): eight teacher goals did not transfer to the student |
| Guided v2 | 65,536 | 0/8, four collisions and four timeouts | [Report](evidence/guided-navigation-v2-results.md): student states differed from teacher states, and KL exceeded the target |
| Critic isolation v3 | 65,536 | 0/8, eight collisions | [Report](evidence/guided-navigation-v3-results.md): separate memories did not prevent excessive changes |
| PPO protection v4 | 32,768 | 0/8 before and after, eight collisions | [Report](evidence/guarded-navigation-v4-results.md): seven accepted updates, nine rejected attempts |
| Spatial readout v5 | 98,304 | 0/8, six collisions and two timeouts | [Report](evidence/spatial-neural-v5-results.md): CPU/CUDA comparison failed after checkpoint saving |
| Neural references v6 | 81,920 | 0/8, eight collisions | [Report](evidence/neural-waypoint-v6-results.md): 16,384 guided steps and 65,536 autonomous steps |
| Body panorama v7 | 98,304 | Separate recovery: 0/8, eight collisions | [Report](evidence/panoramic-neural-v7-results.md): 16 teacher goals; later reporting failure |
| Coverage v8 | 301,056 | 0/8, eight collisions | [Report](evidence/panorama-coverage-v8-results.md): 64 teacher goals, none from the student |
| Directional attention v9 | 32,768 | 0/8, eight collisions | [Report](evidence/directional-and-lookahead-results.md): progress ending in a crash was not success |
| Lookahead v10 | 163,840 | Final: 0/8, zero collisions and eight timeouts | [Report](evidence/directional-and-lookahead-results.md): 35 guided goals; teacher-only and sparse-pooling controls also failed |

Phases, contracts, and datasets differ: this table is neither a causal comparison nor a single curve. Losses on different datasets do not form a navigation-performance curve.

V12 excluded approach-velocity planes from perception to test a possible visual shortcut. It added 8,192 transitions and yielded 0/8, with one collision and seven timeouts. The shortcut remained a hypothesis. October 4 closed with 1,472,512 cumulative substantive transitions and large-map navigation still unresolved.

### 7.3. Losses, KL, and verification errors

A finite loss means that operation produced neither NaN nor infinity. Low imitation loss measures fit on specific samples. Compatible reload checks weights and the contract. None replaces a complete episode from the original start.

In v3, final approximate KL was 0.342514 against a 0.01 target; an earlier entry reached 3.486418. PPO early stopping does not necessarily undo an update already applied. V4 added acceptance and rollback based on rollout KL, but was already failing before PPO; containing changes did not repair its initial behavior.

In v5, CPU/CUDA tensors matched, but CUDA convolutions with TF32 produced action differences above tolerance. Disabling it reduced the discrepancy. The original failure status was retained, and subsequent verification was recorded separately: repairing a numerical comparison did not turn its 0/8 into success.

## 8. Record of all resumed pilots

### 8.1. Counters and original statuses

The table derives from existing records; no training or evaluation was run to document it. Fitting earlier records adds no physical transitions. Verification counts the full batch, including members that had finished and continued with zero actions.

V32 retains its reporting failure after training; subsequent verification added zero training. V33 failed before work began. V49 ended in an exception without eight complete episodes. V45–v47 checked a single map. V41 and v42 use second-reset layouts and cannot be compared by seed with the canonical layouts.

| Experiment | Status | New training | Supervised updates | Physical verification | Arrivals / finished | Collisions | Timeouts |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| `portal-feedback-v13` | Completed | 0 | 1,024 | 3,504 | 0/8 | 8 | 0 |
| `portal-feedback-v14` | Completed | 0 | 4,096 | 6,224 | 0/8 | 8 | 0 |
| `whitened-portal-v15` | Completed | 32,768 | 4,096 | 28,304 | 0/8 | 5 | 3 |
| `local-peak-portal-v16` | Completed | 0 | 0 | 28,480 | 0/8 | 7 | 1 |
| `centered-portal-v17` | Completed | 32,768 | 4,096 | 3,952 | 0/8 | 8 | 0 |
| `guarded-portal-v18` | Completed | 0 | 0 | 26,680 | 0/8 | 8 | 0 |
| `free-space-portal-v19` | Completed | 0 | 0 | 29,496 | 0/8 | 1 | 7 |
| `context-portal-v32` | Script failure | 32,768 | 4,096 | 0 | No completed verification episodes | 0 | 0 |
| `context-portal-v32-verification` | Completed | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `approach-portal-v33` | Script failure | 0 | 0 | 0 | No completed verification episodes | 0 | 0 |
| `approach-portal-v34` | Completed | 0 | 1,536 | 28,480 | 3/8 | 1 | 4 |
| `range-approach-portal-v35` | Completed | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `dagger-approach-v37` | Completed | 32,768 | 4,096 | 29,496 | 1/8 | 2 | 5 |
| `range-only-approach-v38` | Completed | 0 | 2,048 | 28,480 | 0/8 | 3 | 5 |
| `tube-approach-v39` | Completed | 0 | 0 | 29,496 | 1/8 | 0 | 7 |
| `aligned-approach-v40` | Completed | 0 | 2,048 | 29,496 | 1/8 | 2 | 5 |
| `observed-voxel-v41` | Completed | 0 | 0 | 29,584 | 1/8 | 1 | 6 |
| `observed-voxel-v42` | Completed | 0 | 0 | 29,584 | 1/8 | 0 | 7 |
| `observed-voxel-v43` | Completed | 0 | 0 | 29,496 | 5/8 | 0 | 3 |
| `observed-voxel-v44` | Completed | 0 | 0 | 29,496 | 5/8 | 0 | 3 |
| `observed-voxel-v45` | Completed | 0 | 0 | 3,687 | 0/1 | 0 | 1 |
| `observed-voxel-v46` | Completed | 0 | 0 | 3,687 | 0/1 | 0 | 1 |
| `observed-voxel-v47` | Completed | 0 | 0 | 1,999 | 0/1 | 1 | 0 |
| `observed-voxel-v48` | Completed | 0 | 0 | 29,496 | 1/8 | 0 | 7 |
| `observed-voxel-v49` | Script failure | 0 | 0 | 8,480 | No completed verification episodes | 0 | 0 |
| `observed-voxel-v50` | Completed | 0 | 0 | 28,480 | 1/8 | 0 | 7 |
| `observed-voxel-v51` | Completed | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `observed-voxel-v52` | Completed | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `observed-voxel-v53` | Completed | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| `observed-voxel-v54` | Completed | 0 | 0 | 28,480 | 3/8 | 0 | 5 |
| `observed-voxel-v55` | Completed | 0 | 0 | 25,168 | 8/8 | 0 | 0 |
| `observed-v55-development` | Completed | 0 | 0 | 56,544 | 13/16 | 0 | 3 |

V36 is retained separately: 29,496 geometric-diagnostic transitions, 1/8 arrivals, zero collisions, and seven timeouts; zero training and fitting updates.

### 8.2. Geometric diagnostics v20–v31

These were not learned policies. V27–v30 canceled recurrence as an information bound, not as evidence of biological benefit. V31 retained 5% of its projection.

| Variant | Transitions | Arrivals / episodes | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| v20 | 293 | 0/1 | 1 | 0 |
| v21 | 300 | 0/1 | 1 | 0 |
| v22 | 3,687 | 0/1 | 0 | 1 |
| v23 | 3,687 | 0/1 | 0 | 1 |
| v24 | 71 | 0/1 | 1 | 0 |
| v25 | 340 | 0/1 | 1 | 0 |
| v26 | 3,687 | 0/1 | 0 | 1 |
| v27 | 3,687 | 0/1 | 0 | 1 |
| v28 | 1,982 | 0/1 | 1 | 0 |
| v29 | 3,687 | 0/1 | 0 | 1 |
| v30 | 2,399 | 1/1 | 0 | 0 |
| v31 | 29,496 | 4/8 | 0 | 4 |

The group totals 53,316 physical transitions and zero training. One arrival by v30 in a known room demonstrated the feasibility of that flight, not robustness across eight rooms.

### 8.3. Perception diagnostics that changed decisions

V13 had a 90th-percentile angular error of approximately 50.92 degrees on reused samples. V14 added heading equivariance: rotating the image and goal should rotate the reference. That test passed, while flights remained at 0/8. A correct algebraic property of a network does not eliminate every error in a sequential task.

Among 512 v17 records, 72 direction errors exceeded 90 degrees, and 45 labels fell outside the permitted hemisphere. A favorable median could conceal infrequent but decisive errors. V19 expanded candidates to 150 degrees relative to the goal and braked in a 45-degree cone; it ended with one collision and seven timeouts.

V32 fitted direction with a median of 1.55 degrees and a 90th percentile of 3.40 across 512 training fields. Distance RMSE was 1.14 units; for 73 references within two units, it was 0.54. It reached zero goals. A metric error small relative to the room can be large relative to an opening's clearance.

V34 reused v32 data and fitted only the wall normal over 1,536 updates. During alignment it aimed 1.3 units before the center; during crossing, 1.2 beyond it. This is learned perception with proportional control, not new PPO training. Its source history was 98,304 transitions; that is not equivalent to the project's global expenditure.

V37 added 16,384 student steps and 16,384 guided-recovery steps. During collection, the student finished with zero goals and one collision; the teacher had two goals and eight collisions. Joint fitting of direction, distance, and normal worsened angular error: approximately 7.35 degrees median and 30.15 at the 90th percentile. Recovery was not infallible either.

V38 froze angular tensors and verified identical scores while fitting distance; flight did not improve. V39 retained v34 weights and narrowed the protection tube; it reduced collisions but yielded only 1/8. V40 aligned panoramas using the neural goal bearing and fitted existing records 2,048 times; it also yielded 1/8.

The approximate visibility audit found a nearby ray that passed beyond the center for 7,773 of 8,928 v32 references and 7,679 of 9,192 v37 references. In v37, 68 references exceeded panoramic range. The remainder cannot automatically be classified as hidden: the nearest ray is not an exact geometric visibility test of the reference. Earlier labels were privileged supervision references, not centers with certified visibility.

## 9. Data, connectome, and exact transformations

### 9.1. Original data and project choices

MaleCNS v1.0 supplies connectivity, annotations, neurotransmitter predictions, and soma coordinates. Fly RL adds neuronal-segment selection, normalization, simplified signs, an artificial sensory projection, continuous activity, sensors, dynamics, and navigation rules. The dataset authors did not produce this controller. Attribution and licensing are in [references](REFERENCES.md) and [data and model](DATA_AND_MODEL.md).

The official annotation and connectivity tables used specify minimum confidence 0.5 in their names. The criterion retains segments with `Traced` status or an assigned superclass, excluding `Glia`, `Orphan`, and `Unimportant`. Within that criterion, all neurons and connections between them are retained. This does not claim unfiltered inclusion of every segment in the tables.

The retained graph contains 167,184 neurons, 25,583,622 directed pairs, and 124,176,995 represented synapses. No reduced graph replaced it in the cited flights, full diagnostics, or PPO checks. Algebraic tests with synthetic matrices are unit tests, not navigation or evidence of dataset coverage.

There are 140,033 somas with coordinates and 27,151 neurons without supplied coordinates. The latter still participate in computation even though they do not appear as points. The anatomical view represents somas, not complete arborizations or experimentally measured activity.

### 9.2. Matrix and neural activity

The matrix uses postsynaptic rows and presynaptic columns; repeated pairs are summed. With count C_ij and sign sigma_j:

\[
W_{ij}=\frac{0.9\,\sigma_j C_{ij}}{\max(1,\sum_k C_{ik})}.
\]

Sigma is -1 for sources with a GABA prediction and +1 for other or unknown sources. It does not represent conductances, delays, or plasticity by cell type. The fixed update is:

\[
h_t=0.5h_{t-1}+0.5\tanh(Wh_{t-1}+Ax_t-c).
\]

A is the sensory projection, and c is panoramic centering. The base projection uses two assignments per neuron, seed 42, and amplitude 0.5; the panorama adds two assignments, seed 123457, and amplitude 0.25. These are synthetic assignments, not reconstructed biological visual connections. The matrix and these projections are not optimized during PPO.

### 9.3. Projection readout and information bounds

A grouped summary can mix coordinates useful for navigation. The 128-transition diagnostic on the full graph yielded panoramic-distance RMSE of 1.724 for a grouped affine fit, 0.824 for projection with retained recurrence, and approximately 0.0000446 for the bound that cancels it. The affine fit was measured on the samples used to fit it: this is a favorable diagnostic, not independent validation.

From previous and current states:

\[
z_t=\operatorname{atanh}(\operatorname{clip}(2h_t-h_{t-1},-1+10^{-6},1-10^{-6}))+c.
\]

With ideal precision and no saturation, this equals Wh_(t-1)+Ax_t. Clipping avoids inverting tanh at its endpoints, but introduces an approximation for saturated values. The information bound subtracts Wh_(t-1). The whitened readout retains it; contrast subtracts 95%, leaving approximately 5% projected.

V55 separates channels:

\[
f_t=A^+(z_t-Wh_{t-1})+D A^+Wh_{t-1},
\qquad
D_{kk}=\begin{cases}0,&k<269\\0.05,&k\ge269.\end{cases}
\]

If N contains column norms and B=A N^-1, G=B^T B+10^-6 I is formed and N^-1 G^-1 B^T is solved through Cholesky. A^+ here denotes the implemented stabilized reconstruction, not an exact inversion without ridge regularization. `reconstruct_activity` does not consult world sensors; comparing them with reconstructed channels is an external accuracy check.


The full graph continues updating, while the base cancels recurrence in short distances, the goal, and motion; the panorama retains 5%. These are distinct facts. The result does not establish that this fraction or the biological wiring causes the success. No final paired comparison against alternative graphs was performed.

## 10. Sensor contract, memory, and input separation

| Zero-based indices | Count | Content | Reconstruction scale |
| --- | ---: | --- | --- |
| 0–127 | 128 | Short distances | Multiply by 8 |
| 128–255 | 128 | Short-range approach velocities | Velocity with scale 3 |
| 256–258 | 3 | Goal direction in body coordinates | Normalize to obtain a vector |
| 259 | 1 | Goal distance | Multiply by the norm of room - 0.32 |
| 260–262 | 3 | Body velocity | Multiply by 3 |
| 263–266 | 4 | Previous action | Normalized commands |
| 267 | 1 | Altitude | Multiply by 16 in `large` |
| 268 | 1 | Turning velocity | Multiply by 2.6 |
| 269–2068 | 1,800 | Panoramic distances | Multiply by 24 |
| 2069–3868 | 1,800 | Panoramic approach | Velocity with scale 3 |

The panorama has 25 rows and 72 columns: elevation from -84 to 84 degrees, azimuth from -180 to 175, and range 24. Short rays combine 26 three-dimensional neighborhood directions with 102 additional directions distributed over a sphere. There are 1,928 rays and 3,869 values, including goals and state.

Sensors originate at the body center and use uninflated boxes. Collision includes a radius of 0.16. An observed clearance of 0.2 does not mean 0.2 remains after subtracting the radius. This distinction matters when tuning braking.

The adapter requires a finite observation of shape `(1, 9, 3869)`: eight historical frames and the current frame, with a stride of eight decisions. V55 takes the current frame; its useful memory is the map, estimated pose, and route. It does not use those eight frames as a learned recurrent policy; it preserves the pipeline contract.

Resets clear activity, history, and counters. Within a batch, finished members reset independently while the neural state of continuing members is preserved. The viewer also clears the controller at episode end, on R, and on N.

V40 alignment used changes in goal bearing and circular column resampling. Translation also changes that bearing; this was not exact odometry. Passing tests of 45-degree rotation, circular boundaries, and gradients did not establish flight success.

## 11. Odometry and knowledge of the goal

Map position starts at x=y=0, with z reconstructed from altitude. Yaw starts at zero: the frame is relative to initial heading, not the room's absolute pose. Surfaces are rotated into that frame before accumulation.

Each decision integrates observed turning over 0.05 seconds and transforms body velocity using the estimated rotation. The local goal is:

\[
g_{\mathrm{local}}=\frac{f_{256:259}}{\max(\|f_{256:259}\|,10^{-6})}\max(f_{259},0)\|[48,48,16]-0.32\|.
\]

The first observation fixes `initial_goal`. If local horizontal distance exceeds two units, expected anchor bearing is compared with observed bearing. Wrapped yaw error is limited to +/-0.02 radians and multiplied by 0.2. Anchor-based position correction limits each component to +/-0.2 and applies a factor of 0.15. Altitude combines 80% estimate and 20% readout.

The interface contains no true pose, but it does contain a synthetic direction and distance to the goal. This is explicit task assistance; it is neither navigation without a reference nor autonomous goal discovery. True geometry saved for auditing does not enter these calculations.

A yaw bias rotates all accumulated surfaces and can render the map unusable after thousands of decisions. The stable reader reduces that numerical error. V43 and v44 both yielded 5/8, showing that this was not the only limitation.

## 12. Exact map construction

The grid has shape `(216,216,28)`, resolution 0.6, and origin `[-64.8,-64.8,0]` in the relative frame. This is 1,306,368 cells. Its horizontal extent accommodates rooms rotated relative to initial heading; it is not the physical room size.

Evidence uses `int8`, starts at zero, and updates on the first decision and every ten decisions, approximately 0.5 simulated seconds. Planning runs on the first decision and every twenty decisions, approximately one second, or when no route is available.

Free points are sampled at distances from 0.3 to below 24, in increments of 0.45, before the measured distance minus 0.35. Each unique cell observed as free loses one, with a floor of -8. Unique indices prevent repeated changes from many rays within one integration.

Endpoints with distance below 23.4 are hits. Each group of four neighboring panoramic pixels can be filled as a surface if all depths are below 23.4 and their variation is below 1.6. Twenty-five bilinear points are added per group, using coefficients 0, 0.25, 0.5, 0.75, and 1 on each axis. Each unique surface cell gains three, capped at 12. The current cell is marked free, with evidence -8.

Filling reduces gaps between rays but can connect surfaces that should remain separate. Discretization, perspective, readout, and persistence can produce gaps or false occupancy. There is no calibrated uncertainty model or guarantee of exact box reconstruction.

Evidence of at least two means occupied. The bottom and top layers are blocked, and solids are dilated by one cell along axial directions. Cost is 1 for observed free space, 2.8 for unknown space, and infinity for solids or margins.

If the position lies in the margin, `tight` mode activates. In a local region five cells wide on each axis, margin cells that are not solids acquire cost 8; observed surfaces remain blocked. The current cell costs 1. This is a local escape, not global relaxation of walls.

## 13. Route search and following

Search considers 26 displacements. Each transition costs the destination-cell value multiplied by displacement length: 1, square root of 2, or square root of 3 in cell units. Priority is:

\[
F(n)=g(n)+4.5\,h(n),\qquad h(n)=\|n-n_{\mathrm{goal}}\|_2.
\]

The factor 4.5 favors progress with fewer expansions. It does not guarantee the minimum route. A diagonal move is rejected if any axial intermediate cell is blocked. This is not a continuous sphere-clearance proof for every diagonal.

The terminal condition requires the exact goal-voxel index, after which its continuous coordinate is appended. If 12,000 expansions are reached without arriving, closed entries are removed from the heap head and the best remaining open frontier is used. If no open frontier exists, the visited node closest to the goal is retained. This avoids defaulting to a closed node near a wall while another open alternative remains, but can still select an insufficient detour.

The route is reconstructed using parents and cell centers. Its nearest point is found, and the earlier prefix is removed. If another point exists and the first is within 0.35, following advances. This prevents remaining at an already reached center.

Lookahead is three units, or one in `tight` mode. Each segment is sampled approximately every 0.1, requiring points inside the grid with finite costs. The saved cost from the latest planning pass is consulted, not a hidden geometric test. Within 1.5 of the observed goal, its vector is used directly.

Previously, completion was accepted within 1.6 cells of the goal, nearly 0.96 units at this resolution. A search with `found=true` could stop before crossing the reference. Voxel equality plus the continuous goal eliminated that premature condition.

## 14. Three-dimensional braking, flight, and reward

Let d be the reference in body coordinates, D=max(norm(d),10^-6), u=d/D, and p a reconstructed endpoint. The 128 short rays and 1,800 panoramic rays are combined:

\[
\ell=p^Tu,\qquad \rho=\|p-\ell u\|.
\]

Clearance L is the smallest positive ell with rho below 0.25; if none exists, it starts at 24. Requested speed is:

\[
s=\min\left(v_{\max},1.5D,\sqrt{2.4\max(L-0.27,0)}\right),
\quad v_{\max}=\begin{cases}0.8,&\mathrm{tight}\\1.8,&\mathrm{normal}.\end{cases}
\]

The requested direction is measured, rather than the front or current horizontal velocity. This allows checking a clear ascent despite a wall ahead. Rays remain sparse: they do not guarantee seeing every obstacle within the tube.

With yaw error e, desired horizontal velocity is s u_xy max(cos(e),0)^4. Vertical velocity is s u_z, independently of horizontal turning. If the reference's horizontal component has norm at most 0.05, e=0 is used so minimal horizontal noise cannot block nearly vertical movement.

Acceleration commands derive from that velocity:

\[
T=\operatorname{clip}(3(\|v^*_{xy}\|-v_x)+0.6\|v^*_{xy}\|,-1.2,3),
\]

\[
a_{\mathrm{forward}}=\begin{cases}T/3,&T\ge0\\T/1.2,&T<0,\end{cases}
\]

\[
a_{\mathrm{vertical}}=\operatorname{clip}((3(v^*_z-v_z)+0.8v^*_z)/2.5,-1,1),
\qquad a_{\mathrm{yaw}}=\operatorname{clip}(2e/1.8,-1,1).
\]

The lateral command is zero. Factors 0.6 and 0.8 compensate for simplified forward and vertical drag. There is no explicit integral or derivative of position error: this is proportional velocity control with a spatial reference and drag compensation.

Coordinated dynamics calculate desired yaw rate as 1.8 a_yaw + 0.8 a_lateral and smooth it with factor min(1; 5 dt). Positive body acceleration is `[3 a_forward, 0.35 a_lateral, 2.5 a_vertical]`; negative forward acceleration uses 1.2. Drag is `[0.6,2.8,0.8]`. Physical speed is capped at three units per second. Bank and pitch are smoothed visual states; they do not simulate wingbeats or real aerodynamics.

Collision checks the segment from previous to new position against boxes inflated by radius 0.16, as well as room boundaries. It can detect crossing a box between decisions. This physical check remains active and is not replaced by the grid.

Base reward is twice the distance reduction minus 0.02 per step, with +20 on arrival, -5 on collision, and -5 on timeout. V55 does not optimize this reward; it records it for compatibility. The profile's episode limit depends on certified length L_ref:

\[
\operatorname{ceil}\left(\frac{\max(60,2L_{\mathrm{ref}}/1.5+15)}{0.05}\right).
\]

The certified route determines part of the environment protocol but does not enter planner actions. These original deadlines were not extended to obtain 13/16.


## 15. Results for each room and timeout diagnosis

### 15.1. Canonical optimization

| Seed | Outcome | Decisions | Simulated seconds | Final distance |
| --- | --- | ---: | ---: | ---: |
| 370000 | Arrival | 2857 | 142.85 | 0.422525 |
| 370001 | Arrival | 2773 | 138.65 | 0.412719 |
| 370002 | Arrival | 2026 | 101.30 | 0.419600 |
| 370003 | Arrival | 2053 | 102.65 | 0.443625 |
| 370004 | Arrival | 2998 | 149.90 | 0.400518 |
| 370005 | Arrival | 2678 | 133.90 | 0.401159 |
| 370006 | Arrival | 3146 | 157.30 | 0.449248 |
| 370007 | Arrival | 2166 | 108.30 | 0.448753 |

### 15.2. Frozen prospective development

| Seed | Outcome | Decisions | Simulated seconds | Final distance |
| --- | --- | ---: | ---: | ---: |
| 8500000 | Arrival | 3069 | 153.45 | 0.409150 |
| 8500001 | Arrival | 1952 | 97.60 | 0.413202 |
| 8500002 | Arrival | 1918 | 95.90 | 0.398511 |
| 8500003 | Arrival | 1910 | 95.50 | 0.439138 |
| 8500004 | Arrival | 1916 | 95.80 | 0.413129 |
| 8500005 | Arrival | 2088 | 104.40 | 0.421456 |
| 8500006 | Arrival | 1663 | 83.15 | 0.421959 |
| 8500007 | Arrival | 2013 | 100.65 | 0.427010 |
| 8500008 | Arrival | 2029 | 101.45 | 0.446484 |
| 8500009 | Arrival | 3365 | 168.25 | 0.449494 |
| 8500010 | Arrival | 1739 | 86.95 | 0.441575 |
| 8500011 | Timeout | 3345 | 167.25 | 6.853000 |
| 8500012 | Timeout | 3534 | 176.70 | 26.957935 |
| 8500013 | Timeout | 3503 | 175.15 | 14.086490 |
| 8500014 | Arrival | 2872 | 143.60 | 0.408959 |
| 8500015 | Arrival | 2365 | 118.25 | 0.399152 |

Time is simulated, with decisions every 0.05 seconds. Final distance is not route length. Running out of time is not counted as success merely because progress occurred.

Final traces from 8500011 and 8500012 showed `found=false` and 12,000 expansions. In 8500013, a route was found but not completed in time. Increasing only the search limit has not been established as a solution for all three cases. Reference changes, detours, odometry, and costs require further analysis.

Their final distances were 6.853, 26.958, and 14.086 units, respectively. Recorded movement was present: these were neither three omitted arrivals nor three concealed collisions. Details come from existing traces, without new evaluation.

The Wilson interval uses k=13, n=16, p_hat=k/n, and z=1.959964:

\[
\frac{\hat p+z^2/(2n)\ \pm\ z\sqrt{\hat p(1-\hat p)/n+z^2/(4n^2)}}{1+z^2/n}.
\]

It yields 57.0–93.4%. The 81.25% estimate does not establish a guarantee of at least 80%; zero collisions in 16 flights does not imply zero risk either. V55 and v34 were not compared in a paired evaluation on these 16 maps.

## 16. Resources, timing, and GPU use

The tested environment uses Python 3.11, PyTorch 2.7.1 with CUDA 12.8, Stable-Baselines3 2.7.0, and Panda3D 1.10.16 on a 12 GB RTX 3060. V55 added no dependencies.

Sparse connectome updates, reconstruction, and `torch-cuda` sensors use the GPU. Odometry, the grid, SciPy, the search heap, much of the physics, and writing use the CPU. Reconstruction returns features to NumPy, involving transfers and synchronization. Low GPU utilization does not mean execution has stopped or that all time is spent in the optimizer.

The stable-reader diagnostic over 128 transitions recorded approximately 0.682 seconds after initialization, peak allocated VRAM of 560 MiB, normalized base RMSE of 0.00000567, yaw-rate RMSE of 0.00000472 rad/s, and panoramic-distance RMSE of 0.0419. This peak is PyTorch allocated memory during that check, not total process, rendering, or driver memory, nor an end-to-end benchmark.

The eight-map batch began at 13:02:20 UTC and ended at 13:05:35, approximately 195.27 seconds including initialization and closing. The prospective batch began at 13:06:22 and ended at 13:12:22, approximately 360.69 seconds. Dividing physical counters by those durations gives around 129 and 157 batch transitions per second. These are rates for those runs, not universal training or rendered-demo measurements.

The grid contains approximately 1.31 million cells per controller. Search creates cost, score, parent, and visited arrays as well as the heap. Evidence alone does not represent all CPU memory. Batch size, expansions, rays, and anatomical rendering affect different components.

## 17. What the tests and checks established

The integrated version passed 265 tests. They establish the checked properties, not success in every room. The six new planner tests cover advancing an already reached reference, escaping the margin without opening solids, clear ascent in front of a frontal wall, braking toward an obstacle, clearing the map and odometry on reset, and rejecting incompatible or nonfinite history.

Readout tests verify algebra, nonzero visual recurrence, distinct contracts, and independent resets. Visualization tests check body IDs and sensitivity appropriate to the reader. V55 saves activity and change, with sensitivity unavailable; it does not calculate a PPO derivative for an action PPO did not decide.

The batch included three temporary PPO checks of 128 transitions and one update each. These are separate verification, not substantive training or navigation performance. The stable-reader check recorded finite losses, value loss 0.824498, approximate KL 0, and maximum CPU action-reload error of 3.5763e-7. The temporary checkpoint was deleted. One update and zero KL do not establish learning.

Two 40-step launches checked controls and closing. The 3,200-step flight verified a known arrival and automatic reset. Keys and windows were exercised programmatically in offscreen mode; this is not presented as manual testing of every device. Room and brain images were visually inspected.

A neural index applied to a gradient that still contained the history dimension was corrected. For projection readers, the gradient was transformed to the reconstructed neural drive with previous states held fixed, rather than being called sensitivity of the recurrent state. The planner shows only activity and change. Brain-image saving avoids an empty PNG: it encodes in memory, requires data, and replaces through a temporary file.

## 18. Recording, reproduction, and preservation

### 18.1. Historical archive and preview

Each session has a unique directory in `runs/demo`; it does not overwrite earlier sessions. The preview image and `reports/demo.json` can represent the latest session but are not the complete historical archive.

The manifest saves the dataset, brain fingerprint, readout, sensor contract, feature count, dynamics, configuration, software versions, Git revision, and whether the working tree was modified. Compressed blocks save previous and next sensors, features, actions and applied actions, positions, velocities, yaw, reward, and termination. Events record rooms, resets, episode ends, and neural observations. Full-neuron snapshots are optional with `--record-brain`.

V55 archives `controller.py` and `controller.json` with type, version, and SHA-256, rather than a PPO checkpoint suggesting movement weights. The frozen public source has SHA-256 `faec0e96a8fb6e26a88675a25c7fb4468593aca481e70a4e50d463c621053dd2`. The prototype and public module have different structures: equivalence was verified through actions/maps and integrated flight, not by assuming identical hashes across different sources.

Telemetry uses 128-row chunks, checksums, and temporary replacement. Its audit checks schema, finiteness, steps, hashes, and room references. Documented sessions closed without archive errors or warnings. Replay reproduces saved states without recomputing the brain or controller.

### 18.2. Commands and execution contracts

```powershell
.\launch-observed-map.cmd
.\launch-observed-map.cmd --speed 4 --seed 370001
.\launch-observed-map.cmd --record-brain
```

The `.cmd` wrapper calls PowerShell explicitly to avoid a `.ps1` file association opening an editor. The CLI fixes `large`, coordinated dynamics, sensors-v6, and the stable reader. It rejects combining the planner with a PPO checkpoint, another profile, or an incompatible sensor contract. It does not promise arbitrary sizes.

Shift multiplies simulated time by ten, not weights, forces, radius, or maximum physical speed. Accelerating playback requires more decisions per wall-clock second; computation limits may reduce the visible acceleration. The demo does not train.

For an already saved session, replace the name with the actual directory:

```powershell
.\.conda\python.exe -m fly_rl inspect runs/demo/SESSION_NAME
.\.conda\python.exe -m fly_rl replay runs/demo/SESSION_NAME
```

Repeating a flight on a known seed produces new verification data, but not new independent maps. Inspecting or replaying records does not require optimizing a policy.

### 18.3. Sources for each component

| Component | Source |
| --- | --- |
| Neuron selection, counts, normalization, and checksums | [data.py](../fly_rl/connectome/data.py) |
| Recurrent graph, projection, and activity | [brain.py](../fly_rl/connectome/brain.py) |
| Reconstructions and stable reader | [innovation.py](../fly_rl/connectome/innovation.py) |
| Sensor order and geometry | [sensors.py](../fly_rl/simulation/sensors.py) |
| Coordinated dynamics | [flight.py](../fly_rl/simulation/flight.py) |
| Collision, observation, reward, and termination | [world.py](../fly_rl/simulation/world.py) |
| Profiles and geometric deadline | [map_profiles.py](../fly_rl/simulation/map_profiles.py) |
| Batches, history, and neural reset | [learning.py](../fly_rl/training/learning.py) |
| V55 map, search, route following, and commands | [observed_map.py](../fly_rl/navigation/observed_map.py) |
| Viewer, recording, and controller reset | [viewer.py](../fly_rl/visualization/viewer.py) |
| Activity and sensitivity | [neural_view.py](../fly_rl/visualization/neural_view.py) |
| Anatomical window and capture | [brain_map.py](../fly_rl/visualization/brain_map.py) |
| Manifest and telemetry blocks | [recording.py](../fly_rl/recordings/recording.py) |
| Archive audit | [archive.py](../fly_rl/recordings/archive.py) |
| Planner regressions | [test_observed_map.py](../tests/navigation/test_observed_map.py) |

### 18.4. Commits and preserved models

`8bccaf4` incorporated readers/pilots and corrected sensitivity. `972ceb4` integrated the planner and demo. `dedc676` documented the process. This expansion is documentation only: it does not modify frozen code, weights, results, or execution contracts.

The [v55 report](evidence/observed-map-v55-results.md) retains before/after SHA-256 values for the six previous alias files. Source and experimental checkpoints were also verified. Local artifacts retain plans, hashes, failure statuses, frozen sources, audit geometry, and traces. A script failure was not rewritten as navigation success.

## 19. Data separation and scientific limits

Training collects experience to fit parameters; design optimization tests variants on known maps; prospective development checks a frozen version on new maps; the reserved test has its own access protocol. These are not combined into a single rate.

True geometry generates rooms, checks collision, provides supervision during training, and supports later auditing. V55 does not receive it. It does receive a synthetic goal, known size, and a readout constructed with the known projection. Not consulting hidden boxes does not mean being free of artificial assistance.

Reusing 370000–370007 can adapt rules to those maps even without training weights. The 8/8 does not eliminate that risk. The 16 new rooms were fixed before checking, with no changes during flights; they are prospective for v55. Their failures were inspected afterward. If they are now used to tune another version, another new set will be required.

No optimal route, biological advantage, transfer to `maze`, unsupervised learning, robustness to noise, or diversity outside this generator was established. Nor was each final correction isolated through ablation. The change from 3/8 in v54 to 8/8 in v55 combines route advancement, braking direction, margin speed, and independent vertical control; it is not attributed to one parameter.

Cumulative project expenditure is not the history of an individual model. The 131,072 new transitions on October 5 are four batches of 32,768: v15, v17, v32, and v37. V34 reuses records and adds no steps; v55 has no learned weights. Verification transitions and supervised updates remain separate. V32 training and its subsequent verification are not counted twice.

## 20. Completed criteria and remaining work

This delivery's functional scope is to open a demo, observe autonomous flight consuming full-graph activity, and complete large routes with verifiable records. The documented checks meet that scope. A reliable learned policy and the objective of at least 80% on an independent final test remain open.

Next work should retain v55 as a reference, diagnose the three timeouts separately, freeze any correction before opening new maps, and study whether a student can learn complete planner routes. Comparing planning, learned perception, and PPO requires declared contracts and budgets, multiple initializations, and paired evaluation that does not select versions.

Map memory is not presented as learned memory. Retaining all neurons does not establish that anatomy is necessary for the algorithm. The supported explanation is that the artificial readout became more usable, explicit spatial memory was added, and route execution was corrected. Actual arrivals and three new failures define the scope. There is still no evidence that PPO has learned this solution.

## 21. Follow-up: diagnose the three planner timeouts

On October 5, bounded three-instance full-graph checks reproduced all three known failures, then tested a separate v56 candidate. The goal in room 8500011 was observed as free but blocked by the inflated safety margin. V56 locally admits only observed-free margin cells near that goal at high traversal cost, retaining observed solids, unknown blocked cells, boundaries, physical collision checks, and deadlines. That room reached the goal at step 1,939 instead of timing out at step 3,345. The other two rooms still timed out; neither version collided.

The checks used 21,204 physical transitions in total, zero training transitions, zero optimization updates, and no reserved-test access. All original aliases and the frozen v55 source retained their hashes. Maximum measured pose error remained below 0.003 units, which does not support odometry drift as the main cause in these flights. Room 8500012 still exhausted search capacity, whereas room 8500013 found routes throughout; a single goal-margin explanation does not cover both.

The [detailed follow-up report](evidence/planner-timeouts-v56-results.md) records the diagnosis, local rule, regression checks, per-room outcomes, counter definitions, preservation hashes, and reproduction commands. This reused 1/3 result cannot be added to the original prospective 13/16 or presented as independent generalization. V55 remains the operational default; v56 is experimental. The next correction must investigate route execution and detour decisions in the two unresolved rooms before a fresh prospective assessment.

## 22. Follow-up: isolate speed and margin recovery

V57 increased clear-space cruising speed from 1.8 to 2.6 units/s while preserving requested-direction braking and the 0.8 margin speed. It reached two of the three known failures, including room 8500013, which had found routes throughout but exhausted its deadline. V58 separately admitted observed-free inflated cells at cost 8; this eliminated sampled search saturation in room 8500012, but original-speed flights still reached only one goal. Both changes together in v59 reached room 8500012 but regressed room 8500013. All checks retained actual collision detection and original deadlines, with zero recorded collisions.

V60 retains v57's normal clearance until a failed search reaches the existing 12,000-expansion cap. Recovery then admits only observed-free margin cells in subsequent plans, preserving surfaces, unknown blocked cells, boundaries, and the search budget. It reached all three known failures: room 8500011 at step 1,628, room 8500012 at 3,171, and room 8500013 at 2,499. Only room 8500012 activated recovery. A controller reset clears that state.

These four checks used 41,226 physical transitions without training or reserved-test access. Twenty-eight navigation regressions passed. The [attempt-by-attempt report](evidence/planner-followup-v57-v60.md) retains the unconditional regression and offline probes as well as the successful known-case correction. V60 is frozen for fresh development measurement; its tuned 3/3 cannot be added to historical prospective results or substituted for reliable learned navigation.

## 23. Frozen paired development and experimental viewer

The predeclared sixteen-room comparison on seeds 9500000–9500015 completed with both versions unchanged. V55 reached 12/16 goals (zero collisions, four timeouts), while v60 reached 14/16 (zero collisions, two timeouts). Twelve rooms succeeded in both arms, two only in v60, and two in neither. The v60 Wilson 95% interval is 64.0–96.5%, so this small development sample does not establish the independent-final target. Original aliases, frozen sources, initial layouts, and brain fingerprints passed the preservation and matching checks.

Both arms used 55,680 physical transitions, below the separately declared 81,920-per-arm caps, with no optimization or reserved-final access. Distances now sum every scored physical displacement rather than sampled traces. Some successful v60 routes are longer than v55's; neither shortest paths nor optimal flight are established. [Protocol](PLANNER_DEVELOPMENT.md) and [per-room results](evidence/planner-v60-development-results.md) retain the counts and uncertainty.

V60 can be selected explicitly in the viewer while v55 remains the launcher default. Its 800-step rendered verification had finite activity, zero collisions, working controls and brain-window checks, and a valid archive; it ended before completing an episode. Experimental archives retain all inherited controller source files, and inspection checks their hashes and specification. The full regression suite passed 326 tests. Viewing does not train, and the planner still has no learned movement weights.

The two new failures are seeds 9500001 and 9500014. The first barely moved despite repeatedly finding a route; the second exhausted its deadline on detours. Once inspected, these become known correction cases and cannot be reused to claim fresh prospective results for a tuned successor. No further independent claim follows from the rendered check.

## 24. Follow-up: physical ranges cannot contain arbitrary context

Room 9500001 exposed a semantic mismatch between the panoramic readout and braking. The planner interpreted decoded coordinates as physical ranges, but those coordinates retained five percent projected recurrent drive. In a 128-transition full-graph audit, all 104 zero-speed samples had raw requested-direction clearance above the stopping threshold. Audit sensors were compared only after choosing actions. At one sample the decoded endpoint implied 0.048 units of clearance, while raw ranges implied about 10.05 units along the requested direction. The correction changes the range decoder rather than weakening collision checks or the braking tube.

V61 cancels projected recurrence in all distance channels and retains five percent context in panoramic closing speeds. It inherits v60's flight and planning rules unchanged. Full previous/current neuron states and the known projection produce the features; raw observations are not appended or substituted during inference. All neurons and edges still advance. The separate readout fingerprint prevents old checkpoints from silently accepting the new feature semantics. The exact gain slices and interpretation are documented in [Mathematics](MATHEMATICS.md) and the [readout report](evidence/planner-readout-v61-v63.md).

The previously stationary room reached its target at step 2,276 without colliding. Room 9500014 still timed out at 3,480 steps after substantial travel. Pose error stayed below 0.003 units, so this later detour failure is not supported as odometry drift or simple false stopping. It remains a separate navigation problem.

V62 tried retaining a traversable eight-unit route prefix instead of replacing routes on every map update. V63 separately prevented interpolated surfaces from overriding current free-ray evidence while preserving directly measured hits. Both timed out in the same remaining room. Their shorter flown distances and component correctness are not successful arrivals; neither is selected as a navigation solution. Four known-case flights used 12,716 physical transitions, plus 128 separately counted audit transitions, with no optimizer updates or reserved-test access.

V60 and v61 are frozen for a new paired development check on sixteen previously undeclared rooms, with the readout difference explicitly declared and matching graph/layout contracts. Results belong to that separate measurement only after both arms finish. The [development protocol](PLANNER_DEVELOPMENT.md) specifies source preservation, cutoff, physical budgets, and reporting rules.

That comparison completed at 15/16 goals for v60 and 13/16 for v61. V61 had two collisions and one timeout; v60 had one collision. Two rooms succeeded only in v60, with no candidate-only success. The range correction therefore regressed this fresh development measurement and was not selected as the stronger general candidate. [All paired outcomes](evidence/planner-v61-development-results.md).

## 25. Follow-up: steering direction differs from physical momentum

The two v61 collisions occurred while waypoint direction and flight direction were changing. Requested-direction clearance did not cover every surface approached by inertia. Separately bounded batch-one prefixes failed to reproduce those collisions within 1,024 steps each; those incomplete audits remain in the record. A matched four-instance recheck reproduced the original contacts at steps 664 and 684, alongside two successful control rooms. This distinction prevents incomplete rechecks from erasing real failures.

V64 keeps v61 mapping and route following, then checks reconstructed endpoints along measured body-frame velocity as well as the waypoint direction. If measured speed exceeds the existing stopping-distance limit along that motion, desired velocity becomes zero and the proportional controls request braking. Steering remains active. This is an additional approximate safety check, not a change to true collision detection or an avoidance guarantee. Debug fields distinguish requested speed before the guard from effective desired speed after it.

V64 reached all four known rooms without collisions, preserving the two control arrival steps at 1,514 and 1,708. The formerly colliding rooms arrived at 1,582 and 2,415. The two arms used 16,492 physical transitions, zero optimization, and no reserved test. The [detailed report](evidence/planner-momentum-v64-results.md) includes formulas, sampling limits, and the diagnostic figure.

A subsequent frozen sixteen-room comparison on new seeds 11000000–11000015 still regressed: v60 reached 15/16 with one timeout, whereas v64 reached 12/16 with four timeouts. Neither collided. Eleven rooms succeeded in both, four only in v60, and one only in v64. The 112,992 physical transitions remain separate development measurement. [Per-room evidence](evidence/planner-v64-development-results.md). Preventing known contacts did not establish improved overall goal attainment.

## 26. Separate mapping context from physical safety ranges

V61 changed both braking and occupancy integration by replacing every panoramic range with its recurrence-cancelled value. That broad interface change alters mapped surfaces, route selection, and subsequent observations. V65 instead emits two declared neural outputs from one graph update: the unchanged 3,869-coordinate v60 prefix, followed by 1,800 clean panoramic ranges. The occupancy integrator consumes the original contextual prefix. Requested-direction and momentum braking consume the separate clean ranges. Base target, altitude, and motion channels retain their original stable semantics.

Both outputs derive from the same previous/current full-neuron states through the known projection. Neither reads raw world values during reconstruction. A component test confirms that the prefix matches the old decoder exactly, the appended ranges match clean reconstruction within measured numerical tolerance, state is not changed by reconstruction, and independent reset remains valid. A separate controller check confirms original mapping evidence while passing clean coordinates to flight control, with input arrays unchanged.

The width change from 3,869 to 5,669 features is explicit. Viewer selection, checkpoint fingerprints, environment history, source manifests, and schema-three development protocols distinguish it from the unchanged 3,869-value sensor input. An old observation shape is rejected. This added engineered information does not establish biological vision or a benefit from the wiring.

The four known rooms reached 4/4 goals without collisions, at steps 1,688, 2,202, 1,404, and 2,260 for seeds 10000005–10000008. This used 9,040 physical transitions under a declared 12,000 cap. These tuned outcomes do not establish generalization. V60/v65 are separately frozen on new seeds 13000000–13000015 with declared readout widths and source hashes before either arm runs. Their fresh conclusion is recorded only after completion and preservation checks.

The v60/v65 prospective development measurement completed with identical paired outcomes: 15/16 goals, zero collisions, one timeout in room 13000013. Each arm used 55,984 physical transitions; declared widths, source/alias checks, initial layouts, graph data, and base projection/model matched. The Wilson interval is 71.7–98.9%. This is a targeted correction with a tied fresh rate, not a demonstrated general success-rate improvement or independent-final mastery. [All rooms](evidence/planner-v65-development-results.md).

V65 also reached the formerly stationary known room at step 1,782, while retained detour room 9500014 still timed out at 3,480. Those two checks used 5,262 transitions without collisions. The 200-step rendered v65 flight and archive passed, and its temporary full-graph 128-transition/one-update PPO verification reloaded with identical actions. Weights were deleted after that pipeline check. The final full suite passed 359 tests. [Complete evidence and preserved hashes](evidence/planner-dual-v65-results.md).


### Remaining timeout diagnosis after the v65 freeze

Offline inspection of existing second-half traces found continuing motion, zero sampled momentum-guard activations, and estimated pose errors below 0.0011 room units. Routes were reported found in 86/87 and 87/88 sampled frames. This narrows the next investigation to route/search progress and physical execution, rather than treating every failure as a false sensor stop. It does not prove the causal explanation. [Sampled counts and limitations](evidence/planner-dual-v65-results.md#offline-inspection-of-the-remaining-timeouts).
