"""Driver for C1.P: planner reference on level C (168 episodes, four processes of two headings each) and the retained learned
candidate (stage 61 of seeds 801, 851, 901) on the `large` and `maze` profiles (fresh pools 892000 and 893000, 32 episodes per cell, both
modes). Evaluation only. See docs/PLANNER_REFERENCE_PROTOCOL.md. Resumable by cell. Raised ceiling (95 percent), up to 5 processes."""
import json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
os.environ.setdefault('RG_LIMIT', '95')
os.environ.setdefault('RG_START_BELOW', '85')
os.environ.setdefault('RG_MAX_PARALLEL', '5')  # four planner processes use about 2 GiB of VRAM each
os.environ.setdefault('RG_STAGGER', '15')
from resource_guard import run_limited

PY = sys.executable
EVAL = 'runs/training/planner-reference'
RETAINED = {f'seed{s}': f'runs/training/large-budget-2m/seed{s}/stage-61.zip' for s in (801, 851, 901)}
FAMILIES = [('large', 'large', '892000'), ('maze', 'maze', '893000')]
EPISODES = '32'
os.makedirs(EVAL, exist_ok=True)

commands, outputs = [], []
for first in (0, 2, 4, 6):  # planner on level C, two headings per process
    res = f'{EVAL}/planner-levelC-h{first}-{first + 1}.json'
    outputs.append(('planner', 'levelC', f'h{first}-{first + 1}', res))
    if not os.path.exists(res) or json.load(open(res)).get('episodes', 0) < 42:
        commands.append([PY, '-s', 'scripts/eval_planner_architecture.py', res, str(first), str(first + 1)])
for name, ck in RETAINED.items():
    for fam, prof, pool in FAMILIES:
        for mode in ('det', 'sampled'):
            res = f'{EVAL}/{name}-{fam}-{mode}.json'
            outputs.append((name, fam, mode, res))
            if not os.path.exists(res):
                commands.append([PY, '-s', 'scripts/eval_cell_mode.py', ck, prof, pool, EPISODES, res, mode])
run_limited(commands)
print('evaluated', time.strftime('%H:%M:%S'), flush=True)
planner = {'success': 0, 'collision': 0, 'timeout': 0, 'episodes': 0, 'per_scene': {}}
rows = {}
for label, cell, mode, res in outputs:
    d = json.load(open(res))
    if label == 'planner':
        for c in d['cases']:
            planner['episodes'] += 1
            for k in ('success', 'collision', 'timeout'):
                planner[k] += int(c[k])
            s = planner['per_scene'].setdefault(c['scene'], [0, 0]); s[0] += int(c['success']); s[1] += 1
    else:
        rows.setdefault(label, {}).setdefault(cell, {})[mode] = {k: d[k] for k in ('successes', 'collisions', 'timeouts', 'episodes')}
json.dump({'planner_levelC': planner, 'retained': rows}, open(f'{EVAL}/summary.json', 'w'), indent=1)
print('planner level C', {k: v for k, v in planner.items() if k != 'per_scene'}, planner['per_scene'], flush=True)
for label, cells in rows.items():
    for cell, modes in cells.items():
        print(label, cell, {m: (c['successes'], c['collisions'], c['timeouts']) for m, c in modes.items()}, flush=True)
print('driver done', flush=True)
