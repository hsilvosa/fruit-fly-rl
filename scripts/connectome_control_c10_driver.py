"""Driver for C1.0 (feasibility of the fresh two-arm chain, phase 1 only). Trains the real-connectome arm and the edge-shuffled arm
(seed 1001, 27 stages = 884,736 transitions, medium rooms only, random initial weights), then evaluates medium on pool 887000.
The two trainings run in parallel under the raised ceiling (95 percent, user decision of October 13); if the mean CPU over the first
two minutes of overlap exceeds 93 percent, the shuffled training is stopped and run after the real one. A resource log is written.
Resumable by cell; an interrupted training restarts from scratch (delete its directory first). See docs/CONNECTOME_CONTROL_PROTOCOL.md."""
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
SEED = 1001
STAGES = 27
POINTS = [9, 18, 27]
POOL = '887000'
EPISODES = '64'
START = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
ARMS = ['real', 'shuffled']
TRAIN_THREADS = '5'
os.makedirs(RUN, exist_ok=True)
resource_log = open(f'{RUN}/c10-resources.log', 'a')


def out_dir(arm):
    return f'{RUN}/phase1-{arm}{SEED}'


def launch(arm):
    env = {**os.environ, **{k: TRAIN_THREADS for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS')}}
    return subprocess.Popen([PY, '-s', 'scripts/train_fresh_chain.py', arm, str(SEED), out_dir(arm), str(STAGES)],
                            stdout=open(f'{RUN}/train-phase1-{arm}{SEED}.log', 'w'), stderr=subprocess.STDOUT, env=env)


def watch(procs, label):
    """Wait for the processes, sampling CPU and memory every 10 s. Kills everything above the memory ceiling."""
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


pending = [a for a in ARMS if not os.path.exists(f'{out_dir(a)}/stage-{STAGES}.zip')]
if pending:
    procs = {}
    for arm in pending:
        procs[arm] = launch(arm)
        time.sleep(45)  # let the first one finish loading the connectome before the next starts
    if len(procs) == 2:
        samples = [cpu_percent(2.0) for _ in range(40)]  # about two minutes of overlap
        mean_cpu = sum(samples) / len(samples)
        print('overlap mean cpu', round(mean_cpu), 'mem', round(memory_used_percent()), flush=True)
        if mean_cpu > 93:
            print('CPU above 93 percent with both arms: running the shuffled arm after the real one', flush=True)
            procs['shuffled'].kill(); procs['shuffled'].wait()
            shutil.rmtree(out_dir('shuffled'), ignore_errors=True)
            del procs['shuffled']
    watch(procs, 'training')
    for arm, p in procs.items():
        if p.returncode != 0:
            raise RuntimeError(f'training of {arm} failed with code {p.returncode}')
    print('trained', list(procs), time.strftime('%H:%M:%S'), flush=True)
    for arm in ARMS:
        if not os.path.exists(f'{out_dir(arm)}/stage-{STAGES}.zip'):
            p = {arm: launch(arm)}
            watch(p, 'training-' + arm)
            if p[arm].returncode != 0:
                raise RuntimeError(f'training of {arm} failed with code {p[arm].returncode}')
            print('trained', arm, time.strftime('%H:%M:%S'), flush=True)

jobs = [('start', 'real', START)] + [(f'{arm}-s{p}', arm, f'{out_dir(arm)}/stage-{p}.zip') for arm in ARMS for p in POINTS]
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
