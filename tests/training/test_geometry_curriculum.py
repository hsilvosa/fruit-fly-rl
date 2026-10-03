import json
import numpy as np
import pytest
from scipy import sparse
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.sensors import SENSOR_V3
from fly_rl.simulation.map_profiles import PROFILES
from fly_rl.training.learning import BrainEnv, make_policy, save_model, load_model
from fly_rl.training.geometry_curriculum import GeometrySchedule, GeometryWorld, configure_geometry_curriculum
from fly_rl.training.geometry_comparison import run_geometry_comparison, prepare_geometry_comparison, validate_profiles
from fly_rl.training.suites import prepare_suite, load_suite, layout_hash, suite_world


def env(batch=1, seed=42):
    return BrainEnv(batch=batch, device='cpu', seed=seed,
                    brain=Brain(matrix=sparse.eye(16, format='csr'), batch=batch, device='cpu', sensor_version=SENSOR_V3),
                    mode='dense', layout_seeds=[100, 101], dynamics='coordinated', sensor_version=SENSOR_V3, map_profile='large')


def test_transition_schedule_retains_easy_maps_and_preserves_round_offset():
    profiles = ['open', 'passages', 'large']
    s = GeometrySchedule(300, profiles)
    assert s.stage == 0
    s.transitions = 100
    assert s.stage == 1
    s.transitions = 200
    assert s.stage == 2 and s.snapshot()['mixture'] == [.1, .2, .7]
    assert GeometrySchedule(300, profiles, 150).stage == 1
    with pytest.raises(ValueError):GeometrySchedule(0, profiles)
    with pytest.raises(ValueError):GeometrySchedule(300, ['open', 'large'])


def test_profile_sampling_uses_only_training_seeds_and_frozen_geometries():
    schedule = GeometrySchedule(300, ['open', 'passages', 'large'])
    w = GeometryWorld(seed=42, mode='dense', layout_seeds=[100, 101], schedule=schedule,
                      dynamics='coordinated', sensor_version=SENSOR_V3, map_profile='large')
    seen = set()
    for _ in range(100):
        _, info = w.reset()
        assert w.seed_value in [100, 101]
        ordinary = suite_world({'mode': 'dense', 'map_profile': w.map_profile.to_dict()}, w.seed_value)
        assert layout_hash(w) == layout_hash(ordinary)
        seen.add(info['curriculum']['profile'])
    assert seen == {'open', 'passages', 'large'}
    assert sum(schedule.resets.values()) == 101 and schedule.transitions == 0


def test_shared_schedule_switches_at_resets_and_preserves_nonterminal_brain_state():
    e = env(2)
    s = configure_geometry_curriculum(e, 6, 0, 42, ['open', 'passages', 'large'])
    e.seed(42); e.reset()
    before_profile = e.worlds[1].map_profile
    e.worlds[0].episode_limit = 1
    _, _, dones, infos = e.step(np.zeros((2, 4)))
    assert dones.tolist() == [True, False] and s.transitions == 2
    assert e.reset_infos[0]['curriculum']['stage'] == 1
    assert e.worlds[0].ticks == 0 and e.worlds[1].ticks == 1
    assert e.worlds[1].map_profile == before_profile
    assert 'terminal_observation' in infos[0] and np.isfinite(e.brain.state.numpy()).all()
    assert sum(s.steps.values()) == 2 and sum(v['timeout'] for v in s.outcomes.values()) == 1


def test_map_contract_roundtrips_and_transfer_must_be_explicit(tmp_path):
    a = env()
    model = make_policy(a, seed=42)
    path = tmp_path/'policy.zip'; save_model(model, path, a.brain)
    configure_geometry_curriculum(a, 300, 0, 42, ['open', 'passages', 'large'])
    save_model(model, path, a.brain)
    metadata = json.loads(path.with_suffix('.json').read_text())
    assert metadata['environment']['map_profile'] == PROFILES['large'].to_dict()
    assert metadata['training_curriculum']['version'].startswith('geometry-v1')
    load_model(path, a.brain, a)
    b = env(); b.map_profile = PROFILES['passages']
    with pytest.raises(ValueError, match='map profile mismatch'):load_model(path, b.brain, b)
    load_model(path, b.brain, b, allow_transfer=True)


