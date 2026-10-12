"""Driver for B3 (replication of the 2M recipe). Trains seeds 851 and 901 in series (seed 801 already exists from B2), then evaluates
stages 46 and 61 of all three seeds, plus the experiment 7 start as baseline, on pool 886000. Resumable: finished stages and cells are skipped
(an interrupted training restarts from the source; delete its partial output directory first). See docs/REPLICATION_2M_PROTOCOL.md."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, run_limited

PY = sys.executable
RUN = 'runs/training/large-budget-2m'
EVAL = f'{RUN}/b3-eval'
SEEDS = [801, 851, 901]
NEW = [851, 901]
STAGES = 61
POINTS = [46, 61]
POOL = '886000'
EPISODES = '64'
MID = 'scripts/profiles/passages-mid.json'
START = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
CELLS = [('passages', 'passages'), ('medium', 'none')]
FINAL_EXTRA = [('passages-mid', MID), ('passages-wide', 'passages-wide'), ('gate-two', 'gate-two')]
os.makedirs(EVAL, exist_ok=True)

for seed in NEW:
    out = f'{RUN}/seed{seed}'
    if not os.path.exists(f'{out}/stage-{STAGES}.zip'):
        proc = subprocess.Popen([PY, '-s', 'scripts/train_large_budget.py', str(seed), out, str(STAGES)],
                                stdout=open(f'{RUN}/train-seed{seed}.log', 'w'), stderr=subprocess.STDOUT)
        while proc.poll() is None:
            time.sleep(10)
            if memory_used_percent() > 92:
                proc.kill()
                raise RuntimeError(f'memory limit during training of seed {seed}')
        if proc.returncode != 0:
            raise RuntimeError(f'training of seed {seed} failed with code {proc.returncode}')
        print('trained', seed, time.strftime('%H:%M:%S'), flush=True)

jobs = []  # (label, checkpoint, cells)
for seed in SEEDS:
    for stage in POINTS:
        jobs.append((f'seed{seed}-s{stage}', f'{RUN}/seed{seed}/stage-{stage}.zip', CELLS + (FINAL_EXTRA if stage == STAGES else [])))
jobs.append(('start', START, CELLS))
commands, outputs = [], []
for label, ck, cells in jobs:
    for name, prof in cells:
        for mode in ('det', 'sampled'):
            res = f'{EVAL}/{label}-{name}-{mode}.json'
            outputs.append((label, name, mode, res))
            if not os.path.exists(res):
                commands.append([PY, '-s', 'scripts/eval_cell_mode.py', ck, prof, POOL, EPISODES, res, mode])
run_limited(commands)
print('evaluated', time.strftime('%H:%M:%S'), flush=True)
rows = {}
for label, name, mode, res in outputs:
    rows.setdefault(label, {}).setdefault(name, {})[mode] = json.load(open(res))
json.dump(rows, open(f'{EVAL}/summary.json', 'w'), indent=1)
for label, cells in rows.items():
    for name, modes in cells.items():
        print(label, name, {m: (c['successes'], c['collisions'], c['timeouts']) for m, c in modes.items()}, flush=True)
print('driver done', flush=True)
