# Passage perception and flight control through neural activity

Work resumed at the user's request on October 5, 2026. Autonomous navigation in the original large maps remained unresolved after v12. This protocol distinguishes learning a spatial reference from learning to convert it into acceleration.

Pilots v13 and v14 consume only the nine neural-activity samples in the sensors-v6 contract. The brain retains all 167,184 neurons and 25,583,622 connections from MaleCNS v1.0. The encoder predicts a reference in body coordinates and its local velocity. It receives no absolute position, obstacles, opening coordinates, or certified route during flight.

Labels are reconstructed from poses and maps in the 98,304 retained optimization states from v7. For each state, the next opening entry or exit point on the training route is selected, or the goal after the last wall. This geometry is privileged supervision information. It does not enter student observations. Reusing those data adds no physical transitions.

The predicted reference feeds proportional velocity control, with braking during turns and drag compensation. This is a hybrid controller: learned perception and explicit physical control. The pilots fit perception through supervision, without PPO optimization. The interface maintains a Gaussian distribution and consistent PPO prediction and evaluation paths for future reinforcement-learning correction. Flights with this controller are not presented as evidence that PPO learned those movements.

V13 used 1,024 updates and a limit of 32,768 verification transitions across eight optimization maps. It finished after 3,504 transitions, with zero arrivals and eight collisions. Reload reproduced actions, losses were finite, and protected files retained their hashes. Median angular error on 512 optimization states was 11.55 degrees; the 90th percentile was 50.92 degrees. Velocity errors were 0.063, 0.058, and 0.078 units per second. These are diagnostics on reused data, not independent validation.

Initial v13 predictions showed a preference for the body's forward direction even with different initial headings. V14 removes fixed horizontal coordinates from the scoring encoder; it retains neural depth, elevation, and alignment with neural goal direction. A test checks that cyclically rotating the neural image and its goal direction rotates the predicted reference. This verifies an encoder property, not an exact symmetry of the biological connectome or every action.

V14 starts with new weights, 4,096 supervised updates, and the same maximum of 32,768 verification steps. Each batch contains one quarter examples from the first 16 ticks, one half recorded guided states, and one quarter recorded autonomous states. Groups can overlap. Flight is first checked on optimization maps; these results do not establish generalization. The reserved test and original aliases remain protected, with no automatic promotion.

Plans, losses, hashes, and detailed trajectories are in private artifacts and each experiment's local folders. None of these changes supports claiming biological advantage or declaring navigation resolved without verified autonomous arrivals.

## New batch with corrected projections

V14 also finished with zero arrivals and eight collisions, after 6,224 verification transitions. Its 4,096 fitting updates had finite losses and compatible reload. Heading symmetry verified by tests was insufficient for navigation.

A subsequent diagnostic measured substantial precision loss in summaries based on neural means. A least-squares reader was prepared to correct mixing in the artificial sensory projection. The diagnostic variant cancels recurrence and serves only as an information bound; the flight candidate retains the projected recurrent contribution. Code, fingerprints, and documentation distinguish them. Formulas and limitations are in [mathematics](../MATHEMATICS.md).

V15 uses a new controller and a new neural-readout contract. Its budget is 32,768 new guided transitions, 4,096 supervised updates, and up to 32,768 separate autonomous verification transitions on optimization maps. It transfers neither weights nor test observations. Losses, visited maps, valid data, reload, and teacher/student results are recorded separately. Flight checks do not increment the checkpoint's training counter.

An additional temporary check ran exactly 128 transitions and one PPO update, with finite losses and compatible CPU reload; the temporary checkpoint was deleted. That check establishes that the new policy can execute the learning pipeline, but supplies no navigation results and does not count toward substantive training.

## Results of the resumed batches

| Batch | New physical training | Separate physical verification | Autonomous goals | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: | ---: |
| v13, perception and PD | 0 | 3,504 | 0/8 | 8 | 0 |
| v14, equivariant heading | 0 | 6,224 | 0/8 | 8 | 0 |
| v15, corrected reader | 32,768 | 28,304 | 0/8 | 5 | 3 |
| v16, local maximum | 0 | 28,480 | 0/8 | 7 | 1 |
| v17, visible centers | 32,768 | 3,952 | 0/8 | 8 | 0 |
| v18, detours and braking | 0 | 26,680 | 0/8 | 8 | 0 |
| v19, free space | 0 | 29,496 | 0/8 | 1 | 7 |

