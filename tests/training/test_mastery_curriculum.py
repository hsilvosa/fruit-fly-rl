import json
import numpy as np
import pytest
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import PROFILES
from fly_rl.training.mastery_curriculum import MasterySchedule, MasteryWorld, practice_partition, VERSION

PROFILES_LIST = ['gate-near', 'gate-long', 'passages']
PRACTICE = list(range(1000, 1016))


def probes(schedule, counts=(7, 7)):
    return [{'training_invoked': False, 'map_profile': schedule.profiles[schedule.stage].to_dict(),
             'episodes': [{'seed': seed, 'success': j < counts[i], 'collision': j >= counts[i],
                           'timeout': False, 'steps': 100}
                          for j, seed in enumerate(PRACTICE[i*8:(i+1)*8])]} for i in range(2)]


def test_elapsed_budget_and_training_success_cannot_open_gate():
    s = MasterySchedule(100, PROFILES_LIST, PRACTICE)
    s.transitions = 100
    s.outcomes['gate-near']['success'] = 100
    assert s.stage == 0
    assert not s.record_practice(probes(s, (8, 6)))
    assert s.stage == 0
    assert s.record_practice(probes(s)) and s.stage == 1
    assert s.record_practice(probes(s)) and s.stage == 2
    assert s.record_practice(probes(s)) and s.stage == 2


def test_validation_or_wrong_stage_or_optimization_is_not_practice():
    s = MasterySchedule(100, PROFILES_LIST, PRACTICE)
    for kind in ['seeds', 'profile', 'optimizer', 'duplicate']:
        p = probes(s)
        if kind == 'seeds':p[0]['episodes'][0]['seed'] = 2000
        if kind == 'profile':p[0]['map_profile'] = PROFILES['large'].to_dict()
        if kind == 'optimizer':p[0]['training_invoked'] = True
        if kind == 'duplicate':p[0]['episodes'][0]['seed'] = 1001
        with pytest.raises(ValueError, match='training-practice'):s.record_practice(p)
    assert s.stage == 0 and not s.probes


def test_resume_preserves_mastery_and_exposure_instead_of_inferring_stage_from_time():
    s = MasterySchedule(1000, PROFILES_LIST, PRACTICE)
    s.transitions = 500
    s.record_practice(probes(s))
    s.steps['gate-near'] = 500
    state = json.loads(json.dumps(s.snapshot()))
    restored = MasterySchedule(1000, PROFILES_LIST, PRACTICE, 500, state)
    assert restored.stage == 1 and restored.steps['gate-near'] == 500
    assert restored.probes == s.probes
    with pytest.raises(ValueError, match='saved gate'):MasterySchedule(1000, PROFILES_LIST, PRACTICE, 500)
    with pytest.raises(ValueError, match='resume'):MasterySchedule(1000, PROFILES_LIST, PRACTICE, 501, state)


def test_practice_partition_excludes_optimizer_and_validation_layouts():
    suite = {'splits': {'train': {'seeds': list(range(32))}, 'validation': {'seeds': [100]}, 'test': {'seeds': [200]}}}
    optimizer, practice = practice_partition(suite)
    assert optimizer == list(range(16)) and practice == list(range(16,32))
    assert not set(optimizer).intersection(practice)
    with pytest.raises(ValueError, match='32'):practice_partition({'splits': {'train': {'seeds': list(range(16))}}})


def test_profile_changes_only_at_reset_and_easier_tasks_are_retained():
    s = MasterySchedule(1000, PROFILES_LIST, PRACTICE)
    w = MasteryWorld(seed=42, mode='dense', dynamics='coordinated', layout_seeds=list(range(20)),
                     map_profile='passages', schedule=s)
    assert w.map_profile.name == 'gate-near'
    s.record_practice(probes(s))
    w.step(np.zeros(4))
    assert w.map_profile.name == 'gate-near'
    seen = set()
    for seed in range(50):
        w.reset(seed=seed)
        seen.add(w.map_profile.name)
    assert seen == {'gate-near', 'gate-long'}


