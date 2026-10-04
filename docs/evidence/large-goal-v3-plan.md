# Large-room adaptation

This run was interrupted on 2026-10-03 after 98,304 persisted added transitions in the first seed. Each 8,192-transition round recreated eight environments, allowing only 1,024 decisions per fly before discarding incomplete episodes. The minimum timeout is 1,200 decisions, so round boundaries systematically prevented timeout penalties on unfinished episodes. The original process was stopped, existing checkpoints and aliases were preserved, and the reserved final test was not evaluated. The two completed target validation checks both reached 0/32 goals. These results do not establish the requested large-room success. Episode continuity must be corrected before another run.

The requested goal is at least 80% success on the original `large` profile: a 48 by 48 by 16 room with 112 collision boxes and five partitions. The successful single-wall experiment does not establish this result.

This bounded experiment adds 524,288 training transitions, divided between training seeds 42 and 73. Each run starts from the same trained single-wall checkpoint and its optimizer state, then receives 262,144 transitions in 32 rounds. These are two adaptation runs with different training random seeds, rather than two fresh policy initializations.

The ordered stages are `gate-near`, `gate-long`, `gate-two`, `passages-wide`, `large-wide`, `large-narrow`, and `large`. Both batches of eight withheld training-practice episodes must achieve seven goals before advancing a stage. Practice adapts training and is not independent generalization evidence. The final stage retains the original large geometry and obstacle count.

There are 128 frozen training seeds, with 16 reserved for practice, 32 validation seeds, and 64 final-test seeds. All earlier suites are excluded during preparation. The large target is validated every fourth training round and at the last round. Selection uses validation success, collisions, and ending distance. The final pool is accessed only if the selected policy achieves at least 85% validation success. One frozen winner and an untrained control are then assessed through the existing final-test protocol. The 80% goal requires at least 52 successes in 64 final episodes; the Wilson confidence interval will also be reported.

The full annotated MaleCNS graph remains in use. No navigation advantage from biological wiring is claimed. Original policy aliases and the warm-start checkpoint are preserved and checked with SHA-256 hashes.

Preparation checks passed 44 targeted tests. A separate 128-transition inference check verifies checkpoint transfer and finite full-connectome observations without optimization. Configuration, process identity, inference evidence, logs, and checkpoints are retained locally. Completion and navigation performance remain unproven until the recorded experiment finishes.
