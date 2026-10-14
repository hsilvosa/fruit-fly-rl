"""Summarize the variance study (R1) according to docs/experiments/variance-and-stability/VARIANCE_STUDY_PROTOCOL.md."""
import json, os
import numpy as np
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
RUN = 'runs/training/variance-study'
SEEDS = (501, 502, 503, 504, 505)
CELLS = ['medium', 'medium-b', 'gate-two', 'gate-long', 'passages-wide', 'passages-mid', 'passages']
rows = []
for seed in SEEDS:
    f = f'{RUN}/seed{seed}/eval-final.json'
    if not os.path.exists(f):
        continue
    e = json.load(open(f))
    sel = {k: e['select'][k]['successes'] for k in CELLS}
    pools = {'A': e['regab']['medium']['successes'], 'B': e['regab']['medium-b']['successes'],
             'C': sel['medium'], 'D': sel['medium-b']}
    total = sum(pools.values())
    passes = total >= 88 and all(v >= 17 for v in pools.values())
    hard = sel['passages-wide'] + sel['passages-mid'] + sel['passages']
    rows.append({'seed': seed, 'select': sel, 'regression': pools, 'regression_total': total, 'regression_pass': passes,
                 'hard_sum': hard, 'collisions': {k: e['select'][k]['collisions'] for k in CELLS}})
    print(seed, 'select', list(sel.values()), 'regression', list(pools.values()), total, 'PASS' if passes else 'FAIL', 'hard', hard)
if rows:
    print('--- per cell across', len(rows), 'runs')
    for k in CELLS:
        v = [r['select'][k] for r in rows]
        print(f'{k:14s} values {v} mean {np.mean(v):.1f} sd {np.std(v, ddof=1) if len(v) > 1 else 0:.1f} range {max(v) - min(v)}')
    hs = [r['hard_sum'] for r in rows]
    print('hard sum', hs, 'mean', round(float(np.mean(hs)), 1), 'range', max(hs) - min(hs))
    eligible = [r for r in rows if r['regression_pass'] and r['select']['gate-two'] >= 28]
    best = max(eligible, key=lambda r: r['hard_sum']) if eligible else None
    print('best run among eligible:', best['seed'] if best else None, 'hard sum', best['hard_sum'] if best else None)
    print('runs with passages-mid >= 20:', sum(r['select']['passages-mid'] >= 20 for r in rows), 'of', len(rows))
    rng = {k: max(r['select'][k] for r in rows) - min(r['select'][k] for r in rows) for k in ('passages-mid', 'passages-wide')}
    print('decision rule: ranges', rng, '->', 'strict protocol (>=3 seeds, 64 episodes, best-of-N)' if max(rng.values()) >= 10 else '6-episode threshold with two seeds acceptable')
    json.dump(rows, open('private/reference-recovery-1-evidence/variance-study-summary.json', 'w'), indent=1)
