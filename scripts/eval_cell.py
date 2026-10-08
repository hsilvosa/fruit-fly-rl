"""Evaluate one cell in its own process so cells can run in parallel.
Usage: eval_cell.py <checkpoint> <profile|none> <seed> <episodes> <out.json>"""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
from fly_rl.training.evaluation import evaluate
ck, prof, seed, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
r = evaluate('data', 'cuda', ck, episodes=n, mode='dense', seed=seed, dynamics='coordinated',
             map_profile=None if prof == 'none' else prof, allow_transfer=True)
e = r['episodes']
json.dump({'successes': sum(bool(x['success']) for x in e), 'collisions': sum(bool(x['collision']) for x in e),
           'timeouts': sum(bool(x['timeout']) for x in e), 'episodes': n,
           'success_seeds': [x['seed'] for x in e if x['success']]}, open(out, 'w'))
