"""Evaluate one saved checkpoint on the Phase 1 selection pools under the CPU and memory limits.
Usage: eval_checkpoint.py <checkpoint.zip> <label> <output-dir>"""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import run_limited

ck, label, out_dir = sys.argv[1:4]
MID = 'scripts/profiles/passages-mid.json'
OLD = [("medium", None, 100000), ("medium-b", None, 840000), ("gate-two", "gate-two", 830000),
       ("gate-long", "gate-long", 830000), ("passages-wide", "passages-wide", 830000),
       ("passages-mid", MID, 850000), ("passages", "passages", 810000)]
SEL = [('medium', None, 860000), ('medium-b', None, 861000), ('gate-two', 'gate-two', 862000),
       ('gate-long', 'gate-long', 862000), ('passages-wide', 'passages-wide', 863000),
       ('passages-mid', MID, 864000), ('passages', 'passages', 865000)]
POOLS = [('select', SEL), ('old', OLD)] if len(sys.argv) < 5 else [(p, {'select': SEL, 'old': OLD}[p]) for p in sys.argv[4].split(',')]
commands, outputs = [], []
for pool, cells in POOLS:
    for name, prof, seed in cells:
        out = f'{out_dir}/cell-{label}-{pool}-{name}.json'
        outputs.append((pool, name, out))
        if not os.path.exists(out):
            commands.append([sys.executable, '-s', 'scripts/eval_cell.py', ck, prof or 'none', str(seed), '32', out])
run_limited(commands)
result = {}
for pool, name, out in outputs:
    result.setdefault(pool, {})[name] = json.load(open(out))
json.dump({'checkpoint': ck, 'label': label, **result}, open(f'{out_dir}/eval-{label}.json', 'w'), indent=1)
for pool, cells in result.items():
    print('EVAL', label, pool, {k: (v['successes'], v['collisions'], v['timeouts']) for k, v in cells.items()}, flush=True)
