"""Driver for B4: level B (held-out parameter region, development maps) and level C (architectural scenes, development headings)
for stage 61 of seeds 801, 851 and 901 and for the experiment 7 start checkpoint. Resumable: finished cells are skipped.
Evaluation only. See docs/LEVEL_BC_PROTOCOL.md."""
import json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import run_limited

PY = sys.executable
RUN = 'runs/training/large-budget-2m'
EVAL = f'{RUN}/b4-eval'
START = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
CKPTS = [('seed801', f'{RUN}/seed801/stage-61.zip'), ('seed851', f'{RUN}/seed851/stage-61.zip'),
         ('seed901', f'{RUN}/seed901/stage-61.zip'), ('start', START)]
MODES = ['det', 'sampled']
os.makedirs(EVAL, exist_ok=True)

commands, outputs = [], []
for label, ck in CKPTS:
    for mode in MODES:
        if label == 'start' and mode == 'det':
            continue  # level C deterministic for the start was measured earlier (71 of 168, seed 900000, 8 headings); not repeated
        res = f'{EVAL}/{label}-levelC-{mode}.json'
        outputs.append((label, 'levelC', mode, res))
        if not os.path.exists(res):
            commands.append([PY, '-s', 'scripts/eval_architecture.py', ck, '8', res, '900000'] + (['sampled'] if mode == 'sampled' else []))
for label, ck in CKPTS:
    for mode in MODES:
        res = f'{EVAL}/{label}-levelB-{mode}.json'
        outputs.append((label, 'levelB', mode, res))
        if not os.path.exists(res):
            commands.append([PY, '-s', 'scripts/eval_random_cell.py', ck, 'heldout_b', '0.8', '950000', '64', res] + (['sampled'] if mode == 'sampled' else []))
run_limited(commands)
print('evaluated', time.strftime('%H:%M:%S'), flush=True)
rows = {}
for label, level, mode, res in outputs:
    d = json.load(open(res))
    rows.setdefault(label, {}).setdefault(level, {})[mode] = d['total'] if level == 'levelC' else {k: d[k] for k in ('successes', 'collisions', 'timeouts', 'episodes')}
json.dump(rows, open(f'{EVAL}/summary.json', 'w'), indent=1)
for label, levels in rows.items():
    for level, modes in levels.items():
        print(label, level, {m: (c['successes'], c['collisions'], c['timeouts']) for m, c in modes.items()}, flush=True)
print('driver done', flush=True)
