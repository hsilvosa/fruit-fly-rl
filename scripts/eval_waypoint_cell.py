"""Evaluate a waypoint-diagnostic or student checkpoint on one cell (evaluation only).
Arms: waypoint (privileged input, diagnostic only), control, aux, critic (students: the actor is blind to the route input, which is zeros here).
Profile heldout_b draws level B development maps (held-out sampler, difficulty 0.8).
Usage: eval_waypoint_cell.py <checkpoint.zip> <profile|none|heldout_b> <seed> <episodes> <out.json> <arm> [stochastic]"""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
import numpy as np
from stable_baselines3 import PPO
from fly_rl.training.waypoint_students import AuxPPO
from fly_rl.simulation.random_profiles import RandomProfileWorld, ProfileSampler, DifficultyController
from fly_rl.training.learning import checkpoint_sensor_version, checkpoint_readout, checkpoint_history
from fly_rl.training.waypoint_diagnostic import WaypointBrainEnv

ck, prof, seed, n, out, arm = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
det = not (len(sys.argv) > 7 and sys.argv[7] == 'stochastic')
SOURCE = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
sv = checkpoint_sensor_version(SOURCE)
env = WaypointBrainEnv('data', n, 'cuda', seed=seed, mode='dense', dynamics='coordinated', sensor_version=sv,
                       map_profile=None if prof in ('none', 'heldout_b') else prof, readout_version=checkpoint_readout(SOURCE),
                       privileged=(arm == 'waypoint'), **checkpoint_history(SOURCE))
if prof == 'heldout_b':
    fixed = DifficultyController(initial=0.8, window=10 ** 9); sampler = ProfileSampler('heldout_b')
    env.worlds = [RandomProfileWorld(seed + i, 'dense', None, 'coordinated', sv, sampler=sampler, controller=fixed) for i in range(n)]
model = (AuxPPO if arm in ('aux', 'critic', 'pre') else PPO).load(ck, env=env, device='cpu')
env.seed(seed); features = env.reset()
active = np.ones(n, bool); rows = {}
for _ in range(max(w.episode_limit for w in env.worlds)):
    actions = model.predict(features, deterministic=det)[0]
    features, rewards, dones, infos = env.step(actions)
    for i in np.flatnonzero(active):
        if dones[i]:
            rows[int(i)] = (bool(infos[i]['success']), bool(infos[i]['collision']), bool(infos[i]['truncated'])); active[i] = False
    if not active.any(): break
json.dump({'successes': sum(r[0] for r in rows.values()), 'collisions': sum(r[1] for r in rows.values()),
           'timeouts': sum(r[2] for r in rows.values()), 'episodes': n, 'finished': len(rows), 'deterministic': det,
           'arm': arm, 'checkpoint': ck}, open(out, 'w'))
