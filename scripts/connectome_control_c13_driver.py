"""Driver for C1.3 (two more seeds of the fresh two-arm control chain, then evaluation and the frozen four-seed analysis).
See docs/experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C13.md.
Per seed (1101, then 1151), real and shuffled in parallel as one pair: phase 1 (27 stages of medium rooms), phase 2 (61 stages, B2 recipe),
phase 3 (61 more stages, layout offset 100). Same ceiling as C1.2 (95 percent) and same fallback: if the mean CPU over two minutes of overlap
exceeds 93 percent, the second job of the pair runs after the first. Resumable by job and cell; an interrupted training restarts from scratch
(delete its directory first). Resource log written.
Arguments: none = everything; 'train-only' stops after the trainings; 'dry-run' prints the pending jobs and evaluation commands and exits
without starting anything."""
import json, os, shutil, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
os.environ.setdefault('RG_LIMIT', '95')
os.environ.setdefault('RG_START_BELOW', '85')
os.environ.setdefault('RG_MAX_PARALLEL', '6')
os.environ.setdefault('RG_STAGGER', '10')
from resource_guard import memory_used_percent, cpu_percent, run_limited
import connectome_control_stats as cstats

DRY = len(sys.argv) > 1 and sys.argv[1] == 'dry-run'
PY = sys.executable
RUN = 'runs/training/connectome-control'
EVAL = f'{RUN}/c13-eval'
ARMS = ['real', 'shuffled']
SEEDS = [1101, 1151]
OLD_SUMMARY = f'{RUN}/c12-eval/summary.json'
P1_STAGES, P2_STAGES, P3_STAGES, OFFSET = 27, 61, 61, 100
MID = 'scripts/profiles/passages-mid.json'
POOL = '888000'  # the C1.2 pool: the new seeds see the same maps as seeds 1001 and 1051, so the four seeds can be compared directly
TRAIN_THREADS = '5'
CELLS = [('passages', 'passages'), ('passages-mid', MID), ('passages-wide', 'passages-wide'), ('medium', 'none')]
if not DRY:
    os.makedirs(EVAL, exist_ok=True)
    resource_log = open(f'{RUN}/c13-resources.log', 'a')


def d(phase, arm, seed):
    return f'{RUN}/phase{phase}-{arm}{seed}'


def job(phase, arm, seed):
    out = d(phase, arm, seed)
    stages = {1: P1_STAGES, 2: P2_STAGES, 3: P3_STAGES}[phase]
    if phase == 1:
        cmd = [PY, '-s', 'scripts/train_fresh_chain.py', arm, str(seed), out, str(stages)]
    else:
        src = f'{d(phase - 1, arm, seed)}/stage-{P1_STAGES if phase == 2 else P2_STAGES}.zip'
        cmd = [PY, '-s', 'scripts/train_fresh_phase2.py', arm, str(seed), src, out, str(stages)] + ([str(OFFSET)] if phase == 3 else [])
    return {'name': f'phase{phase}-{arm}{seed}', 'out': out, 'last': f'{out}/stage-{stages}.zip', 'cmd': cmd}


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
    if DRY:
        print(label, 'pending:', [j['name'] for j in pending])
        for j in pending:
            print('   ', ' '.join(j['cmd']))
        return
    if not pending:
        return
    procs = {}
    for j in pending:
        procs[j['name']] = launch(j)
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
    for j in pending:
        if not os.path.exists(j['last']):
            q = launch(j)
            watch({j['name']: q}, label + '-' + j['name'])
            if q.returncode != 0:
                raise RuntimeError(f"{j['name']} failed with code {q.returncode}")
    print(label, 'done', time.strftime('%H:%M:%S'), flush=True)


for seed in SEEDS:
    for phase in (1, 2, 3):
        run_pair([job(phase, arm, seed) for arm in ARMS], f'seed{seed}-phase{phase}')
if len(sys.argv) > 1 and sys.argv[1] == 'train-only':
    print('trainings done; evaluation not started', time.strftime('%H:%M:%S'), flush=True)
    sys.exit(0)

commands, outputs = [], []
for arm in ARMS:  # level C, deterministic only (the slowest cell), first
    for seed in SEEDS:
        label, ck = f'{arm}{seed}', job(3, arm, seed)['last']
        res = f'{EVAL}/{label}-levelC-det.json'
        outputs.append((label, 'levelC', 'det', res))
        if not os.path.exists(res):
            commands.append([PY, '-s', 'scripts/eval_architecture.py', ck, '8', res, '900000'] + (['shuffled'] if arm == 'shuffled' else []))
for arm in ARMS:
    for seed in SEEDS:
        label, ck = f'{arm}{seed}', job(3, arm, seed)['last']
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
if DRY:
    print(len(commands), 'evaluation commands pending; first:', ' '.join(commands[0]) if commands else None)
    sys.exit(0)
run_limited(commands)
print('evaluated', time.strftime('%H:%M:%S'), flush=True)
rows = {}
for label, cell, mode, res in outputs:
    r = json.load(open(res))
    rows.setdefault(label, {}).setdefault(cell, {})[mode] = r['total'] if cell == 'levelC' else {k: r[k] for k in ('successes', 'collisions', 'timeouts', 'episodes')}
json.dump(rows, open(f'{EVAL}/summary.json', 'w'), indent=1)
for label, cells in rows.items():
    for cell, modes in cells.items():
        print(label, cell, {m: (c['successes'], c['collisions'], c['timeouts']) for m, c in modes.items()}, flush=True)
analysis = cstats.analyse(cstats.merge([OLD_SUMMARY, f'{EVAL}/summary.json']))
json.dump(analysis, open(f'{EVAL}/analysis.json', 'w'), indent=1)
print('four-seed analysis (frozen rules), runs:', analysis['real_runs'], analysis['shuffled_runs'], 'chain check passes:', analysis.get('chain_check_passes'), flush=True)
for cell, v in analysis['cells'].items():
    print(f"{cell:14s} real {v['real_mean']:6.2f} shuffled {v['shuffled_mean']:6.2f} D {v['difference']:+6.2f} "
          f"95% [{v['ci95'][0]:+.1f}, {v['ci95'][1]:+.1f}] 90% [{v['ci90'][0]:+.1f}, {v['ci90'][1]:+.1f}] margin {v['margin']} -> {v['verdict']}", flush=True)
print('driver done', flush=True)
