"""Synthetic sensing probe on many maps (no policy, no training of any policy).
Question: with enough data, does a longer ray range or a panorama carry the direction to the next stretch of the certified route
better than the 8 m rays the policy uses? The 64-map rollouts of the first probes are too few to tell.
Per map (profile passages, seeds 895000+): 40 poses along the certified route, displaced laterally up to 3 m horizontally and 1.5 m
vertically (rejected inside obstacles), random heading. Inputs: 8 m rays, the same 128 directions at 24 m, the 72x25 panorama at 24 m,
each with goal direction, goal distance and altitude (no velocity). Targets: unit direction (body frame) to the route point 4 m and 8 m
ahead of the pose's nearest route progress. Split by map: 500 train, 50 validation, 150 test.
Usage: probe_synthetic.py <maps> <output-prefix>"""
import json, os, sys, time
import numpy as np
import torch
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
from fly_rl.simulation.world import FlightWorld, RADIUS
from fly_rl.simulation.map_profiles import resolve_profile, segments_hit_boxes
from fly_rl.simulation.sensors import DIRECTIONS, panorama_directions

maps, prefix = int(sys.argv[1]), sys.argv[2]
torch.set_num_threads(2)
PER = 40
PANO = panorama_directions()
rng = np.random.default_rng(895000)
rows = {k: [] for k in ('r8', 'r24', 'p24', 'goal', 'l4', 'l8', 'lg', 'blocked', 'map')}
t0 = time.time()


def rot_of(yaw):
    c, s = np.cos(yaw), np.sin(yaw)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])


def ahead(route, cum, p, dist):
    seg = np.diff(route, axis=0); ln = np.maximum(np.linalg.norm(seg, axis=1), 1e-12)
    u = np.clip(((p - route[:-1]) * seg).sum(1) / ln ** 2, 0, 1)
    proj = route[:-1] + seg * u[:, None]; k = int(np.linalg.norm(p - proj, axis=1).argmin())
    s = min(cum[k] + u[k] * ln[k] + dist, cum[-1])
    return np.array([np.interp(s, cum, route[:, a]) for a in range(3)])


for mi in range(maps):
    seed = 895000 + mi
    w = FlightWorld(seed, 'dense', None, 'coordinated', None, resolve_profile('passages'))
    w.reset(seed=seed)
    pts = [np.asarray(p, float) for p in w.reference_route]
    route = np.vstack([w.position] + pts) if pts else np.vstack([w.position, w.target])
    if np.linalg.norm(route[-1] - w.target) > 0.5: route = np.vstack([route, w.target])
    ln = np.linalg.norm(np.diff(route, axis=0), axis=1); cum = np.concatenate([[0], np.cumsum(ln)])
    boxes = np.asarray(w.obstacles)
    made = 0
    while made < PER:
        s = rng.uniform(0, cum[-1] - 1.0)
        base = np.array([np.interp(s, cum, route[:, a]) for a in range(3)])
        off = np.array([rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(-1.5, 1.5)])
        p = np.clip(base + off, RADIUS + 0.2, w.room - RADIUS - 0.2)
        if len(boxes) and (((p > boxes[:, 0, :] - RADIUS - 0.1) & (p < boxes[:, 1, :] + RADIUS + 0.1)).all(axis=1)).any():
            continue
        yaw = rng.uniform(-np.pi, np.pi); R = rot_of(yaw)
        w.position = p.copy(); w.yaw = yaw
        r8 = w.cast_rays(DIRECTIONS @ R.T, 8.)[1] / 8.
        r24 = w.cast_rays(DIRECTIONS @ R.T, 24.)[1] / 24.
        p24 = w.cast_rays(PANO @ R.T, 24.)[1] / 24.
        gd = (w.target - p) @ R; dist = float(np.linalg.norm(gd)); gd = gd / max(dist, 1e-9)
        goal = np.concatenate([gd, [dist / float(np.linalg.norm(w.room - 2 * RADIUS)), p[2] / w.room[2]]])
        lab = {}
        for key, dd in (('l4', 4.), ('l8', 8.)):
            v = (ahead(route, cum, p, dd) - p) @ R; lab[key] = v / max(np.linalg.norm(v), 1e-9)
        rows['r8'].append(r8); rows['r24'].append(r24); rows['p24'].append(p24); rows['goal'].append(goal)
        rows['l4'].append(lab['l4']); rows['l8'].append(lab['l8']); rows['lg'].append(gd)
        rows['blocked'].append(bool(segments_hit_boxes(np.array([p, w.target]), boxes, RADIUS))); rows['map'].append(mi)
        made += 1
    if mi % 100 == 99: print('maps', mi + 1, round(time.time() - t0), 's', flush=True)
