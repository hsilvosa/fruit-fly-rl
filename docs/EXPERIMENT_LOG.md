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

Planned next: R1 to R6 in [ROADMAP.md](../ROADMAP.md#5-actions-ready-to-start).
