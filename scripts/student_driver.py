"""Driver for the autonomous-student experiment (aux head, privileged critic, controls). Resumable.
See docs/AUXILIARY_STUDENT_PROTOCOL.md."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, run_limited

PY = sys.executable
RUN = 'runs/training/student-experiment'
OLD = 'runs/training/waypoint-diagnostic'
STAGES = 8
MID = 'scripts/profiles/passages-mid.json'
ORDER = [('aux', 801), ('critic', 801), ('control', 703), ('aux', 802), ('critic', 802), ('aux', 803), ('critic', 803)]
EVAL = [('control', 701), ('control', 702)] + ORDER
CELLS = [('passages', 'passages', '882000', None), ('passages-mid', MID, '882000', None), ('passages-wide', 'passages-wide', '882000', None),
         ('medium', 'none', '882000', None), ('passages-sampled', 'passages', '882000', 'stochastic'), ('levelB-dev', 'heldout_b', '950000', None)]
os.makedirs(RUN, exist_ok=True)


def folder(arm, seed):
    return f'{OLD}/{arm}{seed}' if (arm, seed) in (('control', 701), ('control', 702)) else f'{RUN}/{arm}{seed}'


def guarded(cmd, name):
    proc = subprocess.Popen(cmd, stdout=open(f'{RUN}/{name}.log', 'w'), stderr=subprocess.STDOUT)
    while proc.poll() is None:
        time.sleep(10)
        if memory_used_percent() > 92:
            proc.kill()
            raise RuntimeError(f'memory limit while running {name}')
    if proc.returncode != 0:
        raise RuntimeError(f'{name} failed with code {proc.returncode}')


for arm, seed in ORDER:
    out = folder(arm, seed)
    if not os.path.exists(f'{out}/stage-{STAGES}.zip'):
        script = 'scripts/train_waypoint.py' if arm == 'control' else 'scripts/train_student.py'
        guarded([PY, '-s', script, arm, str(seed), out, str(STAGES)], f'train-{arm}{seed}')
        print('trained', arm, seed, time.strftime('%H:%M'), flush=True)
commands = []
for arm, seed in EVAL:
    out = folder(arm, seed)
    os.makedirs(f'{RUN}/eval', exist_ok=True)
    for name, prof, pool, mode in CELLS:
        res = f'{RUN}/eval/{arm}{seed}-{name}.json'
        if not os.path.exists(res):
            cmd = [PY, '-s', 'scripts/eval_waypoint_cell.py', f'{out}/stage-{STAGES}.zip', prof, pool, '64', res, arm]
            commands.append(cmd + ([mode] if mode else []))
run_limited(commands)
print('evaluated', time.strftime('%H:%M'), flush=True)
rows = {f'{arm}{seed}': {n: json.load(open(f'{RUN}/eval/{arm}{seed}-{n}.json')) for n, *_ in CELLS} for arm, seed in EVAL}
json.dump(rows, open(f'{RUN}/summary.json', 'w'), indent=1)
for k, v in rows.items():
    print(k, {n: (c['successes'], c['collisions'], c['timeouts']) for n, c in v.items()}, flush=True)
print('driver done', flush=True)
