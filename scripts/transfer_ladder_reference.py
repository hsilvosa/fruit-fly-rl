"""Bounded development transfer ladder for frozen historical winners (no training, no reserved pools).

Seeds 800000+ are a declared development range created for this check only. Results are development
observations, not tests. Writes runs/verification/reference-recovery-1/transfer-ladder.json.
"""
import json, os, sys, time
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.training.evaluation import evaluate

OUT = 'runs/verification/reference-recovery-1/transfer-ladder.json'
POLICIES = {'ray-risk-v1': 'runs/training/ray-risk-v1/selected/selected-policy.zip',
            'sensors-v3-v1': 'runs/training/sensors-v3-v1/selected/selected-policy.zip'}
PLAN = [('ray-risk-v1', 'open'), ('ray-risk-v1', 'passages'), ('ray-risk-v1', 'large'),
        ('sensors-v3-v1', 'large'), ('sensors-v3-v1', None)]
EPISODES = 16
SEED = 800000
results = json.load(open(OUT)) if os.path.exists(OUT) else []
done = {(r['policy'], r['profile']) for r in results}
for pname, prof in PLAN:
    ck = POLICIES[pname]
    if True:
        label = prof or 'dense-medium-original'
        if (pname, label) in done:
            continue
        t = time.time()
        r = evaluate('data', 'cuda', ck, episodes=EPISODES, mode='dense', seed=SEED, dynamics='coordinated',
                     map_profile=prof, allow_transfer=prof is not None)
        eps = r['episodes']
        row = {'policy': pname, 'profile': label, 'seed_start': SEED, 'episodes': EPISODES,
               'successes': sum(bool(e['success']) for e in eps),
               'collisions': sum(bool(e['collision']) for e in eps),
               'timeouts': sum(bool(e['timeout']) for e in eps),
               'mean_distance_start': sum(e['distance_start'] for e in eps) / len(eps),
               'mean_distance_end': r.get('mean_distance_end'),
               'mean_steps_collision': (sum(e['steps'] for e in eps if e['collision']) /
                                        max(1, sum(bool(e['collision']) for e in eps))),
               'seconds': round(time.time() - t)}
        results.append(row)
        json.dump(results, open(OUT, 'w'), indent=1)
        print(row, flush=True)
