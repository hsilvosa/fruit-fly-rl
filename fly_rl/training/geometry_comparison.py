"""Frozen equal-budget baseline/curriculum experiment, launched explicitly."""
import json
import shutil
import time
from pathlib import Path
from fly_rl.training.geometry_curriculum import VERSION, PROTOCOL, GeometrySchedule
from fly_rl.training.fresh_sensor_comparison import prepare_fresh_comparison, validate_budget, code_hashes, initialize_pair
from fly_rl.training.generalization import sha256, final_test
from fly_rl.training.suites import load_suite
from fly_rl.training.test_access import require_unconsumed
from fly_rl.training.dense_training import train_dense
from fly_rl.training.experiment_selection import select_experiment
from fly_rl.simulation.sensors import SENSOR_V3


def validate_profiles(suite, mastery=False):
    profiles = suite.get('training_profiles', [])
    if mastery:
        from fly_rl.training.mastery_curriculum import validate_mastery_profiles,practice_partition
        validate_mastery_profiles(profiles)
        practice_partition(suite)
    else:GeometrySchedule(1, profiles)
    if suite.get('map_profile') != profiles[-1]:
        raise ValueError('Last frozen training profile must be the fixed evaluation target')
    for a, b in zip(profiles, profiles[1:]):
        if any(x > y for x, y in zip(a['room_size'], b['room_size'])) or a['wall_count'] > b['wall_count'] or a['obstacle_count'] > b['obstacle_count']:
            raise ValueError('Declare profiles in increasing size/partition/count order')
    return profiles


def prepare_geometry_comparison(suite, output, steps_per_seed=None, batch=8, rounds=2, seeds=(42, 73), data='data', mastery=False):
    audited = load_suite(suite)
    profiles = validate_profiles(audited,mastery)
    plan = prepare_fresh_comparison(suite, output, steps_per_seed, batch, rounds, seeds, data)
    plan.update(kind='fresh-v3-geometry-comparison', curriculum=PROTOCOL, sensor_version=SENSOR_V3,
                training_profiles=profiles, evaluation_profile=audited['map_profile'],
                baseline='target profile at every reset',
                selection='validation success, fewer collisions, lower ending distance; baseline wins exact arm tie',
                initialization='same fresh v3 checkpoint per seed in both arms; empty optimizer state')
    if mastery:
        from fly_rl.training.mastery_curriculum import PROTOCOL as MASTERY_PROTOCOL,practice_partition
        training,practice=practice_partition(audited)
        plan.update(kind='fresh-v3-mastery-comparison',curriculum=MASTERY_PROTOCOL,
                    optimization_layout_seeds=training,practice_layout_seeds=practice,
                    selection='trained candidates only; positive validation success required for final assessment; distance rounded to 6 decimals; stable baseline tie')
    Path(output).write_text(json.dumps(plan, indent=2), encoding='utf-8')
    return plan


