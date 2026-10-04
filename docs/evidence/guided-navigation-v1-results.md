# Guided initialization v1: results

Completed on 2026-10-04 with 40,960 added transitions, exhausting the existing cumulative budget of 524,288. Final autonomous validation reached 0/8 goals, with eight collisions and zero timeouts. The navigation problem remains unresolved. No new checkpoint was promoted or reserved final test consumed.

The teacher completed eight optimization episodes with no collisions during 24,576 teacher-action transitions. A subsequent 8,192-transition mixture used 6,567 teacher actions and 1,625 student actions, finishing no episodes. These are guided training outcomes, not autonomous student success. The 8,192 PPO-only transitions then finished 24 collisions and no goals or timeouts. Improving imitation error did not establish successful closed-loop navigation.

The actor's mean loss over its final 100 initial-fit minibatches was 0.003863; the later fit was 0.003995. All recorded supervised and PPO losses were finite, and checkpoint reload matched deterministic predictions. Actual supervised update counts were 2,048 actor, 512 further actor and 512 critic updates. They reused the collected records and are distinct from environment-transition counts.

The full graph retained 167,184 neurons and 25,583,622 edges. Ordinary final validation used the standard FlightWorld, original large geometry and sensors-v3, with no teacher or route reward. The eight existing development validation layouts had already informed earlier development, so these outcomes are not an independent final test. Wilson 95% success interval for 0/8 is approximately 0-32.4%.

All six original launcher aliases and the warm source checkpoint matched their frozen hashes after completion. Detailed local hashes and records are in private/guided-navigation-v1-audit.json and runs/training/guided-navigation-v1/status.json. The new [perception diagnosis](visible-fan-v5.md) demonstrates that early geometric teacher labels can conflict under identical short-range observations; this does not prove a sole cause for every navigation failure.
