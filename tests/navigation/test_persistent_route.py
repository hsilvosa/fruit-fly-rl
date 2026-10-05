"""Route persistence validates local clearance and forces search after stalls."""
import numpy as np
from fly_rl.navigation.persistent_route import PersistentRouteController


def configured():
    c = PersistentRouteController()
    c.shape = (24, 24, 12)
    c.origin = np.zeros(3)
    c.evidence = np.full(c.shape, -8, np.int8)
    c.position = np.array([1.5, 1.5, 3.3])
    c.initial_goal = np.array([10.5, 1.5, 3.3])
    c.plan(c.initial_goal)
    return c


def test_clear_prefix_reuses_route_without_search():
    c = configured()
    route = np.array(c.route)
    c.position[0] += .1
    c.plan(c.initial_goal)
    assert c.debug['plan_reused'] and c.debug['expanded'] == 0
    np.testing.assert_equal(np.array(c.route), route)


def test_new_obstruction_in_prefix_forces_search():
    c = configured()
    c.evidence[tuple(c.cells(np.array([5.1, 1.5, 3.3])))] = 3
    c.plan(c.initial_goal)
    assert not c.debug['plan_reused']
    assert not np.isfinite(c.cost[tuple(c.cells(np.array([5.1, 1.5, 3.3])))])


def test_three_stagnant_checks_force_search():
    c = configured()
    for _ in range(3):
        c.plan(c.initial_goal)
    assert not c.debug['plan_reused']


def test_prefix_samples_have_bounded_spacing_and_length():
    c = configured()
    points = c.prefix_points()
    distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
    assert distances.max() <= .100001
    assert distances.sum() <= 8.00001
