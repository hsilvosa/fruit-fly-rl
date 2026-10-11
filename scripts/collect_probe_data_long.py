"""Long-range variant: also stores the same 8 m ray directions cast to 24 m (rays24) and the 72x25 panorama cast to 24 m (pano24),
normalized by 24, at the world state of each stored sample. Collect (policy features, raw sensors, labels) from rollouts of a frozen policy on passages. Evaluation only, no training.
Labels: unit vector, in the body frame, to the certified-route point 4 m and 8 m ahead of the fly's current progress; unit vector to the goal;
and whether the straight line to the goal is blocked. Every 3rd step is stored.
Usage: collect_probe_data.py <checkpoint.zip> <profile> <seed> <episodes> <output.npz>"""
import json, os, sys
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
from fly_rl.training.learning import BrainEnv, load_model, checkpoint_sensor_version, checkpoint_history
from fly_rl.simulation.planner import reference_path
from fly_rl.simulation.map_profiles import segments_hit_boxes
from fly_rl.simulation.world import RADIUS
from fly_rl.simulation.sensors import DIRECTIONS, panorama_directions

ckpt, profile, seed, episodes, out = sys.argv[1:6]
seed, episodes = int(seed), int(episodes)
sv = checkpoint_sensor_version(ckpt)
readout = json.loads(open(ckpt[:-4] + '.json').read()).get('readout_version', 'random-pool-256-v1')
env = BrainEnv('data', episodes, 'cuda', seed=seed, mode='dense', dynamics='coordinated', sensor_version=sv,
               map_profile=profile, readout_version=readout, **checkpoint_history(ckpt))
model = load_model(ckpt, env.brain, env, True)
env.seed(seed); features = env.reset()
sensors0 = env.latest_sensors.copy()
refs = [np.asarray(reference_path(w.room, w.obstacles, w.position, w.target, fallback=w.reference_route or None)['points'], float) for w in env.worlds]
cums = []
for r in refs:
    ln = np.linalg.norm(np.diff(r, axis=0), axis=1); cums.append(np.concatenate([[0], np.cumsum(ln)]))
goals = [w.target.copy() for w in env.worlds]; boxes = [np.asarray(w.obstacles).copy() for w in env.worlds]
active = np.ones(episodes, bool)
F, S, L4, L8, LG, BL, EP, ST, OFF, R24, P24 = [], [], [], [], [], [], [], [], [], [], []
PANO = panorama_directions()


def body(delta, yaw):
    c, s = np.cos(yaw), np.sin(yaw)
    rot = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])
    v = delta @ rot
    return v / max(np.linalg.norm(v), 1e-9)


def ahead(route, cum, p, dist):
    seg = np.diff(route, axis=0); ln = np.linalg.norm(seg, axis=1)
    u = np.clip(((p - route[:-1]) * seg).sum(1) / np.maximum(ln ** 2, 1e-12), 0, 1)
    proj = route[:-1] + seg * u[:, None]; dd = np.linalg.norm(p - proj, axis=1); k = int(dd.argmin())
    s = min(cum[k] + u[k] * ln[k] + dist, cum[-1]); off = float(dd[k])
    return np.array([np.interp(s, cum, route[:, a]) for a in range(3)]), off


step = 0
for t in range(max(w.episode_limit for w in env.worlds)):
    actions = model.predict(features, deterministic=True)[0]
    features, rewards, dones, infos = env.step(actions)
    step += 1
    for i in np.flatnonzero(active):
        if dones[i]:
            active[i] = False
            continue
        if step % 3:
            continue
        st = infos[i]['transition_state']; p = np.asarray(st['position']); yaw = float(st['yaw'])
        a4, off = ahead(refs[i], cums[i], p, 4.); a8, _ = ahead(refs[i], cums[i], p, 8.)
        w = env.worlds[i]; rot = w.rotation()
        R24.append(w.cast_rays(DIRECTIONS @ rot.T, 24.)[1] / 24.); P24.append(w.cast_rays(PANO @ rot.T, 24.)[1] / 24.)
        F.append(infos[i]['next_brain_features']); S.append(infos[i]['next_sensors'])
        L4.append(body(a4 - p, yaw)); L8.append(body(a8 - p, yaw)); LG.append(body(goals[i] - p, yaw))
        BL.append(bool(segments_hit_boxes(np.array([p, goals[i]]), boxes[i], RADIUS))); EP.append(i); ST.append(step); OFF.append(off)
    if not active.any(): break
env.close()
np.savez_compressed(out, features=np.asarray(F, np.float32), sensors=np.asarray(S, np.float32), l4=np.asarray(L4, np.float32),
                    l8=np.asarray(L8, np.float32), lg=np.asarray(LG, np.float32), blocked=np.asarray(BL), episode=np.asarray(EP),
                    step=np.asarray(ST), offset=np.asarray(OFF, np.float32),
                    rays24=np.asarray(R24, np.float32), pano24=np.asarray(P24, np.float32))
print('saved', out, 'samples', len(F), 'blocked share', round(float(np.mean(BL)), 2), flush=True)
