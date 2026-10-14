"""C1.1 phase 2: the B2 recipe (61 stages, 1,998,848 transitions, mixed partitioned rooms) from a phase 1 checkpoint of the fresh chain,
with the real connectome ('real') or the edge-shuffled one ('shuffled'). See docs/experiments/connectome-control/CONNECTOME_CONTROL_PROTOCOL_C11.md.
Usage: train_fresh_phase2.py <real|shuffled> <seed> <phase1-checkpoint.zip> <output-dir> [stages, default 61] [layout offset, default 0]
A nonzero offset shifts the simulator layout seeds (SEED + offset + index) so that a continuation does not replay the layouts of the earlier phase."""
import hashlib, json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
import numpy as np
from stable_baselines3.common.buffers import RolloutBuffer
from stable_baselines3.common.utils import constant_fn
from fly_rl.training.learning import BrainEnv, load_model, save_model, checkpoint_sensor_version, checkpoint_readout, checkpoint_history
from fly_rl.connectome.shuffled import ShuffledBrain
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import resolve_profile

ARM, SEED, SRC, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
assert ARM in ('real', 'shuffled')
STAGE, STAGES = 32768, int(sys.argv[5]) if len(sys.argv) > 5 else 61
OFFSET = int(sys.argv[6]) if len(sys.argv) > 6 else 0
MID = 'scripts/profiles/passages-mid.json'
ASSIGN = [None] * 8 + [MID] * 12 + ['passages'] * 4 + ['passages-wide'] * 4 + ['gate-two'] * 4
BUDGET = STAGE * STAGES
LR0, LR1 = 3e-4, 3e-5
SHUFFLE_SEED = 1


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


os.makedirs(OUT, exist_ok=True)
src_hash = (sha(SRC), sha(SRC[:-4] + '.json'))
sv = checkpoint_sensor_version(SRC)
brain = ShuffledBrain(SHUFFLE_SEED, 'data', len(ASSIGN), 'cuda', sensor_version=sv) if ARM == 'shuffled' else None
env = BrainEnv('data', len(ASSIGN), 'cuda', seed=SEED, brain=brain, mode='dense', dynamics='coordinated', sensor_version=sv,
               map_profile=None, readout_version=checkpoint_readout(SRC), **checkpoint_history(SRC))
env.worlds = [FlightWorld(SEED + OFFSET + i, 'dense', None, 'coordinated', sv, resolve_profile(p)) for i, p in enumerate(ASSIGN)]
model = load_model(SRC, env.brain, env, True)
model.set_random_seed(SEED + OFFSET)
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
log = {'arm': ARM, 'seed': SEED, 'layout_offset': OFFSET, 'source': SRC, 'source_sha256': src_hash, 'fingerprint': env.brain.fingerprint,
       'assignment': [a or 'medium' for a in ASSIGN], 'budget': BUDGET, 'stage': STAGE, 'lr': [LR0, LR1], 'clip_range': 0.1,
       'n_epochs': 3, 'batch_size': 256, 'n_steps': 128, 'target_kl': 0.02, 'envs': len(ASSIGN), 'stages': []}
for stage in range(1, STAGES + 1):
    t = time.time()
    model.learn(total_timesteps=STAGE, reset_num_timesteps=False)
    schedule = model.lr_schedule
    model.lr_schedule = constant_fn(float(schedule(0.0)))  # a closure over the model cannot be pickled
    save_model(model, f'{OUT}/stage-{stage}.zip', env.brain)
    model.lr_schedule = schedule
    losses = {k: float(v) for k, v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}
    log['stages'].append({'stage': stage, 'added': model.num_timesteps - start, 'seconds': round(time.time() - t), 'losses': losses})
    print('stage', stage, model.num_timesteps - start, round(time.time() - t), 's',
          {k: round(v, 4) for k, v in losses.items() if k in ('train/learning_rate', 'train/approx_kl', 'train/clip_fraction', 'train/value_loss')}, flush=True)
    log['source_unchanged'] = (sha(SRC), sha(SRC[:-4] + '.json')) == src_hash
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
env.close()
print('done; source unchanged:', log['source_unchanged'], flush=True)
