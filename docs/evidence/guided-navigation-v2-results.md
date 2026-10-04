# Guided navigation v2: verified results

Completed on 2026-10-04 after 65,536 added environment transitions. Cumulative substantive use is 589,824, the approved cap. Autonomous development validation on the original large rooms reached 0/8 goals, four collisions and four timeouts. Navigation remains unresolved. No checkpoint was promoted or reserved final test consumed.

## Training and autonomous outcomes

| Phase | Transitions | Actions | Finished goals | Collisions | Timeouts |
| --- | ---: | --- | ---: | ---: | ---: |
| Teacher collection | 32,768 | Teacher only | 8 | 0 | 0 |
| Corrective collection 1 | 8,192 | Student only | 0 | 23 | 0 |
| Corrective collection 2 | 8,192 | Student only | 0 | 6 | 0 |
| PPO refinement | 16,384 | Student policy | 0 | 10 | 0 |

Teacher arrivals are privileged-supervision training outcomes, not autonomous student success. Corrective rounds execute only student actions and retain teacher labels for fitting. Episode counts include finished flights only, not unfinished suffixes or forced reset cuts.

The actor completed 3,072 initial updates and two corrective fits of 768 updates each; critic initialization used 768 updates. Mean final-100 losses were 0.003333, 0.024477 and 0.031604 for actor fits, and 362.444093 for the critic. All recorded supervised and PPO loss values were finite. The final logged PPO approximate KL was 0.159238 despite target KL 0.01; finiteness does not establish optimization quality. Deterministic predictions matched after checkpoint reload.

## Validation scope

The full graph retained 167,184 neurons and 25,583,622 edges. The controller used sensors-v5 and temporal connectome features; no route or teacher was supplied during validation. All eight layouts are reused development validation seeds 430000-430007, not an independent final pool. Observed success is 0%; the descriptive Wilson 95% interval is approximately 0-32.4% and does not account for development reuse. Mean ending distance was 37.169201; mean idle fraction was 0.486032. This run does not demonstrate navigation improvement or a biological advantage.

The complete run took 43.81 minutes including initialization, fitting and 10.50 minutes of validation. This is not a pure training throughput or GPU-utilization measurement.

## Integrity

SHA-256 checks independently confirmed all six original launcher aliases, the warm source and frozen implementation match their pre-run hashes. The source ZIP hash is `0feaf5702386e09e48ac1ffee026308cf444c8ffac47390e7f4c7c79ee13cb0e`. The final experiment ZIP hash is `34e138c6d640c1103bc13a157449f04d7d226fd285c76d8040d994b07342f3db`. Detailed before/after alias hashes and retained numerical evidence are in the local private/guided-navigation-v2-audit.json; runtime status is runs/training/guided-navigation-v2/status.json. No reserved final test was evaluated and no automatic alias promotion occurred.
