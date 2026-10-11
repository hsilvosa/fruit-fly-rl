# Experiment log

One row per iteration, in order. Protocols were committed before the runs. Results documents hold the tables. Last updated October 10, 2026. The live status is in [ROADMAP.md](../ROADMAP.md).

| ID | Date | Question | Change | Result | Documents |
| --- | --- | --- | --- | --- | --- |
| R0 | Oct 7 | Which checkpoints produced the 70 to 80% medium-room results? | Read-only recovery, hash check, replay | All winners recovered. Replay matched per episode. Reference scores 0/16 on `large` and `passages` | [HISTORICAL_REFERENCE.md](HISTORICAL_REFERENCE.md) |
| T1 | Oct 8 | Does the retained 48/64 policy learn `passages`? | 65,536 transitions, retained and fresh arms | 0/32 on passages. Retained medium 24/32. Fresh 11/32 | [protocol](REFERENCE_TRANSFER_PROTOCOL.md), [results](REFERENCE_TRANSFER_RESULTS.md) |
| F1 | Oct 8 | Why does it fail on `passages`? | Evaluation-only failure classification | Collisions into partitions and hovering near them. No episode crossed all partitions | [PASSAGES_FAILURE_CLASSIFICATION.md](PASSAGES_FAILURE_CLASSIFICATION.md) |
| T2 | Oct 8 | Do a route-progress reward or more steps help? | Two arms | No. Passages 0/32. Medium fell to 17/32 | [protocol](REFERENCE_TRANSFER_PROTOCOL_2.md), [results](REFERENCE_TRANSFER_RESULTS_2.md) |
| T3 | Oct 8 | Does training on graded gates work? | 50/64 policy, gates plus 25% medium | First signal: gate-long 32/32, passages-wide 4/16. Medium 19/32, rejected | [protocol](REFERENCE_TRANSFER_PROTOCOL_3.md), [results](REFERENCE_TRANSFER_RESULTS_3.md) |
| T4 | Oct 8 | Does 50% medium recover the medium rooms? | Medium share 50% | Yes: medium 24/32, gates 32/32. Positive | [protocol](REFERENCE_TRANSFER_PROTOCOL_4.md), [results](REFERENCE_TRANSFER_RESULTS_4.md) |
| T5 | Oct 8 | Does `passages` in the mix work? | Add `passages` | Passages-wide 26/32, passages 2/32. Not positive | [protocol](REFERENCE_TRANSFER_PROTOCOL_5.md), [results](REFERENCE_TRANSFER_RESULTS_5.md) |
| T6 | Oct 8 | Does an intermediate profile help? | Add `passages-mid` | Passages-mid 9 to 12/32. Swings of 21 episodes between checkpoints | [protocol](REFERENCE_TRANSFER_PROTOCOL_6.md), [results](REFERENCE_TRANSFER_RESULTS_6.md) |
| T7 | Oct 8 | Does mixing profiles inside each update help? | 8 simulators with different profiles | Passages-mid 15/32, passages 4/32. One episode short of positive. Selected on reported pools, optimistic | [protocol](REFERENCE_TRANSFER_PROTOCOL_7.md), [results](REFERENCE_TRANSFER_RESULTS_7.md) |
| T8 | Oct 8 | Do the gains hold with more training and two seeds? | 262,144 transitions | No. Gains lost, medium dropped at times | [protocol](REFERENCE_TRANSFER_PROTOCOL_8.md), [results](REFERENCE_TRANSFER_RESULTS_8.md) |
| C1 | Oct 8 | Free disk | Removed 84.5 GB of regenerable datasets | `runs/` from 87 GB to 1.9 GB | [RUNS_CLEANUP.md](RUNS_CLEANUP.md) |
| P9 | Oct 9 | Does a stabilized trainer keep the gains? | Pilot: one seed, 98,304 transitions | Passages-mid 21/32, passages 5/32, passages-wide fell to 12/32. A first launch with 28 parallel evaluations restarted the PC. The guard was added | [protocol](PHASE1_PILOT_PROTOCOL.md), [results](PHASE1_PILOT_RESULTS.md) |
| P10 | Oct 10 | Does the stabilized trainer meet the Phase 1 criterion? | Two seeds, four evaluations | Seed 442 stable (range 1), seed 443 not (range 18). Hardest profile not raised. Negative | [protocol](PHASE1_RUN_PROTOCOL.md), [results](PHASE1_RUN_RESULTS.md) |
| M11 | Oct 10 | Does memory help? | Two history windows, seed 442 | Long window +19 on the hard-profile sum. Short window worse | [protocol](PHASE3_SCREENING_PROTOCOL.md), [results](PHASE3_SCREENING_RESULTS.md) |
| M12 | Oct 10 | Does the long window replicate? | Seed 443 | No: +5, -9, 0 against the control | [protocol](PHASE3_REPLICATION_PROTOCOL.md), [results](PHASE3_REPLICATION_RESULTS.md) |
| V1 | Oct 10 | Is evaluation or training the noisy part? | Re-evaluate the pilot checkpoint | Evaluation repeats within one episode. Training varies | [addendum](PHASE1_PILOT_RESULTS.md) |

