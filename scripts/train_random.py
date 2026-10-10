"""R5: stabilized PPO on the randomized map distribution (Phase 2).

Mix of 32 simulators: 8 original medium rooms (kept to catch forgetting), 4 two-gate rooms, 20 randomized
partitioned rooms from the training sampler (the level B region excluded) under an adaptive difficulty controller.
Settings are the Phase 1 stabilization bundle. See docs/RANDOM_DISTRIBUTION_PROTOCOL.md.

Usage: train_random.py <start checkpoint without .zip> <seed> <output-dir> <stages>
"""
import hashlib, json, os, sys, time
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from stable_baselines3.common.buffers import RolloutBuffer
from stable_baselines3.common.utils import constant_fn
from fly_rl.training.learning import (BrainEnv, load_model, save_model, checkpoint_sensor_version,
                                      checkpoint_readout, checkpoint_history)
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import resolve_profile
from fly_rl.simulation.random_profiles import RandomProfileWorld, ProfileSampler, DifficultyController

SOURCE, SEED, OUT, STAGES = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
STAGE = int(os.environ.get("STAGE_OVERRIDE", 32768))
BUDGET = STAGE * STAGES
LR0, LR1 = 3e-4, 3e-5
N_MEDIUM, N_GATE, N_RANDOM = 8, 4, 20


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


os.makedirs(OUT, exist_ok=True)
src = SOURCE + '.zip'
src_hash = (sha(src), sha(SOURCE + '.json'))
sv = checkpoint_sensor_version(src)
n = N_MEDIUM + N_GATE + N_RANDOM
env = BrainEnv('data', n, 'cuda', seed=SEED, mode='dense', dynamics='coordinated', sensor_version=sv,
               map_profile=None, readout_version=checkpoint_readout(src), **checkpoint_history(src))
controller = DifficultyController(initial=0.2, window=64, up=0.7, down=0.3, step=0.05)
sampler = ProfileSampler('train')
worlds = [FlightWorld(SEED + i, 'dense', None, 'coordinated', sv, None) for i in range(N_MEDIUM)]
worlds += [FlightWorld(SEED + N_MEDIUM + i, 'dense', None, 'coordinated', sv, resolve_profile('gate-two')) for i in range(N_GATE)]
worlds += [RandomProfileWorld(SEED + N_MEDIUM + N_GATE + i, 'dense', None, 'coordinated', sv, sampler=sampler, controller=controller)
           for i in range(N_RANDOM)]
env.worlds = worlds
model = load_model(src, env.brain, env, True)
model.set_random_seed(SEED)
model.gamma = 0.995
model.n_steps, model.batch_size, model.n_epochs = 128, 256, 3
model.clip_range = constant_fn(0.1)
model.target_kl = 0.02
model.rollout_buffer = RolloutBuffer(128, model.observation_space, model.action_space, device=model.device,
                                     gamma=0.995, gae_lambda=model.gae_lambda, n_envs=n)
model.tensorboard_log = None
start = model.num_timesteps
model.lr_schedule = lambda _remaining: LR0 + (LR1 - LR0) * min(1.0, (model.num_timesteps - start) / BUDGET)
log = {'source': SOURCE, 'source_sha256': src_hash, 'seed': SEED, 'stages_planned': STAGES, 'mix': {'medium': N_MEDIUM, 'gate-two': N_GATE, 'random': N_RANDOM},
       'lr': [LR0, LR1], 'sampler': 'train', 'controller': {'initial': 0.2, 'window': 64, 'up': 0.7, 'down': 0.3, 'step': 0.05}, 'stages': []}
for stage in range(1, STAGES + 1):
    t = time.time()
    model.learn(total_timesteps=STAGE, reset_num_timesteps=False)
    out = f'{OUT}/stage-{stage}.zip'
    schedule = model.lr_schedule
    model.lr_schedule = constant_fn(float(schedule(0.0)))  # a closure over the model cannot be pickled
    save_model(model, out, env.brain)
    model.lr_schedule = schedule
    profiles = [w.current_profile for w in worlds[N_MEDIUM + N_GATE:] if w.current_profile is not None]
    log['stages'].append({'stage': stage, 'added': model.num_timesteps - start, 'seconds': round(time.time() - t),
                          'difficulty': controller.difficulty, 'controller_history': controller.history[-8:],
                          'current_profile_walls_mean': float(np.mean([p.wall_count for p in profiles])),
                          'current_profile_aperture_mean': float(np.mean([p.aperture_width for p in profiles]))})
    print('stage', stage, round(time.time() - t), 's difficulty', round(controller.difficulty, 2),
          'walls', round(log['stages'][-1]['current_profile_walls_mean'], 1), flush=True)
    log['source_unchanged'] = (sha(src), sha(SOURCE + '.json')) == src_hash
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
env.close()
print('done; source unchanged:', log['source_unchanged'])
