"""Driver for the Phase 1 run: train seed 442, train seed 443, then evaluate all checkpoints.
Sends Telegram updates at milestones and stops a child that pushes memory above 88 percent."""
import json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import memory_used_percent, cpu_percent

PY = sys.executable
RUN = 'runs/training/phase1-run'


def notify(text):
    subprocess.run(['hermes', 'send', '-t', 'telegram', text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_guarded(cmd, env=None, name=''):
    proc = subprocess.Popen(cmd, env=env, stdout=open(f'{RUN}/{name}.log', 'w'), stderr=subprocess.STDOUT)
    peak_cpu = peak_mem = 0.0
    while proc.poll() is None:
        time.sleep(10)
        mem = memory_used_percent()
        peak_mem = max(peak_mem, mem)
        if mem > 88:
            proc.kill()
            notify(f'Fly RL: paro {name}, la memoria llego a {mem:.0f}%.')
            raise RuntimeError('memory limit')
    if proc.returncode != 0:
        notify(f'Fly RL: {name} fallo (codigo {proc.returncode}).')
        raise RuntimeError(name)
    return peak_mem


env = {**os.environ, 'NOEVAL': '1'}
notify('Fly RL fase 1: empieza el entrenamiento de la semilla 442 (4 etapas, unos 6 min).')
for seed in (442, 443):
    t = time.time()
    peak = run_guarded([PY, '-s', 'scripts/train_phase1_run.py', f'seed{seed}', f'{RUN}/seed{seed}'], env, f'train-seed{seed}')
    notify(f'Fly RL fase 1: semilla {seed} entrenada en {(time.time() - t) / 60:.1f} min (RAM maxima {peak:.0f}%). '
           + ('Sigue la semilla 443.' if seed == 442 else 'Empiezan las evaluaciones.'))
for seed in (442, 443):
    for stage in (1, 2, 3, 4):
        label = f'after-{stage * 32768}'
        run_guarded([PY, '-s', 'scripts/eval_checkpoint.py', f'{RUN}/seed{seed}/stage-{stage}.zip', label, f'{RUN}/seed{seed}'],
                    None, f'eval-seed{seed}-{label}')
        e = json.load(open(f'{RUN}/seed{seed}/eval-{label}.json'))
        fmt = lambda pool: ' '.join(f"{k[:6]}={v['successes']}" for k, v in e[pool].items())
        notify(f'Fly RL fase 1 | semilla {seed} | {label}\nseleccion: {fmt("select")}\nviejos: {fmt("old")}')
notify('Fly RL fase 1: evaluaciones terminadas. Preparo el resumen.')
print('driver done')
