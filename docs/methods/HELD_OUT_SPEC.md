# Held-out specification (levels B and C)

Sealed October 10, 2026 (roadmap action R4), before any training on the randomized distribution. The user chose level C: the six synthetic architectural scenes. This document fixes what the training runs of Phase 2 and later must never use, and which seeds are reserved. A change needs a new commit that states why, and the old text stays in the history.

## Level A: new layouts of a trained family

- Family: the partitioned-room generator, sampled by [the map sampler](MAP_SAMPLER.md) with the training sampler.
- Training uses seeds drawn at run time by the training script, from ranges that no evaluation pool uses.
- Development and selection pools: the pools in the roadmap registry (800000 to 865000). They are inspected.
- Reserved for the report: seeds 940000 to 949999. Not used before Phase 5 or the full Phase 1 style report.

## Level B: held-out parameter region

- Definition: an opening width below 3.8 m together with at least four partitions (`in_heldout_b` in `fly_rl/simulation/random_profiles.py`).
- The training sampler never draws a profile inside the region. A test checks this.
- Development draws, for looking at progress: the held-out sampler with seeds 950000 to 959999. Results may be inspected. They may not choose checkpoints or settings.
- Reserved for the final assessment: the held-out sampler with seeds 960000 to 969999. Not opened before Phase 5.
- The existing `large` profile lies inside the region. Its earlier results, including the consumed 0/64 pool, were produced by other policies and do not change this rule.

## Level C: held-out family

- Family: the six synthetic architectural scenes: `office-floor`, `apartment`, `street-block`, `atrium`, `warehouse`, `courtyard`. They have 21 situations in total (3, 3, 5, 3, 4 and 3).
- The lineage under test has never trained on them. The recovered 50/64 reference, transfer experiments 1 to 8, the Phase 1 runs and the Phase 3 runs used no architectural scene. Earlier architectural policies (sensor v6 curricula) belong to other lineages.
- Rule: no training run, checkpoint selection or setting choice may use level C results before Phase 5. One measurement of a starting checkpoint is allowed, because it cannot influence a recipe. Every other use is logged in [EXPERIMENT_LOG.md](../EXPERIMENT_LOG.md) with its reason.
- Evaluation tool: `scripts/eval_architecture.py`, with `fly_rl/simulation/architectural_transfer.py`. It runs every situation with several initial headings and reports per scene. The geometry equals the protected `ArchitecturalWorld` (a test compares them).
- Headings seeds: development 900000 and above (the tool default). Reserved for the final assessment: 970000 to 979999.

## Limits of level C

- The geometry is fixed. Each situation has one start, one goal and one scene, so the only randomness is the initial heading. Twenty-one situations with several headings are not independent samples of unseen buildings. Level C shows how the policy behaves in a family it never trained on, and it does not show generalization to real buildings.
- The synthetic scenes were designed and inspected by the project, and the explicit planner has results on them. The scenes are not hidden. The protection comes from the rule above, not from secrecy.
- Real buildings and street reconstructions stay outside this release, as in the roadmap.
