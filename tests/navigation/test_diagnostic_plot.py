"""Missing planner references must remain missing in saved-trace analysis."""
import json
from scripts.plot_planner_diagnostics import summarize


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
