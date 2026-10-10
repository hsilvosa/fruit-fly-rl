"""Evaluate a frozen policy on the synthetic architectural scenes (level C). Evaluation only, no training.

Every one of the 21 situations runs with K initial headings (the only randomness). Output: per-situation outcomes.
Usage: eval_architecture.py <checkpoint.zip> <headings per situation> <output.json> [seed]
"""
import json, os, sys, time
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.training.learning import BrainEnv, load_model, checkpoint_sensor_version, checkpoint_readout, checkpoint_history
from fly_rl.simulation.architectural_transfer import ArchitecturalSceneWorld, all_situations

ck, k, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 900000
sv = checkpoint_sensor_version(ck)
env = BrainEnv('data', k, 'cuda', seed=seed, mode='empty', dynamics='coordinated', sensor_version=sv,
               readout_version=checkpoint_readout(ck), **checkpoint_history(ck))
model = load_model(ck, env.brain, env, True)
rows = []
started = time.time()
for scene, index, name in all_situations():
    env.worlds = [ArchitecturalSceneWorld(scene, index, seed + i, sv) for i in range(k)]
    env.seed(seed)
    features = env.reset()
    active = np.ones(k, dtype=bool)
    result = {}
    for _ in range(max(w.episode_limit for w in env.worlds)):
        actions = model.predict(features, deterministic=True)[0]
        features, rewards, dones, infos = env.step(actions)
        for i in np.flatnonzero(active):
            if dones[i]:
                result[int(i)] = {'success': bool(infos[i]['success']), 'collision': bool(infos[i]['collision']),
                                  'timeout': bool(infos[i]['truncated']), 'distance_end': float(infos[i]['distance'])}
                active[i] = False
        if not active.any():
            break
    rows.append({'scene': scene, 'situation': name, 'index': index, 'headings': k,
                 'successes': sum(r['success'] for r in result.values()),
                 'collisions': sum(r['collision'] for r in result.values()),
                 'timeouts': sum(r['timeout'] for r in result.values()), 'finished': len(result)})
    print(scene, name, rows[-1]['successes'], '/', k, flush=True)
total = {kk: sum(r[kk] for r in rows) for kk in ('successes', 'collisions', 'timeouts', 'finished')}
total['episodes'] = k * len(rows)
per_scene = {}
for r in rows:
    d = per_scene.setdefault(r['scene'], {'successes': 0, 'episodes': 0})
    d['successes'] += r['successes']; d['episodes'] += r['headings']
json.dump({'checkpoint': ck, 'seed': seed, 'headings': k, 'total': total, 'per_scene': per_scene, 'situations': rows,
           'seconds': round(time.time() - started)}, open(out, 'w'), indent=1)
print('TOTAL', total, per_scene, flush=True)