| R2 | Oct 10 | Does a candidate keep the medium-room skill? | Frozen four-pool regression suite, five baselines | Historical winners 90 to 98 of 128, experiment 7 start 111, pilot candidate 104. The first per-pool rule failed two winners and was relaxed, openly | [MEDIUM_REGRESSION_SUITE.md](MEDIUM_REGRESSION_SUITE.md) |

| R3 | Oct 10 | Can maps be drawn at random with a held-out region? | Sampler, difficulty controller, level B region | 14 tests pass. No generation failure in 600 resets. Reset takes at most 0.05 s | [MAP_SAMPLER.md](MAP_SAMPLER.md) |

| R4 | Oct 10 | Which family is never trained on? | Sealed level B region and level C scenes; architectural world for older sensor contracts | 5 tests pass. Geometry equals the protected world | [HELD_OUT_SPEC.md](HELD_OUT_SPEC.md) |

| R1 | Oct 10 | How much does one recipe vary between training runs? | Five seeds of the pilot recipe, plus a 64-episode confirmation | Passages-wide range 11 of 32. Pilot checkpoint confirmed as a real outlier: 58% passages-mid and 27% passages on a fresh pool | [protocol](VARIANCE_STUDY_PROTOCOL.md), [results](VARIANCE_STUDY_RESULTS.md) |

| R5 | Oct 11 | Does training on random maps help? | Random-map mix, three seeds, against five control runs | Negative by the rule (+1.1 and +0.6 of 64). The difficulty controller stayed at 0.2 to 0.25. Run 601 is an outlier (passages-wide 32/32) | [protocol](RANDOM_DISTRIBUTION_PROTOCOL.md), [results](RANDOM_DISTRIBUTION_RESULTS.md) |
| Audit | Oct 11 | Is hard-map exposure the gap? Does the reward favor hovering? | Controller windows from R5; discounted returns on certified routes | R5 randomized simulators finished 64 to 127 episodes in a whole run. An ideal route follower beats hovering at every point (refutes the reward-hover idea) | [LIGHT_AUDIT_RESULTS.md](LIGHT_AUDIT_RESULTS.md) |
| Eval | Oct 11 | Is 601 a real candidate? Is the pilot hover a fixed point? | Fresh-pool evaluation of 601 and stochastic sampling | 601 holds medium 92, wide 86, mid 55, passages 14 percent. Pilot wide 14 to 55 of 64 when sampled; not general | [COMMITTEE_EVAL_RESULTS.md](COMMITTEE_EVAL_RESULTS.md) |
| Anatomy | Oct 11 | Are passages collisions edge clips or navigation errors? | Collision anatomy on 4 evaluations of 64 episodes | Collisions end 1.5 to 3.5 m off the route, around mid-route; edge clips are rare. Does not separate exposure from information | [COLLISION_ANATOMY.md](COLLISION_ANATOMY.md) |
| Probe | Oct 11 | Do the 256 features carry the direction to the next opening? | Ridge and MLP probes on rollouts of run 601 and the pilot | Features equal raw sensors (within 5 degrees) but decode the route direction only to 45 to 53 degrees on hard samples. Readout is not the lever; sensors or memory are | [FEATURE_PROBE.md](FEATURE_PROBE.md) |
| Waypoint | Oct 11 | Is missing route information the limit? | Privileged waypoint input vs zero-input control, two seeds each, 262k transitions | Partial by the rule (passages 37.5 vs 11 of 64; threshold 40). Information is a major limit; exact information still leaves passages below the gate | [protocol](WAYPOINT_DIAGNOSTIC_PROTOCOL.md), [results](WAYPOINT_DIAGNOSTIC_RESULTS.md) |
| Sensing | Oct 11 | Do history or longer rays carry the route direction? | Probes on rollouts and on 700 synthetic maps | With enough maps the 8 m rays already decode the direction to 34 degrees (hard subset); 24 m rays reach 28. Rollout probes were too small. Points to a learning problem, not a sensor limit, for passages | [SENSING_PROBES.md](SENSING_PROBES.md) |

Planned next: R6 in [ROADMAP.md](../ROADMAP.md#5-actions-ready-to-start).