D = {k: np.asarray(v, np.float32 if k != 'blocked' and k != 'map' else None) for k, v in rows.items()}
np.savez_compressed(prefix + '.npz', **D)
print('generated', len(D['map']), 'samples', round(time.time() - t0), 's', flush=True)


def ang(a, b):
    a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-9); b = b / np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-9)
    return np.degrees(np.arccos(np.clip((a * b).sum(1), -1, 1)))


def ridge(Xtr, Ytr, Xte, lam):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    A = (Xtr - mu) / sd; B = (Xte - mu) / sd
    A1 = np.hstack([A, np.ones((len(A), 1))]); B1 = np.hstack([B, np.ones((len(B), 1))])
    return B1 @ np.linalg.solve(A1.T @ A1 + lam * np.eye(A1.shape[1]), A1.T @ Ytr)


def mlp(Xtr, Ytr, Xva, Yva, Xte):
    torch.manual_seed(0)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    f = lambda X: torch.tensor((X - mu) / sd, dtype=torch.float32)
    net = torch.nn.Sequential(torch.nn.Linear(Xtr.shape[1], 512), torch.nn.ReLU(), torch.nn.Dropout(0.2), torch.nn.Linear(512, 256), torch.nn.ReLU(), torch.nn.Linear(256, 3))
    opt = torch.optim.Adam(net.parameters(), 1e-3, weight_decay=1e-4)
    Xt, Yt, Xv = f(Xtr), torch.tensor(Ytr, dtype=torch.float32), f(Xva)
    best, state = 1e9, None
    for ep in range(80):
        net.train(); perm = torch.randperm(len(Xt))
        for k in range(0, len(Xt), 256):
            idx = perm[k:k + 256]; opt.zero_grad()
            torch.nn.functional.mse_loss(net(Xt[idx]), Yt[idx]).backward(); opt.step()
        net.eval()
        with torch.no_grad(): e = float(np.median(ang(net(Xv).numpy(), Yva)))
        if e < best: best, state = e, {k: v.clone() for k, v in net.state_dict().items()}
    net.load_state_dict(state); net.eval()
    with torch.no_grad(): return net(f(Xte)).numpy()


mp = D['map']
tr, va, te = mp < 500, (mp >= 500) & (mp < 550), mp >= 550
hard = D['blocked'] & (ang(D['lg'], D['l4']) > 40)
print(f'train {tr.sum()}, val {va.sum()}, test {te.sum()}, hard share on test {hard[te].mean():.2f}', flush=True)
inputs = {'goal direction, distance, altitude only': D['goal'], '8 m rays (as the policy)': np.hstack([D['r8'], D['goal']]),
          '24 m rays, same 128 directions': np.hstack([D['r24'], D['goal']]), '24 m panorama 72x25': np.hstack([D['p24'], D['goal']]),
          '8 m rays + 24 m rays': np.hstack([D['r8'], D['r24'], D['goal']])}
res = {}
for target in ('l4', 'l8'):
    Y = D[target]; res[target] = {}
    print(f'target: route point {"4" if target == "l4" else "8"} m ahead (median angular error, degrees: all / hard)', flush=True)
    for label, X in inputs.items():
        best = min(((float(np.median(ang(ridge(X[tr], Y[tr], X[va], lam), Y[va]))), lam) for lam in (10., 100., 1000., 10000.)))
        for kind, pred in (('ridge', ridge(X[tr], Y[tr], X[te], best[1])), ('mlp', mlp(X[tr], Y[tr], X[va], Y[va], X[te]))):
            a = ang(pred, Y[te])
            res[target][f'{label} [{kind}]'] = (float(np.median(a)), float(np.median(a[hard[te]])))
            print(f'  {label + " [" + kind + "]":50s} {res[target][f"{label} [{kind}]"][0]:6.1f} / {res[target][f"{label} [{kind}]"][1]:5.1f}', flush=True)
json.dump(res, open(prefix + '-results.json', 'w'), indent=1)
