# Maze experiment wrap-up

October 7, 2026. New maze candidates and the planned fresh suite are deferred at the user's request. The final earlier-map regression check has finished. The project is not claiming that arbitrary maze navigation or independent generalization is solved.

## Measured progress

The operational large-room planner remains planner-1.3-exp.9: six retained goals and eight fresh development goals without collisions or timeouts. Maze development is a separate result.

| Candidate | Goals on the inspected eight-map pool | Collisions | Decision |
| --- | ---: | ---: | --- |
| Exp.26, extended opening range | 6/8 | 0 | Missed the gate |
| Exp.27, progress-only wall scan | 4/8 | 0 | Regressed |
| Exp.28, revisit gate | 6/8 | 0 | Preserved six successes, missed gate |
| Exp.29, coverage-directed scan | 6/8 | 0 | Improved one search trajectory, missed gate |
| Exp.30, unreachable crossing release | 5/8 | 0 | Regressed |
| Exp.31, completed-surface consensus | 6/8 | 0 | Fixed one timeout but regressed one success |
| Exp.32, terminal-distance consensus | 7/8 | 0 | Passed retained gate and preserved all six exp.29 successes |

Exp.32 combines exp.29's revisit/coverage recovery with observation-based crossing-normal consensus during the final quarter of decoded goal distance. It excludes exp.30's rejected release. Seed 17000007 reaches its goal at 6,018 steps; seed 17000002 remains a timeout at 12.222 units from the goal. All six preceding successful arrival step counts are preserved.

The retained check used the full 167,184-neuron, 25,583,622-edge connectome, 54,016 physical transitions and 654.92 seconds. Frozen runtime sources and protected checkpoint aliases match their before-run hashes. No training, optimizer update or reserved final test was performed.

## Remaining evidence

The earlier-map regression check completed at **7/8 goals, zero collisions and one timeout**, preserving all seven prior exp.25 successes. Seed 16000004 remains a timeout. The complete graph executed 56,048 physical transitions in 742.18 seconds; frozen sources and protected aliases match. No training or reserved test was performed. A fresh suite has not started and is explicitly deferred. The new candidate's rendering and control checks have not been completed. Therefore exp.32 is an experimental candidate, not a promoted reliable maze solution. The default maze launcher remains exp.11.

## View the candidate explicitly

From the repository directory:

```powershell
.\.conda\python.exe -s -m fly_rl --device cuda demo --controller observed-map --controller-version planner-1.3-exp.32 --map-profile maze --seed 17000007 --brain-view
```

This selects the candidate for live autonomous execution on a known successful development seed. It does not replay a saved flight or train weights. The known seed is not independent evaluation evidence. Existing camera, pause, reset and speed controls apply.

## Next work

Keep the completed maze evidence frozen. Resume fresh maze verification only with new authorization. The architectural stage has six revised original designs and 21 situations with geometry and input-contract checks; complete full-connectome GPU flights and a usable architectural launcher remain to be implemented. These designs are not reconstructions of actual buildings or streets.

The [detailed development history](../MAZE_NAVIGATION.md) contains the hypotheses, regressions and acceptance criteria.