@pytest.mark.parametrize('profile', ['gate-near', 'gate-long'])
def test_passage_is_traversable_with_actual_flight_controls(profile):
    # An oracle follows the hidden certificate solely to test dynamics. It is
    # never a policy input, training reward, demonstration or learning claim.
    for seed in range(8):
        w = FlightWorld(seed, mode='dense', dynamics='coordinated', map_profile=profile)
        route, index = w.reference_route[1:], 0
        for _ in range(w.episode_limit):
            delta = route[index]-w.position
            if np.linalg.norm(delta) < .3 and index < len(route)-1:
                index += 1
                delta = route[index]-w.position
            error = (np.arctan2(delta[1], delta[0])-w.yaw+np.pi)%(2*np.pi)-np.pi
            desired = min(.7, np.linalg.norm(delta[:2])*.8)*max(0, np.cos(error))
            thrust = np.clip((desired-np.linalg.norm(w.velocity[:2]))*2+.6*desired, -1, 1)/3
            vz = np.clip(delta[2], -.5, .5)
            vertical = np.clip((vz-w.velocity[2])*2+.8*vz, -2.5, 2.5)/2.5
            _, _, terminated, truncated, info = w.step([thrust, 0, vertical, np.clip(error*2/1.8, -1, 1)])
            if terminated or truncated:break
        assert info['success'] and not info['collision']


def test_mastery_preparation_freezes_practice_without_starting_training(tmp_path):
    from fly_rl.training.suites import prepare_suite
    from fly_rl.training.geometry_comparison import prepare_geometry_comparison
    data = tmp_path/'data'/'processed'
    data.mkdir(parents=True)
    (data/'audit.json').write_text('{"fingerprint":"test-only"}')
    suite = tmp_path/'suite.json'
    prepare_suite(suite, 100, 200, 300, 32, 2, 2, map_profile='passages', training_profiles=PROFILES_LIST)
    plan = prepare_geometry_comparison(suite, tmp_path/'draft.json', data=data.parent, mastery=True)
    assert plan['status'] == 'draft-budget-required' and plan['total_training_transitions'] is None
    assert plan['optimization_layout_seeds'] == list(range(100,116))
    assert plan['practice_layout_seeds'] == list(range(116,132))
    assert plan['curriculum']['version'] == VERSION


def test_zero_success_stops_comparison_before_final_access(tmp_path, monkeypatch):
    import fly_rl.training.geometry_comparison as module
    from fly_rl.training.suites import prepare_suite
    from fly_rl.training.generalization import sha256
    from fly_rl.simulation.sensors import SENSOR_V3
    monkeypatch.chdir(tmp_path)
    data = tmp_path/'data'/'processed'
    data.mkdir(parents=True)
    (data/'audit.json').write_text('{"fingerprint":"test-only"}')
    suite = tmp_path/'suite.json'
    prepare_suite(suite, 100, 200, 300, 32, 2, 2, map_profile='passages', training_profiles=PROFILES_LIST)
    configuration = tmp_path/'plan.json'
    plan = module.prepare_geometry_comparison(suite, configuration, 4096, 8, 1, data=data.parent, mastery=True)
    validation = {'success_rate':0., 'collision_rate':0., 'mean_distance_end':20.}
    calls = []
    def initialize(data, device, suite, seed, folder):
        folder.mkdir()
        (folder/'v3.zip').write_bytes(b'initial')
        return {'data_fingerprint':'test-only'}
    def train(*args, **kwargs):
        calls.append(kwargs)
        return {'training':{'added_transitions':4096},'validation':validation,'results':[]}
    def select(members, folder, **kwargs):
        folder.mkdir()
        checkpoint=folder/'policy.zip';checkpoint.write_bytes(b'test-only')
        checkpoint.with_suffix('.json').write_text('{"timesteps":4096}')
        (folder/'experiment.json').write_text(json.dumps({'status':'completed','seed_experiments':[
            {'training_seed':s,'added_transitions':4096} for s in [42,73]]}))
        (folder/'selection.json').write_text(json.dumps({'checkpoint':str(checkpoint),'checkpoint_sha256':sha256(checkpoint),
            'metadata_sha256':sha256(checkpoint.with_suffix('.json')),'suite':str(suite),'suite_sha256':sha256(suite),
            'dynamics':'coordinated','validation':validation,'evaluation_configuration':{'sensor_version':SENSOR_V3,
            'map_profile':plan['evaluation_profile']}}))
    monkeypatch.setattr(module,'initialize_pair',initialize)
    monkeypatch.setattr(module,'train_dense',train)
    monkeypatch.setattr(module,'select_experiment',select)
    monkeypatch.setattr(module,'final_test',lambda *a,**k:pytest.fail('Final pool must remain unused'))
    result=module.run_geometry_comparison(configuration,tmp_path/'run','cpu')
    assert result['status']=='completed' and result['stage']=='no-successful-candidate'
    assert result['selected_arm'] is None and result['test_evaluated'] is False
    assert all(c['mastery'] for c in calls)
    assert not (tmp_path/'run'/'selected').exists()


