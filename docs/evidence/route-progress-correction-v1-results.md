# Reward-only correction results

Completed on 2026-10-04 with 32,768 added transitions, all on unchanged original-large optimization layouts. Final development validation: 0/8 goals, one collision and seven timeouts; mean final distance 37.126, mean idle fraction 0.205. Wilson 95% success interval: approximately 0-32.4%. The navigation problem remains unresolved.

Training finished ten episodes: zero goals, three collisions and seven timeouts. There were 276 route-field fallback transitions out of 32,768 (including collisions). All four recorded PPO loss reports were finite, and live episodes continued between chunks. The opt-in reward corrected the demonstrated local detour penalty but did not produce successful student navigation within this experiment.

The training objective used privileged obstacle geometry only for rewards; ordinary validation used unchanged sensing and no route field. This is a stronger training objective than the former direct-distance reward. No biological effect is established. The certificate itself is not an optimal or dynamically executable route.

The original six launcher aliases and warm source were preserved. No reserved final test was evaluated or checkpoint promoted. Cumulative substantive use is 483,328 of 524,288; 40,960 transitions remain. The next [guided initialization protocol](guided-navigation-v1-plan.md) supplies successful training trajectories, with its teacher removed at inference.
