import numpy as np
from fly_rl.navigation.coverage_wall_scan import CoverageWallScanController


def prepared(monkeypatch):
    c = CoverageWallScanController((64., 64., 20.))
    c.position = np.array([0., 0., 10.])
    c.current_values = np.ones(3869)
    monkeypatch.setattr(c, 'reference_clear', lambda point: True)
    scan = {'normal': np.array([1., 0., 0.]), 'tangent': np.array([0., 1., 0.]),
            'center': np.array([1., 0., 10.]), 'direction': -1}
    return c, scan


def test_less_visited_side_overrides_goalward_tie_break(monkeypatch):
    c, scan = prepared(monkeypatch)
    c.seen_positions = {(0, -3, 4), (0, -5, 5), (0, -7, 7)}
    point = c.choose_scan_target(scan)
    assert point[1] > 0 and scan['direction'] == 1
    assert len(scan['coverage_direction_scores']) == 2


def test_distant_other_wall_visits_do_not_bias_this_scan(monkeypatch):
    c, scan = prepared(monkeypatch)
    c.seen_positions = {(10, -3, 4), (10, -5, 5)}
    assert c.choose_scan_target(scan)[1] < 0


def test_failed_reference_penalty_prevents_immediate_reselection(monkeypatch):
    c, scan = prepared(monkeypatch)
    first = c.choose_scan_target(scan)
    c.scan_visits[c.scan_key(first)] = 1
    second = c.choose_scan_target(scan)
    assert first[1] < 0 < second[1]


def test_coverage_cannot_override_observed_clearance(monkeypatch):
    c, scan = prepared(monkeypatch)
    c.current_values[269:2069] = .01
    assert c.choose_scan_target(scan) is None
    monkeypatch.setattr(c, 'reference_clear', lambda point: False)
    c.current_values.fill(1)
    assert c.choose_scan_target(scan) is None
