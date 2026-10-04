# Passage-mastery v2 results

Completed on 2026-10-03. Exactly 524,288 optimizer transitions were added across four fresh runs, 131,072 per method and initialization seed. Each run used eight rounds of 16,384 transitions. The 128-transition implementation smoke is separate. Total experiment time, including initialization, practice, validation and final assessment, was 60.4 minutes.

The target is `gate-long`: a 24 by 12 by 10 room with one partition, a 4.5 by 4 opening and four collision boxes. This is a simpler task than the historical large-room experiment. Its success does not demonstrate navigation in multiple narrow passages or biological benefits.

## Shared target validation

| Method | Seed | Added transitions | Selected lifetime transitions | Goals / 32 | Collisions | Timeouts |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 42 | 131,072 | 114,688 | 30/32 | 0 | 2 |
| baseline | 73 | 131,072 | 114,688 | 25/32 | 6 | 1 |
| curriculum | 42 | 131,072 | 81,920 | 29/32 | 2 | 1 |
| curriculum | 73 | 131,072 | 114,688 | 1/32 | 0 | 31 |

Validation selected baseline seed 42, round seven, with 114,688 lifetime transitions. The baseline arm ranked ahead of the curriculum under the frozen rule. The curriculum was not final-tested as a paired alternative.

## Training-practice gates

Each entry below gives goal counts out of eight in the two distinct practice batches. Practice adapts training and is not independent generalization evidence. Stages refer to the profile checked before a possible advance.

| Round | Added transitions to date | Seed 42 stage | Seed 42 goals A / B | Gate passed | Seed 73 stage | Seed 73 goals A / B | Gate passed |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| 1 | 16,384 | gate-near | 0 / 0 | no | gate-near | 0 / 0 | no |
| 2 | 32,768 | gate-near | 0 / 1 | no | gate-near | 0 / 0 | no |
| 3 | 49,152 | gate-near | 0 / 0 | no | gate-near | 0 / 0 | no |
| 4 | 65,536 | gate-near | 3 / 5 | no | gate-near | 0 / 1 | no |
| 5 | 81,920 | gate-near | 7 / 7 | yes | gate-near | 0 / 1 | no |
| 6 | 98,304 | gate-long | 5 / 7 | no | gate-near | 3 / 3 | no |
| 7 | 114,688 | gate-long | 5 / 7 | no | gate-near | 4 / 4 | no |
| 8 | 131,072 | gate-long | 0 / 4 | no | gate-near | 4 / 5 | no |

Seed 42 advanced from stage zero to stage one after round five (81,920 transitions), when both batches reached 7/8. It subsequently failed the gate-long checks, finishing with 0/8 and 4/8. Seed 73 never advanced from gate-near, finishing with 4/8 and 5/8. Baseline always trained on gate-long and had no practice-controlled progression. These outcomes do not establish that the curriculum improved learning.

## One reserved final assessment

The frozen baseline winner reached **61/64 goals (95.3%)**, with **zero collisions and three timeouts**. The Wilson 95% success interval is **87.1–98.4%**. Successful arrivals averaged 14.53 simulated seconds; mean flown/feasible-reference length was 1.092. The reference is approximate geometry, not an optimal executable trajectory.

The same-interface untrained control reached **0/64**, with zero collisions and 64 timeouts; Wilson 95% interval **0.0–5.7%**. The selected controller and control are the only policies assessed on this final pool, which is now consumed. There is no paired final comparison of the two training methods. The result supports success on this single-opening distribution; larger-map and broader seed robustness remain unestablished.

## Integrity and preservation

Both initializations had zero transitions, zero optimizer updates and empty optimizer state. All 32 round loss reports were finite. Frozen configuration, suite, source snapshot and selected checkpoint hashes passed the read-only audit. The full fixed MaleCNS graph was retained. No new policy evaluation or optimization was performed while collecting these results.

Selected checkpoint SHA256: `4745908c1ffa491bb8de447847c6ce2e42c3595ef9fe19c0a10f3dc1093e614d`.

All six original launcher files retained their before/after hashes; their actual current bytes also match. No alias was promoted.

| File | SHA256 before | SHA256 after |
| --- | --- | --- |
| dense-flight-policy.json | `0ca02c89a6e17d16cfd949a56d46909cdf8638758a4536953e3e3d8ecef5e2db` | `0ca02c89a6e17d16cfd949a56d46909cdf8638758a4536953e3e3d8ecef5e2db` |
| dense-flight-policy.zip | `085963d6e95b2a25647e3e6dd7ad2dc61f8f3c61bbfaaf3ce0db2c067a287d66` | `085963d6e95b2a25647e3e6dd7ad2dc61f8f3c61bbfaaf3ce0db2c067a287d66` |
| dense-policy.json | `88c3e01eb7926dedfc1679f23b4a92c3783384782ad4203013afa8d38fe4e3c3` | `88c3e01eb7926dedfc1679f23b4a92c3783384782ad4203013afa8d38fe4e3c3` |
| dense-policy.zip | `db0839a921ae8775bbad9dbea62c28ab3752d33dad0e8edcfa72c7dc1318cab6` | `db0839a921ae8775bbad9dbea62c28ab3752d33dad0e8edcfa72c7dc1318cab6` |
| navigation-policy.json | `aa47f7ef830c491958a16bd121497c703d689b2a9717c566ad9888de5815460f` | `aa47f7ef830c491958a16bd121497c703d689b2a9717c566ad9888de5815460f` |
| navigation-policy.zip | `2aa3469b6c56fa7f29c56399a7737b29c1870432e005714782d8efe23bf6be01` | `2aa3469b6c56fa7f29c56399a7737b29c1870432e005714782d8efe23bf6be01` |

Full records and the read-only audit are retained locally under ignored `private/passage-mastery-v2-results/`. Source logs and checkpoints remain under `runs/training/passage-mastery-v2/`. See [aggregate results](../RESULTS.md) and [protocol](../GEOMETRY_CURRICULUM.md).
