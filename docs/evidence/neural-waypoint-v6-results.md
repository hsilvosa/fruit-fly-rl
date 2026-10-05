# Neural waypoint v6: results

The experiment completed 81,920 new transitions: 16,384 guided and 65,536 autonomous. It reused 98,304 earlier optimization examples and performed 6,144 supervised updates; those updates are neither additional world transitions nor PPO updates. Cumulative substantive training totals 868,352 transitions, separate from brief checks.

Autonomous validation in the eight original `large` development rooms finished with zero successes, eight collisions, and zero timeouts. Seeds 430000–430007 have been reused for diagnosis: this result is not an independent test. The reserved test was not consumed, and no launcher alias was promoted.

The four student batches recorded zero goals, with 28, 39, 30, and 25 collisions. Guided fragments retained original positions and orientations but lasted only 12.8 seconds per world and completed no goals. Autonomous flights did preserve episodes and brain state between fits. Losses were finite; this is insufficient to establish navigation.

Reload preserved every tensor and produced identical predictions on the same GPU. Maximum CPU/GPU error was 0.00000891, within the declared tolerance. The source checkpoint and six original alias files retain their hashes. Detailed hashes and results were saved in private evidence.

The [control and coverage diagnosis](neural-waypoint-v6-diagnostics.md) identifies turning and altitude errors and insufficient dense coverage in some recovery states. It does not establish that a single cause explains every collision. The next correction expands the visual field and duration of complete guided flights; it must still demonstrate autonomous success.
