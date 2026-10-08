import numpy as np
from fly_rl.navigation.unreachable_crossing import UnreachableCrossingController
from fly_rl.navigation.coverage_wall_scan import CoverageWallScanController


def prepared():
    c = UnreachableCrossingController()
    c.portal = dict(center=np.array([4., 2., 10.]), normal=np.array([1., 0., 0.]), ray_support=3)
    c.portal_phase = 'cross'
    c.debug = {'found': False}
    return c


def test_sustained_unreachable_crossing_releases_without_marking_completed():
    c = prepared()
    c.tick = 10
    assert not c.release_unreachable_crossing()
    c.tick = 109
    assert not c.release_unreachable_crossing()
    c.tick = 110
    assert c.release_unreachable_crossing()
    assert c.portal is None and c.portal_phase == 'none'
    assert c.completed_planes == [] and c.portal_crossings == 0
    assert len(c.rejected_openings) == 1 and c.crossing_releases == 1


def test_route_recovery_resets_failure_timer():
    c = prepared()
    c.tick = 1
    c.release_unreachable_crossing()
    c.tick = 80
    c.debug['found'] = True
    assert not c.release_unreachable_crossing()
    c.tick = 100
    c.debug['found'] = False
    assert not c.release_unreachable_crossing()
    c.tick = 199
    assert not c.release_unreachable_crossing()


def test_approach_and_new_portal_do_not_inherit_cross_failure():
    c = prepared()
    c.tick = 1
    c.release_unreachable_crossing()
    c.portal = dict(c.portal)
    c.tick = 110
    assert not c.release_unreachable_crossing()
    c.portal_phase = 'approach'
    c.tick = 300
    assert not c.release_unreachable_crossing()
    assert c.unreachable_since is None


def test_rejection_is_local_directional_and_temporary(monkeypatch):
    c = prepared()
    observed = c.portal.copy()
    c.rejected_openings = [(observed['center'].copy(), observed['normal'].copy(), 600)]
    monkeypatch.setattr(CoverageWallScanController, 'detect_portal', lambda self, values: observed)
    assert c.detect_portal(None) is None
    observed['center'] = observed['center'] + np.array([0., 4., 0.])
    assert c.detect_portal(None) is observed
    observed['center'] -= np.array([0., 4., 0.])
    observed['normal'] *= -1
    assert c.detect_portal(None) is observed
    observed['normal'] *= -1
    c.tick = 600
    assert c.detect_portal(None) is observed
    assert c.rejected_openings == []


def test_independent_episode_state():
    c = prepared()
    other = UnreachableCrossingController()
    c.tick = 1
    c.release_unreachable_crossing()
    c.tick = 101
    c.release_unreachable_crossing()
    assert other.rejected_openings == [] and other.crossing_releases == 0