def test_dense_rounds_restore_gate_and_exclude_practice_from_optimizer(tmp_path, monkeypatch):
    import fly_rl.training.dense_training as module
    from fly_rl.training.suites import prepare_suite
    from fly_rl.simulation.sensors import SENSOR_V3
    monkeypatch.chdir(tmp_path)
    suite=tmp_path/'suite.json'
    prepare_suite(suite,100,200,300,32,2,2,map_profile='passages',training_profiles=PROFILES_LIST)
    initial=tmp_path/'initial.zip';initial.write_bytes(b'initial');initial.with_suffix('.json').write_text('{}')
    training=[]
    def train(*args,**kwargs):
        training.append(kwargs)
        assert kwargs['layout_seeds']==list(range(100,116))
        assert kwargs['practice_seeds']==list(range(116,132))
        s=MasterySchedule(8192,PROFILES_LIST,kwargs['practice_seeds'],kwargs['curriculum_offset'],kwargs['curriculum_state'])
        assert s.stage==len(training)-1
        s.transitions+=4096
        path=args[4];path.parent.mkdir(parents=True);path.write_bytes(b'trained');path.with_suffix('.json').write_text('{}')
        return {'added_transitions':4096,'curriculum':s.snapshot()}
    def evaluate(*args,**kwargs):
        if kwargs.get('allow_transfer'):
            return {'training_invoked':False,'map_profile':kwargs['map_profile'],'episodes':[
                {'seed':seed,'success':True,'collision':False,'timeout':False,'steps':100} for seed in range(args[5],args[5]+8)]}
        return {'success_rate':0.,'collision_rate':0.,'mean_distance_end':10.,'sensor_version':SENSOR_V3}
    monkeypatch.setattr(module,'train',train);monkeypatch.setattr(module,'evaluate',evaluate)
    result=module.train_dense('unused','cpu',suite,tmp_path/'run',initial,8192,8,'coordinated',2,42,False,
                              curriculum=VERSION,mastery=True)
    assert result['selection_outcome']=='no_successful_candidate' and not result['promoted']
    assert result['results'][-1]['training']['curriculum']['stage']==2
    assert training[1]['curriculum_state']['practice_checks'][0]['passed']


def test_initialization_cannot_win_and_both_method_results_are_retained(tmp_path, monkeypatch):
    from test_sensor_comparison import groups
    from fly_rl.training.suites import prepare_suite,load_suite
    from fly_rl.training.geometry_comparison import freeze_geometry_winner
    from fly_rl.training.generalization import sha256
    from fly_rl.simulation.sensors import SENSOR_V3
    monkeypatch.chdir(tmp_path)
    members=groups(tmp_path)
    suite=tmp_path/'suite.json'
    prepare_suite(suite,100,200,300,32,2,2,map_profile='gate-long',training_profiles=PROFILES_LIST[:2])
    target=load_suite(suite)['map_profile']
    for i,group in enumerate(members):
        path=group/'selection.json';record=json.loads(path.read_text())
        metadata=__import__('pathlib').Path(record['checkpoint']).with_suffix('.json')
        metadata.write_text(json.dumps({'timesteps':0 if i==0 else 4096}))
        record.update(suite=str(suite),suite_sha256=sha256(suite),metadata_sha256=sha256(metadata),
                      validation={'success_rate':1. if i==0 else .5,'collision_rate':0.,'mean_distance_end':1.})
        record['evaluation_configuration']={'sensor_version':SENSOR_V3,'map_profile':target}
        path.write_text(json.dumps(record))
    result=freeze_geometry_winner([('baseline',members[0]),('curriculum',members[1])],tmp_path/'selected',
                                  {42:65536,73:65536},mastery=True)
    assert result['selected_arm']=='curriculum'
    assert len(result['geometry_comparison'])==2
