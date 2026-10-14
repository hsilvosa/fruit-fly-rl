"""Supervised pretraining of the actor trunk on route-direction labels while preserving the source behavior.
Data: rollouts of the SOURCE policy with sampled actions on many maps (scripts/collect_pretrain.py). Inputs are the 256 connectome
features the actor reads. Loss = (1 - cosine(head(trunk(x)), route direction)) + LAMBDA * mean squared error between the new mean
action and the source mean action on the same features. Split by map. Output: runs/training/pretrain/trunk.pt and metrics.json.
Usage: pretrain_trunk.py <data-dir> <output-dir>"""
import glob, json, os, sys, time
import numpy as np
import torch
from torch import nn
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
from stable_baselines3 import PPO

DATA, OUT = sys.argv[1], sys.argv[2]
SOURCE = 'runs/training/reference-transfer-7/mix3e4/stage-2.zip'
LAMBDA = 1.0
torch.set_num_threads(2); torch.manual_seed(0); np.random.seed(0)
os.makedirs(OUT, exist_ok=True)


def ang(a, b):
    a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-9); b = b / np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-9)
    return np.degrees(np.arccos(np.clip((a * b).sum(1), -1, 1)))


files = sorted(glob.glob(f'{DATA}/*.npz'))
X, Y, LG, BL, MAP = [], [], [], [], []
for fi, f in enumerate(files):
    d = np.load(f)
    X.append(d['features']); Y.append(d['l4']); LG.append(d['lg']); BL.append(d['blocked']); MAP.append(d['episode'] + 1000 * fi)
X, Y, LG, BL, MAP = map(np.concatenate, (X, Y, LG, BL, MAP))
maps = np.unique(MAP); rng = np.random.default_rng(0); rng.shuffle(maps)
n_va, n_te = max(1, len(maps) // 10), max(1, len(maps) // 5)
te_maps, va_maps = set(maps[:n_te]), set(maps[n_te:n_te + n_va])
split = np.array(['te' if m in te_maps else 'va' if m in va_maps else 'tr' for m in MAP])
hard = BL & (ang(LG, Y) > 40)
print(f'{len(files)} files, {len(maps)} maps, {len(X)} samples; train {np.sum(split == "tr")}, val {np.sum(split == "va")}, test {np.sum(split == "te")}; hard share {hard.mean():.2f}', flush=True)

src = PPO.load(SOURCE, device='cpu')
trunk = nn.Sequential(nn.Linear(256, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh())
act = nn.Linear(128, 4)
head = nn.Sequential(nn.Linear(128, 64), nn.Tanh(), nn.Linear(64, 3))
with torch.no_grad():
    for i in (0, 2):
        trunk[i].weight.copy_(src.policy.mlp_extractor.policy_net[i].weight); trunk[i].bias.copy_(src.policy.mlp_extractor.policy_net[i].bias)
    act.weight.copy_(src.policy.action_net.weight); act.bias.copy_(src.policy.action_net.bias)
    Xt_all = torch.tensor(X)
    teacher = torch.cat([src.policy.get_distribution(Xt_all[i:i + 8192]).distribution.loc for i in range(0, len(X), 8192)]).numpy()
var = float(teacher.var(0).sum())
T = torch.tensor(teacher)
Xt, Yt = torch.tensor(X), torch.tensor(Y)
idx = {k: np.flatnonzero(split == k) for k in ('tr', 'va', 'te')}
params = list(trunk.parameters()) + list(act.parameters()) + list(head.parameters())
opt = torch.optim.Adam(params, 1e-3)


def evaluate(k):
    with torch.no_grad():
        i = idx[k]; z = trunk(Xt[i]); pred = head(z).numpy(); mean = act(z)
        a = ang(pred, Y[i]); h = hard[i]
        mse = float(((mean - T[i]) ** 2).sum(1).mean())
        r2 = 1.0 - float(((mean - T[i]) ** 2).sum(1).mean()) / var
        return {'median_error_all': float(np.median(a)), 'median_error_hard': float(np.median(a[h])), 'action_mse': mse, 'action_r2': r2,
                'cosine_loss': float(1 - torch.nn.functional.cosine_similarity(torch.tensor(pred), Yt[i], dim=1).mean())}


before = evaluate('va')
best, state, t0 = 1e9, None, time.time()
for epoch in range(60):
    perm = np.random.permutation(idx['tr'])
    for k in range(0, len(perm), 512):
        b = perm[k:k + 512]
        z = trunk(Xt[b])
        loss = (1 - torch.nn.functional.cosine_similarity(head(z), Yt[b], dim=1)).mean() + LAMBDA * ((act(z) - T[b]) ** 2).sum(1).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    v = evaluate('va'); score = v['cosine_loss'] + LAMBDA * v['action_mse']
    if score < best:
        best = score; state = [{k: x.clone() for k, x in m.state_dict().items()} for m in (trunk, act, head)]
    if epoch % 5 == 4:
        print(f"epoch {epoch + 1} val hard error {v['median_error_hard']:.1f} all {v['median_error_all']:.1f} action r2 {v['action_r2']:.3f} ({time.time() - t0:.0f} s)", flush=True)
for m, s in zip((trunk, act, head), state):
    m.load_state_dict(s)
metrics = {'samples': int(len(X)), 'maps': int(len(maps)), 'lambda': LAMBDA, 'before_val': before, 'val': evaluate('va'), 'test': evaluate('te'),
           'source': SOURCE, 'files': files}
torch.save({'trunk': trunk.state_dict(), 'act': act.state_dict(), 'head': head.state_dict()}, f'{OUT}/trunk.pt')
json.dump(metrics, open(f'{OUT}/metrics.json', 'w'), indent=1)
print('TEST (held-out maps):', json.dumps(metrics['test']), flush=True)
