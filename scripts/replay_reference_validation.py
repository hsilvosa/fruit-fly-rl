"""Read-only reproducibility replay of the three historical medium dense-room winners on their own
recorded VALIDATION pools (not reserved tests). Writes only to runs/verification/reference-recovery-1."""
import json, os, sys, time, hashlib
os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
import torch
from fly_rl.training.evaluation import evaluate

OUT = 'runs/verification/reference-recovery-1'
os.makedirs(OUT, exist_ok=True)
names = sys.argv[1:] or ['sensors-v3-v1', 'ray-risk-v1', 'approach-v1']
for n in names:
    ft = json.load(open(f'runs/training/{n}/selected/final-test.json'))
    sel = ft['selection']
    val = sel['validation']
    ckpt = f'runs/training/{n}/selected/selected-policy.zip'
    seed = val['seed_start']
    episodes = len(val['episodes'])
    t = time.time()
    result = evaluate('data', 'cuda', ckpt, episodes=episodes, mode='dense', seed=seed,
                      dynamics='coordinated', route_metrics=False)
    rec = {r['seed']: r for r in val['episodes']}
    rows = result['episodes'] if 'episodes' in result else []
    same = 0
    detail = []
    for r in rows:
        o = rec.get(r['seed'])
        if o is None:
            continue
        key = lambda x: (bool(x['success']), bool(x['collision']), bool(x['timeout']))
        match = key(r) == key(o)
        same += match
        detail.append({'seed': r['seed'], 'replay': key(r), 'recorded': key(o), 'steps_replay': r.get('steps'),
                       'steps_recorded': o.get('steps'), 'match': match})
    summary = {
        'experiment': n, 'checkpoint': ckpt,
        'checkpoint_sha256': hashlib.sha256(open(ckpt, 'rb').read()).hexdigest(),
        'validation_seed_start': seed, 'episodes': episodes,
        'replay_success_rate': result.get('success_rate'), 'recorded_validation_success_rate': val.get('success_rate'),
        'replay_collision_rate': result.get('collision_rate'), 'replay_timeout_rate': result.get('timeout_rate'),
        'outcome_matches': same, 'compared': len(detail), 'seconds': time.time() - t,
        'torch': torch.__version__, 'detail': detail,
    }
    json.dump(summary, open(f'{OUT}/{n}-validation-replay.json', 'w'), indent=1)
    print(n, 'replay', summary['replay_success_rate'], 'recorded', summary['recorded_validation_success_rate'],
          'outcome matches', same, '/', len(detail), 'sec', round(summary['seconds']), flush=True)
