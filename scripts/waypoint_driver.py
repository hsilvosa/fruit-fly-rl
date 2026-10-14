"""Driver for the privileged-waypoint diagnostic: four trainings in series, then the evaluation cells. Resumable.
See docs/experiments/diagnostics/WAYPOINT_DIAGNOSTIC_PROTOCOL.md."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, run_limited

PY = sys.executable
RUN = 'runs/training/waypoint-diagnostic'
STAGES = 8
MID = 'scripts/profiles/passages-mid.json'
RUNS = [('waypoint', 701), ('control', 701), ('waypoint', 702), ('control', 702)]
CELLS = [('passages', 'passages'), ('passages-mid', MID), ('passages-wide', 'passages-wide'), ('medium', 'none')]
os.makedirs(RUN, exist_ok=True)


def guarded(cmd, name):
    proc = subprocess.Popen(cmd, stdout=open(f'{RUN}/{name}.log', 'w'), stderr=subprocess.STDOUT)
    while proc.poll() is None:
        time.sleep(10)
        if memory_used_percent() > 92:
            proc.kill()
            raise RuntimeError(f'memory limit while running {name}')
    if proc.returncode != 0:
        raise RuntimeError(f'{name} failed with code {proc.returncode}')


for arm, seed in RUNS:
    out = f'{RUN}/{arm}{seed}'
    if not os.path.exists(f'{out}/stage-{STAGES}.zip'):
        guarded([PY, '-s', 'scripts/train_waypoint.py', arm, str(seed), out, str(STAGES)], f'train-{arm}{seed}')
        print('trained', arm, seed, time.strftime('%H:%M'), flush=True)
commands = []
for arm, seed in RUNS:
    out = f'{RUN}/{arm}{seed}'
    for name, prof in CELLS:
        res = f'{out}/final-{name}.json'
        if not os.path.exists(res):
            commands.append([PY, '-s', 'scripts/eval_waypoint_cell.py', f'{out}/stage-{STAGES}.zip', prof, '880000', '64', res, arm])
run_limited(commands)
print('evaluated', time.strftime('%H:%M'), flush=True)
rows = {f'{arm}{seed}': {n: json.load(open(f'{RUN}/{arm}{seed}/final-{n}.json')) for n, _ in CELLS} for arm, seed in RUNS}
json.dump(rows, open(f'{RUN}/summary.json', 'w'), indent=1)
for k, v in rows.items():
    print(k, {n: (c['successes'], c['collisions'], c['timeouts']) for n, c in v.items()}, flush=True)
print('driver done', flush=True)
