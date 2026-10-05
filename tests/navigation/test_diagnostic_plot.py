"""Offline plots reject malformed traces and distinguish reuse from search."""
import json
import pytest
from scripts.plot_planner_diagnostics import summarize


def write_trace(path, steps=(0, 20)):
    rows = [dict(seed=4, step=step, position=[step*.01, 0., 1.],
                 controller=dict(expanded=3, found=True, requested_speed=1.,
                     target_delta_global=[1., 0., 0.], plan_reused=bool(index)))
            for index, step in enumerate(steps)]
    (path/'trace.json').write_text(json.dumps(rows))


def test_single_room_plot_uses_recorded_seed_and_stride(tmp_path):
    write_trace(tmp_path)
    summarize(tmp_path, tmp_path/'plots')
    result = json.loads((tmp_path/'plots/summary.json').read_text())
    room = result['rooms'][0]
    assert room['seed'] == 4 and room['samples'] == 2
    assert room['reused_route_samples'] == 1
    assert room['sampled_stride_min'] == room['sampled_stride_max'] == 20
    assert not result['training_invoked'] and not result['evaluation_invoked']
    assert (tmp_path/'plots/planner-diagnostics.png').is_file()


@pytest.mark.parametrize('steps', [(20, 0), (0, 0), (-1, 20)])
def test_invalid_sample_order_is_rejected(tmp_path, steps):
    write_trace(tmp_path, steps)
    with pytest.raises(ValueError, match='strictly increasing'):
        summarize(tmp_path, tmp_path/'plots')


def test_unrecorded_or_duplicate_selection_is_rejected(tmp_path):
    write_trace(tmp_path)
    with pytest.raises(ValueError, match='Missing diagnostic seed'):
        summarize(tmp_path, tmp_path/'plots', [5])
    with pytest.raises(ValueError, match='distinct'):
        summarize(tmp_path, tmp_path/'plots', [4, 4])


def test_direct_goal_frames_without_route_reference_can_be_plotted(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    rows = []
    for seed in [8500011, 8500012, 8500013]:
        for step in [0, 20]:
            debug = dict(expanded=12, found=True, requested_speed=1.)
            if step == 0:
                debug['target_delta_global'] = [2., 0., 0.]
            rows.append(dict(seed=seed, step=step, position=[step*.05, 0., 3.], controller=debug))
    (source / 'trace.json').write_text(json.dumps(rows))
    output = tmp_path / 'plots'
    summarize(source, output)
    report = json.loads((output / 'summary.json').read_text())
    assert all(room['missing_route_reference_samples'] == 1 for room in report['rooms'])
    assert all(room['reference_reversals_over_90_degrees'] == 0 for room in report['rooms'])
    assert not report['training_invoked'] and not report['evaluation_invoked']
    assert (output / 'planner-diagnostics.png').is_file()