def test_geometry_draft_cannot_train_or_create_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path/'draft.json'
    path.write_text(json.dumps({'steps_per_seed': None, 'batch': 8, 'rounds': 2, 'seeds': [42, 73], 'status': 'draft-budget-required'}))
    with pytest.raises(ValueError, match='budget'):run_geometry_comparison(path, tmp_path/'run')
    assert not (tmp_path/'run').exists()


def test_preparation_requires_audited_three_profiles_and_explicit_budget(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    suite = tmp_path/'suite.json'
    prepare_suite(suite, 100, 200, 300, 1, 1, 1, map_profile='large', training_profiles=['open', 'passages', 'large'])
    data = tmp_path/'data/processed'; data.mkdir(parents=True)
    (data/'audit.json').write_text(json.dumps({'fingerprint': 'fake-for-preparation-only'}))
    plan = prepare_geometry_comparison(suite, tmp_path/'draft.json', data=data.parent)
    assert plan['status'] == 'draft-budget-required' and plan['total_training_transitions'] is None
    assert plan['evaluation_profile']['name'] == 'large' and plan['curriculum']['validation_controls_schedule'] is False
    audited = load_suite(suite)
    audited['training_profiles'].reverse()
    with pytest.raises(ValueError, match='Last'):validate_profiles(audited)


def test_curriculum_rejects_validation_and_mixed_interventions():
    with pytest.raises(ValueError, match='training layouts'):
        GeometryWorld(mode='dense', schedule=GeometrySchedule(300, ['open', 'passages', 'large']))
    e = env(); e.reward_shaping = object()
    with pytest.raises(ValueError, match='combine'):
        configure_geometry_curriculum(e, 300, 0, 42, ['open', 'passages', 'large'])


def test_evaluation_waits_for_different_profile_time_limits(monkeypatch):
    import fly_rl.training.evaluation as module
    e = env(2)
    original_reset = e.reset
    def reset():
        features = original_reset()
        for w, limit in zip(e.worlds, [1, 3]):w.episode_limit = limit
        return features
    e.reset = reset
    class Stationary:
        def predict(self, observation, **kwargs):return np.zeros((2, 4)), None
    monkeypatch.setattr(module, 'BrainEnv', lambda *args, **kwargs: e)
    monkeypatch.setattr(module, 'make_policy', lambda *args, **kwargs: Stationary())
    result = module.evaluate('unused', 'cpu', None, 2, 'dense', 200, dynamics='coordinated', map_profile='large')
    assert sorted(r['steps'] for r in result['episodes']) == [1, 3]
    assert all(r['timeout'] for r in result['episodes']) and result['training_invoked'] is False


def test_comparison_refuses_changed_sources_before_initialization(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    suite = tmp_path/'suite.json'
    prepare_suite(suite, 100, 200, 300, 1, 1, 1, map_profile='large', training_profiles=['open', 'passages', 'large'])
    data = tmp_path/'data/processed'; data.mkdir(parents=True)
    (data/'audit.json').write_text('{"fingerprint":"preparation-only"}')
    path = tmp_path/'plan.json'
    plan = prepare_geometry_comparison(suite, path, 4096, 8, 1, data=data.parent)
    plan['source_hashes'] = {}
    path.write_text(json.dumps(plan))
    with pytest.raises(ValueError, match='source or suite changed'):
        run_geometry_comparison(path, tmp_path/'run', 'cpu')
    assert not (tmp_path/'run').exists()


def test_geometry_selection_uses_shared_target_and_baseline_exact_tie(tmp_path, monkeypatch):
    from test_sensor_comparison import groups
    from fly_rl.training.geometry_comparison import freeze_geometry_winner
    from fly_rl.training.generalization import sha256
    monkeypatch.chdir(tmp_path)
    members = groups(tmp_path)
    suite = tmp_path/'profiled.json'
    prepare_suite(suite, 100, 200, 300, 1, 1, 1, map_profile='large', training_profiles=['open', 'passages', 'large'])
    target = load_suite(suite)['map_profile']
    for group in members:
        path = group/'selection.json'; record = json.loads(path.read_text())
        record.update(suite=str(suite), suite_sha256=sha256(suite), validation={'success_rate': .8, 'collision_rate': .2, 'mean_distance_end': 2.})
        record['evaluation_configuration'] = {'sensor_version': SENSOR_V3, 'map_profile': target}
        path.write_text(json.dumps(record))
    result = freeze_geometry_winner([('curriculum', members[1]), ('baseline', members[0])], tmp_path/'winner', {42: 65536, 73: 65536})
    assert result['selected_arm'] == 'baseline' and result['training']['added_transitions'] == 262144
    assert not result['final_test_evaluated']
    path = members[1]/'selection.json'; record = json.loads(path.read_text())
    record['evaluation_configuration']['map_profile'] = PROFILES['maze'].to_dict()
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match='fixed-target'):
        freeze_geometry_winner([('baseline', members[0]), ('curriculum', members[1])], tmp_path/'bad', {42: 65536, 73: 65536})


def test_dense_rounds_use_target_validation_and_training_only_variants(tmp_path, monkeypatch):
    import fly_rl.training.dense_training as module
    from fly_rl.training.geometry_curriculum import VERSION
    monkeypatch.chdir(tmp_path)
    suite_path = tmp_path/'suite.json'
    prepare_suite(suite_path, 100, 200, 300, 1, 1, 1, map_profile='large', training_profiles=['open', 'passages', 'large'])
    suite = load_suite(suite_path)
    initial = tmp_path/'initial.zip'; initial.write_bytes(b'initial'); initial.with_suffix('.json').write_text('{}')
    evaluations, training = [], []
    def evaluate(*args, **kwargs):
        evaluations.append((args[5], kwargs['map_profile']))
        return {'success_rate': len(evaluations)/10, 'collision_rate': 0., 'mean_distance_end': 1., 'sensor_version': SENSOR_V3}
    def train(*args, **kwargs):
        training.append(kwargs)
        path = args[4]; path.parent.mkdir(parents=True); path.write_bytes(b'round'); path.with_suffix('.json').write_text('{}')
        return {'added_transitions': args[2]}
    monkeypatch.setattr(module, 'evaluate', evaluate)
    monkeypatch.setattr(module, 'train', train)
    result = module.train_dense('unused', 'cpu', suite_path, tmp_path/'experiment', initial, 8192, 8,
                                 'coordinated', 2, 42, False, False, curriculum=VERSION)
    assert evaluations == [(200, suite['map_profile'])]*3
    assert [t['curriculum_offset'] for t in training] == [0, 4096]
    assert all(t['curriculum_total'] == 8192 and t['layout_seeds'] == [100] and t['curriculum_profiles'] == suite['training_profiles'] for t in training)
    assert result['training']['added_transitions'] == 8192 and result['promoted'] is False


def test_validation_trace_restores_the_frozen_profile_without_optimization(tmp_path, monkeypatch):
    import fly_rl.training.learning as learning
    from fly_rl.training.validation_trace import trace_validation
    from fly_rl.training.generalization import sha256
    monkeypatch.chdir(tmp_path)
    suite_path = tmp_path/'suite.json'
    prepare_suite(suite_path, 100, 200, 300, 1, 1, 1, map_profile='large', training_profiles=['open', 'passages', 'large'])
    suite = load_suite(suite_path)
    e = env(); model = make_policy(e, seed=42)
    checkpoint = tmp_path/'policy.zip'; save_model(model, checkpoint, e.brain)
    folder = tmp_path/'experiment'; folder.mkdir()
    (folder/'experiment.json').write_text('{"status":"completed"}')
    frozen = {'checkpoint': str(checkpoint), 'checkpoint_sha256': sha256(checkpoint),
              'metadata_sha256': sha256(checkpoint.with_suffix('.json')), 'suite': str(suite_path),
              'suite_sha256': sha256(suite_path), 'mode': 'dense', 'dynamics': 'coordinated',
              'selection_split': 'validation', 'validation': {'episodes': [
                  {'seed': 200, 'success': False, 'collision': False, 'timeout': True, 'steps': 3000, 'distance_end': 40.}]}}
    (folder/'selection.json').write_text(json.dumps(frozen))
    original = learning.BrainEnv
    created = []
    def factory(*args, **kwargs):
        created.append(kwargs['map_profile'])
        return original(batch=args[1], device='cpu',
                        brain=Brain(matrix=sparse.eye(16, format='csr'), batch=args[1], device='cpu', sensor_version=SENSOR_V3), **kwargs)
    monkeypatch.setattr(learning, 'BrainEnv', factory)
    result = trace_validation('unused', 'cpu', folder, tmp_path/'trace', 1, 2)
    assert created == [suite['map_profile']] and result['map_profile'] == suite['map_profile']
    assert result['optimizer_updates_added'] == 0 and result['test_evaluated'] is False
