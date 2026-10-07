# Autonomous architectural learning

## Objective and closed planner stage

The primary objective is a policy that learns navigation through reinforcement learning and chooses its own flight actions. The explicit planner is a reference or a possible imitation-learning teacher. It must not choose the student's evaluation actions.

The maze and architectural planner iteration is closed using its existing evidence. Maze exp.32 reached 7/8 goals in two retained pools; fresh verification is deferred. Architectural exp.3 reached 19/21 inspected original objectives with no collisions and preserved all exp.1 successes. Apartment bathroom and atrium climb remain unresolved. These are explicit-planner results, not learned navigation. Existing demo defaults are retained; no promotion or further planner variants are part of this transition. See the [architectural closing report](evidence/architectural-closing-results.md) and [maze closure](evidence/maze-wrap-up.md).

## Implemented first learned controller

learned-architecture-1.0-exp.1 is a freshly initialized PPO actor/critic. It consumes nine frames of 5,669 segmented neural features produced by the complete 167,184-neuron, 25,583,622-edge MaleCNS graph. A learned 128-coordinate frame encoder and GRU provide a temporal representation; the actor outputs the existing four coordinated flight actions. No portal detection, map search, hand-written braking or escape recovery chooses these actions. Physical collision handling remains part of the environment.

The frozen graph is not optimized. PPO updates the policy's frame encoder, memory, actor and critic from environment rewards. The input features reconstruct simulated sensory signals from neural activity; this engineered readout is not evidence of biological perception. The student initially uses the existing synthetic goal direction/distance signal rather than discovering an unknown goal from vision.

Policy and full-connectome execution use CUDA. GPU utilization alone is not a success metric; this small PPO policy and CPU world physics may not saturate the GPU. The first implementation is a single selected architectural situation, not yet a complete multi-scene training experiment. It does not include a planner teacher, imitation stage, raw-sensor baseline, independent evaluation suite or learned-policy viewer integration yet.

## Verified learning pipeline

The explicit smoke command is:

```powershell
.\.conda\python.exe -s scripts/verify_autonomous_architecture.py runs/verification/autonomous-architecture-ppo-smoke-new
```

Use a new output directory. This command performs exactly 128 environment transitions and one PPO update, then saves and reloads a temporary learned-policy checkpoint. It never starts extended training or consumes a reserved test. Opening existing demos does not call it.

The completed initial smoke passed: 128 transitions, one update, finite logged losses, changed trainable parameters and matching deterministic actions after checkpoint reload. Execution took 4.44 seconds after initialization on CUDA. All six original checkpoint aliases retained their hashes. No planner supplied actions, no reserved test was accessed and no navigation-performance claim follows from this short check. Three focused tests also cover the encoder gradient/shape, absence of planner imports and rejection of planner-assisted checkpoint metadata. The detailed status is local under runs/verification/autonomous-architecture-ppo-smoke and private/autonomous-learning-start.

The checkpoint contract records graph fingerprint, readout, sensor version, history dimensions, flight dynamics and planner_assistance=false. Load rejects mismatched contracts. It permits different architectural scenes with the same input contract for later declared evaluation; compatibility is not generalization evidence. Checkpoints use explicit .zip paths and cannot overwrite an existing model or metadata file.

## Next bounded experiment

A substantial training budget is awaiting the user's choice. No extended run has started. Before execution, declare training situations, validation selection, seeds and an untouched held-out collection. The six existing inspected designs are development data; varying headings within them does not make their geometry independent.

Use a freshly initialized learner without a planner at inference. If demonstrations are later added, report imitation updates and teacher-assisted rollouts separately from autonomous PPO rollouts. Evaluate the resulting student separately from the planner. A matched no-connectome learner must receive the same sensory information and history, task distribution and training budget; document representation and parameter-count differences. No advantage or necessity of the connectome can be asserted from the current smoke.

The [mathematics guide](MATHEMATICS.md) describes PPO rewards, advantage estimation and optimization. The [roadmap](../ROADMAP.md) records the agreed ordering: close planner experiments, autonomous learning, then controlled comparisons. Navigation is not marked solved until actual student flights support that claim.

## Authorized first PPO pilot

On October 7 the user requested starting training. The first pilot is bounded at 131,072 fresh PPO transitions, excluding the prior 128-transition verification and pre/post validation flights. It uses seed 42, 512-step rollouts, five PPO epochs and 128-sample minibatches. The 32 fixed chunks of 4,096 transitions cycle through the 15 training situations across all six scenes. Each scene's last situation is withheld from training and checked before and after at seed 200001. All original geometry, endpoints, rewards and deadlines are preserved.

These six validation tasks share the inspected scene geometry with training, so they measure withheld-task performance rather than independent building generalization. Final-budget checkpoint selection is fixed before execution; there is no validation-driven retry, teacher assistance, imitation update or reserved-test access. Checkpoints are saved every 32,768 training transitions and at the final budget, under a new experiment directory. Per-episode and PPO-update metrics distinguish training from validation. Source and original-alias hashes are checked. No checkpoint is automatically promoted.

```powershell
.\.conda\python.exe -s scripts/train_autonomous_architecture.py runs/training/autonomous-architecture-pilot-1 --transitions 131072
```

This command explicitly trains; opening the demo still does not. The pilot's outcome is pending and no successful navigation is claimed in advance.

## First autonomous PPO pilot completed