Training added 65,536 transitions, all guided and advancing the full connectome. V15 and v17 each recorded eight teacher arrivals without collisions or timeouts; these are not autonomous successes. Perception fits used finite losses, and checkpoints reproduced actions after reload. V16, v18, and v19 modify inference without weight updates. V18 expands two auxiliary matrices from six to nine inputs using zeros; v19 preserves their values exactly. None of those transfers preserves earlier actions, because control or candidate selection changes.

Every autonomous flight in this table is a check on the same eight optimization maps. These are neither independent validation nor a final test. After v19, navigation remained unresolved: reducing collisions converted failures into timeouts. The v13 and v14 checkpoint counters include their checks, although no new physical training occurred; the table explicitly separates them from substantive training.

Completed substantive use totals 1,538,048 transitions. The table's 126,640 verification steps, two 128-step diagnostics, the 128-step PPO smoke, and the short 40-step demo are counted separately. Protected hashes match at the end of each batch. The reserved test was not consumed, and no alias was promoted.

V17 retains poses, velocities, headings, seeds, and ticks for 8,984 valid samples to audit its geometric center references. In v19, selection considers candidates up to 150 degrees from neural goal direction, requires 1.5 meters of estimated space when a candidate is available, and uses a 45-degree horizontal braking cone. This is a heuristic filter with readout uncertainty, not a safety guarantee; the result confirms that one collision still occurred.

The new distribution and its gradients were checked; earlier training and simulation tests passed 204 cases, and later tests cover changes to centers, braking, and checkpoint contracts. The v19 demo opened, rendered 40 steps, and closed normally without training. Its screenshot was inspected; controls were checked programmatically, without claiming physical keyboard or anatomical-window verification in that check.

## Subsequent geometric diagnosis

The audit of 512 v17 states found 72 direction errors greater than 90 degrees; 45 labels were outside that version's permitted hemisphere. Expanding candidate directions and braking was insufficient to resolve flight. Finite losses and a good fit median can conceal selection errors that destroy an entire trajectory.

Geometric references built exclusively from distances, goal direction, and motion reconstructed from neural states were tested. The algorithm fits walls to the distance cloud, finds openings, maintains a reference through observed odometry, and selects local detours. It receives no positions, seeds, boxes, walls, or certified route. Room size is known as part of the environment contract. This is explicit geometric navigation, not a learned policy.

V20–v29 checked a single optimization map. None reached the goal. V30 arrived in 2,399 steps without collision, using the diagnostic reader that cancels recurrent contribution. This is a simulator information bound, not evidence that biological recurrence provides an advantage.

V31 retains five percent of the projected recurrent contribution with the same full graph. Across eight reused optimization maps, it achieved four arrivals, zero collisions, and four timeouts after 29,496 verification transitions. It trained no weights and generated no checkpoint. Geometric selection and artificial readout contribute to this result; these four arrivals must not be attributed to the v19 student.

Diagnostic variants v20–v31 total 53,316 physical transitions, separate from training, without using the reserved test. Their sources, states, and trajectories are retained locally with private artifacts. They remain optimization checks, including failed variants.

V32 begins a bounded learned-perception batch with 32,768 new guided transitions, 4,096 supervised updates, and up to 32,768 autonomous verification transitions. It adds global panoramic context to local scores and explicitly changes the readout contract to a five-percent recurrent contribution. Observations still originate from full-connectome states; center labels are privileged training supervision. The plan protects all original checkpoints and separates teacher flights from student flights.

## Global perception and separate approach

V32 consumed its 32,768 guided transitions and 4,096 supervised updates, with nine teacher arrivals. Its checkpoint was saved with finite losses. The script then failed while calculating the audit because velocity and braking columns were mixed. That failure status and the original error are retained. A separate check corrected only the report, loaded the same checkpoint without training or modifying it, and verified reload.

Median and 90th-percentile angular errors on 512 training fields were 1.55 and 3.40 degrees, respectively. Despite that, autonomous flight reached zero of eight goals, with eight timeouts and no collisions, after 29,496 verification transitions. A good perception fit does not establish navigation. Predicted-distance root mean square error was 1.14 meters; across 73 states with a reference within two meters, error was 0.54 meters.

