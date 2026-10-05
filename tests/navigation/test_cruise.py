"""Physical command regressions for the isolated cruise-speed candidate."""
import numpy as np
import pytest
from fly_rl.navigation.cruise import CruiseController
from fly_rl.navigation.speed_margin import SpeedMarginController
from fly_rl.simulation.sensors import DIRECTIONS


@pytest.fixture(params=[CruiseController, SpeedMarginController])
def kind(request):
    return request.param


def action(monkeypatch, delta, velocity=0., tight=False, blocked=False, kind=CruiseController):
    c = kind()
    c.tick = 2
    c.tight = tight
    c.route = [np.ones(3)]
    c.local_goal = np.array([10., 0, 0])
    monkeypatch.setattr(c, 'update', lambda _: np.ones(3))
    monkeypatch.setattr(c, 'target', lambda: np.asarray(delta, dtype=float))
    values = np.zeros((9, 3869), np.float32)
    values[-1, :128] = 1
    values[-1, 269:2069] = 1
    values[-1, 260] = velocity / 3
    if blocked:
        values[-1, np.argmax(DIRECTIONS[:, 0])] = .22 / 8
    commands = c.action(values)
    assert np.isfinite(commands).all() and (np.abs(commands) <= 1).all()
    return c, commands


def test_clear_flight_can_request_higher_speed(monkeypatch, kind):
    c, commands = action(monkeypatch, [4, 0, 0], kind=kind)
    assert c.debug['requested_speed'] > 2.5 and commands[0] > 0


def test_tight_margin_still_limits_speed(monkeypatch, kind):
    c, _ = action(monkeypatch, [4, 0, 0], tight=True, kind=kind)
    assert c.debug['requested_speed'] == .8


def test_obstacle_still_brakes_forward_motion(monkeypatch, kind):
    c, commands = action(monkeypatch, [4, 0, 0], velocity=2., blocked=True, kind=kind)
    assert c.debug['requested_speed'] == 0 and commands[0] < 0


def test_forward_obstacle_does_not_block_vertical_escape(monkeypatch, kind):
    c, commands = action(monkeypatch, [0, 0, 4], blocked=True, kind=kind)
    assert c.debug['requested_speed'] > 2.5 and commands[2] > 0
