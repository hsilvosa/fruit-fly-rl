"""Build the historical medium dense-room reference manifest from preserved records (read-only).

Writes private/reference-recovery-1-evidence/historical-reference-manifest.json. Does not train, does not open any pool,
and does not modify checkpoints, aliases or sources.
"""
import hashlib
import json
import os
import subprocess

ROOT = 'C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'
os.chdir(ROOT)
GIT = ['git', '-c', f'safe.directory={ROOT}']
BS = chr(92)

# Experiments that produced the historical medium dense-room results (own final pools).
EXPERIMENTS = {
    'sensors-v3-v1': 'Warm-start sensor comparison',
    'approach-v1': 'Near-goal curriculum comparison (selected: normal training)',
    'ray-risk-v1': 'Observed-ray risk comparison (selected: normal training)',
    'dense-flight-v1': 'Dense adaptation / original coordinated dense launcher',
    'sensors-fresh-v1': 'Fresh sensor comparison',
}
ALIASES = ['runs/dense-flight-policy.zip', 'runs/dense-policy.zip', 'runs/navigation-policy.zip']
CORE = ['fly_rl/simulation/sensors.py', 'fly_rl/simulation/flight.py', 'fly_rl/simulation/world.py',
        'fly_rl/simulation/planner.py', 'fly_rl/training/dense_training.py', 'fly_rl/training/learning.py',
        'fly_rl/training/evaluation.py', 'fly_rl/connectome/brain.py', 'fly_rl/connectome/anatomy.py']


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    path = path.replace(BS, '/')
    return os.path.relpath(path, ROOT).replace(BS, '/') if os.path.isabs(path) else path


def final_test_path(name):
    for p in (f'runs/training/{name}/selected/final-test.json', f'runs/training/{name}/final-test.json'):
        if os.path.exists(p):
            return p
    return None


def core_diff(rev):
    out = subprocess.run(GIT + ['diff', '--ignore-cr-at-eol', '--shortstat', rev, 'HEAD', '--'] + CORE,
                         capture_output=True, text=True).stdout.strip()
    per_file = {}
    for f in CORE:
        d = subprocess.run(GIT + ['diff', '--ignore-cr-at-eol', '--numstat', rev, 'HEAD', '--', f],
                           capture_output=True, text=True).stdout.split()
        per_file[f] = {'added': int(d[0]), 'removed': int(d[1])} if d else {'added': 0, 'removed': 0}
    return {'shortstat': out or 'identical', 'per_file': per_file}


records = []
for name, label in EXPERIMENTS.items():
    fp = final_test_path(name)
    if fp is None:
        records.append({'experiment': name, 'label': label, 'status': 'final-test record not found'})
        continue
    ft = json.load(open(fp))
    sel = ft['selection']
    summary = ft['selected_summary']
    ckpt = rel(sel['checkpoint'])
    meta = ckpt[:-4] + '.json'
    policy_meta = json.load(open(meta))
    env = dict(policy_meta.get('environment', {}))
    layouts = env.pop('training_layout_seeds', None)
    rev = sel['software']['source_revision']
    consumed = ft.get('test_access_record')
    rec = {
        'experiment': name,
        'label': label,
        'final_test_record': fp,
        'final_test_sha256': sha(fp),
        'result': {
            'successes': summary['successes'], 'episodes': summary['episodes'],
            'success_rate': summary['success_rate'], 'wilson_95': summary['success_wilson_95'],
            'collisions': round(summary['collision_rate'] * summary['episodes']),
            'timeouts': round(summary['timeout_rate'] * summary['episodes']),
            'untrained_same_interface_successes': ft['untrained_summary']['successes'],
            'evaluation_seed_start': ft['selected']['seed_start'],
            'pool_consumed_record': rel(consumed) if consumed else None,
        },
        'checkpoint': {
            'path': ckpt,
            'sha256_recorded_at_test': sel['checkpoint_sha256'],
            'sha256_now': sha(ckpt),
            'metadata_sha256_recorded_at_test': sel['metadata_sha256'],
            'metadata_sha256_now': sha(meta),
            'hashes_match_record': sha(ckpt) == sel['checkpoint_sha256'] and sha(meta) == sel['metadata_sha256'],
            'selected_from': rel(sel['source']),
        },
        'contract': {
            'fingerprint': policy_meta.get('fingerprint'),
            'sensor_version': policy_meta.get('sensor_version',
                                              'sensors-v2-128-distance-128-approach-13-state (default; key absent)'),
            'reward_version': policy_meta.get('reward_version'),
            'lifetime_timesteps': policy_meta.get('timesteps'),
            'readout_version': policy_meta.get('readout_version', 'random-pool-256-v1 (default; key absent)'),
            'environment': env,
            'training_layout_seed_count': len(layouts) if layouts is not None else None,
            'evaluation_configuration': sel.get('evaluation_configuration'),
            'dataset': policy_meta.get('dataset'),
        },
        'software_at_test': sel['software'],
        'source_revision': rev,
        'core_source_drift_to_HEAD': core_diff(rev),
        'validation_record': {
            'pool_seed_start': sel['validation']['seed_start'],
            'episodes': len(sel['validation']['episodes']),
            'success_rate': sel['validation']['success_rate'],
        },
    }
    records.append(rec)

aliases = {a: {'sha256': sha(a), 'bytes': os.path.getsize(a)} for a in ALIASES if os.path.exists(a)}
manifest = {
    'purpose': 'Trace historical medium dense-room learned results to exact preserved checkpoints.',
    'task': 'dense room 32 x 32 x 12, 48 obstacles, coordinated dynamics, episode limit 1200 ticks',
    'note': 'Each result used its own final pool. Pools are consumed. Rows are not a paired ranking.',
    'aliases_now': aliases,
    'experiments': records,
}
os.makedirs('private/reference-recovery-1-evidence', exist_ok=True)
with open('private/reference-recovery-1-evidence/historical-reference-manifest.json', 'w') as f:
    json.dump(manifest, f, indent=1)
for r in records:
    if 'result' in r:
        print(r['experiment'], f"{r['result']['successes']}/{r['result']['episodes']}",
              'hash match', r['checkpoint']['hashes_match_record'], r['source_revision'][:8],
              r['contract']['sensor_version'][:10], r['contract']['lifetime_timesteps'])
print('aliases', {k: v['sha256'][:12] for k, v in aliases.items()})
