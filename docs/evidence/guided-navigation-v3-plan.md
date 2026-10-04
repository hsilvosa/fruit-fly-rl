# Matched critic-history isolation: authorized experiment

The original-large navigation objective remains unmet. This prepared experiment changes actor/critic history sharing to test the [identified gradient coupling](critic-history-diagnosis.md) under the same environment-transition budget as completed v2.

The user instructed continuation on 2026-10-04 after the prepared additional budget was identified as the blocker. This authorizes the prepared 65,536 additional environment transitions, bringing cumulative substantive use from 589,824 to 655,360. Source and alias hashes passed prelaunch checks; the process is running with the full graph. No new navigation outcome exists yet.

The run uses the same byte-preserving sensors-v5 warm source, seed 42, full MaleCNS graph, 112 optimization layouts, original large geometry, 32,768 teacher transitions, two 8,192-transition student-only correction rounds and 16,384 PPO transitions. Supervised update limits remain 3,072 initial actor updates, two corrective actor fits of 768 updates and 768 critic updates. Separate critic memory is copied once from fitted actor before critic initialization. The actor cannot receive value-loss gradients through its history extractor.

The teacher exposure is deliberately matched to v2 to isolate this change; the limited observed 15 teacher layouts in v2 is not being corrected simultaneously. This one-seed experiment is a development diagnostic, not a repeated-seed performance comparison. The same eight reused development validation layouts are measured once after the final budget. No teacher or route geometry enters evaluation policy inputs. No reserved final test or automatic alias promotion occurs.

Freeze implementation, warm-source, configuration and original alias hashes before launch. Preserve exact process identity, all numerical training data and before/after alias hashes. Report supervised fits separately from physical outcomes and state failure explicitly if the autonomous student still reaches no goals. Do not infer independent generalization or biological advantages from a better development score.


## Matched initialization verification

A new paired test verifies that shared and isolated versions begin with exactly identical actor history parameters and produce exactly identical deterministic actions after matching imitation minibatches. All five temporal-policy tests passed. A prelaunch audit confirms that the only experiment changes are the isolation option, output location, new budget accounting, authorization state and updated implementation hashes. Maps, observations, warm source, collection counts and optimizer-fit limits are unchanged. This establishes the comparison setup, not navigation performance. This review preceded the user-authorized launch. The full-graph run is active; navigation remains unverified.


## Observed teacher collection matching

The completed 32,768-transition teacher collection matches v2 exactly in layout seeds, positions, velocities and teacher actions. Full-connectome history features differ by at most 2.14576721e-06; they are not bitwise identical. This check uses existing records, adds no environment transitions and does not measure student navigation. The live process has advanced into actor fitting.
