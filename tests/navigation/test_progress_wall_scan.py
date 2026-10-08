import numpy as np

from fly_rl.navigation.distant_opening import DistantOpeningController
from fly_rl.navigation.progress_wall_scan import ProgressWallScanController
from fly_rl.navigation.room_aware import RoomAwareController


def prepared(monkeypatch):
    c = ProgressWallScanController((64., 64., 20.))
    c.position = np.array([0., 0., 10.])
    c.initial_goal = np.array([40., 0., 10.])
    c.current_values = np.ones(3869)
    c.debug = {'found': True}
    monkeypatch.setattr(DistantOpeningController, 'plan', lambda self, goal: self.debug.update(found=True))
    monkeypatch.setattr(RoomAwareController, 'plan', lambda self, goal: self.debug.update(found=True))
    monkeypatch.setattr(c, 'reference_clear', lambda point: True)
    monkeypatch.setattr(c, 'direct_goal_visible', lambda values: False)
    monkeypatch.setattr(c, 'blocking_surface', lambda values: {'normal': np.array([1., 0., 0.]),
                                                             'center': np.array([1., 0., 10.])})
    return c


def test_normal_navigation_preserved_until_declared_stall(monkeypatch):
    c = prepared(monkeypatch)
    c.tick = 319
    c.plan(c.initial_goal)
    assert c.scan is None
    c.tick = 320
    c.plan(c.initial_goal)
    assert c.scan is not None
    assert c.scan['target'] is not None


def test_scanning_target_requires_observed_ray_clearance(monkeypatch):
    c = prepared(monkeypatch)
    c.current_values[269:2069] = .01
    c.tick = 320
    c.plan(c.initial_goal)
    assert c.scan['target'] is None


def test_scan_expires_without_changing_occupancy(monkeypatch):
    c = prepared(monkeypatch)
    c.tick = 320
    c.plan(c.initial_goal)
    evidence = c.evidence.copy()
    c.tick = 721
    c.plan(c.initial_goal)
    assert c.scan is None
    assert np.array_equal(c.evidence, evidence)


def test_active_opening_cancels_scan(monkeypatch):
    c = prepared(monkeypatch)
    c.tick = 320
    c.plan(c.initial_goal)
    c.portal = {'normal': np.array([1., 0., 0.])}
    c.tick += 20
    c.plan(c.initial_goal)
    assert c.scan is None
