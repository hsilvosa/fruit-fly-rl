"""Probe variants on frozen rollouts (no policy training): history and sensing range.
Usage: analyze_probe_variants.py history <name> | range <name-long>
Same targets, split, metric and models as analyze_probe.py. Median angular error in degrees, all test samples / hard subset.
history: current 256 features alone, plus lagged features at 1,2,4 / +8,16 / +32 stored samples (0.15 s each), clamped at the episode start.
range:   8 m sensors (as in the policy), the same 128 ray directions cast to 24 m, the 72x25 panorama cast to 24 m (each with the
         non-ray sensor values), and the 256 features for reference."""
import json, os, sys
import numpy as np
import torch
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
D = 'runs/verification/probe'
torch.set_num_threads(2)
N = 128


def ang(a, b):
    a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-9); b = b / np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-9)
    return np.degrees(np.arccos(np.clip((a * b).sum(1), -1, 1)))


def ridge(Xtr, Ytr, Xte, lam):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    A = (Xtr - mu) / sd; B = (Xte - mu) / sd
    A1 = np.hstack([A, np.ones((len(A), 1))]); B1 = np.hstack([B, np.ones((len(B), 1))])
    W = np.linalg.solve(A1.T @ A1 + lam * np.eye(A1.shape[1]), A1.T @ Ytr)
    return B1 @ W


def best_ridge(Xtr, Ytr, Xva, Yva, Xte):
    best = None
    for lam in (10., 100., 1000., 10000., 100000.):
        e = float(np.median(ang(ridge(Xtr, Ytr, Xva, lam), Yva)))
        if best is None or e < best[0]: best = (e, lam)
    return ridge(Xtr, Ytr, Xte, best[1])


def mlp(Xtr, Ytr, Xva, Yva, Xte, seed=0):
    torch.manual_seed(seed)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    f = lambda X: torch.tensor((X - mu) / sd, dtype=torch.float32)
    net = torch.nn.Sequential(torch.nn.Linear(Xtr.shape[1], 256), torch.nn.ReLU(), torch.nn.Dropout(0.3), torch.nn.Linear(256, 128), torch.nn.ReLU(), torch.nn.Linear(128, 3))
    opt = torch.optim.Adam(net.parameters(), 1e-3, weight_decay=1e-3)
    Xt, Yt, Xv = f(Xtr), torch.tensor(Ytr, dtype=torch.float32), f(Xva)
    best, state = 1e9, None
    for ep in range(60):
        net.train(); perm = torch.randperm(len(Xt))
        for k in range(0, len(Xt), 512):
            idx = perm[k:k + 512]; opt.zero_grad()
            torch.nn.functional.mse_loss(net(Xt[idx]), Yt[idx]).backward(); opt.step()
        net.eval()
        with torch.no_grad(): e = float(np.median(ang(net(Xv).numpy(), Yva)))
        if e < best: best, state = e, {k: v.clone() for k, v in net.state_dict().items()}
    net.load_state_dict(state); net.eval()
    with torch.no_grad(): return net(f(Xte)).numpy()


def lagged(X, ep, lags):
    """Row i gets X at index i-lag of the same episode (clamped at the episode's first stored sample). Rows are time-ordered per episode."""
    out = [X]
    first = {}
    for i, e in enumerate(ep):
        first.setdefault(int(e), i)
    start = np.array([first[int(e)] for e in ep])
    idx = np.arange(len(ep))
    for lag in lags:
        out.append(X[np.maximum(idx - lag, start)])
    return np.hstack(out)


mode, name = sys.argv[1], sys.argv[2]
d = np.load(f'{D}/{name}.npz'); ep = d['episode']
m = {k: np.array([e in s for e in ep]) for k, s in (('tr', set(range(0, 40))), ('va', set(range(40, 48))), ('te', set(range(48, 64))))}
hard = d['blocked'] & (ang(d['lg'], d['l4']) > 40)
S = d['sensors']
if mode == 'history':
    F = d['features']
    inputs = {'features now': F, 'features + lags 1,2,4 (0.6 s)': lagged(F, ep, (1, 2, 4)),
              'features + lags 1,2,4,8,16 (2.4 s)': lagged(F, ep, (1, 2, 4, 8, 16)),
              'features + lags 1,2,4,8,16,32 (4.8 s)': lagged(F, ep, (1, 2, 4, 8, 16, 32)),
              'raw sensors now': S, 'raw sensors + lags to 2.4 s': lagged(S, ep, (1, 2, 4, 8, 16))}
else:
    tail = S[:, N:]
    inputs = {'raw sensors (8 m, as the policy)': S, 'same 128 rays cast to 24 m': np.hstack([d['rays24'], tail]),
              'panorama 72x25 cast to 24 m': np.hstack([d['pano24'], tail]), '256 connectome features (8 m)': d['features']}
print(f'== {mode} {name}: samples {len(ep)}, test {m["te"].sum()}, hard share on test {hard[m["te"]].mean():.2f}', flush=True)
res = {}
for target in ('l4', 'l8'):
    Y = d[target]; res[target] = {}
    print(f'  target: route point {"4" if target == "l4" else "8"} m ahead (median angular error, degrees: all / hard)', flush=True)
    for label, X in inputs.items():
        for kind in ('ridge', 'mlp'):
            if kind == 'ridge': pred = best_ridge(X[m['tr']], Y[m['tr']], X[m['va']], Y[m['va']], X[m['te']])
            else: pred = mlp(X[m['tr']], Y[m['tr']], X[m['va']], Y[m['va']], X[m['te']])
            a = ang(pred, Y[m['te']])
            res[target][f'{label} [{kind}]'] = (float(np.median(a)), float(np.median(a[hard[m['te']]])))
            print(f'    {label + " [" + kind + "]":52s} {res[target][f"{label} [{kind}]"][0]:6.1f} / {res[target][f"{label} [{kind}]"][1]:5.1f}', flush=True)
json.dump(res, open(f'{D}/probe-{mode}-{name}.json', 'w'), indent=1)