The 131,072-transition pilot reached 0 goals in 457 training episodes and 0/6 validation goals both before and after; final validation had five collisions and one timeout. The learning pipeline and checkpoint reload passed, but navigation did not. No model was promoted. A structured neural panorama/goal-state encoder is implemented as the next representation candidate; its focused gradient test passes, while full-connectome learning verification and training remain pending. [Results and diagnosis](evidence/autonomous-architecture-pilot-1-results.md).

## Structured PPO iteration

learned-architecture-1.0-exp.2 is integrated into the explicit smoke and training runners through --policy-version. It uses learned circular convolutions over the three neural panorama channels, a separate near-body encoder, recurrent history and direct access to the existing 13 neural goal/state coordinates. It applies no goal-to-action formula, planner, teacher or hand-written recovery.

The first CUDA smoke collected 128 verification transitions but failed during its update because adaptive pooling backward was incompatible with deterministic CUDA algorithms. Fixed-size average pooling preserves the mode rather than relaxing determinism. A separate repaired smoke completed 128 transitions and one update, finite losses, changed parameters and matching checkpoint reload in 4.31 seconds after initialization. Both attempts are verification, not substantial training or evidence of navigation. Original aliases matched. Version/encoder consistency is checked on checkpoint load; original exp.1 checkpoints remain supported.

The second pilot uses 131,072 fresh training transitions, the same 15 training tasks, six withheld validation tasks, seed, physical geometry, original endpoints, deadlines, reward and PPO settings as pilot 1. Only the representation changes. The same validation pool is now reused development evidence; it cannot be presented as independent confirmation. There is no imitation, planner assistance, curriculum or reserved-test access. The final-budget checkpoint is assessed without automatic promotion. The first pilot's exact runtime sources were archived and hash-checked before integration changes.

```powershell
.\.conda\python.exe -s scripts/train_autonomous_architecture.py runs/training/autonomous-architecture-pilot-2 --transitions 131072 --policy-version learned-architecture-1.0-exp.2
```

Pilot 2 results are pending. A single training seed is insufficient to establish a robust improvement even if its development outcome rises.

## Prepared training-goal curriculum tool

While pilot 2 runs unchanged, architectural_training_goals.py provides an isolated sampler for future short training objectives. It samples a requested displacement between 0.5 and 12 m, rejects out-of-room endpoints and checks the complete swept body segment against solids with an additional 0.1 m clearance margin. Geometry is used only to construct valid training tasks; it is not an observation or an action policy. Sampling never reads the connecting reference route or modifies a world's target, pose or deadline. Failure to find a sample is explicit rather than silently changing the task.

Seven CPU geometry tests pass across all six scenes, including deterministic sampling, body clearance, unchanged original tasks and impossible-sample rejection. These checks are not CPU training or learned navigation evidence. The tool is not yet wired into an environment reset, mastery schedule or PPO run. Pilot 2's frozen sources still match and its objectives remain unchanged.

If pilot 2 still cannot reach training goals, the next declared experiment can introduce short tasks as a curriculum, with a separate environment adapter and explicit progression/episode accounting. Original evaluation endpoints, geometry and deadlines must stay unchanged. Curriculum success must be reported separately from original-route performance, with no planner choosing student actions.

## Separate curriculum world and environment

ArchitecturalCurriculumWorld now applies the sampled training goal only in explicitly selected lesson worlds. Stages request 1, 2, 4 and 8 m clear displacements; the fifth stage restores the scene's original goal and physical deadline. Short lessons use a declared deadline of min(original deadline, ceil((10 + 2 * distance) / 0.05)) physical steps. Episode/reset/snapshot metadata identifies the stage, original goal, original deadline and training deadline. The existing evaluation world is unchanged.

Twenty-three CPU geometry tests pass: stage-one tasks on all 15 training situations, original geometry/start preservation, valid distances, reproducibility, sampling failure and restoration of the original goal/deadline. These are simulation contract tests, not training or navigation-performance evidence. The separate ArchitecturalCurriculumEnv adapter is implemented for full-connectome use, but its actual neural reset/learning smoke is pending until the active pilot has finished. It is not used by pilot 2.

Longer clear displacements may be unavailable in constrained interiors; the sampler reports failure. A future curriculum protocol must handle and log that availability explicitly, rather than remove obstacles, silently shorten requested stages or change evaluation goals. Mastery progression, per-stage accounting, checkpoint curriculum compatibility and original-task validation still need integration before launching a curriculum experiment.

## Curriculum availability audit

A CPU-only audit sampled each of the 15 training situations at three declared seeds (310001-310003), with at most 256 direction attempts per sample. It found body-clear endpoints at 1, 2 and 4 m in all 45 samples per distance. At 8 m it found 39/45; both apartment training starts failed on all three seeds. The audit did not load the connectome, a movement policy, train weights or run evaluation. Original targets remained unchanged. Sampling success on these seeds does not guarantee universal availability or dynamic navigability.

This evidence changes the proposed common progression to stages 0, 1, 2 and 4: 1 m, 2 m, 4 m and then the original task. Stage 3 (8 m) stays an optional explicit lesson where available; it must not be forced globally or silently shortened in apartments. A future runner must declare this stage order before training and record any sampling failures. Geometry and original-route validation stay unchanged. The active pilot has not adopted the curriculum.

The audit can be regenerated without a policy:

```powershell
.\.conda\python.exe -s scripts/audit_architectural_curriculum_goals.py reports/architectural-curriculum-availability-new.json
```

Detailed sampled endpoints are preserved locally in private/architectural-curriculum-availability. Mastery-controlled progression still needs integration and a full-connectome smoke after pilot 2 finishes.
