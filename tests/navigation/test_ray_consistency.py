"""Static component checks; geometry observation is not a policy evaluation."""
import numpy as np
from fly_rl.navigation.distance_stable import DistanceStableController
from fly_rl.navigation.ray_consistent import RayConsistentController
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.sensors import SENSOR_V6


def test_interpolation_cannot_mark_current_free_ray_cells_solid():
    world = FlightWorld(9500014, 'dense', dynamics='coordinated', sensor_version=SENSOR_V6, map_profile='large')
    values = world.observe()
    baseline, candidate = DistanceStableController(), RayConsistentController()
    for c in [baseline, candidate]:
        c.position[2] = world.position[2]
        c.integrate(values)
    ranges = np.clip(values[269:2069]*24, .05, 24)
    steps = np.arange(.3, 24, .45)
    points = candidate.position[None, None]+candidate.directions[:, None]*steps[None, :, None]
    cells = candidate.cells(points[steps[None] < ranges[:, None]-.35])
    cells = cells[candidate.valid(cells)]
    free_ids = np.unique(np.ravel_multi_index(tuple(cells.T), candidate.shape))
    hits = candidate.cells(candidate.position+candidate.directions[ranges < 23.4]*ranges[ranges < 23.4, None])
    hits = hits[candidate.valid(hits)]
    hit_ids = np.unique(np.ravel_multi_index(tuple(hits.T), candidate.shape))
    free_only = np.setdiff1d(free_ids, hit_ids)
    assert (baseline.evidence.ravel()[free_only] >= 2).any()
    assert not (candidate.evidence.ravel()[free_only] >= 2).any()
    np.testing.assert_equal(candidate.evidence.ravel()[hit_ids], baseline.evidence.ravel()[hit_ids])


def test_integration_does_not_modify_input_activity():
    c = RayConsistentController()
    values = np.zeros(3869, np.float32)
    values[269:2069] = 1
    before = values.copy()
    c.position[2] = 6.
    c.integrate(values)
    np.testing.assert_equal(values, before)
