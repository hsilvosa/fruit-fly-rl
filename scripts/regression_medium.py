"""Frozen medium-room regression suite.

Evaluates a checkpoint on four fixed pools of the original medium dense-room task (32 x 32 x 12, 48 obstacles,
coordinated dynamics, no map profile) and applies the declared pass rule. Evaluation only; no training.

Usage: regression_medium.py <checkpoint.zip> <label> <output-dir> [reference-result.json]
"""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import run_limited

POOLS = [('A', 100000), ('B', 840000), ('C', 860000), ('D', 861000)]  # 32 episodes each; frozen
EPISODES = 32
ORIGINAL_POOL_FLOOR = 21  # of 32, declared first
PER_POOL_FLOOR = 17   # of 32, amended after the baselines (see docs/MEDIUM_REGRESSION_SUITE.md)
TOTAL_FLOOR = 88      # of 128

ck, label, out_dir = sys.argv[1:4]
reference = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
os.makedirs(out_dir, exist_ok=True)
commands, outputs = [], []
for name, seed in POOLS:
    out = f'{out_dir}/regression-{label}-{name}.json'
    outputs.append((name, seed, out))
    if not os.path.exists(out):
        commands.append([sys.executable, '-s', 'scripts/eval_cell.py', ck, 'none', str(seed), str(EPISODES), out])
run_limited(commands)
cells = {name: json.load(open(out)) for name, _, out in outputs}
total = sum(c['successes'] for c in cells.values())
result = {'label': label, 'checkpoint': ck, 'pools': {n: s for n, s in POOLS}, 'episodes_per_pool': EPISODES,
          'per_pool': {n: {k: c[k] for k in ('successes', 'collisions', 'timeouts')} for n, c in cells.items()},
          'success_seeds': {n: c['success_seeds'] for n, c in cells.items()},
          'total_successes': total, 'total_episodes': EPISODES * len(POOLS),
          'rule': {'per_pool_floor': PER_POOL_FLOOR, 'total_floor': TOTAL_FLOOR}}
result['passes'] = total >= TOTAL_FLOOR and all(c['successes'] >= PER_POOL_FLOOR for c in cells.values())
result['passes_original_rule'] = total >= TOTAL_FLOOR and all(c['successes'] >= ORIGINAL_POOL_FLOOR for c in cells.values())
if reference:
    lost = {n: sorted(set(reference['success_seeds'][n]) - set(c['success_seeds'])) for n, c in cells.items()}
    result['reference'] = reference['label']
    result['lost_successes_vs_reference'] = lost
    result['lost_count'] = sum(len(v) for v in lost.values())
    result['gained_count'] = sum(len(set(c['success_seeds']) - set(reference['success_seeds'][n])) for n, c in cells.items())
json.dump(result, open(f'{out_dir}/regression-{label}.json', 'w'), indent=1)
print('REGRESSION', label, {n: v['successes'] for n, v in result['per_pool'].items()}, 'total', total, '/', result['total_episodes'],
      'PASS' if result['passes'] else 'FAIL',
      (f"lost {result['lost_count']} gained {result['gained_count']} vs {result['reference']}" if reference else ''), flush=True)
