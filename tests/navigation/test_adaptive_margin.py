"""Recovery is conditional, keeps observed solids, and resets with the episode."""
import numpy as np
from fly_rl.navigation.adaptive_margin import AdaptiveMarginController
from fly_rl.navigation.cruise import CruiseController


def configured():
    c = AdaptiveMarginController()
    c.shape = (16, 16, 12)
    c.origin = np.zeros(3)
    c.evidence = np.full(c.shape, -8, np.int8)
    c.position = np.array([1.5, 1.5, 3.3])
    c.initial_goal = np.array([8.1, 8.1, 3.3])
    c.evidence[7, 7, 5] = 3
    return c


def test_uncapped_navigation_keeps_normal_margin():
    c = configured()
    c.plan(c.initial_goal)
    assert c.debug['found'] and not c.margin_recovery
    assert not np.isfinite(c.grid()[6, 7, 5])


def test_capped_search_enables_recovery_on_next_plan(monkeypatch):
    c = configured()
    c.tick = 101
    monkeypatch.setattr(CruiseController, 'plan', lambda self, goal:
        setattr(self, 'debug', dict(found=False, expanded=12000)))
    c.plan(c.initial_goal)
    assert c.margin_recovery and c.recovery_tick == 101
    costs = c.grid()
    assert costs[6, 7, 5] == 8 and not np.isfinite(costs[7, 7, 5])
    assert not np.isfinite(costs[:, :, 0]).any()
    assert not configured().margin_recovery


def test_uncapped_failure_does_not_relax_clearance(monkeypatch):
    c = configured()
    monkeypatch.setattr(CruiseController, 'plan', lambda self, goal:
        setattr(self, 'debug', dict(found=False, expanded=300)))
    c.plan(c.initial_goal)
    assert not c.margin_recovery
