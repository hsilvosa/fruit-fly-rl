"""Braking follows actual velocity even when the route points elsewhere."""
import numpy as np
from fly_rl.navigation.momentum_guard import MomentumGuardController


def controller(kind=MomentumGuardController):
    c = kind()
    c.update = lambda values: np.array([20., 0., 6.])
    c.tick = 2; c.route = [np.array([3., 1., 1.])]
    c.local_goal = np.array([20., 0., 0.]); c.tight = False
    c.target = lambda: np.array([3., 1., 1.])
    return c


def features(c, obstacle_range):
    v = np.zeros((9, 3869), np.float32)
    v[-1, :128] = 1
    v[-1, 269:2069] = 1
    v[-1, 260] = 1/3
    index = int(np.argmax(c.directions[:, 0]))
    v[-1, 269+index] = obstacle_range/24
    return v


def test_current_motion_requests_braking_without_requested_direction_hit():
    c = controller(); values = features(c, .6); before = values.copy()
    action = c.action(values)
    assert c.debug['ahead'] > 1 and c.debug['momentum_ahead'] < .7
    assert c.debug['momentum_guard'] and c.debug['effective_desired_speed'] == 0
    assert action[0] < 0 and action[2] == 0
    np.testing.assert_equal(values, before)


def test_clear_momentum_preserves_route_following():
    c = controller(); action = c.action(features(c, 8.))
    assert not c.debug['momentum_guard'] and c.debug['effective_desired_speed'] > 0
    assert action[0] > 0 and action[2] > 0


def test_stationary_fly_is_not_held_by_momentum_guard():
    c = controller(); values = features(c, .6); values[-1, 260:263] = 0
    c.action(values)
    assert not c.debug['momentum_guard']


def test_clear_motion_preserves_previous_controller_action():
    from fly_rl.navigation.distance_stable import DistanceStableController
    candidate, baseline = controller(), controller(DistanceStableController)
    values = features(candidate, 8.)
    np.testing.assert_equal(candidate.action(values), baseline.action(values))
