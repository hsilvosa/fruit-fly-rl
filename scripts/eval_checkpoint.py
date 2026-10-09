"""Evaluate one saved checkpoint on the Phase 1 selection pools under the CPU and memory limits.
Usage: eval_checkpoint.py <checkpoint.zip> <label> <output-dir>"""
import json, os, sys
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, 'scripts')
from resource_guard import run_limited

ck, label, out_dir = sys.argv[1:4]
MID = 'scripts/profiles/passages-mid.json'
SEL = [('medium', None, 860000), ('medium-b', None, 861000), ('gate-two', 'gate-two', 862000),
       ('gate-long', 'gate-long', 862000), ('passages-wide', 'passages-wide', 863000),
       ('passages-mid', MID, 864000), ('passages', 'passages', 865000)]
commands, outputs = [], []
for name, prof, seed in SEL:
    out = f'{out_dir}/cell-{label}-select-{name}.json'
    outputs.append((name, out))
    if not os.path.exists(out):
        commands.append([sys.executable, '-s', 'scripts/eval_cell.py', ck, prof or 'none', str(seed), '32', out])
run_limited(commands)
result = {name: json.load(open(out)) for name, out in outputs}
json.dump({'checkpoint': ck, 'label': label, 'select': result}, open(f'{out_dir}/eval-{label}.json', 'w'), indent=1)
print('EVAL', label, {k: (v['successes'], v['collisions'], v['timeouts']) for k, v in result.items()}, flush=True)
