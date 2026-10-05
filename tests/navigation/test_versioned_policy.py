"""Experimental viewer selection preserves episode state and dependency provenance."""
import hashlib
import json
import numpy as np
import pytest
from fly_rl.navigation.registry import VersionedPlannerPolicy
from fly_rl.recordings.recording import FlightRecorder
from fly_rl.recordings.archive import Archive


def test_adaptive_policy_reset_clears_all_episode_memory():
    policy = VersionedPlannerPolicy('v60')
    old = policy.controller
    old.margin_recovery = True
    old.recovery_tick = 900
    old.evidence.fill(3)
    old.position[:] = 4
    policy.reset()
    assert policy.controller is not old and not policy.controller.margin_recovery
    assert policy.controller.recovery_tick is None
    assert not policy.controller.evidence.any() and not policy.controller.position.any()


def test_archive_contains_every_dependency_with_matching_hash(tmp_path):
    policy = VersionedPlannerPolicy('v60')
    policy.archive_sources(tmp_path)
    spec = json.loads((tmp_path/'controller.json').read_text())
    expected = {'adaptive_margin', 'cruise', 'goal_margin', 'observed_map', 'registry', 'versions'}
    assert {entry['module'].split('.')[-1] for entry in spec['sources']} == expected
    for entry in spec['sources']:
        assert hashlib.sha256((tmp_path/entry['archive_file']).read_bytes()).hexdigest() == entry['sha256']
    assert spec['experimental'] and not spec['learned'] and not spec['training_invoked']
    assert hashlib.sha256((tmp_path/'controller.py').read_bytes()).hexdigest() == spec['source_sha256']


def test_distance_readout_and_dependencies_are_identified(tmp_path):
    policy = VersionedPlannerPolicy('v61')
    policy.archive_sources(tmp_path)
    spec = json.loads((tmp_path/'controller.json').read_text())
    assert spec['readout'] == 'neural-projection-distance-stable-speed005-v1'
    modules = {entry['module'] for entry in spec['sources']}
    assert {'fly_rl.connectome.distance_readout', 'fly_rl.connectome.innovation',
            'fly_rl.connectome.brain'}.issubset(modules)


def test_bad_version_or_observation_is_rejected():
    with pytest.raises(ValueError):
        VersionedPlannerPolicy('unknown')
    policy = VersionedPlannerPolicy('v60')
    with pytest.raises(ValueError):
        policy.predict(np.zeros((1, 256)))
    observation = np.zeros((1, 9, 3869))
    observation[0, 0, 0] = np.nan
    with pytest.raises(ValueError):
        policy.predict(observation)


def test_cli_help_lists_every_registered_planner(monkeypatch, capsys):
    import sys
    from fly_rl.cli import main
    from fly_rl.navigation.registry import CONTROLLERS
    monkeypatch.setattr(sys, 'argv', ['fly-rl', 'demo', '--help'])
    with pytest.raises(SystemExit) as stopped:
        main()
    assert stopped.value.code == 0
    help_text = capsys.readouterr().out
    assert all(version in help_text for version in CONTROLLERS)


@pytest.mark.parametrize('corruption', ['dependency', 'primary', 'specification', 'missing'])
def test_inspection_detects_controller_provenance_corruption(tmp_path, corruption):
    policy = VersionedPlannerPolicy('v60')
    recorder = FlightRecorder(tmp_path, {'controller': policy.specification})
    policy.archive_sources(recorder.path)
    recorder.close()
    assert Archive(recorder.path).inspect()['integrity_ok']
    if corruption == 'dependency':
        (recorder.path/'controller-cruise.py').write_text('changed')
    elif corruption == 'primary':
        (recorder.path/'controller.py').write_text('changed')
    elif corruption == 'specification':
        spec = policy.specification
        spec['version'] = 'different'
        (recorder.path/'controller.json').write_text(json.dumps(spec))
    else:
        (recorder.path/'controller-adaptive_margin.py').unlink()
    report = Archive(recorder.path).inspect()
    assert not report['integrity_ok'] and any('Controller sources' in error for error in report['errors'])
