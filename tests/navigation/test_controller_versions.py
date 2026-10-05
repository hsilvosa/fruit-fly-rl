"""Public naming preserves controller identity, source provenance, and old commands."""
import json
import sys
import numpy as np
import pytest
from fly_rl.navigation.registry import CONTROLLERS, VersionedPlannerPolicy
from fly_rl.navigation.versions import REVISIONS, catalog, public_version, legacy_version


@pytest.mark.parametrize('entry', REVISIONS, ids=lambda entry: entry.name)
def test_every_alias_selects_the_same_controller_and_readout(entry):
    policies = [VersionedPlannerPolicy(alias) for alias in (entry.number, entry.name, entry.legacy)]
    assert len({type(policy.controller) for policy in policies}) == 1
    assert all(policy.specification == policies[0].specification for policy in policies)
    spec = policies[0].specification
    assert spec['controller_version'] == entry.name and spec['legacy_alias'] == entry.legacy
    assert spec['controller_label'] == entry.label and spec['experimental'] == entry.experimental
    assert spec['version'] != entry.name  # Original artifact identifier is retained.


def test_catalog_is_complete_and_unambiguous():
    assert {entry.legacy for entry in REVISIONS} == set(CONTROLLERS)
    assert len({entry.name for entry in REVISIONS}) == len(REVISIONS)
    assert public_version('v65') == 'planner-1.2'
    assert legacy_version('planner-1.2') == 'v65'


def test_alias_actions_and_independent_reset_are_identical():
    old, new = VersionedPlannerPolicy('v65'), VersionedPlannerPolicy('1.2')
    features = np.zeros((1, 9, 5669), dtype=np.float32)
    assert np.array_equal(old.predict(features)[0], new.predict(features)[0])
    other_evidence = new.controller.evidence.copy()
    old.controller.evidence.fill(3); old.reset()
    assert not old.controller.evidence.any()
    assert np.array_equal(new.controller.evidence, other_evidence)


@pytest.mark.parametrize('option,value,expected', [('--controller-version', '1.2', 'planner-1.2'),
    ('--controller-version', 'planner-1.1', 'planner-1.1'),
    ('--planner-version', 'v65', 'planner-1.2'),
    ('--planner-version', 'v55', 'planner-1.0')])
def test_cli_new_and_old_commands_dispatch_without_running_a_flight(monkeypatch, option, value, expected):
    from fly_rl.cli import main
    import fly_rl.visualization.viewer as viewer
    seen=[]
    monkeypatch.setattr(viewer, 'run', lambda args: seen.append(args.planner_version))
    monkeypatch.setattr(sys, 'argv', ['fly-rl', 'demo', '--controller', 'observed-map', option, value])
    main()
    assert seen == [expected]


def test_listing_needs_no_data_or_viewer(monkeypatch, capsys):
    from fly_rl.cli import main
    monkeypatch.setattr(sys, 'argv', ['fly-rl', 'controller-versions'])
    main()
    assert json.loads(capsys.readouterr().out) == catalog()


@pytest.mark.parametrize('value', ['1.3', 'v66', 'planner-1.2-exp.5'])
def test_unknown_revision_rejected(value):
    with pytest.raises(ValueError):
        VersionedPlannerPolicy(value)


def test_public_names_cannot_bypass_nonplanner_guard(monkeypatch):
    from fly_rl.cli import main
    monkeypatch.setattr(sys, 'argv', ['fly-rl', 'demo', '--controller-version', '1.2'])
    with pytest.raises(SystemExit) as stopped:
        main()
    assert stopped.value.code == 2
