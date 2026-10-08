"""Experiment 4: medium-heavy recovery stage from the experiment 3 final checkpoint. See docs/REFERENCE_TRANSFER_PROTOCOL_4.md.
Usage: train_reference_transfer3.py <output-dir>
"""
import hashlib, json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.training.learning import train
from fly_rl.training.evaluation import evaluate

OUT = sys.argv[1]
ORIGIN = 'runs/training/sensors-v3-v1/selected/selected-policy.zip'
SOURCE = 'runs/training/reference-transfer-3/gates/chunk-16'
CHUNK = 8192
PLAN = [None, 'passages-wide', None, 'gate-two'] * 2
EVAL_AFTER = {4, 8}
CELLS = [('medium', None, 100000, 32), ('medium-b', None, 840000, 32), ('gate-two', 'gate-two', 830000, 32),
         ('gate-long', 'gate-long', 830000, 32), ('passages-wide', 'passages-wide', 830000, 32)]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run_cells(ck, label, transitions, cells=None):
    ev = {'label': label, 'transitions_added': transitions, 'checkpoint': ck, 'checkpoint_sha256': sha(ck)}
    for name, prof, seed, n in (cells or CELLS):
        r = evaluate('data', 'cuda', ck, episodes=n, mode='dense', seed=seed, dynamics='coordinated',
                     map_profile=prof, allow_transfer=True)
        e = r['episodes']
        ev[name] = {'successes': sum(bool(x['success']) for x in e), 'collisions': sum(bool(x['collision']) for x in e),
                    'timeouts': sum(bool(x['timeout']) for x in e), 'episodes': n,
                    'success_seeds': [x['seed'] for x in e if x['success']]}
    print('EVAL', label, {k: v['successes'] for k, v in ev.items() if isinstance(v, dict)}, flush=True)
    return ev


os.makedirs(OUT, exist_ok=True)
src_hash = (sha(SOURCE + '.zip'), sha(SOURCE + '.json'))
log = {'source': SOURCE, 'source_sha256': src_hash, 'chunk_transitions': CHUNK, 'plan': PLAN,
       'budget': CHUNK * len(PLAN), 'batch': 8, 'gamma': 0.995, 'dynamics': 'coordinated', 'chunks': [], 'evaluations': []}
log['origin_sha256'] = sha(ORIGIN)
log['evaluations'].append(run_cells(ORIGIN, 'origin-50-64-medium-b-only', 0, [CELLS[1]]))
log['evaluations'].append(run_cells(SOURCE + '.zip', 'baseline-exp3-final', 0))
prev = SOURCE + '.zip'
for i, prof in enumerate(PLAN, start=1):
    t = time.time()
    out = f'{OUT}/chunk-{i}.zip'
    res = train('data', 'cuda', CHUNK, 8, out, resume=prev, mode='dense', dynamics='coordinated',
                allow_transfer=True, training_seed=142 + i, map_profile=prof)
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
