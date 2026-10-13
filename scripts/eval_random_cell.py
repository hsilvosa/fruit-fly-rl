"""Evaluate a frozen policy on randomized maps at a fixed difficulty (levels A and B). Evaluation only.
Usage: eval_random_cell.py <checkpoint.zip> <train|heldout_b> <difficulty> <seed> <episodes> <output.json> [sampled]"""
import json, os, sys
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.training.learning import BrainEnv, load_model, checkpoint_sensor_version, checkpoint_readout, checkpoint_history
from fly_rl.simulation.random_profiles import RandomProfileWorld, ProfileSampler, DifficultyController

ck, mode, difficulty, seed, n, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
SAMPLED = len(sys.argv) > 7 and sys.argv[7] == 'sampled'  # optional action mode; default deterministic
sv = checkpoint_sensor_version(ck)
env = BrainEnv('data', n, 'cuda', seed=seed, mode='dense', dynamics='coordinated', sensor_version=sv,
               readout_version=checkpoint_readout(ck), **checkpoint_history(ck))
model = load_model(ck, env.brain, env, True)
fixed = DifficultyController(initial=difficulty, window=10 ** 9)  # never updates: the difficulty stays fixed
sampler = ProfileSampler(mode)
env.worlds = [RandomProfileWorld(seed + i, 'dense', None, 'coordinated', sv, sampler=sampler, controller=fixed) for i in range(n)]
env.seed(seed)
features = env.reset()
profiles = [w.current_profile for w in env.worlds]
active = np.ones(n, dtype=bool)
result = {}
for _ in range(max(w.episode_limit for w in env.worlds)):
    actions = model.predict(features, deterministic=not SAMPLED)[0]
    features, rewards, dones, infos = env.step(actions)
    for i in np.flatnonzero(active):
        if dones[i]:
            result[int(i)] = {'success': bool(infos[i]['success']), 'collision': bool(infos[i]['collision']),
                              'timeout': bool(infos[i]['truncated'])}
            active[i] = False
    if not active.any():
        break
json.dump({'successes': sum(r['success'] for r in result.values()), 'collisions': sum(r['collision'] for r in result.values()),
           'timeouts': sum(r['timeout'] for r in result.values()), 'episodes': n, 'finished': len(result),
           'mode': mode, 'actions': 'sampled' if SAMPLED else 'deterministic', 'difficulty': difficulty, 'seed': seed,
           'mean_walls': float(np.mean([p.wall_count for p in profiles])),
           'mean_aperture': float(np.mean([p.aperture_width for p in profiles])),
           'success_seeds': [seed + i for i, r in result.items() if r['success']]}, open(out, 'w'))
