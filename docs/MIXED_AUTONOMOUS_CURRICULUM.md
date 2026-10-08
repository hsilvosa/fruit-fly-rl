# Mixed autonomous architectural curriculum

The balanced curriculum learned short, unobstructed goals but failed all six full-route development validation tasks. This variant adds exposure to original navigation goals while retaining lesson practice. It continues learned PPO weights and optimizer state; no explicit planner supplies actions.

## Schedule and continuation

`scripts/train_architectural_curriculum_mixed.py` requires an explicit source checkpoint and additional transition budget. It alternates 2,048-transition lesson and original-goal chunks over the 15 training situations. Original chunks rotate through every training situation. Lesson chunks select incomplete mastery windows. At the original-goal terminal stage every chunk uses original goals. Evaluation situations are excluded from the training schedule.

The source must have a compatible autonomous input contract and saved curriculum metadata. Completed rounds are replayed and checked against their criterion; pending outcomes and curriculum stage are retained. PPO weights, optimizer and accumulated update counters are loaded. The task scheduler starts a declared new cycle; this is not an exact interruption replay. Logs record added and cumulative transitions separately. Original-task outcomes do not enter lesson mastery windows while the lesson stage is active.

Original and lesson chunks have equal transition budgets. Each chunk resets episode, brain and observation history. Episodes unfinished at a task switch are interrupted and do not count as completed outcomes; 2,048 transitions exceed the current original-task deadline. The experiment does not silently alter scenes, rewards, acceptance thresholds or sensor inputs. Source ZIP and JSON and protected aliases are hashed before and after. New checkpoints use a separate output directory; existing experiments cannot be overwritten or restarted.

## Verification

Eight CPU tests passed for task alternation, original-stage behavior, disjoint mastery progression and restoration consistency. The full-connectome GPU smoke completed 128 additional learning transitions and one PPO optimizer epoch pass from the 131,072-transition source. It also performed one original-goal action probe, separate from the learning budget. Losses were finite, deterministic checkpoint reload matched, restored mastery exactly matched the source, and all source and alias hashes remained unchanged. No reserved test was accessed and no checkpoint was promoted. Smoke outcomes are implementation checks, not performance evidence.

Local smoke evidence: `runs/verification/architectural-curriculum-mixed-smoke/`; archived metadata and telemetry: `private/architectural-curriculum-mixed-smoke/`.

## Explicit training command

After agreeing the additional budget, use a new output directory:

```powershell
.\.conda\python.exe -s scripts/train_architectural_curriculum_mixed.py runs/training/autonomous-architecture-mixed-1 --source runs/training/autonomous-architecture-curriculum-2/final-policy.zip --transitions 65536
```

The command allows 65,536 or 131,072 additional transitions. Verification requires `--verification --transitions 128` and its own directory. Opening a demonstration does not invoke this runner.

Before and after development validation uses the unchanged original goals. These repeatedly inspected situations share geometry with training and are not an independent generalization test. No held-out test should be consumed to tune this change. A substantial new run awaits an agreed budget. The autonomous navigation objective remains unresolved.
