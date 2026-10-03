# Generalization and routes

Separate layout pools, frozen selection and explicit geometric references make navigation measurements interpretable. They do not prove general robustness or global route optimality.

## Build independent pools

```powershell
.\.conda\python.exe -s -m fly_rl prepare-suite --output runs/suites/dense-v2.json --train-start 30000 --validation-start 40000 --test-start 50000 --exclude-suite runs/suites/dense-v1.json
```

The defaults are 256 training, 32 validation, and 64 test layouts, using the starts shown above. Each split also has a `--train-count`, `--validation-count`, or `--test-count` option. Evaluation pools are capped at 64 and training pools at 4096. Seed ranges must be nonnegative, valid, and disjoint. Existing output files cannot be overwritten.

Repeat `--exclude-suite` for every historical pool that must be excluded. The generator audits all pools in each exclusion, rejects seed reuse, and compares room/start/target/obstacle geometry without relying on heading differences to establish novelty. Novelty is certified only against the supplied exclusions. The suite records their hashes. A new filename alone is not an independence claim.

Loading now checks every layout fingerprint and duplicate geometry even when the generator source hash matches. Legacy suites containing valid geometry fingerprints remain readable. The generator itself is unchanged: these are independent rooms from the same 48-box distribution, not evidence of robustness to a new distribution.

Versioned suites include a canonical test-pool fingerprint. The local exposure registry under `runs/suites/consumed/` records test use across experiment copies. A failed final evaluation still consumes the pool; deleting a report must not restore an untouched claim. Back up this registry with the suites and experiments. This local guard is not a claim that arbitrary external scripts or deletion of the registry cannot bypass the protocol.
## Diagnose validation before learning

```powershell
.\.conda\python.exe -s -m fly_rl diagnose-validation runs/training/dense-flight-v1/experiment.json --output reports/priority-validation-failures.json
```

This reads retained validation outcomes and invokes neither a policy nor an optimizer. It classifies collisions, timeouts with frequent stopping, timeouts near the goal, and other non-arrivals. The old records do not retain collision locations or complete altitude histories, so they cannot distinguish obstacle impacts from altitude-control causes reliably. The report says this rather than inventing causal diagnoses. Final-test result files are rejected for tuning diagnostics.

The October 1 audit found 24 successes, 6 collisions of unknown location, and 2 timeouts with frequent stopping in the original selected validation record. Initial states of the new 32-room validation pool showed 21 saturated distance and 16 saturated altitude readings under sensors-v2. The final sensor value remains the previous yaw command rather than measured yaw rate. The bounded experiment deliberately preserves this trained interface and uses warm-start adaptation. A corrected interface needs explicit versioning and a separate experiment; these implementation changes do not silently reinterpret saved weights.
## Bounded adaptation and selection across seeds

```powershell
.\.conda\python.exe -s -m fly_rl train-dense --suite runs/suites/NEW-suite.json --output runs/training/NEW-seed42 --baseline runs/dense-flight-policy.zip --steps 65536 --batch 8 --rounds 2 --dynamics coordinated --training-seed 42 --no-promote --route-metrics
.\.conda\python.exe -s -m fly_rl train-dense --suite runs/suites/NEW-suite.json --output runs/training/NEW-seed73 --baseline runs/dense-flight-policy.zip --steps 65536 --batch 8 --rounds 2 --dynamics coordinated --training-seed 73 --no-promote --route-metrics
.\.conda\python.exe -s -m fly_rl select-experiment runs/training/NEW-seed42 runs/training/NEW-seed73 --output runs/training/NEW-selected
.\.conda\python.exe -s -m fly_rl final-test runs/training/NEW-selected
```

Generate a new, audited `NEW-suite.json` that excludes all previous pools before using these command templates. Choose new output directories too. The saved `dense-v2.json` test is consumed; the guards reject using it for another untouched experiment. The two adaptations each add 65,536 transitions in two rounds of 32,768. PPO sampling and environment seeds differ; graph projection remains seed 42 and both runs start from the same trained baseline. These are repeated adaptation seeds, not independently trained connectomes or independent from-scratch initializations.

Training samples only training seeds. Validation chooses the best round, including the baseline, using success, then fewer collisions, then lower final distance. `--no-promote` preserves the launcher alias while candidate experiments are compared. `select-experiment` requires distinct adaptation seeds, identical suite/dynamics, completed runs, and no final evaluation; it copies the winning validation checkpoint into a frozen bundle. Final outcomes never rank candidates.

Frozen records include checkpoint, metadata, and suite hashes, plus evaluation settings and evaluator/planner source hashes. `final-test` verifies them before reserving the test pool. The selected and untrained controllers then use the same final layouts with deterministic actions and no optimizer updates. Generic `evaluate --split test` now requires `--expose-test` and records exposure for versioned pools; use `final-test` for an independent final claim. The exposure ledger also records geometry IDs: a renamed pool or partially overlapping subset is still exposed. Candidate selection rejects globally exposed suites, including runs whose individual records do not mark a final test.
## What the route reference measures

`--route-metrics` enables a deterministic 3D visibility roadmap during evaluation. Nodes include start, target, and corners outside obstacle boxes inflated by body radius 0.16 plus clearance 0.02. Candidate segments undergo the same closed segment/AABB collision test as flight, with room-bound checks. Dijkstra chooses the shortest path among those sampled visibility edges. A clear direct line is used immediately when available.

If corner sampling cannot connect the endpoints, the generator's certified route can be returned only as a separately labeled, collision-validated fallback. A missing sampled route is reported, not called physically unreachable. Every successful reference includes points, length, clearance, method/status, version, and planner time. The reference stays in evaluation code and is never added to sensor observations or policy features.

This is a feasible geometric reference, not a global continuous-space optimum. Corner sampling and fallback paths can exceed a shorter route outside the sampled graph. Inertia, turning radius, and flight-control constraints are not modeled by the planner. Its endpoint is the goal center, while the fly arrives within 0.45 units. A flown/reference ratio below one is possible and is not proof that the policy beat an optimum.

Reports show success, collisions, timeouts, successful arrival time, traveled distance, and **successful flown length / feasible reference length**. Failed flights never enter efficient-route averages. Reference coverage and missing successful references are explicit. The original straight-line ratio remains a separate historical lower-bound comparison.

## Protocol and measured outcomes

Use a new suite, explicit transition budget and independent initialization seeds for each comparison. Select checkpoints and methods using validation only; freeze the winner before one final assessment. Include the initial controller in selection and retain unsuccessful results. A completed optimizer budget does not guarantee improved navigation.

See [Results](RESULTS.md) for aggregate validation, final counts, uncertainty and limits, [Mathematics](MATHEMATICS.md) for optimization, and [Commands](COMMANDS.md) for execution. Detailed trajectories, decisions, launch records and original machine evidence remain local and private. No biological advantage is inferred from navigation performance.
