"""Driver for the supervised-pretraining experiment. Resumable. See docs/experiments/students/PRETRAIN_PROTOCOL.md."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, run_limited

PY = sys.executable
SOURCE = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
MID = 'scripts/profiles/passages-mid.json'
RUN = 'runs/training/pretrain'
DATA = f'{RUN}/data'
STUDENT = 'runs/training/student-experiment'
BATCHES = [('mid-a', MID, 896000), ('mid-b', MID, 896064), ('mid-c', MID, 896128), ('passages-a', 'passages', 896300),
           ('passages-b', 'passages', 896364), ('wide-a', 'passages-wide', 896500), ('gate-a', 'gate-two', 896600), ('medium-a', 'none', 896700)]
SEEDS = [901, 902, 903]
CELLS = [('passages', 'passages', '882000', None), ('passages-mid', MID, '882000', None), ('passages-wide', 'passages-wide', '882000', None),
         ('medium', 'none', '882000', None), ('passages-sampled', 'passages', '882000', 'stochastic'), ('levelB-dev', 'heldout_b', '950000', None)]
os.makedirs(DATA, exist_ok=True)


def guarded(cmd, name):
    proc = subprocess.Popen(cmd, stdout=open(f'{RUN}/{name}.log', 'w'), stderr=subprocess.STDOUT)
    while proc.poll() is None:
        time.sleep(10)
        if memory_used_percent() > 92:
            proc.kill()
            raise RuntimeError(f'memory limit while running {name}')
    if proc.returncode != 0:
        raise RuntimeError(f'{name} failed with code {proc.returncode}')


commands = [[PY, '-s', 'scripts/collect_pretrain.py', SOURCE, prof, str(seed), '64', f'{DATA}/{name}.npz']
            for name, prof, seed in BATCHES if not os.path.exists(f'{DATA}/{name}.npz')]
run_limited(commands)
print('collected', time.strftime('%H:%M'), flush=True)
if not os.path.exists(f'{RUN}/trunk.pt'):
    guarded([PY, '-s', 'scripts/pretrain_trunk.py', DATA, RUN], 'pretrain')
m = json.load(open(f'{RUN}/metrics.json'))
t = m['test']
print('pretrained', time.strftime('%H:%M'), {k: round(v, 3) for k, v in t.items()}, flush=True)
if not (t['median_error_hard'] <= 45.0 and t['action_r2'] >= 0.9):
    print('GATE FAILED: stopping before PPO (protocol rule)', flush=True)
    sys.exit(0)
print('GATE PASSED', flush=True)
for seed in SEEDS:
    out = f'{RUN}/pre{seed}'
    if not os.path.exists(f'{out}/stage-8.zip'):
        guarded([PY, '-s', 'scripts/train_student.py', 'pre', str(seed), out, '8'], f'train-pre{seed}')
        print('trained pre', seed, time.strftime('%H:%M'), flush=True)
commands = []
os.makedirs(f'{RUN}/eval', exist_ok=True)
for seed in SEEDS:
    for name, prof, pool, mode in CELLS:
        res = f'{RUN}/eval/pre{seed}-{name}.json'
        if not os.path.exists(res):
            cmd = [PY, '-s', 'scripts/eval_waypoint_cell.py', f'{RUN}/pre{seed}/stage-8.zip', prof, pool, '64', res, 'pre']
            commands.append(cmd + ([mode] if mode else []))
run_limited(commands)
print('evaluated', time.strftime('%H:%M'), flush=True)
rows = {f'pre{s}': {n: json.load(open(f'{RUN}/eval/pre{s}-{n}.json')) for n, *_ in CELLS} for s in SEEDS}
json.dump(rows, open(f'{RUN}/summary.json', 'w'), indent=1)
for k, v in rows.items():
    print(k, {n: (c['successes'], c['collisions'], c['timeouts']) for n, c in v.items()}, flush=True)
print('driver done', flush=True)
