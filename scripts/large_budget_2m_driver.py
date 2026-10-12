"""Driver for B2 (2M budget, same seed and recipe as B1). Trains one run, then evaluates the curve points. Resumable: finished stages and cells are skipped
(an interrupted training restarts from the source, because the PPO state is not saved; delete a partial output directory first).
See docs/LARGE_BUDGET_2M_PROTOCOL.md."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, run_limited

PY = sys.executable
SEED = 801
RUN = 'runs/training/large-budget-2m'
OUT = f'{RUN}/seed{SEED}'
STAGES = 61
POOL = '885000'
B1_FINAL = 'runs/training/large-budget/seed801/stage-31.zip'  # matched 1M reference, same pool
EPISODES = '64'
MID = 'scripts/profiles/passages-mid.json'
CURVE = [15, 31, 46, 61]
CURVE_CELLS = [('passages', 'passages'), ('medium', 'none')]
FINAL_EXTRA = [('passages-mid', MID), ('passages-wide', 'passages-wide'), ('gate-two', 'gate-two')]
os.makedirs(RUN, exist_ok=True)

if not os.path.exists(f'{OUT}/stage-{STAGES}.zip'):
    proc = subprocess.Popen([PY, '-s', 'scripts/train_large_budget.py', str(SEED), OUT, str(STAGES)],
                            stdout=open(f'{RUN}/train-seed{SEED}.log', 'w'), stderr=subprocess.STDOUT)
    while proc.poll() is None:
        time.sleep(10)
        if memory_used_percent() > 92:
            proc.kill()
            raise RuntimeError('memory limit during training')
    if proc.returncode != 0:
        raise RuntimeError(f'training failed with code {proc.returncode}')
    print('trained', time.strftime('%H:%M:%S'), flush=True)

commands, outputs = [], []
for stage in CURVE:
    cells = CURVE_CELLS + (FINAL_EXTRA if stage == STAGES else [])
    for name, prof in cells:
        for mode in ('det', 'sampled'):
            res = f'{OUT}/eval-s{stage}-{name}-{mode}.json'
            outputs.append((stage, name, mode, res))
            if not os.path.exists(res):
                commands.append([PY, '-s', 'scripts/eval_cell_mode.py', f'{OUT}/stage-{stage}.zip', prof, POOL, EPISODES, res, mode])
for name, prof in CURVE_CELLS:
    for mode in ('det', 'sampled'):
        res = f'{OUT}/eval-b1ref-{name}-{mode}.json'
        outputs.append(('b1ref', name, mode, res))
        if not os.path.exists(res):
            commands.append([PY, '-s', 'scripts/eval_cell_mode.py', B1_FINAL, prof, POOL, EPISODES, res, mode])
run_limited(commands)
print('evaluated', time.strftime('%H:%M:%S'), flush=True)
rows = {}
for stage, name, mode, res in outputs:
    rows.setdefault(f'stage{stage}' if stage != 'b1ref' else 'b1_final_on_this_pool', {}).setdefault(name, {})[mode] = json.load(open(res))
json.dump(rows, open(f'{OUT}/summary.json', 'w'), indent=1)
for stage, cells in rows.items():
    for name, modes in cells.items():
        print(stage, name, {m: (c['successes'], c['collisions'], c['timeouts']) for m, c in modes.items()}, flush=True)
print('driver done', flush=True)
