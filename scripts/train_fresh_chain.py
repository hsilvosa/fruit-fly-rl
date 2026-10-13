"""C1.0 phase 1: a fresh policy trained only on medium dense rooms, with the real connectome ('real') or the edge-shuffled one ('shuffled').
See docs/CONNECTOME_CONTROL_PROTOCOL.md. Usage: train_fresh_chain.py <real|shuffled> <seed> <output-dir> [stages, default 27]
The policy starts from random weights (declared control, not the retained lineage)."""
import hashlib, json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
import numpy as np
from stable_baselines3.common.buffers import RolloutBuffer
from stable_baselines3.common.utils import constant_fn
from fly_rl.training.learning import BrainEnv, make_policy, save_model, checkpoint_sensor_version
from fly_rl.connectome.shuffled import ShuffledBrain

ARM, SEED, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3]
assert ARM in ('real', 'shuffled')
STAGE, STAGES = 32768, int(sys.argv[4]) if len(sys.argv) > 4 else 27
START = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'  # only read for its sensor version, never loaded as weights
SHUFFLE_SEED = 1
ENVS = 32
BUDGET = STAGE * STAGES
LR0, LR1 = 3e-4, 3e-5

os.makedirs(OUT, exist_ok=True)
sv = checkpoint_sensor_version(START)
brain = ShuffledBrain(SHUFFLE_SEED, 'data', ENVS, 'cuda', sensor_version=sv) if ARM == 'shuffled' else None
env = BrainEnv('data', ENVS, 'cuda', seed=SEED, brain=brain, mode='dense', dynamics='coordinated', sensor_version=sv, map_profile=None,
               readout_version='random-pool-256-v1')
model = make_policy(env, seed=SEED)
model.tensorboard_log = None
model.gamma = 0.995
model.n_steps = 128
model.batch_size = 256
model.n_epochs = 3
model.clip_range = constant_fn(0.1)
model.target_kl = 0.02
model.rollout_buffer = RolloutBuffer(128, model.observation_space, model.action_space, device=model.device,
                                     gamma=0.995, gae_lambda=model.gae_lambda, n_envs=ENVS)
start = model.num_timesteps
model.lr_schedule = lambda _remaining: LR0 + (LR1 - LR0) * min(1.0, (model.num_timesteps - start) / BUDGET)
log = {'arm': ARM, 'seed': SEED, 'init': 'random weights', 'fingerprint': env.brain.fingerprint, 'sensor_version': sv,
       'assignment': ['medium'] * ENVS, 'budget': BUDGET, 'stage': STAGE, 'lr': [LR0, LR1], 'clip_range': 0.1, 'n_epochs': 3,
       'batch_size': 256, 'n_steps': 128, 'target_kl': 0.02, 'gamma': 0.995, 'envs': ENVS, 'stages': []}
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
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
env.close()
print('done', flush=True)
