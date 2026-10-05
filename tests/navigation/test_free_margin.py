"""Check that known-free margin traversal does not erase physical map evidence."""
import numpy as np
import pytest
from fly_rl.navigation.free_margin import FreeMarginController
from fly_rl.navigation.speed_margin import SpeedMarginController


@pytest.fixture(params=[FreeMarginController, SpeedMarginController])
def controller(request):
    c = request.param()
    c.shape = (16, 16, 12)
    c.origin = np.zeros(3)
    c.evidence = np.full(c.shape, -8, np.int8)
    c.position = np.array([1.5, 1.5, 3.3])
    c.initial_goal = np.array([8.1, 8.1, 3.3])
    c.evidence[7, 7, 5] = 3
    return c


def test_known_free_margin_has_high_cost_and_surface_stays_blocked(controller):
    c = controller
    before = c.evidence.copy()
    costs = c.grid()
    assert costs[6, 7, 5] == 8 and not np.isfinite(costs[7, 7, 5])
    assert costs[5, 7, 5] == 1
    np.testing.assert_equal(c.evidence, before)


def test_unknown_margin_stays_blocked(controller):
    c = controller
    c.evidence[6, 7, 5] = 0
    assert not np.isfinite(c.grid()[6, 7, 5])


def test_room_top_and_bottom_stay_blocked(controller):
    c = controller
    costs = c.grid()
    assert not np.isfinite(costs[:, :, 0]).any()
    assert not np.isfinite(costs[:, :, -1]).any()
