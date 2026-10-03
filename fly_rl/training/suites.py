"""Freeze and audit configurable, disjoint layouts before learning/testing."""
import hashlib
import json
from pathlib import Path
from fly_rl.simulation.world import FlightWorld, WORLD_VERSION
from fly_rl.simulation import world as world_module
from fly_rl.simulation.map_profiles import PROFILE_VERSION, resolve_profile, difficulty_metrics


def suite_world(suite, seed, profile=None):
    return FlightWorld(seed, suite['mode'], map_profile=profile or suite.get('map_profile'))


def suite_geometries(suite):
    for pool in suite['splits'].values():
        for seed in pool['seeds']:
            yield geometry_hash(suite_world(suite, seed))
    for variant in suite.get('training_variants', []):
        for seed in suite['splits']['train']['seeds']:
            yield geometry_hash(suite_world(suite, seed, variant['profile']))


def layout_hash(world):
    payload = {'room': world.room.tolist(), 'start': world.position.tolist(), 'target': world.target.tolist(),
               'yaw': world.yaw, 'boxes': [(a.tolist(), b.tolist()) for a, b in world.obstacles]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def geometry_hash(world):
    payload = {'room': world.room.tolist(), 'start': world.position.tolist(), 'target': world.target.tolist(),
               'boxes': [(a.tolist(), b.tolist()) for a, b in world.obstacles]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def load_suite(path):
    suite = json.loads(Path(path).read_text(encoding='utf-8'))
    if suite['world_version'] != (PROFILE_VERSION if suite.get('map_profile') else WORLD_VERSION):
        raise ValueError('Suite generator version mismatch')
    if suite.get('map_profile'):
        if suite.get('schema_version')!=3 or suite.get('mode')!='dense': raise ValueError('Profiled suite requires schema 3 dense mode')
        if resolve_profile(suite['map_profile']).to_dict()!=suite['map_profile']: raise ValueError('Noncanonical frozen map profile')
    if set(suite['splits']) != {'train', 'validation', 'test'}:
        raise ValueError('Suite must contain train, validation, and test')
    seeds = [s for pool in suite['splits'].values() for s in pool['seeds']]
    if len(seeds) != len(set(seeds)):
        raise ValueError('Overlapping suite seeds')
    if any(type(s) is not int or not 0 <= s < 2**32 for s in seeds):
        raise ValueError('Invalid suite seeds')
    if len(suite.get('source_sha256', '')) != 64:
        raise ValueError('Frozen suite generator code has changed')
    seen = set()
    for name, pool in suite['splits'].items():
        if not pool['seeds'] or len(pool.get('layout_sha256', [])) != len(pool['seeds']):
            raise ValueError('Frozen layout hashes missing')
        if name != 'train' and len(pool['seeds']) > 64:
            raise ValueError('Evaluation pools support at most 64 layouts')
        geometries, metrics = [], []
        for seed, expected in zip(pool['seeds'], pool['layout_sha256']):
            world = suite_world(suite, seed)
            if layout_hash(world) != expected:
                raise ValueError('Frozen layout fingerprint mismatch')
            geometry = geometry_hash(world)
            if geometry in seen:
                raise ValueError('Duplicate geometry across frozen suite')
            seen.add(geometry)
            geometries.append(geometry)
            if suite.get('map_profile'):metrics.append(difficulty_metrics(world))
        if 'geometry_sha256' in pool:
            if geometries != pool['geometry_sha256']:
                raise ValueError('Frozen geometry fingerprint mismatch')
        if suite.get('map_profile'):
            if pool.get('metrics') != metrics:
                raise ValueError('Frozen difficulty metrics mismatch')
    if suite.get('map_profile'):
        profiles=suite.get('training_profiles', [])
        canonical=[resolve_profile(p).to_dict() for p in profiles]
        names=[p['name'] for p in canonical]
        if not names or len(names)!=len(set(names)) or canonical!=profiles or suite['map_profile'] not in profiles:
            raise ValueError('Invalid frozen training profiles')
        variants=suite.get('training_variants', [])
        if [v['profile'] for v in variants]!=[p for p in profiles if p!=suite['map_profile']]:
            raise ValueError('Missing curriculum training variants')
        for variant in variants:
            worlds=[suite_world(suite,s,variant['profile']) for s in suite['splits']['train']['seeds']]
            if variant.get('layout_sha256')!=[layout_hash(w) for w in worlds] or variant.get('geometry_sha256')!=[geometry_hash(w) for w in worlds]:
                raise ValueError('Frozen curriculum variant fingerprint mismatch')
            if variant.get('metrics')!=[difficulty_metrics(w) for w in worlds]:raise ValueError('Frozen curriculum metrics mismatch')
            for w in worlds:
                geometry=geometry_hash(w)
                if geometry in seen:raise ValueError('Duplicate geometry across curriculum variants')
                seen.add(geometry)
    if 'test_fingerprint' in suite:
        expected=hashlib.sha256(json.dumps(sorted(suite['splits']['test']['geometry_sha256'])).encode()).hexdigest()
        if suite['test_fingerprint']!=expected: raise ValueError('Test pool fingerprint mismatch')
    return suite


def prepare_suite(output, train_start=30000, validation_start=40000, test_start=50000,
                  train_count=256, validation_count=32, test_count=64, exclude_suites=(),map_profile=None,training_profiles=()):
    output = Path(output)
    if output.exists():
        raise ValueError('Choose a new suite path; frozen suites are never overwritten')
    ranges = {'train': (train_start, train_count), 'validation': (validation_start, validation_count),
              'test': (test_start, test_count)}
    for name, (start, count) in ranges.items():
        if type(start) is not int or type(count) is not int or start < 0 or count < 1 or start+count > 2**32:
            raise ValueError('Split starts/counts must be valid positive ranges')
        if count > (4096 if name == 'train' else 64):
            raise ValueError('Split exceeds bounded suite size')
    all_seeds = [s for start, count in ranges.values() for s in range(start, start+count)]
    if len(all_seeds) != len(set(all_seeds)):
        raise ValueError('Overlapping suite seeds')
    excluded_seeds, excluded_geometry, exclusions = set(), set(), []
    for path in exclude_suites:
        previous = load_suite(path)
        for pool in previous['splits'].values():
            excluded_seeds.update(pool['seeds'])
        excluded_geometry.update(suite_geometries(previous))
        exclusions.append({'path': str(Path(path).resolve()), 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()})
    if excluded_seeds.intersection(all_seeds):
        raise ValueError('Seed reuse from excluded historical suite')
    suite = {'schema_version': 2, 'mode': 'dense', 'world_version': WORLD_VERSION,
             'room_size': [32, 32, 12], 'obstacles': 48,
             'source_sha256': hashlib.sha256(Path(world_module.__file__).read_bytes()).hexdigest(),
             'excluded_suites': exclusions, 'splits': {}}
    profile=resolve_profile(map_profile)
    if training_profiles and profile is None:raise ValueError('Training profiles require a profiled suite')
    if profile:
        profiles=[resolve_profile(p).to_dict() for p in (training_profiles or [profile])]
        names=[p['name'] for p in profiles]
        if len(names)!=len(set(names)) or profile.to_dict() not in profiles:raise ValueError('Use unique training profiles including the target')
        suite.update(schema_version=3,world_version=PROFILE_VERSION,map_profile=profile.to_dict(),
                     room_size=list(profile.room_size),obstacles=profile.obstacle_count,training_profiles=profiles,training_variants=[])
    seen = set()
    for name, (start, count) in ranges.items():
        fingerprints, geometries = [], []
        for seed in range(start, start+count):
            world = suite_world(suite, seed); geometry = geometry_hash(world)
            if geometry in seen or geometry in excluded_geometry:
                raise ValueError('Duplicate geometry within suite or excluded historical pools')
            seen.add(geometry); fingerprints.append(layout_hash(world)); geometries.append(geometry)
        suite['splits'][name] = {'seeds': list(range(start, start+count)),
                                'layout_sha256': fingerprints, 'geometry_sha256': geometries}
        if profile:suite['splits'][name]['metrics']=[difficulty_metrics(suite_world(suite,s)) for s in range(start,start+count)]
    if profile:
        for variant in [p for p in profiles if p!=profile.to_dict()]:
            worlds=[suite_world(suite,s,variant) for s in suite['splits']['train']['seeds']]
            for w in worlds:
                geometry=geometry_hash(w)
                if geometry in seen or geometry in excluded_geometry:raise ValueError('Duplicate or historical curriculum geometry')
                seen.add(geometry)
            suite['training_variants'].append({'profile':variant,'layout_sha256':[layout_hash(w) for w in worlds],
                'geometry_sha256':[geometry_hash(w) for w in worlds],'metrics':[difficulty_metrics(w) for w in worlds]})
    suite['test_fingerprint'] = hashlib.sha256(json.dumps(sorted(suite['splits']['test']['geometry_sha256'])).encode()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as handle:
        json.dump(suite, handle, indent=2)
    return {'suite': str(output), 'splits': {k: len(v['seeds']) for k, v in suite['splits'].items()},
            'excluded_suites': exclusions, 'duplicates': 0, 'final_test_evaluated': False}
