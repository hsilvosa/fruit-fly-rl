"""Linear and small nonlinear probes: does the policy input carry the direction to the next stretch of the certified route?
Targets: unit vector (body frame) to the route point 4 m and 8 m ahead. Splits by episode (48 train / 16 test).
Inputs compared: goal direction only (3 numbers), raw sensors, the 256 pooled connectome features, features + goal direction.
Reports the median angular error in degrees on the test episodes, overall and on the hard subset (straight line to goal blocked and the
route-ahead direction differs from the goal direction by more than 40 degrees). Evaluation of frozen data only."""
import json, os, sys
import numpy as np
import torch
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
D = 'runs/verification/probe'
torch.set_num_threads(2)


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
    for lam in (1., 10., 100., 1000., 10000.):
        e = float(np.median(ang(ridge(Xtr, Ytr, Xva, lam), Yva)))
        if best is None or e < best[0]: best = (e, lam)
    return ridge(Xtr, Ytr, Xte, best[1]), best[1]


def mlp(Xtr, Ytr, Xva, Yva, Xte, seed=0):
    torch.manual_seed(seed)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    f = lambda X: torch.tensor((X - mu) / sd, dtype=torch.float32)
    net = torch.nn.Sequential(torch.nn.Linear(Xtr.shape[1], 256), torch.nn.ReLU(), torch.nn.Dropout(0.2), torch.nn.Linear(256, 128), torch.nn.ReLU(), torch.nn.Linear(128, 3))
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


out = {}
for name in sys.argv[1:]:
    d = np.load(f'{D}/{name}.npz'); ep = d['episode']
    train_eps, val_eps, test_eps = [set(range(0, 40)), set(range(40, 48)), set(range(48, 64))]
    m = {k: np.array([e in s for e in ep]) for k, s in (('tr', train_eps), ('va', val_eps), ('te', test_eps))}
    angle_goal_route = ang(d['lg'], d['l4'])
    hard = d['blocked'] & (angle_goal_route > 40)
    print(f'== {name}: samples {len(ep)}, train {m["tr"].sum()}, val {m["va"].sum()}, test {m["te"].sum()}; hard share on test {hard[m["te"]].mean():.2f}; '
          f'median angle goal vs route-ahead(4 m) {np.median(angle_goal_route[m["te"]]):.0f} deg', flush=True)
    inputs = {'goal direction only': d['lg'], 'raw sensors': d['sensors'], '256 connectome features': d['features'],
              'features + goal direction': np.hstack([d['features'], d['lg']])}
    res = {}
    for target in ('l4', 'l8'):
        Y = d[target]
        res[target] = {}
        base = ang(d['lg'][m['te']], Y[m['te']])
        res[target]['predict the goal direction (no model)'] = (float(np.median(base)), float(np.median(base[hard[m['te']]])) if hard[m['te']].any() else None, '-')
        for label, X in inputs.items():
            for kind in ('ridge', 'mlp'):
                if kind == 'ridge': pred, lam = best_ridge(X[m['tr']], Y[m['tr']], X[m['va']], Y[m['va']], X[m['te']])
                else: pred, lam = mlp(X[m['tr']], Y[m['tr']], X[m['va']], Y[m['va']], X[m['te']]), '-'
                a = ang(pred, Y[m['te']])
                res[target][f'{label} [{kind}]'] = (float(np.median(a)), float(np.median(a[hard[m['te']]])) if hard[m['te']].any() else None, lam)
        print(f'  target: direction to the route point {"4" if target == "l4" else "8"} m ahead (median angular error in degrees, all test samples / hard subset)')
        for k, v in res[target].items():
            print(f'    {k:48s} {v[0]:6.1f} / {v[1] if v[1] is None else round(v[1], 1)}')
    out[name] = res
json.dump(out, open(f'{D}/probe-results.json', 'w'), indent=1)
