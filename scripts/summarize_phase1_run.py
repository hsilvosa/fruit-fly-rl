"""Aggregate the Phase 1 run: acceptance, selection and stability, per the declared rules."""
import json, os
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
RUN = 'runs/training/phase1-run'
CELLS = ['medium', 'medium-b', 'gate-two', 'gate-long', 'passages-wide', 'passages-mid', 'passages']
rows = []
for seed in (442, 443):
    for st in (1, 2, 3, 4):
        e = json.load(open(f'{RUN}/seed{seed}/eval-after-{st * 32768}.json'))
        sel = {k: e['select'][k]['successes'] for k in CELLS}
        old = {k: e['old'][k]['successes'] for k in CELLS}
        accepted = sel['medium'] >= 21 and sel['medium-b'] >= 20 and sel['passages-wide'] >= 16 and sel['gate-two'] >= 28
        rows.append({'seed': seed, 'added': st * 32768, 'select': sel, 'old': old, 'accepted': accepted,
                     'collisions_select': {k: e['select'][k]['collisions'] for k in CELLS}})
for r in rows:
    print(r['seed'], r['added'], 'ACC' if r['accepted'] else '---', 'select', list(r['select'].values()), 'old', list(r['old'].values()))
acc = [r for r in rows if r['accepted']]
best = sorted(acc, key=lambda r: (-r['select']['passages-mid'], -r['select']['passages'], r['added']))
print('selected', (best[0]['seed'], best[0]['added']) if best else None)
for seed in (442, 443):
    rs = [r for r in rows if r['seed'] == seed]
    wide = [r['old']['passages-wide'] for r in rs]
    mid = [r['old']['passages-mid'] for r in rs]
    med = [r['select']['medium'] for r in rs]
    print('seed', seed, 'wide old', wide, 'range', max(wide) - min(wide), '| mid old', mid, 'range', max(mid) - min(mid),
          '| medium select min', min(med), '| accepted', sum(r['accepted'] for r in rs))
json.dump(rows, open('private/reference-recovery-1-evidence/phase1-run-summary.json', 'w'), indent=1)
