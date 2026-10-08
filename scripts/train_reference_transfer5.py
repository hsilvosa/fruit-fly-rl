"""Experiment 5: full passages in the mix, from the experiment 4 selected checkpoint.
See docs/REFERENCE_TRANSFER_PROTOCOL_5.md. Usage: train_reference_transfer5.py <output-dir>"""
import hashlib, json, os, subprocess, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.training.learning import train

OUT = sys.argv[1]
SOURCE = 'runs/training/reference-transfer-4/recover/chunk-8'
CHUNK = 8192
PLAN = [None, 'passages', None, 'passages-wide', None, 'passages', 'gate-two', 'passages-wide'] * 2
EVAL_AFTER = {8, 16}
CELLS = [('medium', None, 100000, 32), ('medium-b', None, 840000, 32), ('gate-two', 'gate-two', 830000, 32),
         ('gate-long', 'gate-long', 830000, 32), ('passages-wide', 'passages-wide', 830000, 32),
         ('passages', 'passages', 810000, 32)]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run_cells(ck, label, transitions):
    ev = {'label': label, 'transitions_added': transitions, 'checkpoint': ck, 'checkpoint_sha256': sha(ck)}
    procs = []
    for name, prof, seed, n in CELLS:
        out = f'{OUT}/cell-{label}-{name}.json'
        cmd = [sys.executable, '-s', 'scripts/eval_cell.py', ck, prof or 'none', str(seed), str(n), out]
        procs.append((name, out, subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
    for name, out, p in procs:
        if p.wait() != 0:
            raise RuntimeError(f'cell {name} failed')
        ev[name] = json.load(open(out))
    print('EVAL', label, {k: v['successes'] for k, v in ev.items() if isinstance(v, dict)}, flush=True)
    return ev


os.makedirs(OUT, exist_ok=True)
src_hash = (sha(SOURCE + '.zip'), sha(SOURCE + '.json'))
log = {'source': SOURCE, 'source_sha256': src_hash, 'chunk_transitions': CHUNK, 'plan': PLAN,
       'budget': CHUNK * len(PLAN), 'batch': 8, 'gamma': 0.995, 'dynamics': 'coordinated', 'chunks': [], 'evaluations': []}
log['evaluations'].append(run_cells(SOURCE + '.zip', 'baseline-exp4-selected', 0))
prev = SOURCE + '.zip'
for i, prof in enumerate(PLAN, start=1):
    t = time.time()
    out = f'{OUT}/chunk-{i}.zip'
    res = train('data', 'cuda', CHUNK, 8, out, resume=prev, mode='dense', dynamics='coordinated',
                allow_transfer=True, training_seed=242 + i, map_profile=prof)
    prev = out
    log['chunks'].append({'chunk': i, 'profile': prof or 'dense-medium-original', 'seconds': round(time.time() - t),
                          'transitions': res['transitions'], 'updates': res['updates'],
                          'parameters_changed': res['parameters_changed'], 'losses': res['losses']})
    print('chunk', i, prof, res['transitions'], flush=True)
    if i in EVAL_AFTER:
        log['evaluations'].append(run_cells(out, f'after-{i * CHUNK}', i * CHUNK))
    log['source_unchanged'] = (sha(SOURCE + '.zip'), sha(SOURCE + '.json')) == src_hash
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
print('done; source unchanged:', log['source_unchanged'])
