# Large-map experiment pause

The user requested a pause on 2026-10-03T22:20:19.033774+00:00. The original process (PID 36976, start UTC 2026-10-03T20:54:16.8235196Z) was stopped after a saved round checkpoint, during practice.

The latest preserved checkpoint is `runs/training/large-continuous-v4/mastery-seed-42/round-23/policy.zip` with SHA-256 `0feaf5702386e09e48ac1ffee026308cf444c8ffac47390e7f4c7c79ee13cb0e`. It records 188,416 added training transitions for seed 42; seed 73 has not started. Including the earlier interrupted experiment, 286,720 added transitions are preserved. The separate smoke verification is excluded.

The latest completed target validation (round 20) reached 0/32 goals, with 2 collisions and 30 timeouts on the original large profile. These are validation results, not final-test results. The independent final test remains unused and the 80% objective is not achieved. Practice outcomes adapt training and do not establish independent generalization.

All six original alias files retain their initial hashes. Detailed hashes and pause evidence are in `private/large-continuous-v4-pause.json`. No checkpoint was modified.

The checkpoint preserves policy and optimizer state, but the stopped process's live episodes and random streams are not recoverable from it. Future continuation must explicitly record the interruption and a new continuation protocol; it cannot be described as an uninterrupted run. No training process was left running.