V33 failed before any fitting or physical transition because a NumPy seed type was incompatible with Gymnasium. V34 corrected the type and reused v32's recorded neural fields. It fitted only a wall-orientation head over 1,536 supervised updates. Labels derive from training poses; inference does not consult poses or the map. It added no physical training or PPO updates.

Learned orientation allows maintaining 1.3 meters of separation while aligning with the opening, then aiming 1.2 meters beyond it when aligned. Across eight reused optimization maps, v34 completed three goals, with one collision and four timeouts, after 28,480 verification transitions. Losses were finite, and reload reproduced actions. Reliable navigation remains unresolved, and this result is not an independent generalization test.

V35 preserves every v34 tensor and checks an inference correction: it uses short neural distances to avoid approaching inside the intended separation while still misaligned. It adds no training and does not consume the reserved test.

## Later corrections and accounting

Checks continue to use the eight optimization maps 370000–370007. They are reused to diagnose and select variants; they are not an independent test. None of these batches consumes the reserved final set.

| Variant | New physical training | Supervised updates | Physical verification | Arrivals | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v32, global context | 32,768 | 4,096 | 29,496 | 0/8 | 0 | 8 |
| v34, approach and crossing | 0 | 1,536 | 28,480 | 3/8 | 1 | 4 |
| v35, median separation | 0 | 0 | 29,496 | 0/8 | 0 | 8 |
| v37, student exposure | 32,768 | 4,096 | 29,496 | 1/8 | 2 | 5 |
| v38, isolated distance fit | 0 | 2,048 | 28,480 | 0/8 | 3 | 5 |
| v39, trajectory protection | 0 | 0 | 29,496 | 1/8 | 0 | 7 |
| v40, temporal alignment | 0 | 2,048 | 29,496 | 1/8 | 2 | 5 |

V35 did not improve approach: nearby obstacles could be mistaken for the wall. Geometric diagnostic v36 did not improve on v31 either: it reached 1/8 goals with seven timeouts and no collisions after 29,496 transitions. It trained no policy and remains separate from the student.

V37 added 32,768 transitions: 16,384 under student actions and 16,384 with teacher recovery. During collection, the student reached no goals and had one collision; the teacher recorded two arrivals and eight collisions. Recovery is not infallible either. Joint fitting of direction, metric distance, and normal worsened angular precision. V38 froze angular tensors and the orientation head to isolate distance losses. It verified identical angular scores, but better distance fitting did not improve navigation.

V39 preserved every v34 tensor and changed braking protection to a 0.28-meter tube around motion. The geometry test distinguishes a side obstacle from a frontal obstacle. Flight had fewer collisions but more timeouts; that is not adopted as an improvement.

Panoramas from different times were not aligned during turns. In saved data, goal-orientation changes between images reached around 40 degrees. V40 approximates turning through the difference in neural goal orientation and circularly resamples the previous image. Translation also changes that orientation, so this is not exact odometry. A test verifies 45-degree rotation, boundary continuity, and finite gradients with empty history. After 2,048 fits on saved fields, v40 did not improve on v34. Correcting that hypothesis is insufficient to declare navigation resolved.

The resumed batch adds 131,072 physical training transitions: v15, v17, v32, and v37 contribute 32,768 each. Cumulative substantive use increases from 1,472,512 to 1,603,584. Fits by v34, v38, and v40 reuse records and add no physical transitions. The two 128-step PPO checks are separate temporary tests, with one update each and finite losses; they are not performance experiments.

## Neural inspection and demonstration

The anatomical window failed when applying neuron indices to a gradient shaped as history by features. It now selects the current sample and transforms the gradient according to the actual reader. For neural means, it displays sensitivity to recurrent state; for projection readouts, sensitivity to reconstructed neural drive, holding the previous state fixed. Traces record that basis and conditioning. It is not presented as causal attribution or measured biological activity.

A short v34 demonstration with the full graph and brain window closed normally after 40 steps and 40 images. The room screenshot was inspected. This check establishes startup and execution; it supplies no additional arrival and does not physically verify every key. Targeted perception, reconstruction, checkpoint, and visualization tests passed 25 cases, in addition to the earlier 214 training and simulation cases.

