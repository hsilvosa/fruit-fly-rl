# Timeout correction development pilot

The diagnosis found zero training exposure to the original target, a short discount horizon, mixed deadline semantics, and repeated turning near subsequent partitions. This pilot checks the combined correction on development layouts. It cannot attribute an effect to any individual intervention and cannot establish independent generalization.

The source is the preserved large-continuous-v4 round-23 checkpoint, transferred explicitly from sensors v3 to v4. The initial policy archive remains byte-identical; the copied metadata declares the added deadline input. The original policy and six launcher aliases must retain their hashes.

The budget is 32,768 added transitions, four continuous chunks of 8,192 with eight environments and seed 42. This uses part of the original unspent 524,288-transition substantive budget: 286,720 transitions were preserved before the pilot; cumulative added transitions after completion will be 319,488. Separate 128-transition smoke checks are verification and excluded from these totals.

Four dedicated environments use the unchanged original large profile from initialization: 48 by 48 by 16, 112 collision boxes, five partitions and 3.2 by 3.2 openings. They guarantee exactly 16,384 target transitions across this budget. The other four environments retain the previous checkpoint's documented mastery stage four, large-wide, with the existing easier-task mixture. The pilot freezes that stage and does not run practice gates or adapt it from evaluation. Episodes and recurrent activity remain live across chunks.

The learning controls are gamma=0.9995, failure-terminal timeout handling and the sensors-v4 remaining-time channel. PPO and its rollout buffer use the same discount. The full annotated MaleCNS graph remains required. No map reduction, opening oracle, hidden route observation or direct sensor bypass is supplied to the movement policy.

Optimization layouts are the previous declared optimization pool. The four diagnostic before/after layouts are seeds 370000 through 370003, which belong to that same optimization pool. These measurements assess development behavior only and may be influenced by training. Withheld practice seeds remain excluded from optimizer updates. No independent final-test pool is accessed or consumed.

The same transferred initial checkpoint and last trained checkpoint are measured before and after on those four layouts. Record goals, collisions, timeouts, path length, idle fraction and terminal distance. A before/after improvement would support this development correction, not the 80 percent independent-test objective. No checkpoint is promoted automatically and no budget expansion occurs on failure.

Verification before launch: 165 tests passed. An additional full-graph CUDA smoke used 128 transitions and one PPO update across two environments, recorded exactly 64 target transitions and 64 gate-near transitions while mastery stayed at stage zero, and had finite losses. Dedicated target lanes survive natural timeout resets and cannot change a live curriculum episode. Detailed configuration, hashes, process identity and results are private.
