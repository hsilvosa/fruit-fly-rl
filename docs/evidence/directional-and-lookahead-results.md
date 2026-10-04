# Directional attention and look-ahead results

The directional v9 correction completed 32,768 new autonomous training transitions. Its two student fragments recorded zero arrivals, 36 then 31 collisions and no timeouts. Supervised losses were finite and checkpoint reloading preserved tensors and same-device actions. The eight reused development rooms recorded 0/8 arrivals, eight collisions and no timeouts. One flight progressed farther through the room, but it still collided; this is not successful navigation.

The look-ahead v10 correction completed 163,840 new physical transitions: 131,072 under the training teacher and 32,768 under the student. The teacher recorded 35 arrivals without collisions or timeouts. The student recorded zero arrivals, 30 then 12 collisions and no terminal timeouts in its two fragments. All 6,144 supervised updates reported finite losses and same-device reload checks passed.

Three diagnostic development candidates used the same eight previously reused rooms:

| Candidate | Goals | Collisions | Timeouts |
| --- | ---: | ---: | ---: |
| Look-ahead v10 final checkpoint | 0/8 | 0 | 8 |
| Look-ahead v10 teacher-only checkpoint | 0/8 | 8 | 0 |
| Teacher-only checkpoint with sparse directional pooling | 0/8 | 8 | 0 |

The sparse candidate changed inference pooling while retaining identical learned tensors. It added no physical training transitions or optimizer updates. These diagnostic comparisons guide development; they are not independent final evidence or a paired final test. Fewer collisions in the final v10 checkpoint were accompanied by exhausted deadlines, not arrivals.

Completed substantive training expenditure through v10 is 1,464,320 transitions. Reserved final tests and original aliases remain preserved. A final bounded distance-only visual correction is pending within the user's two-hour limit. It tests whether directly using approach-speed planes encourages a shortcut in visual direction prediction; the shortcut is a hypothesis, not an established cause.