## Observed map in diagnosis

At this stage, an explicit-planning alternative was tested that builds occupancy from distances and motion reconstructed from neural activity. Its interface does not accept the world object, seeds, boxes, true poses, or certified route. It uses declared room size and a local memory grid. It is not a learned policy, and its arrivals are reported separately. Final version v55 and best student v34 are retained as distinct controllers.

## Stable motion readout

Accumulated map drift motivated a variant that cancels projected recurrence in the 269 base channels, including short distances, the goal, and motion, while retaining five percent in the 3,600 panoramic channels. Reconstruction uses only previous and current neural states and the known fixed projection. It has a new fingerprint; earlier checkpoints are not silently reinterpreted. Formulas and numerical diagnostics are in [mathematics](../MATHEMATICS.md). This is neither an established biological mechanism nor evidence of particular usefulness of fly wiring.

The algebraic test checks each block, nonzero visual recurrence, and independent resets. The full-graph check retained 167,184 neurons and 25,583,622 connections. The PPO pipeline passed an additional temporary check of 128 transitions and one update, with finite losses and compatible reload; the temporary file was deleted. This third PPO check remains separate from substantive training.

Initial map variants v41 and v42 generated the room with the generator's second reset. Their labeled seeds do not identify the same canonical layouts as earlier checks; the generation procedure is retained, and those flights are not compared by seed with v34. V43 corrected the explicit reset and saved initial boxes to audit layout identity. Across eight reused canonical maps, it reached 5/8 goals, without collisions and with three timeouts. V44, with the stable reader, also reached 5/8, without collisions and with three timeouts. Both used 29,496 verification transitions; v44 added its separate 128-transition diagnostic. These are geometric-planning algorithms, not learned-student results.

On map 370000, the hard occupancy margin left only one accessible cell around the fly. V45 confirmed that blockage. V46 converted the margin into a high cost while keeping observed surfaces impassable, allowing progress but ending in timeout. V47 reduced lateral protection and progressed farther, but collided while smoothing a corner. V48 limited smoothing in margins, reduced speed there, and added three-dimensional braking. It reached 1/8 goals without collisions and with seven timeouts. V48 was not promoted to the demo.

## Reference audit and subsequent blockages

Center references used in training were selected from room geometry. Visibility was not checked before labeling each image. They must therefore be described as geometric references that may be hidden, rather than verified visible centers. An audit of existing records found that the nearest panoramic ray passed beyond the center in 7,773 of 8,928 v32 references and 7,679 of 9,192 v37 references. This is an angular approximation, not an exact visibility test. These remain training data, not independent generalization evidence.

V49 failed after 8,480 verification transitions: a predicted neural reference fell outside the grid and caused an index error. The failure and its records are retained; it added no training. V50 rejects such references before converting them to indices. It reached 1/8 goals, without collisions and with seven timeouts, after 28,480 transitions.

V51 geometric fitting mistook groups of boxes for a complete wall. A surface-coverage check was added to v52; eight geometry tests now identify the first wall when observable. These are geometry tests with synthetic inputs, without brain or flight, separate from navigation checks. Premature search termination was also corrected: the route ended up to 0.96 meters before its reference. V53 released a stored opening after crossing it. V51, v52, and v53 still reached none of eight goals, with zero collisions and eight timeouts each, over 29,496 transitions per variant. Correcting these errors was insufficient to resolve flight.

V54 retains only the observed map and goal, without a learned opening proposal. It uses the stable reader, permits escape from a precautionary occupied margin, searches for the exact final cell, and maintains an open frontier upon reaching the search limit. It reached 3/8 goals without collisions and with five timeouts after 28,480 transitions. V55 checks advancement past reached references and brakes in the requested three-dimensional direction, retaining altitude control during turns. It reached 8/8 in optimization and 13/16 in a frozen prospective check; see the [v55 report](observed-map-v55-results.md). V41–v54 and the first v55 check are diagnostics on reused optimization maps, with zero new physical training and zero weight changes. Protected checkpoint and alias hashes match at the close of completed batches.

The [resolution history](../NAVIGATION_RESOLUTION.md) brings these attempts together and explains the transition to operational planner v55 without attributing its performance to the learned policy.
