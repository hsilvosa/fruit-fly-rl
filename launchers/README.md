# Launchers

Windows launchers for the live viewer. Each demo is a pair: a `.cmd` wrapper that starts PowerShell explicitly (so a `.ps1` file association cannot open an editor) and the `.ps1` script that sets the repository root, picks the controller and calls `python -m fly_rl demo`. Run them from the repository root, for example `.\launchers\current\launch-observed-map.cmd`, and pass any extra viewer arguments after the name (`--speed 4`, `--seed 370001`, `--record-brain`; see [COMMANDS.md](../docs/operations/COMMANDS.md)). The environment installer stays at the repository root as [`setup.ps1`](../setup.ps1).

Viewing never starts training and never changes weights. The launchers are numbered in the order in which they were created, which is the order of the project's iterations ([project history](../docs/overview/PROJECT_HISTORY.md)).

## Current (need only the prepared data, no checkpoint)

| Order | Launcher | What it opens | Iteration |
| --- | --- | --- | --- |
| 5 | [`current/launch-observed-map`](current/launch-observed-map.cmd) | The explicit observed-map planner in the original large room, planner-1.0 by default (`--controller-version 1.2` selects the dual-readout version). This is the demo to start with | 6 |
| 6 | [`current/launch-large`](current/launch-large.cmd) | Frozen planner-1.3-exp.9 in `large`, verified on six retained and eight fresh rooms | 7 |
| 7 | [`current/launch-maze`](current/launch-maze.cmd) | Experimental planner-1.3-exp.11 in `maze`: two retained goals, five of eight fresh development goals | 7 |
| 8 | [`current/launch-architecture`](current/launch-architecture.cmd) | The six architectural scenes with the explicit planner (`N` changes situation, `G` changes scene; `--architecture-scene NAME --situation K` selects one) | 8 |

These four compute live sensors, connectome activity and planner actions. None of them is a recording of a successful flight, and the planner is a reference, not a learned result ([planner documentation](../docs/planner/PLANNER_DEVELOPMENT.md)).

## Historical (learned policies; need local checkpoints that are not shipped)

| Order | Launcher | What it opens | Iteration |
| --- | --- | --- | --- |
| 1 | [`historical/launch-demo`](historical/launch-demo.cmd) | The generic demo. It opens the selected small-room navigation policy (`runs/navigation-policy.zip`) when it exists, or an untrained controller with `--untrained`. The other historical launchers call it | 2 |
| 2 | [`historical/launch-flight`](historical/launch-flight.cmd) | The coordinated-flight demo with the selected `flight-v1` policy, or an untrained controller until it exists | 2 |
| 3 | [`historical/launch-dense`](historical/launch-dense.cmd) | The dense-room demo with the original coordinated dense policy (`runs/dense-flight-policy.zip`), falling back to older policies; reports a missing-model error when no candidate exists | 3 |
| 4 | [`historical/launch-panorama`](historical/launch-panorama.ps1) | The experimental panoramic controller in an original large room, from the local demo manifest `runs/latest-large-demo.json` with a checksum check (a `.ps1` only, no wrapper) | 5 |

The order is by creation in the repository history: the demo, dense and flight launchers were committed together, so their relative order inside Iterations 2 and 3 is by the controllers they open, from the small room to the coordinated dense room. The trained weights these launchers look for are local artifacts (the folder `runs/` is ignored by git), so on a fresh clone they report that no model is available. The learned results of the project are evaluated with the scripts in [`scripts/`](../scripts/README.md), not with these viewers; to reproduce them see [REPRODUCE.md](../docs/operations/REPRODUCE.md).
