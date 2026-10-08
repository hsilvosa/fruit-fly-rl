"""Regression for sparse visible-goal rays that disagree with body clearance."""
import numpy as np
from fly_rl.navigation.clearance_goal import ClearanceGoalController
from fly_rl.navigation.portal_visible_goal import VisibleGoalController
from fly_rl.simulation.sensors import DIRECTIONS

def controller():
    c = ClearanceGoalController((64., 64., 20.))
    c.local_goal = np.array([10., 0., 0.])
    return c

def test_saturated_short_rays_are_not_obstacles_at_maximum_range():
    assert controller().direct_goal_visible(np.ones(3869))

def test_short_ray_obstruction_vetoes_sparse_panorama_visibility():
    c = controller()
    values = np.ones(3869)
    forward = np.flatnonzero(np.all(DIRECTIONS == [1, 0, 0], axis=1))[0]
    values[forward] = .2 / 8
    assert VisibleGoalController.direct_goal_visible(c, values)
    assert not c.direct_goal_visible(values)

def test_off_corridor_obstacle_does_not_veto_clear_handover():
    c = controller()
    values = np.ones(3869)
    diagonal = np.flatnonzero(np.all(np.isclose(DIRECTIONS, [2**-.5, 2**-.5, 0]), axis=1))[0]
    values[diagonal] = 2 / 8
    assert c.direct_goal_visible(values)

def test_active_opening_is_not_abandoned_for_the_goal():
    c = controller()
    c.portal = {'normal': np.array([1., 0., 0.])}
    assert not c.direct_goal_visible(np.ones(3869))
