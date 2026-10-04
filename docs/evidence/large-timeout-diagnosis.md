# Why the large-map runs timed out

Diagnosis recorded on 2026-10-04. The paused experiment is preserved. No reserved final layouts were inspected or evaluated.

## Confirmed observations

The round-23 checkpoint trained for 71,732 transitions on gate-near, 16,356 on gate-long, 9,130 on gate-two, 63,202 on passages-wide and 27,996 on large-wide. It trained for zero transitions on large-narrow and the original large target. The practice gate had not advanced that far. Reporting target validation as large-map training progress without this exposure breakdown was misleading. The 0/32 measurements remain valid transfer measurements, not evidence that the policy trained on the final task and then failed.

Round-20 validation covered the original 48 by 48 by 16 room with 112 boxes. It had 0/32 successes, 2 collisions and 30 timeouts. Mean path length was 226.27 units; mean target distance changed from 44.36 to 34.57 units. Mean idle fraction was 1.15 percent. These are existing validation results, not new tests.

A separate inference diagnostic used four optimization-layout seeds (370000 through 370003), the full 167,184-neuron, 25,583,622-edge graph and the saved round-23 policy. Each flight was capped at 1,800 decisions. Absolute heading rotation ranged from 8.64 to 16.26 turns. Three flights reached the diagnostic cap and one collided; none reached its goal. A diagnostic cap is not an environment timeout or a final evaluation. Detailed traces are preserved in private/large-timeout-traces.json.

## Learning objective mismatch

At 50 ms per decision, gamma=0.995 gives an effective discount horizon of 0.05/(1-gamma)=10 seconds. On 32 optimization layouts, the large-profile certificate averaged 118.85 units. At an illustrative constant route speed of 1.5 units/second, its arrival bonus of 20 has mean discounted value 0.00748. The corresponding value on gate-long is 4.84. This calculation uses hidden certificates only for diagnosis; the policy does not receive them. It is not a proof of a feasible flight speed or a sole cause of failure.

The world penalizes an exhausted attempt by five but labels it truncated. SB3 consequently bootstraps the terminal value. An actual PPO-rollout regression test fixes the terminal critic estimate at 10: the previous timeout reward becomes -5.02 + 0.995*10 = 4.93 in the rollout buffer. An explicit failure-terminal setting retains -5.02. Bootstrapping is correct for external sampling cuts, but a defined failed navigation attempt has different semantics. See [Gymnasium handling time limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/). A finite-horizon Markov observation also needs remaining time; the current sensor contract lacks it. This clock omission is now corrected by an explicit sensors-v4 contract. Geometry is still partially observed; a clock does not make the navigation task fully observed.

## Implemented controls and verification

The explicit train command now accepts --gamma and --timeout-as-terminal. The defaults preserve previous behavior. The requested discount is applied both to PPO and its rollout buffer, including checkpoint resumes, recorded in model metadata and results, and included in the continuous-session contract. The failure-terminal flag changes SB3 learning semantics while preserving physical timeout records for diagnostics and evaluation.

A candidate gamma of 0.9995 gives a 100-second effective horizon and an illustrative large-route bonus value of 9.06. This is a proposed experiment parameter, not a demonstrated navigation improvement. It does not provide obstacle information or fix exploration by itself.

The full suite passed 157 tests. Eight targeted tests passed, including actual SB3 timeout bootstrapping and continuous-episode regressions. A separate 128-transition smoke verification on the full graph, original large room, gamma=0.9995 and failure-terminal handling completed one PPO update with finite losses and checkpoint reload. It is verification only, not a trained navigation result. Evidence is in private/navigation-horizon-smoke.json.

## Remaining work

The versioned remaining-time observation and its reset/terminal behavior are now verified. Partition analysis on the four saved development traces shows one or two of five partitions passed, followed by final positions 0.85 to 1.41 units from the next wall face. This supports an opening-search/turning failure rather than complete loss of target response. Freeze an experiment that allocates explicit training exposure to the original target, rather than spending its entire budget before reaching it. Preserve training, practice, validation and final-test separation. Compare corrected behavior on development layouts before consuming the still-unused independent final pool. Do not resume the previous frozen protocol after source changes, and do not claim 80 percent success from these corrections.


## Deadline correction verified on 2026-10-04

Sensors v4 append remaining_time_fraction = max(0, 1 - ticks / episode_limit), producing 270 values. The existing 269 values retain v3 semantics. The deadline is explicit task information, not an opening location, reference path or obstacle map. Profile deadlines are computed by the existing generator; this dependence must be disclosed in comparisons.

The original seeded two-input projection and 256-feature pooling assignments remain unchanged. A separate seed-104729 clock projection assigns weights -0.25, 0 and 0.25 to neurons with probabilities 0.125, 0.75 and 0.125. The remaining-time value enters recurrent activity through that projection, with no direct policy bypass. With zero clock input, v3 and v4 produce identical activity/features under matched state. With nonzero clock input, activity changes. The fingerprint distinguishes the sensor versions.

Explicit migration supports v3 to v4 by copying the policy archive and declaring the changed sensory semantics. Original ZIP and metadata remain untouched. This transfer is not evidence that the old policy has learned to use the clock. The demo selects sensor version from checkpoint metadata, and recording manifests include all 270 names.

The full test suite passed 161 tests. A separate full-graph CUDA smoke on the unchanged large profile used 128 transitions and one PPO update at gamma=0.9995 with failed-timeout bootstrapping disabled. Losses were finite and checkpoint reload matched actions. Detailed evidence is in private/deadline-sensors-v4-smoke.json. The 128 steps are verification, not substantive training or performance evidence.

No new large training run was started. The original final pool remains unused. Target exposure allocation and measured navigation improvement are still pending; the diagnosis does not establish that clock or discount alone resolves the repeated turning.
