"""Driver for C1.0 (feasibility of the fresh two-arm chain, phase 1 only). Trains the real-connectome arm and the edge-shuffled arm
(seed 1001, 27 stages = 884,736 transitions, medium rooms only, random initial weights), then evaluates medium on pool 887000.
Resumable by cell; an interrupted training restarts from scratch (delete its directory first). See docs/CONNECTOME_CONTROL_PROTOCOL.md."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, run_limited

PY = sys.executable
RUN = 'runs/training/connectome-control'
SEED = 1001
STAGES = 27
POINTS = [9, 18, 27]
POOL = '887000'
EPISODES = '64'
START = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
ARMS = ['real', 'shuffled']
os.makedirs(RUN, exist_ok=True)

for arm in ARMS:
    out = f'{RUN}/phase1-{arm}{SEED}'
    if not os.path.exists(f'{out}/stage-{STAGES}.zip'):
        proc = subprocess.Popen([PY, '-s', 'scripts/train_fresh_chain.py', arm, str(SEED), out, str(STAGES)],
                                stdout=open(f'{RUN}/train-phase1-{arm}{SEED}.log', 'w'), stderr=subprocess.STDOUT)
        while proc.poll() is None:
            time.sleep(10)
            if memory_used_percent() > 92:
                proc.kill()
                raise RuntimeError(f'memory limit during training of {arm}')
        if proc.returncode != 0:
            raise RuntimeError(f'training of {arm} failed with code {proc.returncode}')
        print('trained', arm, time.strftime('%H:%M:%S'), flush=True)

jobs = [('start', 'real', START)] + [(f'{arm}-s{p}', arm, f'{RUN}/phase1-{arm}{SEED}/stage-{p}.zip') for arm in ARMS for p in POINTS]
commands, outputs = [], []
os.makedirs(f'{RUN}/c10-eval', exist_ok=True)
for label, arm, ck in jobs:
    for mode in ('det', 'sampled'):
        res = f'{RUN}/c10-eval/{label}-medium-{mode}.json'
        outputs.append((label, mode, res))
        if not os.path.exists(res):
            commands.append([PY, '-s', 'scripts/eval_cell_brain.py', arm, ck, 'none', POOL, EPISODES, res, mode])
run_limited(commands)
print('evaluated', time.strftime('%H:%M:%S'), flush=True)
rows = {}
for label, mode, res in outputs:
    rows.setdefault(label, {})[mode] = json.load(open(res))
json.dump(rows, open(f'{RUN}/c10-eval/summary.json', 'w'), indent=1)
for label, modes in rows.items():
    print(label, 'medium', {m: (c['successes'], c['collisions'], c['timeouts']) for m, c in modes.items()}, flush=True)
print('driver done', flush=True)
