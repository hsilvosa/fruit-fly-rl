"""Evaluate one cell in its own process, with an explicit action mode.
Usage: eval_cell_mode.py <checkpoint> <profile|none> <seed> <episodes> <out.json> <det|sampled>"""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
from fly_rl.training.evaluation import evaluate
ck, prof, seed, n, out, mode = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
assert mode in ('det', 'sampled')
r = evaluate('data', 'cuda', ck, episodes=n, mode='dense', seed=seed, dynamics='coordinated',
             map_profile=None if prof == 'none' else prof, allow_transfer=True, deterministic=(mode == 'det'))
e = r['episodes']
json.dump({'successes': sum(bool(x['success']) for x in e), 'collisions': sum(bool(x['collision']) for x in e),
           'timeouts': sum(bool(x['timeout']) for x in e), 'episodes': n, 'mode': mode,
           'success_seeds': [x['seed'] for x in e if x['success']]}, open(out, 'w'))