def freeze_geometry_winner(groups, output, budgets, mastery=False):
    records = []
    for arm, folder in sorted(groups):
        folder = Path(folder)
        state = json.loads((folder/'experiment.json').read_text(encoding='utf-8'))
        frozen = json.loads((folder/'selection.json').read_text(encoding='utf-8'))
        if state['status'] != 'completed' or state.get('final_test_evaluated'):
            raise ValueError('Completed validation-only groups required')
        if sorted((r['training_seed'], r['added_transitions']) for r in state['seed_experiments']) != sorted(budgets.items()):
            raise ValueError('Matched declared seed budgets required')
        for path, digest in [(frozen['checkpoint'], frozen['checkpoint_sha256']),
                             (str(Path(frozen['checkpoint']).with_suffix('.json')), frozen['metadata_sha256']),
                             (frozen['suite'], frozen['suite_sha256'])]:
            if sha256(path) != digest:
                raise ValueError('Frozen integrity mismatch')
        suite = load_suite(frozen['suite'])
        require_unconsumed(suite)
        validate_profiles(suite,mastery)
        config = frozen['evaluation_configuration']
        if config.get('sensor_version') != SENSOR_V3 or config.get('map_profile') != suite['map_profile']:
            raise ValueError('Matched v3 fixed-target evaluation required')
        records.append((arm, state, frozen))
    if len(records) != 2 or {r[0] for r in records} != {'baseline', 'curriculum'}:
        raise ValueError('Exactly one baseline and curriculum group required')
    if len({(r[2]['suite_sha256'], r[2]['dynamics'], json.dumps(r[2]['evaluation_configuration'], sort_keys=True)) for r in records}) != 1:
        raise ValueError('Matched evaluation configuration required')
    def rank(record):
        v = record[2]['validation']
        distance=round(v['mean_distance_end'],6) if mastery else v['mean_distance_end']
        return v['success_rate'], -v['collision_rate'], -distance
    all_records=records
    if mastery:
        eligible=[r for r in records if r[2]['validation']['success_rate']>0
                  and json.loads(Path(r[2]['checkpoint']).with_suffix('.json').read_text())['timesteps']>0]
        if not eligible:
            return {'status':'no_successful_candidate','selected_arm':None,'final_test_evaluated':False,
                    'reason':'No trained candidate reached a target in validation; final pool remains unused'}
        records=eligible
    arm, state, frozen = max(records, key=rank)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for source, name in [(frozen['checkpoint'], 'selected-policy.zip'),
                         (Path(frozen['checkpoint']).with_suffix('.json'), 'selected-policy.json'), (frozen['suite'], 'suite.json')]:
        shutil.copy2(source, output/name)
    comparisons = [{'arm': r[0], 'validation': r[2]['validation'], 'seed_experiments': r[1]['seed_experiments']} for r in all_records]
    frozen = dict(frozen, checkpoint=str((output/'selected-policy.zip').resolve()),
                  suite=str((output/'suite.json').resolve()), selected_arm=arm, geometry_comparison=comparisons)
    (output/'selection.json').write_text(json.dumps(frozen, indent=2), encoding='utf-8')
    result = {'status': 'completed', 'kind': 'validation-selected-geometry-comparison', 'selected_arm': arm,
              'selected_experiment': state['selected_experiment'], 'validation': frozen['validation'],
              'geometry_comparison': comparisons, 'final_test_evaluated': False,
              'training': {'added_transitions': 2*sum(budgets.values())}}
    (output/'experiment.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def run_geometry_comparison(configuration, output, device='cuda'):
    plan = json.loads(Path(configuration).read_text(encoding='utf-8'))
    total = validate_budget(plan['steps_per_seed'], plan['batch'], plan['rounds'], plan['seeds'])
    if total is None or plan['status'] != 'configured':
        raise ValueError('Agree an explicit training budget before running this draft')
    from fly_rl.training.mastery_curriculum import VERSION as MASTERY_VERSION,PROTOCOL as MASTERY_PROTOCOL,practice_partition
    mastery=plan['kind']=='fresh-v3-mastery-comparison'
    expected_protocol=MASTERY_PROTOCOL if mastery else PROTOCOL
    if (plan['kind'] not in ['fresh-v3-geometry-comparison','fresh-v3-mastery-comparison'] or plan['version'] != 1 or plan['curriculum'] != expected_protocol
            or plan['sensor_version'] != SENSOR_V3 or plan['dynamics'] != 'coordinated' or plan['route_metrics'] is not True
            or total != plan['total_training_transitions']):
        raise ValueError('Unsupported or inconsistent geometry protocol')
    if code_hashes() != plan['source_hashes'] or sha256(plan['suite']) != plan['suite_sha256']:
        raise ValueError('Frozen source or suite changed; prepare a new configuration')
    suite = load_suite(plan['suite'])
    if validate_profiles(suite,mastery) != plan['training_profiles'] or suite['map_profile'] != plan['evaluation_profile']:
        raise ValueError('Frozen curriculum profile mismatch')
    if mastery:
        training,practice=practice_partition(suite)
        if plan['optimization_layout_seeds']!=training or plan['practice_layout_seeds']!=practice:
            raise ValueError('Frozen training-practice partition mismatch')
    require_unconsumed(suite)
    audit = json.loads((Path(plan['data'])/'processed/audit.json').read_text(encoding='utf-8'))
    if audit['fingerprint'] != plan['data_fingerprint']:
        raise ValueError('Dataset fingerprint mismatch')
    base = Path(output)
    base.mkdir(parents=True, exist_ok=False)
    started = time.time()
    aliases = {str(p.resolve()): sha256(p) for p in Path('runs').glob('*policy.*') if p.suffix in ['.zip', '.json']}
    state = {'status': 'running', 'kind': plan['kind'], 'configuration_sha256': sha256(configuration),
             'budget_added_transitions': total, 'initializations': [], 'results': [],
             'test_evaluated': False, 'alias_hashes_before': aliases, 'evaluation_profile': suite['map_profile']}
    shutil.copy2(configuration, base/'configuration.json')
    def save():
        temporary = base/'status.tmp'
        temporary.write_text(json.dumps(state, indent=2), encoding='utf-8')
        temporary.replace(base/'status.json')
    save()
    try:
        root = Path(__file__).resolve().parents[2]
        for name in plan['source_hashes']:
            target = base/'source'/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root/name, target)
        for seed in plan['seeds']:
            state['stage'] = f'initialize-{seed}'
            save()
            proof = initialize_pair(plan['data'], device, suite, seed, base/f'initial-{seed}')
            if proof['data_fingerprint'] != plan['data_fingerprint']:
                raise ValueError('Actual full graph does not match plan')
            state['initializations'].append(proof)
            save()
        groups = []
        for arm, intervention in [('baseline', None), ('curriculum', MASTERY_VERSION if mastery else VERSION)]:
            members = []
            for seed in plan['seeds']:
                state['stage'] = f'{arm}-seed-{seed}'
                save()
                folder = base/f'{arm}-seed-{seed}'
                result = train_dense(plan['data'], device, plan['suite'], folder, base/f'initial-{seed}/v3.zip',
                                     plan['steps_per_seed'], plan['batch'], 'coordinated', plan['rounds'], seed,
                                     False, True, curriculum=intervention,**({'mastery':True} if mastery else {}))
                if result['training']['added_transitions'] != plan['steps_per_seed']:
                    raise ValueError('Declared training budget mismatch')
                counters = [r['training'].get('curriculum') for r in result['results']]
                state['results'].append({'arm': arm, 'seed': seed, 'validation': result['validation'],
                                         'added_transitions': result['training']['added_transitions'], 'curriculum_rounds': counters})
                members.append(folder)
                save()
            group = base/f'{arm}-selected'
            select_experiment(members, group,**({'distance_precision':6} if mastery else {}))
            groups.append((arm, group))
        state['stage'] = 'validation-only-selection'
        save()
        winner = freeze_geometry_winner(groups, base/'selected', {s: plan['steps_per_seed'] for s in plan['seeds']},mastery=mastery)
        if winner['status']=='no_successful_candidate':
            state.update(status='completed',stage='no-successful-candidate',selection_outcome=winner,
                         selected_arm=None,test_evaluated=False)
            return state
        state['selected_arm'], state['stage'] = winner['selected_arm'], 'frozen-final-test'
        save()
        final = final_test(plan['data'], device, base/'selected')
        if not all(sha256(p) == h for p, h in aliases.items()):
            raise RuntimeError('Original launcher alias changed')
        state.update(status='completed', stage='done', test_evaluated=True,
                     final_summary=final['selected_summary'], untrained_summary=final['untrained_summary'])
    except BaseException as exc:
        state.update(status='failed', error=repr(exc))
        raise
    finally:
        state['alias_hashes_after'] = {p: sha256(p) if Path(p).exists() else None for p in aliases}
        state['aliases_unchanged'] = state['alias_hashes_after'] == aliases
        state['elapsed_seconds'] = time.time()-started
        save()
    return state
