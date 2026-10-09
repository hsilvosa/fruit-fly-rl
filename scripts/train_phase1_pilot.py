"""Phase 1 pilot (experiment 9): stabilized PPO on the mixed profile distribution.
See docs/PHASE1_PILOT_PROTOCOL.md. Usage: train_phase1_pilot.py <seed442|seed443> <output-dir>"""
import hashlib, json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
import numpy as np
from stable_baselines3.common.buffers import RolloutBuffer
from stable_baselines3.common.utils import constant_fn
from fly_rl.training.learning import (BrainEnv, load_model, save_model, checkpoint_sensor_version,
                                      checkpoint_readout, checkpoint_history)
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import resolve_profile

ARM, OUT = sys.argv[1], sys.argv[2]
assert ARM in ('seed442', 'seed443')
SEED = int(ARM[4:])
SOURCE = 'runs/training/reference-transfer-7/mix3e4/stage-2'
MID = 'scripts/profiles/passages-mid.json'
ASSIGN = [None] * 8 + [MID] * 12 + ['passages'] * 4 + ['passages-wide'] * 4 + ['gate-two'] * 4
STAGE, STAGES = 32768, 3
EVAL_STAGES = {3}  # reduced after the resource incident; see docs/PHASE1_PILOT_PROTOCOL.md
BUDGET = STAGE * STAGES
LR0, LR1 = 3e-4, 3e-5
OLD = [('medium', None, 100000), ('medium-b', None, 840000), ('gate-two', 'gate-two', 830000),
       ('gate-long', 'gate-long', 830000), ('passages-wide', 'passages-wide', 830000),
       ('passages-mid', MID, 850000), ('passages', 'passages', 810000)]
SEL = [('medium', None, 860000), ('medium-b', None, 861000), ('gate-two', 'gate-two', 862000),
       ('gate-long', 'gate-long', 862000), ('passages-wide', 'passages-wide', 863000),
       ('passages-mid', MID, 864000), ('passages', 'passages', 865000)]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run_cells(ck, label, transitions, pools):
    sys.path.insert(0, 'scripts')
    from resource_guard import run_limited
    ev = {'label': label, 'transitions_added': transitions, 'checkpoint': ck, 'checkpoint_sha256': sha(ck)}
    commands, outputs = [], []
    for pool, cells in pools:
        for name, prof, seed in cells:
            out = f'{OUT}/cell-{label}-{pool}-{name}.json'
            outputs.append((pool, name, out))
            if not os.path.exists(out):
                commands.append([sys.executable, '-s', 'scripts/eval_cell.py', ck, prof or 'none', str(seed), '32', out])
    run_limited(commands)
    for pool, name, out in outputs:
        ev.setdefault(pool, {})[name] = json.load(open(out))
    for pool, _ in pools:
        print('EVAL', label, pool, {k: v['successes'] for k, v in ev[pool].items()}, flush=True)
    return ev


os.makedirs(OUT, exist_ok=True)
src = SOURCE + '.zip'
src_hash = (sha(src), sha(SOURCE + '.json'))
log = {'arm': ARM, 'source': SOURCE, 'source_sha256': src_hash, 'assignment': [a or 'medium' for a in ASSIGN],
       'budget': BUDGET, 'stage': STAGE, 'lr': [LR0, LR1], 'clip_range': 0.1, 'n_epochs': 3, 'batch_size': 256,
       'n_steps': 128, 'target_kl': 0.02, 'envs': len(ASSIGN), 'seed': SEED, 'stages': [], 'evaluations': []}
if SEED == 442 and not os.environ.get('NOEVAL'):
    log['evaluations'].append(run_cells(src, 'baseline', 0, [('select', SEL)]))

sv = checkpoint_sensor_version(src)
env = BrainEnv('data', len(ASSIGN), 'cuda', seed=SEED, mode='dense', dynamics='coordinated', sensor_version=sv,
               map_profile=None, readout_version=checkpoint_readout(src), **checkpoint_history(src))
env.worlds = [FlightWorld(SEED + i, 'dense', None, 'coordinated', sv, resolve_profile(p)) for i, p in enumerate(ASSIGN)]
model = load_model(src, env.brain, env, True)
model.set_random_seed(SEED)
model.gamma = 0.995
model.n_steps = 128
model.batch_size = 256
model.n_epochs = 3
model.clip_range = constant_fn(0.1)
model.target_kl = 0.02
model.rollout_buffer = RolloutBuffer(128, model.observation_space, model.action_space, device=model.device,
                                     gamma=0.995, gae_lambda=model.gae_lambda, n_envs=len(ASSIGN))
start = model.num_timesteps
model.lr_schedule = lambda _remaining: LR0 + (LR1 - LR0) * min(1.0, (model.num_timesteps - start) / BUDGET)
for stage in range(1, STAGES + 1):
    t = time.time()
    model.learn(total_timesteps=STAGE, reset_num_timesteps=False)
    out = f'{OUT}/stage-{stage}.zip'
    schedule = model.lr_schedule
    model.lr_schedule = constant_fn(float(schedule(0.0)))  # a closure over the model cannot be pickled
    save_model(model, out, env.brain)
    model.lr_schedule = schedule
    losses = {k: float(v) for k, v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}
    log['stages'].append({'stage': stage, 'added': model.num_timesteps - start, 'seconds': round(time.time() - t), 'losses': losses})
    print('stage', stage, model.num_timesteps - start, round(time.time() - t), 's',
          {k: round(v, 4) for k, v in losses.items() if k in ('train/learning_rate', 'train/approx_kl', 'train/clip_fraction', 'train/value_loss')}, flush=True)
    if not os.environ.get('NOEVAL') and stage in EVAL_STAGES:
        log['evaluations'].append(run_cells(out, f'after-{stage * STAGE}', stage * STAGE, [('select', SEL)]))
    log['source_unchanged'] = (sha(src), sha(SOURCE + '.json')) == src_hash
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
env.close()
print('done; source unchanged:', log['source_unchanged'])
