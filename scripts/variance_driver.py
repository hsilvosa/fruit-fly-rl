"""Driver for the variance study (R1): five training seeds in sequence, each followed by its evaluation."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent

PY = sys.executable
RUN = 'runs/training/variance-study'
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


for seed in (501, 502, 503, 504, 505):
    arm = f'seed{seed}'
    if not os.path.exists(f'{RUN}/{arm}/stage-3.zip'):
      run_guarded([PY, '-s', 'scripts/train_variance.py', arm, f'{RUN}/{arm}'], {**os.environ, 'NOEVAL': '1'}, f'train-{arm}')
      print('trained', arm, time.strftime('%H:%M'), flush=True)
    if os.path.exists(f'{RUN}/{arm}/eval-final.json'):
        continue
    run_guarded([PY, '-s', 'scripts/eval_checkpoint.py', f'{RUN}/{arm}/stage-3.zip', 'final', f'{RUN}/{arm}', 'select,regab'],
                None, f'eval-{arm}')
    print('evaluated', arm, time.strftime('%H:%M'), flush=True)
print('driver done', flush=True)
