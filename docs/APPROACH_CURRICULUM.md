# Terminal-approach curriculum

This training-only reset schedule tests whether practice near the goal helps terminal approach while preserving the ordinary success condition.

## Intervention

Only training resets change. Dense room geometry and its target still come from the frozen training layouts. Some episodes start 0.7–3.0 simulation units from that target. Candidate directions are sampled from normalized independent Gaussian vectors and distances uniformly from the declared interval. The position must remain inside the room with body radius plus 0.02 clearance, and its direct segment to the target must avoid every equally inflated obstacle box. After 64 unsuccessful proposals, the episode uses the ordinary start.

The curriculum probability is

$$p(n)=0.5\max(0,1-2n/B),$$

where $n$ counts curriculum-arm training transitions across all vector slots and $B$ is that seed's complete transition budget. It starts at 50%, reaches zero halfway through the budget, and remains zero afterward. Resets use the current probability; a running episode is not moved when the probability changes. The schedule continues across rounds using a declared offset instead of restarting. Reset statistics include initialization resets and record ordinary, near, and fallback counts separately.

The goal, success radius, episode limit, collision geometry, reward equation, actions, sensor v3 interface, dynamics, brain wiring, projection and pooled features are unchanged. No reference route is supplied to the policy. The short direct reference retained by a near episode describes its training geometry only. Standard evaluation creates ordinary FlightWorld instances and never installs this curriculum.

## Protocol and measured outcomes

Use a new suite, explicit transition budget and independent initialization seeds for each comparison. Select checkpoints and methods using validation only; freeze the winner before one final assessment. Include the initial controller in selection and retain unsuccessful results. A completed optimizer budget does not guarantee improved navigation.

The comparison uses matched fresh v3 policies, a normal-training control, seeds 42 and 73, two rounds and 131,072 transitions per method and seed. Only the validation winner and untrained control are final-tested; this is not a paired final comparison of methods.

See [Results](RESULTS.md) for aggregate validation, final counts, uncertainty and limits, [Mathematics](MATHEMATICS.md) for optimization, and [Commands](COMMANDS.md) for execution. Detailed trajectories, decisions, launch records and original machine evidence remain local and private. No biological advantage is inferred from navigation performance.
