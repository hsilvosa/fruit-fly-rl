# Panoramic v7 results

Training completed all 98,304 authorized physical transitions: 65,536 teacher-controlled and 32,768 student-controlled. The 12,288 supervised updates reported finite losses. The full graph contained 167,184 annotated neurons and 25,583,622 connections. No PPO update or reserved final test was performed.

The teacher recorded 16 arrivals, no collisions and no timeouts. The student's two fragments recorded zero arrivals and 68 then nine collisions, with no timeouts. These are completed outcomes within fixed transition fragments; unfinished flights are not included as terminal outcomes.

The final checkpoint passed tensor equality, exact same-device prediction reload and the declared CPU tolerance. The run then failed while closing its report: a protected checkpoint key used Windows backslashes while the lookup used forward slashes. This did not undo training or corrupt the saved checkpoint. Its original development evaluation result was not persisted. The original pre-recovery status and error are retained privately; the run is marked failed at report finalization rather than silently relabeled successful.

A separately recorded recovery evaluation used the same eight reused development maps, with CUDA sensor calculations and no optimization. It recorded zero arrivals, eight collisions and no timeouts. This repeated development measurement is not an independent final test. It consumed no new training transitions or reserved pool.

The pre-integration audit verified all frozen runtime sources, all protected source artifacts and all six original launcher aliases. The path lookup is now normalized and covered by a regression test. Navigation remains unresolved.
