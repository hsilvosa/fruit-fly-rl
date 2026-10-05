"""Synthetic regressions for goal reachability; not navigation-performance evidence."""
import numpy as np
from fly_rl.navigation.goal_margin import GoalMarginController
from fly_rl.navigation.observed_map import ObservedMapController


def configured(kind):
    c = kind()
    c.shape = (12, 12, 12)
    c.origin = np.zeros(3)
    c.evidence = np.full(c.shape, -8, np.int8)
    c.position = np.array([1.5, 1.5, 3.3])
    c.initial_goal = np.array([5.1, 3.3, 3.3])
    cell = c.cells(c.initial_goal)
    c.evidence[tuple(cell+np.array([1, 0, 0]))] = 3
    return c


def test_known_free_goal_margin_can_be_reached_without_opening_solids():
    baseline = configured(ObservedMapController)
    baseline.plan(baseline.initial_goal)
    assert not baseline.debug['found']
    candidate = configured(GoalMarginController)
    candidate.plan(candidate.initial_goal)
    assert candidate.debug['found']
    cell = candidate.cells(candidate.initial_goal)
    assert candidate.cost[tuple(cell)] == 8
    assert not np.isfinite(candidate.cost[tuple(cell+np.array([1, 0, 0]))])
    np.testing.assert_equal(candidate.evidence, baseline.evidence)


def test_unknown_goal_margin_is_not_relaxed():
    c = configured(GoalMarginController)
    c.evidence[tuple(c.cells(c.initial_goal))] = 0
    assert not np.isfinite(c.grid()[tuple(c.cells(c.initial_goal))])


def test_solid_goal_is_not_relaxed():
    c = configured(GoalMarginController)
    c.evidence[tuple(c.cells(c.initial_goal))] = 3
    assert not np.isfinite(c.grid()[tuple(c.cells(c.initial_goal))])


def test_goal_relaxation_is_local_and_does_not_open_boundaries():
    c = configured(GoalMarginController)
    c.evidence[3, 3, 3] = 3
    costs = c.grid()
    assert not np.isfinite(costs[2, 3, 3])
    assert not np.isfinite(costs[:, :, 0]).any()
    assert not np.isfinite(costs[:, :, -1]).any()
