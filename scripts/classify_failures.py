"""Record and classify failures of frozen policies on a map profile (evaluation only, no training).

Usage: classify_failures.py <label> <checkpoint.zip> <profile> <seed> <episodes> <output.json>
"""
import json, os, sys, time
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.training.learning import BrainEnv, load_model, checkpoint_sensor_version, checkpoint_history
from fly_rl.simulation.planner import reference_path
from fly_rl.simulation.map_profiles import segments_hit_boxes

label, ckpt, profile, seed, episodes, out = sys.argv[1:7]
seed, episodes = int(seed), int(episodes)
sv = checkpoint_sensor_version(ckpt)
readout = json.loads(open(ckpt[:-4] + '.json').read()).get('readout_version', 'random-pool-256-v1')
env = BrainEnv('data', episodes, 'cuda', seed=seed, mode='dense', dynamics='coordinated', sensor_version=sv,
               map_profile=profile, readout_version=readout, **checkpoint_history(ckpt))
model = load_model(ckpt, env.brain, env, True)
env.seed(seed); features = env.reset()
refs = [reference_path(w.room, w.obstacles, w.position, w.target, fallback=w.reference_route or None) for w in env.worlds]
start = [w.position.copy() for w in env.worlds]; goal = [w.target.copy() for w in env.worlds]
boxes = [np.asarray(w.obstacles).copy() for w in env.worlds]; rooms = [w.room.copy() for w in env.worlds]
traj = [[w.position.copy()] for w in env.worlds]; speed = [[] for _ in env.worlds]
active = np.ones(episodes, bool); rows = {}
for t in range(max(w.episode_limit for w in env.worlds)):
    actions = model.predict(features, deterministic=True)[0]
    features, rewards, dones, infos = env.step(actions)
    for i in np.flatnonzero(active):
        st = infos[i]['transition_state']
        traj[i].append(np.asarray(st['position']).copy()); speed[i].append(float(np.linalg.norm(st['velocity'])))
        if dones[i]:
            rows[i] = {'success': bool(infos[i]['success']), 'collision': bool(infos[i]['collision']),
                       'timeout': bool(infos[i]['truncated']), 'steps': len(traj[i]) - 1,
                       'distance_end': float(infos[i]['distance'])}
            active[i] = False
    if not active.any(): break
env.close()


def arc_progress(points, route):
    route = np.asarray(route, float); seg = np.diff(route, axis=0); ln = np.linalg.norm(seg, axis=1)
    cum = np.concatenate([[0], np.cumsum(ln)]); best = 0.; dist_to_route = []
    for p in points[::5]:
        d = p - route[:-1]; u = np.clip((d * seg).sum(1) / np.maximum(ln ** 2, 1e-12), 0, 1)
        proj = route[:-1] + seg * u[:, None]; dd = np.linalg.norm(p - proj, axis=1); k = int(dd.argmin())
        dist_to_route.append(float(dd[k])); best = max(best, float(cum[k] + u[k] * ln[k]))
    return best / max(cum[-1], 1e-9), float(np.mean(dist_to_route))


report = []
for i in range(episodes):
    r = rows[i]; P = np.asarray(traj[i]); path = float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum())
    net = float(np.linalg.norm(P[-1] - P[0])); d0 = float(np.linalg.norm(goal[i] - start[i]))
    prog, off = arc_progress(P, refs[i]['points'])
    blocked = bool(segments_hit_boxes(np.array([start[i], goal[i]]), boxes[i], 0.16))
    wall = float(np.minimum(P[-1], rooms[i] - P[-1]).min())
    near_box = None
    if len(boxes[i]):
        lo, hi = boxes[i][:, 0, :], boxes[i][:, 1, :]
        near_box = float(np.linalg.norm(np.maximum(0, np.maximum(lo - P[-1], P[-1] - hi)), axis=1).min())
    voxels = len({tuple((p // 2).astype(int)) for p in P})
    if r['success']: cls = 'success'
    elif r['collision']:
        cls = 'collision-room-boundary' if wall < 0.45 and (near_box is None or near_box > 0.45) else 'collision-obstacle'
    elif path < 0.25 * d0: cls = 'timeout-stuck-near-start'
    elif path > 3 * max(net, 1.) : cls = 'timeout-looping'
    else: cls = 'timeout-wandering'
    report.append({**r, 'class': cls, 'direct_line_blocked': blocked, 'start_goal_distance': d0,
                   'reference_route_length': refs[i]['length'], 'reference_status': refs[i]['status'],
                   'route_progress_fraction': prog, 'mean_offset_from_route': off, 'path_length': path,
                   'net_displacement': net, 'visited_2m_cells': voxels, 'final_wall_clearance': wall,
                   'final_obstacle_clearance': near_box, 'mean_speed': float(np.mean(speed[i])) if speed[i] else 0.,
                   'seed': seed + i})
json.dump({'label': label, 'checkpoint': ckpt, 'profile': profile, 'seed': seed, 'episodes': report}, open(out, 'w'), indent=1)
from collections import Counter
c = Counter(x['class'] for x in report)
print(label, dict(c), 'blocked', sum(x['direct_line_blocked'] for x in report), '/', episodes,
      'mean route progress', round(float(np.mean([x['route_progress_fraction'] for x in report])), 3),
      'max', round(max(x['route_progress_fraction'] for x in report), 3), flush=True)
