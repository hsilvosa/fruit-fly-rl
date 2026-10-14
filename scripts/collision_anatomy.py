"""Collision anatomy on the passages profile (evaluation only, no training).
For every episode of a frozen policy: where along the certified route it ended, how far from the route, which obstacle
it hit (partition wall piece or box), its speed, and the angle between its velocity and the direction to the next
route waypoint 4 m ahead and to the goal. Optional STOCHASTIC=1 samples actions.
Usage: collision_anatomy.py <label> <checkpoint.zip> <profile> <seed> <episodes> <output.json>"""
import json, os, sys
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
from fly_rl.training.learning import BrainEnv, load_model, checkpoint_sensor_version, checkpoint_history
from fly_rl.simulation.planner import reference_path
from fly_rl.simulation.world import RADIUS

label, ckpt, profile, seed, episodes, out = sys.argv[1:7]
seed, episodes = int(seed), int(episodes)
det = os.environ.get('STOCHASTIC') != '1'
sv = checkpoint_sensor_version(ckpt)
readout = json.loads(open(ckpt[:-4] + '.json').read()).get('readout_version', 'random-pool-256-v1')
env = BrainEnv('data', episodes, 'cuda', seed=seed, mode='dense', dynamics='coordinated', sensor_version=sv,
               map_profile=profile, readout_version=readout, **checkpoint_history(ckpt))
model = load_model(ckpt, env.brain, env, True)
env.seed(seed); features = env.reset()
refs = [np.asarray(reference_path(w.room, w.obstacles, w.position, w.target, fallback=w.reference_route or None)['points'], float) for w in env.worlds]
goals = [w.target.copy() for w in env.worlds]; boxes = [[(np.asarray(l), np.asarray(h)) for l, h in w.obstacles] for w in env.worlds]
active = np.ones(episodes, bool); rows = {}
last = [None] * episodes
for t in range(max(w.episode_limit for w in env.worlds)):
    before = [w.position.copy() for w in env.worlds]
    actions = model.predict(features, deterministic=det)[0]
    features, rewards, dones, infos = env.step(actions)
    for i in np.flatnonzero(active):
        st = infos[i]['transition_state']
        last[i] = (before[i], np.asarray(st['position']).copy(), np.asarray(st['velocity']).copy())
        if dones[i]:
            rows[int(i)] = {'success': bool(infos[i]['success']), 'collision': bool(infos[i]['collision']), 'timeout': bool(infos[i]['truncated']), 'steps': t + 1}
            active[i] = False
    if not active.any(): break
env.close()


def route_stats(p, route):
    seg = np.diff(route, axis=0); ln = np.linalg.norm(seg, axis=1); cum = np.concatenate([[0], np.cumsum(ln)])
    u = np.clip(((p - route[:-1]) * seg).sum(1) / np.maximum(ln ** 2, 1e-12), 0, 1)
    proj = route[:-1] + seg * u[:, None]; dd = np.linalg.norm(p - proj, axis=1); k = int(dd.argmin())
    return float(dd[k]), float((cum[k] + u[k] * ln[k]) / cum[-1]), float(cum[k] + u[k] * ln[k]), cum, route


def point_at(route, cum, s):
    s = min(s, cum[-1]); return np.array([np.interp(s, cum, route[:, a]) for a in range(3)])


def angle(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.degrees(np.arccos(np.clip(np.dot(a, b) / max(na * nb, 1e-9), -1, 1)))) if na > 1e-6 and nb > 1e-6 else None


report = []
for i in range(episodes):
    r = rows[i]; before, pos, vel = last[i]
    off, prog, s, cum, route = route_stats(pos, refs[i])
    row = {**r, 'seed': seed + i, 'offset_from_route_m': off, 'route_progress': prog, 'route_length': float(cum[-1]),
           'speed': float(np.linalg.norm(vel)), 'distance_to_goal': float(np.linalg.norm(goals[i] - pos))}
    if r['collision']:
        hit = None; best = 1e9
        for lo, hi in boxes[i]:
            d = float(np.linalg.norm(np.maximum(0, np.maximum(lo - pos, pos - hi))))
            if d < best: best, hit = d, (lo, hi)
        size = (hit[1] - hit[0]) if hit is not None else np.zeros(3)
        wall = float(min(pos.min(), (env.worlds[i].room - pos).min()))
        row['hit'] = 'room-boundary' if wall < RADIUS + 0.05 and best > 0.4 else ('partition-piece' if float(size.max()) >= 6. else 'box')
        row['hit_size_max_m'] = float(size.max())
        ahead = point_at(route, cum, s + 4.)
        row['angle_velocity_vs_route_ahead_deg'] = angle(vel, ahead - pos)
        row['angle_velocity_vs_goal_deg'] = angle(vel, goals[i] - pos)
    report.append(row)
json.dump({'label': label, 'checkpoint': ckpt, 'profile': profile, 'seed': seed, 'deterministic': det, 'episodes': report}, open(out, 'w'), indent=1)
col = [x for x in report if x['collision']]
print(label, 'det' if det else 'stoch', 'succ', sum(x['success'] for x in report), 'coll', len(col), 'tmo', sum(x['timeout'] for x in report), flush=True)
if col:
    print('  hit', {k: sum(x['hit'] == k for x in col) for k in ('partition-piece', 'box', 'room-boundary')},
          'offset<1m', sum(x['offset_from_route_m'] < 1. for x in col), 'offset>3m', sum(x['offset_from_route_m'] > 3. for x in col),
          'median offset', round(float(np.median([x['offset_from_route_m'] for x in col])), 2),
          'median route progress', round(float(np.median([x['route_progress'] for x in col])), 2),
          'median speed', round(float(np.median([x['speed'] for x in col])), 2), flush=True)
