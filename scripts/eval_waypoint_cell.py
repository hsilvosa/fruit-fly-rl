"""Evaluate a waypoint-diagnostic checkpoint on one cell (evaluation only). Privileged: never a student result.
Usage: eval_waypoint_cell.py <checkpoint.zip> <profile|none> <seed> <episodes> <out.json> <waypoint|control> [stochastic]"""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
import numpy as np
from stable_baselines3 import PPO
from fly_rl.training.learning import checkpoint_sensor_version, checkpoint_readout, checkpoint_history
from fly_rl.training.waypoint_diagnostic import WaypointBrainEnv

ck, prof, seed, n, out, arm = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
det = not (len(sys.argv) > 7 and sys.argv[7] == 'stochastic')
SOURCE = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
sv = checkpoint_sensor_version(SOURCE)
env = WaypointBrainEnv('data', n, 'cuda', seed=seed, mode='dense', dynamics='coordinated', sensor_version=sv,
                       map_profile=None if prof == 'none' else prof, readout_version=checkpoint_readout(SOURCE),
                       privileged=(arm == 'waypoint'), **checkpoint_history(SOURCE))
model = PPO.load(ck, env=env, device='cpu')
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
