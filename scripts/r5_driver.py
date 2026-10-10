"""Driver for R5: train three seeds on the randomized distribution, then evaluate R5 and control checkpoints.
Resumable. See docs/RANDOM_DISTRIBUTION_PROTOCOL.md."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, run_limited

PY = sys.executable
RUN = 'runs/training/random-run'
START = 'runs/training/reference-transfer-7/mix3e4/stage-2'
SEEDS = (601, 602, 603)
CONTROL = {s: f'runs/training/variance-study/seed{s}/stage-3.zip' for s in (501, 502, 503, 504, 505)}
RANDOM_CELLS = [('randomA-0.5', 'train', '0.5', '890000'), ('randomA-0.9', 'train', '0.9', '891000'),
                ('randomB-dev', 'heldout_b', '0.8', '950000')]
os.makedirs(RUN, exist_ok=True)


def run_guarded(cmd, env=None, name=''):
    proc = subprocess.Popen(cmd, env=env, stdout=open(f'{RUN}/{name}.log', 'w'), stderr=subprocess.STDOUT)
    while proc.poll() is None:
        time.sleep(10)
        if memory_used_percent() > 92:
            proc.kill()
            raise RuntimeError(f'memory limit while running {name}')
    if proc.returncode != 0:
        raise RuntimeError(f'{name} failed with code {proc.returncode}')


def random_cell_commands(ck, label, out_dir):
    commands = []
    for name, mode, difficulty, seed in RANDOM_CELLS:
        out = f'{out_dir}/random-{label}-{name}.json'
        if not os.path.exists(out):
            commands.append([PY, '-s', 'scripts/eval_random_cell.py', ck, mode, difficulty, seed, '64', out])
    return commands


for seed in SEEDS:
    arm = f'seed{seed}'
    if not os.path.exists(f'{RUN}/{arm}/stage-3.zip'):
        run_guarded([PY, '-s', 'scripts/train_random.py', START, str(seed), f'{RUN}/{arm}', '3'], None, f'train-{arm}')
        print('trained', arm, time.strftime('%H:%M'), flush=True)
for seed in SEEDS:
    arm = f'seed{seed}'
    ck = f'{RUN}/{arm}/stage-3.zip'
    if not os.path.exists(f'{RUN}/{arm}/eval-final.json'):
        run_guarded([PY, '-s', 'scripts/eval_checkpoint.py', ck, 'final', f'{RUN}/{arm}', 'select,regab'], None, f'eval-{arm}')
    run_limited(random_cell_commands(ck, 'final', f'{RUN}/{arm}'))
    print('evaluated', arm, time.strftime('%H:%M'), flush=True)
for seed, ck in CONTROL.items():
    out_dir = f'{RUN}/control-seed{seed}'
    os.makedirs(out_dir, exist_ok=True)
    run_limited(random_cell_commands(ck, 'final', out_dir))
    print('evaluated control', seed, time.strftime('%H:%M'), flush=True)
out = f'{RUN}/level-c-baseline-start.json'
if not os.path.exists(out):
    run_guarded([PY, '-s', 'scripts/eval_architecture.py', START + '.zip', '8', out, '900000'], None, 'level-c-baseline')
    print('level C baseline', time.strftime('%H:%M'), flush=True)
print('driver done', flush=True)
