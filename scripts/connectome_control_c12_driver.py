"""Driver for C1.2 (extension of the four C1.1 control runs by 61 more stages, then evaluation on a fresh pool).
See docs/experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C12.md. Schedule: pair A = continuation of seed 1001 (real, shuffled in parallel), pair B = seed 1051.
Raised ceiling (95 percent): if the mean CPU over two minutes of overlap exceeds 93 percent, the second job of the pair runs after the first.
Resumable by job and cell; an interrupted training restarts from scratch (delete its directory first).
Optional first argument 'train-only' stops after the trainings."""
import json, os, shutil, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
os.environ.setdefault('RG_LIMIT', '95')
os.environ.setdefault('RG_START_BELOW', '85')
os.environ.setdefault('RG_MAX_PARALLEL', '6')
os.environ.setdefault('RG_STAGGER', '10')
from resource_guard import memory_used_percent, cpu_percent, run_limited

PY = sys.executable
RUN = 'runs/training/connectome-control'
EVAL = f'{RUN}/c12-eval'
ARMS = ['real', 'shuffled']
SEEDS = [1001, 1051]
STAGES = 61
OFFSET = 100
MID = 'scripts/profiles/passages-mid.json'
POOL = '888000'
TRAIN_THREADS = '5'
RETAINED = {f'retained{s}': f'runs/training/large-budget-2m/seed{s}/stage-61.zip' for s in (801, 851, 901)}
CELLS = [('passages', 'passages'), ('passages-mid', MID), ('passages-wide', 'passages-wide'), ('medium', 'none')]
os.makedirs(EVAL, exist_ok=True)
resource_log = open(f'{RUN}/c12-resources.log', 'a')


def phase2(arm, seed):
    return f'{RUN}/phase2-{arm}{seed}/stage-61.zip'


def phase3(arm, seed):
    return f'{RUN}/phase3-{arm}{seed}'


def job(arm, seed):
    return {'name': f'phase3-{arm}{seed}', 'out': phase3(arm, seed), 'last': f'{phase3(arm, seed)}/stage-{STAGES}.zip',
            'cmd': [PY, '-s', 'scripts/train_fresh_phase2.py', arm, str(seed), phase2(arm, seed), phase3(arm, seed), str(STAGES), str(OFFSET)]}


def launch(j):
    env = {**os.environ, **{k: TRAIN_THREADS for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS')}}
    return subprocess.Popen(j['cmd'], stdout=open(f"{RUN}/train-{j['name']}.log", 'w'), stderr=subprocess.STDOUT, env=env)


def watch(procs, label):
    peak_cpu = peak_mem = 0.0
    while any(p.poll() is None for p in procs.values()):
        cpu, mem = cpu_percent(1.0), memory_used_percent()
        peak_cpu, peak_mem = max(peak_cpu, cpu), max(peak_mem, mem)
        resource_log.write(f'{time.strftime("%H:%M:%S")} {label} cpu {cpu:.0f} mem {mem:.0f}\n'); resource_log.flush()
        if mem > 95:
            for p in procs.values():
                p.kill()
            raise RuntimeError('memory above 95 percent during training')
        time.sleep(9)
    print(label, 'peak cpu', round(peak_cpu), 'peak mem', round(peak_mem), flush=True)


def run_pair(jobs, label):
    pending = [j for j in jobs if not os.path.exists(j['last'])]
    if not pending:
        return
    procs = {}
    for j in pending:
        procs[j['name']] = launch(j)
        time.sleep(45)
    if len(procs) == 2:
        samples = [cpu_percent(2.0) for _ in range(40)]
        mean_cpu = sum(samples) / len(samples)
        print(label, 'overlap mean cpu', round(mean_cpu), 'mem', round(memory_used_percent()), flush=True)
        if mean_cpu > 93:
            second = pending[1]
            print(label, 'CPU above 93 percent: running', second['name'], 'after the first', flush=True)
            procs[second['name']].kill(); procs[second['name']].wait()
            shutil.rmtree(second['out'], ignore_errors=True)
            del procs[second['name']]
    watch(procs, label)
    for name, p in procs.items():
        if p.returncode != 0:
            raise RuntimeError(f'{name} failed with code {p.returncode}')
    for j in pending:
        if not os.path.exists(j['last']):
            q = launch(j)
            watch({j['name']: q}, label + '-' + j['name'])
            if q.returncode != 0:
                raise RuntimeError(f"{j['name']} failed with code {q.returncode}")
    print(label, 'done', time.strftime('%H:%M:%S'), flush=True)


run_pair([job(a, 1001) for a in ARMS], 'pairA-phase3-1001')
run_pair([job(a, 1051) for a in ARMS], 'pairB-phase3-1051')
if len(sys.argv) > 1 and sys.argv[1] == 'train-only':
    print('trainings done; evaluation not started', time.strftime('%H:%M:%S'), flush=True)
    sys.exit(0)

commands, outputs = [], []
for arm in ARMS:  # level C, deterministic only (the slowest cell), first
    for seed in SEEDS:
        label, ck = f'{arm}{seed}', f'{phase3(arm, seed)}/stage-{STAGES}.zip'
        res = f'{EVAL}/{label}-levelC-det.json'
        outputs.append((label, 'levelC', 'det', res))
        if not os.path.exists(res):
            commands.append([PY, '-s', 'scripts/eval_architecture.py', ck, '8', res, '900000'] + (['shuffled'] if arm == 'shuffled' else []))
for arm in ARMS:
    for seed in SEEDS:
        label, ck = f'{arm}{seed}', f'{phase3(arm, seed)}/stage-{STAGES}.zip'
        for mode in ('det', 'sampled'):
            res = f'{EVAL}/{label}-levelB-{mode}.json'
            outputs.append((label, 'levelB', mode, res))
            if not os.path.exists(res):
                commands.append([PY, '-s', 'scripts/eval_random_cell.py', ck, 'heldout_b', '0.8', '950000', '64', res] + (['sampled'] if mode == 'sampled' else []) + (['shuffled'] if arm == 'shuffled' else []))
            for name, prof in CELLS:
                res = f'{EVAL}/{label}-{name}-{mode}.json'
                outputs.append((label, name, mode, res))
                if not os.path.exists(res):
                    commands.append([PY, '-s', 'scripts/eval_cell_brain.py', arm, ck, prof, POOL, '64', res, mode])
for label, ck in RETAINED.items():  # the retained arm on the same fresh pool
    for mode in ('det', 'sampled'):
        for name, prof in CELLS:
            res = f'{EVAL}/{label}-{name}-{mode}.json'
            outputs.append((label, name, mode, res))
            if not os.path.exists(res):
                commands.append([PY, '-s', 'scripts/eval_cell_brain.py', 'real', ck, prof, POOL, '64', res, mode])
run_limited(commands)
print('evaluated', time.strftime('%H:%M:%S'), flush=True)
rows = {}
for label, cell, mode, res in outputs:
    d = json.load(open(res))
    rows.setdefault(label, {}).setdefault(cell, {})[mode] = d['total'] if cell == 'levelC' else {k: d[k] for k in ('successes', 'collisions', 'timeouts', 'episodes')}
json.dump(rows, open(f'{EVAL}/summary.json', 'w'), indent=1)
for label, cells in rows.items():
    for cell, modes in cells.items():
        print(label, cell, {m: (c['successes'], c['collisions'], c['timeouts']) for m, c in modes.items()}, flush=True)
print('driver done', flush=True)
