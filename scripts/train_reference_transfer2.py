"""Reference-preserving transfer experiment: continue (or freshly start) a v3 policy on partitioned rooms.

Arms: 'retained' continues the 48/64 ray-risk-v1 checkpoint; 'fresh' is a matched v3 control.
Both arms use the same chunk plan, seeds, budget and evaluations. Originals are never written.
Evaluation uses development seeds only; no reserved pool is touched.
Experiment 2 arms: 'route65' (retained, certified-route-progress-v1 on passages chunks, 65,536 transitions)
and 'budget262' (retained, unchanged reward, 262,144 transitions). Medium chunks never use shaping.
Usage: train_reference_transfer2.py <route65|budget262> <output-dir>
"""
import hashlib, json, os, shutil, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.training.learning import train
from fly_rl.training.evaluation import evaluate
from fly_rl.simulation.sensors import SENSOR_V3

ARM, OUT = sys.argv[1], sys.argv[2]
assert ARM in ('route65', 'budget262')
LAYOUTS = list(range(900000, 900256))  # training layouts, disjoint from every evaluation pool
SOURCE = 'runs/training/ray-risk-v1/selected/selected-policy'
CHUNK = 8192
BASE = ['passages', 'passages', None, 'passages', 'passages', 'passages', None, 'passages']  # None = original medium
PLAN = BASE if ARM == 'route65' else BASE * 4
EVAL_AFTER = {4, 8} if ARM == 'route65' else {16, 32}
SHAPING = 'certified-route-progress-v1' if ARM == 'route65' else None
MEDIUM_SEED, MEDIUM_EPISODES = 240000, 32      # replayed regression pool (27/32 for the source)
PASSAGES_SEED, PASSAGES_EPISODES = 810000, 32  # declared development pool for this experiment


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def summarize(r):
    e = r['episodes']
    return {'successes': sum(bool(x['success']) for x in e), 'collisions': sum(bool(x['collision']) for x in e),
            'timeouts': sum(bool(x['timeout']) for x in e), 'episodes': len(e),
            'success_seeds': [x['seed'] for x in e if x['success']]}


os.makedirs(OUT, exist_ok=True)
src_hash = (sha(SOURCE + '.zip'), sha(SOURCE + '.json'))
log = {'arm': ARM, 'reward_shaping': SHAPING, 'source': SOURCE, 'source_sha256': src_hash, 'chunk_transitions': CHUNK, 'plan': PLAN,
       'budget': CHUNK * len(PLAN), 'batch': 8, 'gamma': 0.995, 'dynamics': 'coordinated',
       'sensor_version': SENSOR_V3, 'chunks': [], 'evaluations': []}
prev = SOURCE + '.zip'
for i, prof in enumerate(PLAN, start=1):
    t = time.time()
    out = f'{OUT}/chunk-{i}.zip'
    res = train('data', 'cuda', CHUNK, 8, out, resume=prev, mode='dense', dynamics='coordinated',
                allow_transfer=True, training_seed=42 + i, sensor_version=SENSOR_V3, map_profile=prof,
                layout_seeds=LAYOUTS if (prof and SHAPING) else None, reward_shaping=SHAPING if prof else None)
    prev = out
    log['chunks'].append({'chunk': i, 'profile': prof or 'dense-medium-original', 'route_shaping': res.get('reward_shaping'), 'seconds': round(time.time() - t),
                          'transitions': res['transitions'], 'updates': res['updates'],
                          'parameters_changed': res['parameters_changed'], 'losses': res['losses']})
    print('chunk', i, prof, res['transitions'], res['losses'], flush=True)
    if i in EVAL_AFTER:
        m = evaluate('data', 'cuda', out, episodes=MEDIUM_EPISODES, mode='dense', seed=MEDIUM_SEED,
                     dynamics='coordinated', allow_transfer=True)
        p = evaluate('data', 'cuda', out, episodes=PASSAGES_EPISODES, mode='dense', seed=PASSAGES_SEED,
                     dynamics='coordinated', map_profile='passages', allow_transfer=True)
        ev = {'after_chunk': i, 'transitions': res['transitions'], 'checkpoint': out, 'checkpoint_sha256': sha(out),
              'medium': summarize(m), 'passages': summarize(p)}
        log['evaluations'].append(ev)
        print('EVAL', i, 'medium', ev['medium']['successes'], 'passages', ev['passages']['successes'], flush=True)
    log['source_unchanged'] = (sha(SOURCE + '.zip'), sha(SOURCE + '.json')) == src_hash
    json.dump(log, open(f'{OUT}/experiment.json', 'w'), indent=1)
print('done; source unchanged:', log['source_unchanged'])
