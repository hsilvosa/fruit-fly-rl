"""Driver for the Phase 3 replication: train the long window with seed 443, then evaluate all four stages."""
import os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent

PY = sys.executable
RUN = 'runs/training/phase3-screen'
ARM = 'long443'


def run_guarded(cmd, env=None, name=''):
    proc = subprocess.Popen(cmd, env=env, stdout=open(f'{RUN}/{name}.log', 'w'), stderr=subprocess.STDOUT)
    while proc.poll() is None:
        time.sleep(10)
        if memory_used_percent() > 92:
            proc.kill()
            raise RuntimeError(f'memory limit while running {name}')
    if proc.returncode != 0:
        raise RuntimeError(f'{name} failed with code {proc.returncode}')


run_guarded([PY, '-s', 'scripts/train_phase3.py', ARM, f'{RUN}/{ARM}'], {**os.environ, 'NOEVAL': '1'}, f'train-{ARM}')
print('trained', ARM, time.strftime('%H:%M'), flush=True)
for stage in (4, 2, 3, 1):
    label = f'after-{stage * 32768}'
    run_guarded([PY, '-s', 'scripts/eval_checkpoint.py', f'{RUN}/{ARM}/stage-{stage}.zip', label, f'{RUN}/{ARM}'],
                None, f'eval-{ARM}-{label}')
    print('evaluated', ARM, label, time.strftime('%H:%M'), flush=True)
print('driver done', flush=True)
