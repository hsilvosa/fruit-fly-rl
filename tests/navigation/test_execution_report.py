"""Saved-trace diagnostics distinguish observations from missing fields."""
import copy
import pytest
from scripts.report_planner_execution import summarize


def rows():
    return [dict(seed=7, step=i*20, position=[float(i), 0., 1.], controller=dict(
        found=True, expanded=12000 if i == 2 else 10, momentum_guard=i == 3,
        actual_speed=float(i), estimated_pose_error=i*.001,
        target_delta_global=[1. if i % 2 == 0 else -1., 0., 0.])) for i in range(4)]


def test_reversals_caps_and_second_half_are_sampled_counts():
    result = summarize(rows(), 7)
    assert result['sampled_step_stride_range'] == [20, 20]
    assert result['full']['reference_reversals_over_90_degrees'] == 3
    assert result['full']['eligible_reference_pairs'] == 3
    assert result['full']['search_cap_samples'] == 1
    assert result['second_half']['momentum_guard_samples'] == 1
    assert result['second_half']['position_span'] == [1., 0., 0.]


def test_missing_fields_are_not_reported_as_observed_zero():
    data = rows()
    for row in data:
        row['controller'] = {}
    result = summarize(data, 7)['full']
    assert result['momentum_guard_observed_samples'] == 0
    assert result['eligible_reference_pairs'] == 0
    assert result['sampled_speed_range'] is None


@pytest.mark.parametrize('field,value', [('step', 0), ('position', [float('nan'), 0., 0.]),
    ('controller', {'actual_speed': -1.}), ('controller', {'found': 1}),
    ('controller', {'target_delta_global': [1., 2.]})])
def test_invalid_trace_rejected(field, value):
    data = copy.deepcopy(rows()); data[1][field] = value
    with pytest.raises(ValueError):
        summarize(data, 7)


def test_missing_seed_rejected():
    with pytest.raises(ValueError):
        summarize(rows(), 9)
