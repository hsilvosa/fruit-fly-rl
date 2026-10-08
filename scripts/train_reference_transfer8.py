"""Experiment 8: longer mixed-batch run from the experiment 7 selected checkpoint, two training seeds.
See docs/REFERENCE_TRANSFER_PROTOCOL_8.md. Usage: train_reference_transfer8.py <seed442|seed443> <output-dir>"""
import hashlib, json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
import numpy as np
from stable_baselines3.common.utils import constant_fn
from fly_rl.training.learning import (BrainEnv, load_model, save_model, checkpoint_sensor_version,
                                      checkpoint_readout, checkpoint_history)
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import resolve_profile

ARM, OUT = sys.argv[1], sys.argv[2]
assert ARM in ('seed442', 'seed443')
LR = 3e-4
SOURCE = 'runs/training/reference-transfer-7/mix3e4/stage-2'
MID = 'scripts/profiles/passages-mid.json'
ASSIGN = [None, None, MID, MID, MID, 'passages', 'passages-wide', 'gate-two']
STAGE = 65536
SEED = int(ARM[4:])
CELLS = [('medium', None, 100000, 32), ('medium-b', None, 840000, 32), ('gate-two', 'gate-two', 830000, 32),
         ('gate-long', 'gate-long', 830000, 32), ('passages-wide', 'passages-wide', 830000, 32),
         ('passages-mid', MID, 850000, 32), ('passages', 'passages', 810000, 32)]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run_cells(ck, label, transitions):
    ev = {'label': label, 'transitions_added': transitions, 'checkpoint': ck, 'checkpoint_sha256': sha(ck)}
    procs = []
    for name, prof, seed, n in CELLS:
        out = f'{OUT}/cell-{label}-{name}.json'
        cmd = [sys.executable, '-s', 'scripts/eval_cell.py', ck, prof or 'none', str(seed), str(n), out]
        procs.append((name, out, subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
    for name, out, p in procs:
        if p.wait() != 0:
            raise RuntimeError(f'cell {name} failed')
        ev[name] = json.load(open(out))
    print('EVAL', label, {k: v['successes'] for k, v in ev.items() if isinstance(v, dict)}, flush=True)
    return ev


os.makedirs(OUT, exist_ok=True)
src = SOURCE + '.zip'
src_hash = (sha(src), sha(SOURCE + '.json'))
log = {'arm': ARM, 'learning_rate': LR, 'source': SOURCE, 'source_sha256': src_hash, 'assignment': [a or 'medium' for a in ASSIGN],
       'stage_transitions': STAGE, 'batch': 8, 'gamma': 0.995, 'seed': SEED, 'evaluations': [], 'stages': []}
log['evaluations'].append(run_cells(src, 'baseline-exp7-selected', 0))

sv = checkpoint_sensor_version(src)
env = BrainEnv('data', 8, 'cuda', seed=SEED, mode='dense', dynamics='coordinated', sensor_version=sv,
               map_profile=None, readout_version=checkpoint_readout(src), **checkpoint_history(src))
env.worlds = [FlightWorld(SEED + i, 'dense', None, 'coordinated', sv, resolve_profile(p)) for i, p in enumerate(ASSIGN)]
model = load_model(src, env.brain, env, True)
model.set_random_seed(SEED)
model.gamma = 0.995
model.rollout_buffer.gamma = 0.995
model.lr_schedule = constant_fn(LR)
model.learning_rate = LR
start = model.num_timesteps
for stage in (1, 2, 3, 4):
    t = time.time()
    model.learn(total_timesteps=STAGE, reset_num_timesteps=False)
    out = f'{OUT}/stage-{stage}.zip'
    save_model(model, out, env.brain)
    losses = {k: float(v) for k, v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}
    log['stages'].append({'stage': stage, 'transitions': model.num_timesteps, 'added': model.num_timesteps - start,
                          'seconds': round(time.time() - t), 'losses': losses})
    print('stage', stage, model.num_timesteps, losses, flush=True)
    log['evaluations'].append(run_cells(out, f'after-{stage * STAGE}', stage * STAGE))
    log['source_unchanged'] = (sha(src), sha(SOURCE + '.json')) == src_hash
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
env.close()
print('done; source unchanged:', log['source_unchanged'])
