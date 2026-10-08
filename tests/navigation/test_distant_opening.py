import numpy as np

from fly_rl.navigation.distant_opening import DistantOpeningController
from fly_rl.navigation.clearance_goal import ClearanceGoalController


def wall_observation(controller, distance):
    directions = controller.directions
    projected = np.divide(distance, directions[:, 0], out=np.full(len(directions), np.inf), where=directions[:, 0] > .01)
    points = directions * np.minimum(projected[:, None], 24)
    ranges = np.minimum(projected, 24)
    opening = (np.abs(points[:, 1]) < 2) & (np.abs(points[:, 2]) < 2)
    ranges[opening] = 24
    values = np.ones(3869)
    values[269:2069] = ranges / 24
    return values


def prepared():
    c = DistantOpeningController((64., 64., 20.))
    c.position = np.array([0., 0., 10.])
    c.initial_goal = np.array([40., 0., 10.])
    return c


def test_opening_beyond_old_detection_window_is_observed():
    c = prepared()
    values = wall_observation(c, 8.)
    assert ClearanceGoalController.detect_portal(c, values) is None
    portal = c.detect_portal(values)
    assert portal is not None
    assert abs(portal['center'][0] - 8.) < .2


def test_near_choice_preserved_exactly():
    c = prepared()
    values = wall_observation(c, 3.)
    old = ClearanceGoalController.detect_portal(c, values)
    new = c.detect_portal(values)
    assert old is not None
    assert np.array_equal(new['center'], old['center'])
    assert np.array_equal(new['normal'], old['normal'])


def test_completed_plane_not_selected_again():
    c = prepared()
    c.completed_planes = [(np.array([8., 0., 10.]), np.array([1., 0., 0.]))]
    assert c.detect_portal(wall_observation(c, 8.)) is None
