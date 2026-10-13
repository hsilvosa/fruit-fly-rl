"""Driver for C1.1 (phase 2 of the fresh two-arm chain, seeds 1001 and 1051, then evaluation). See docs/CONNECTOME_CONTROL_PROTOCOL_C11.md.
Schedule (two trainings at a time, under the 95 percent ceiling): pair A = phase 2 of seed 1001 (real, shuffled); pair B = phase 1 of
seed 1051; pair C = phase 2 of seed 1051. If the mean CPU over two minutes of overlap exceeds 93 percent, the second job of the pair is
stopped and run after the first. Resource log written. Resumable: finished jobs and evaluation cells are skipped; an interrupted
training restarts from scratch (delete its directory first)."""
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
EVAL = f'{RUN}/c11-eval'
ARMS = ['real', 'shuffled']
SEEDS = [1001, 1051]
P1_STAGES, P2_STAGES = 27, 61
MID = 'scripts/profiles/passages-mid.json'
POOL = '886000'
TRAIN_THREADS = '5'
os.makedirs(EVAL, exist_ok=True)
resource_log = open(f'{RUN}/c11-resources.log', 'a')


def p1(arm, seed):
    return f'{RUN}/phase1-{arm}{seed}'


def p2(arm, seed):
    return f'{RUN}/phase2-{arm}{seed}'


def job_phase1(arm, seed):
    return {'name': f'phase1-{arm}{seed}', 'out': p1(arm, seed), 'last': f'{p1(arm, seed)}/stage-{P1_STAGES}.zip',
            'cmd': [PY, '-s', 'scripts/train_fresh_chain.py', arm, str(seed), p1(arm, seed), str(P1_STAGES)]}


def job_phase2(arm, seed):
    return {'name': f'phase2-{arm}{seed}', 'out': p2(arm, seed), 'last': f'{p2(arm, seed)}/stage-{P2_STAGES}.zip',
            'cmd': [PY, '-s', 'scripts/train_fresh_phase2.py', arm, str(seed), f'{p1(arm, seed)}/stage-{P1_STAGES}.zip', p2(arm, seed), str(P2_STAGES)]}


def launch(job):
    env = {**os.environ, **{k: TRAIN_THREADS for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS')}}
    return subprocess.Popen(job['cmd'], stdout=open(f"{RUN}/train-{job['name']}.log", 'w'), stderr=subprocess.STDOUT, env=env)


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
    for job in pending:
        procs[job['name']] = launch(job)
        time.sleep(45)  # the connectome load is the memory and CPU peak
    if len(procs) == 2:
        samples = [cpu_percent(2.0) for _ in range(40)]  # about two minutes of overlap
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
    for job in pending:
        if not os.path.exists(job['last']):
            watch({job['name']: (q := launch(job))}, label + '-' + job['name'])
            if q.returncode != 0:
                raise RuntimeError(f"{job['name']} failed with code {q.returncode}")
    print(label, 'done', time.strftime('%H:%M:%S'), flush=True)


run_pair([job_phase2(a, 1001) for a in ARMS], 'pairA-phase2-1001')
run_pair([job_phase1(a, 1051) for a in ARMS], 'pairB-phase1-1051')
run_pair([job_phase2(a, 1051) for a in ARMS], 'pairC-phase2-1051')

commands, outputs = [], []
for arm in ARMS:
    for seed in SEEDS:
        label, ck = f'{arm}{seed}', f'{p2(arm, seed)}/stage-{P2_STAGES}.zip'
        tag = ['shuffled'] if arm == 'shuffled' else []
        for mode in ('det', 'sampled'):
            m = ['sampled'] if mode == 'sampled' else []
            res = f'{EVAL}/{label}-levelC-{mode}.json'
            outputs.append((label, 'levelC', mode, res))
            if not os.path.exists(res):
                commands.append([PY, '-s', 'scripts/eval_architecture.py', ck, '8', res, '900000'] + m + tag)
    for seed in SEEDS:
        label, ck = f'{arm}{seed}', f'{p2(arm, seed)}/stage-{P2_STAGES}.zip'
        tag = ['shuffled'] if arm == 'shuffled' else []
        for mode in ('det', 'sampled'):
            m = ['sampled'] if mode == 'sampled' else []
            res = f'{EVAL}/{label}-levelB-{mode}.json'
            outputs.append((label, 'levelB', mode, res))
            if not os.path.exists(res):
                commands.append([PY, '-s', 'scripts/eval_random_cell.py', ck, 'heldout_b', '0.8', '950000', '64', res] + m + tag)
            for name, prof in (('passages', 'passages'), ('passages-mid', MID), ('passages-wide', 'passages-wide'), ('medium', 'none')):
                res = f'{EVAL}/{label}-{name}-{mode}.json'
                outputs.append((label, name, mode, res))
                if not os.path.exists(res):
                    commands.append([PY, '-s', 'scripts/eval_cell_brain.py', arm, ck, prof, POOL, '64', res, mode])
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
