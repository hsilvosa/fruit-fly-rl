"""Observed surface geometry and survey memory, without hidden layout inputs."""
import numpy as np
from fly_rl.navigation.wall_survey import WallSurveyController

def wall_observation(controller, distance=3.):
    directions = controller.directions
    forward = np.divide(distance, directions[:, 0], out=np.full(len(directions), 24.), where=directions[:, 0] > 0)
    floor = np.divide(-10., directions[:, 2], out=np.full(len(directions), 24.), where=directions[:, 2] < 0)
    ceiling = np.divide(10., directions[:, 2], out=np.full(len(directions), 24.), where=directions[:, 2] > 0)
    values = np.zeros(3869)
    values[269:2069] = np.minimum.reduce([forward, floor, ceiling, np.full(len(directions), 24.)]) / 24
    return values

def controller():
    result = WallSurveyController()
    result.position = np.array([0., 0., 10.])
    result.initial_goal = np.array([60., 5., 10.])
    return result

def test_surface_fit_uses_ranges_and_rejects_distant_surface():
    c = controller()
    surface = c.blocking_surface(wall_observation(c))
    assert surface is not None
    np.testing.assert_allclose(surface['normal'], [1., 0., 0.], atol=1e-6)
    np.testing.assert_allclose(surface['center'], [3., 0., 10.], atol=1e-6)
    assert c.blocking_surface(wall_observation(c, 8.)) is None

def test_survey_stays_on_near_side_and_advances_then_reverses():
    c = controller()
    surface = c.blocking_surface(wall_observation(c))
    first = c.survey_destination(surface)
    np.testing.assert_allclose(first, [1., 4., 10.], atol=1e-6)
    c.position = first.copy()
    c.tick += 20
    np.testing.assert_allclose(c.survey_destination(surface), [1., 8., 10.], atol=1e-6)
    c.tick += 20
    c.survey_destination(surface)
    c.tick += 180
    np.testing.assert_allclose(c.survey_destination(surface), [1., 0., 10.], atol=1e-6)
    assert c.survey['direction'] == -1 and c.survey['reversals'] == 1

def test_new_episode_has_independent_search_memory():
    first, second = controller(), controller()
    first.survey_destination(first.blocking_surface(wall_observation(first)))
    assert second.survey is None and second.no_opening_since is None
    assert second.survey_count == 0
