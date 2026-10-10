"""Driver for the Phase 3 screening: train both memory windows, then evaluate stages 2 and 4. No Telegram."""
import os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent

PY = sys.executable
RUN = 'runs/training/phase3-screen'
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


env = {**os.environ, 'NOEVAL': '1'}
for arm in ('short442', 'long442'):
    run_guarded([PY, '-s', 'scripts/train_phase3.py', arm, f'{RUN}/{arm}'], env, f'train-{arm}')
    print('trained', arm, time.strftime('%H:%M'), flush=True)
for arm in ('short442', 'long442'):
    for stage in (2, 4):
        label = f'after-{stage * 32768}'
        run_guarded([PY, '-s', 'scripts/eval_checkpoint.py', f'{RUN}/{arm}/stage-{stage}.zip', label, f'{RUN}/{arm}'],
                    None, f'eval-{arm}-{label}')
        print('evaluated', arm, label, time.strftime('%H:%M'), flush=True)
print('driver done', flush=True)
