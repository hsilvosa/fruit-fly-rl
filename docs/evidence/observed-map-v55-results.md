# Observed neuronal map v55

The frozen version completed eight of eight reused optimization maps, without collisions or timeouts. In a prospective development check of 16 new rooms, it completed 13 without collisions and with three timeouts: 81.25% success, with a 95% Wilson interval of 57.0 to 93.4%. This is a small sample from the `large` generator, not a guarantee about arbitrary maps or the reserved final test.

This is explicit geometric planning from full-connectome activity, with flight control and no learned movement weights. It is not PPO success and does not establish a biological advantage. The best learned student in this batch remains at 3/8 on reused optimization maps; reliable learning remains unresolved.

## Method and protocol

The controller reconstructs distances, the goal, and motion from previous and current neural states, builds occupancy and odometry, and searches for a route. It receives no true poses, boxes, seeds, or certified routes. It knows the 48 x 48 x 16 room contract and has the observed synthetic goal, as earlier policies did. It retains 167,184 neurons and 25,583,622 recurrent connections. The reader cancels recurrence in the 269 base channels and retains 5% in panoramas: an artificial transformation documented in [mathematics](../MATHEMATICS.md).

V55 was selected using eight optimization maps. Before development began, code and 16 new seeds, 8500000–8500015, were frozen. The controller was not adjusted between those flights. Failures are timeouts on 8500011, 8500012, and 8500013. The remaining 13 finished within 0.45 meters of the goal, according to the original physical condition. Partial progress is not an arrival.

| Batch | Verification transitions | Arrivals | Collisions | Timeouts |
| --- | ---: | ---: | ---: | ---: |
| Reused optimization | 25,168 | 8/8 | 0 | 0 |
| Prospective development | 56,544 | 13/16 | 0 | 3 |

These two batches added no training transitions or weight updates. The physical counter includes the entire batch, including members that had finished and continued advancing with zero actions. No reserved set was consumed, and no aliases were promoted. Plans, frozen code, initial audit geometry, trajectories, and per-episode results are retained in local records. That audit geometry is not supplied to the controller.

Corrected blockages included a map margin enclosing the start, a search ending before its reference, following already reached cells, and frontal braking preventing ascent or descent. Vertical control is retained during turns. Search has an expansion limit and can select insufficient detours; the three development timeouts show that limitation.

## Alias preservation

The following SHA-256 hashes match before and after. Protected source and experimental checkpoints were also verified. No original alias was overwritten.

| File | SHA-256 before and after |
| --- | --- |
| `runs/dense-flight-policy.json` | `0ca02c89a6e17d16cfd949a56d46909cdf8638758a4536953e3e3d8ecef5e2db` |
| `runs/dense-flight-policy.zip` | `085963d6e95b2a25647e3e6dd7ad2dc61f8f3c61bbfaaf3ce0db2c067a287d66` |
| `runs/dense-policy.json` | `88c3e01eb7926dedfc1679f23b4a92c3783384782ad4203013afa8d38fe4e3c3` |
| `runs/dense-policy.zip` | `db0839a921ae8775bbad9dbea62c28ab3752d33dad0e8edcfa72c7dc1318cab6` |
| `runs/navigation-policy.json` | `aa47f7ef830c491958a16bd121497c703d689b2a9717c566ad9888de5815460f` |
| `runs/navigation-policy.zip` | `2aa3469b6c56fa7f29c56399a7737b29c1870432e005714782d8efe23bf6be01` |

## Demo and limits

`launch-observed-map.cmd` opens this version with a separate brain window. It loads no PPO checkpoint and starts no training. The viewer identifies the planner, resets map and odometry on reset, new room, and episode end, and archives specification and code alongside states, actions, and optional activity. Replay reproduces saved states without running the brain or controller. Gradient sensitivity is marked unavailable for this algorithm; anatomical points show actual modeled activity.

Two short 40-step starts verified controls and closing. Room and brain screenshots were inspected, and the flight archive passed its audit without errors or warnings. These 80 steps are verification, not additional navigation or training. The interface retains Shift to accelerate simulated time. Current scope is `large` with coordinated dynamics; it is not extrapolated to `maze` or other sizes.

The complete viewer flight reached the goal of optimization map 370000 in 2,857 steps without a collision. It then automatically reset the episode and controller memory. It closed after 3,200 physical verification steps; the full archive passed audit without errors or warnings. This repetition of a known map is not counted as another independent development goal. The complete suite passed 265 tests, and the Windows launcher responded correctly to `--help`.

The [resolution report](../NAVIGATION_RESOLUTION.md) details the problem, failed attempts, retained corrections, and limits of this solution.
