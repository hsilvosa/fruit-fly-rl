"""Reports reject incompatible or incomplete measurements instead of mixing them."""
import copy
import pytest
from scripts.report_planner_development import compare, wilson


def states():
    baseline = dict(controller='v55', kind='frozen-prospective-development', status='completed',
        incomplete_episodes=0, added_training_transitions=0, optimizer_updates=0,
        reserved_test_evaluated=False, protected_unchanged=True, sources_unchanged=True,
        graph_neurons=167184, graph_edges=25583622, seeds=list(range(16)),
        episodes=[dict(seed=i, success=True, collision=False, timeout=False,
                       steps=10, flown_distance=1.) for i in range(16)],
        physical_transitions=160, physical_cap=81920, protocol_sha256='fixture',
        layout_hashes=['same']*16, brain_fingerprint='same', frozen_sources_before={},
        protected_before={}, elapsed_seconds=1., peak_vram_gb=1.)
    candidate = copy.deepcopy(baseline)
    candidate['controller'] = 'v60'
    return baseline, candidate


def test_paired_counts_retain_discordant_rooms():
    baseline, candidate = states()
    baseline['episodes'][0].update(success=False, timeout=True)
    candidate['episodes'][1].update(success=False, collision=True)
    result = compare(baseline, candidate)
    assert result['paired'] == dict(both_success=14, baseline_only=1, candidate_only=1, neither_success=0)
    assert result['arms']['v60']['collisions'] == 1
    assert not result['reserved_test_access']


@pytest.mark.parametrize('field,value', [('status', 'running'), ('incomplete_episodes', 1),
    ('sources_unchanged', False), ('reserved_test_evaluated', True),
    ('protocol_sha256', 'different'), ('layout_hashes', ['different']*16)])
def test_report_rejects_invalid_pair(field, value):
    baseline, candidate = states()
    candidate[field] = value
    with pytest.raises(ValueError):
        compare(baseline, candidate)


def test_wilson_extremes_retain_small_sample_uncertainty():
    low, high = wilson(16, 16)
    assert low == pytest.approx(.8064, abs=5e-5) and high == pytest.approx(1.)
    low, high = wilson(0, 16)
    assert low == pytest.approx(0.) and high == pytest.approx(.1936, abs=5e-5)


def test_declared_readout_difference_preserves_graph_pairing():
    baseline, candidate = states()
    baseline['controller'] = 'v60'
    candidate['controller'] = 'v63'
    baseline['brain_fingerprint'] = 'same:base-model:motion-readout'
    candidate['brain_fingerprint'] = 'same:base-model:distance-readout'
    baseline['graph_data_fingerprint'] = candidate['graph_data_fingerprint'] = 'same'
    baseline['readout_version'] = 'neural-projection-motion-stable-visual005-v1'
    candidate['readout_version'] = 'neural-projection-distance-stable-speed005-v1'
    result = compare(baseline, candidate, ('v60', 'v63'))
    assert result['controllers'] == ['v60', 'v63']
    candidate['graph_data_fingerprint'] = 'different'
    with pytest.raises(ValueError, match='fingerprints'):
        compare(baseline, candidate, ('v60', 'v63'))
