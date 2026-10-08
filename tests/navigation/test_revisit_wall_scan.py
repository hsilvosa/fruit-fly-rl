import numpy as np

from fly_rl.navigation.progress_wall_scan import ProgressWallScanController
from fly_rl.navigation.revisit_wall_scan import RevisitWallScanController


def test_new_space_does_not_trigger_recovery():
    c = RevisitWallScanController((64., 64., 20.))
    for i in range(40):
        c.position = np.array([0., i * 2.1, 10.])
        c.sample_position()
    assert len(c.recent_novelty) == 16
    assert sum(c.recent_novelty) == 16
    assert c.low_novelty_streak == 0


def test_repeated_region_requires_complete_window_and_sustained_streak():
    c = RevisitWallScanController((64., 64., 20.))
    for _ in range(15):
        c.sample_position()
    assert c.low_novelty_streak == 0
    c.sample_position()
    assert c.low_novelty_streak == 1
    c.sample_position()
    c.sample_position()
    assert c.low_novelty_streak == 3


def test_active_opening_resets_revisit_streak():
    c = RevisitWallScanController((64., 64., 20.))
    for _ in range(20):
        c.sample_position()
    assert c.low_novelty_streak >= 3
    c.portal = {'normal': np.array([1., 0., 0.])}
    c.sample_position()
    assert c.low_novelty_streak == 0


def test_gate_defers_parent_without_destroying_progress_memory(monkeypatch):
    c = RevisitWallScanController((64., 64., 20.))
    c.tick = 1000
    c.longitudinal_tick = 7
    seen = []
    monkeypatch.setattr(ProgressWallScanController, 'plan', lambda self, goal: seen.append(self.longitudinal_tick))
    c.plan(np.ones(3))
    assert seen == [1000]
    assert c.longitudinal_tick == 7


def test_active_scan_keeps_parent_expiry_and_recovery_logic(monkeypatch):
    c = RevisitWallScanController((64., 64., 20.))
    c.tick = 1000
    c.longitudinal_tick = 7
    c.scan = {'target': np.ones(3)}
    seen = []
    monkeypatch.setattr(ProgressWallScanController, 'plan', lambda self, goal: seen.append(self.longitudinal_tick))
    c.plan(np.ones(3))
    assert seen == [7]


def test_instances_have_independent_visit_history():
    first, second = RevisitWallScanController(), RevisitWallScanController()
    first.sample_position()
    assert not second.seen_positions and not second.recent_novelty
