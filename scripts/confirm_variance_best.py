"""Confirmation of the best variance-study run and of the pilot candidate on a fresh pool, 64 episodes per cell.
Fresh pool seeds 880000 to 880063 (a new development pool, never used by selection). Evaluation only."""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import run_limited

MID = 'scripts/profiles/passages-mid.json'
CKS = {'seed505-best-of-5': 'runs/training/variance-study/seed505/stage-3.zip',
       'pilot-candidate': 'runs/training/phase1-pilot/seed442/stage-3.zip'}
CELLS = [('passages-wide', 'passages-wide'), ('passages-mid', MID), ('passages', 'passages'), ('medium', 'none')]
out_dir = 'runs/verification/variance-confirmation'
os.makedirs(out_dir, exist_ok=True)
commands = []
for label, ck in CKS.items():
    for name, prof in CELLS:
        out = f'{out_dir}/{label}-{name}.json'
        if not os.path.exists(out):
            commands.append([sys.executable, '-s', 'scripts/eval_cell.py', ck, prof, '880000', '64', out])
run_limited(commands)
result = {label: {name: json.load(open(f'{out_dir}/{label}-{name}.json')) for name, _ in CELLS} for label in CKS}
json.dump(result, open(f'{out_dir}/confirmation.json', 'w'), indent=1)
for label, cells in result.items():
    print(label, {k: (v['successes'], v['collisions'], v['timeouts']) for k, v in cells.items()}, '(64 episodes each)', flush=True)
