import numpy as np
import pytest
import torch
from stable_baselines3 import PPO
from gymnasium import spaces

from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import resolve_profile
from fly_rl.training.waypoint_diagnostic import EXTRA, expand_policy, waypoint_vector, _route


def make_world(seed=3):
    w = FlightWorld(seed, 'dense', None, 'coordinated', None, resolve_profile('passages'))
    w.reset(seed=seed)
    return w


def test_waypoint_is_a_unit_vector_toward_the_route_not_the_straight_line():
    w = make_world()
    route, cum = _route(w)
    v = waypoint_vector(w, route, cum)
    assert v.shape == (3,) and abs(np.linalg.norm(v) - 1) < 1e-5 and np.isfinite(v).all()
    # at the start of a partitioned map the route differs from the straight line to the goal
    c, s = np.cos(w.yaw), np.sin(w.yaw)
    rot = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])
    goal = (w.target - w.position) @ rot
    goal /= np.linalg.norm(goal)
    assert np.degrees(np.arccos(np.clip(v @ goal, -1, 1))) > 5


def test_waypoint_moves_along_the_route_as_the_fly_advances():
    w = make_world(5)
    route, cum = _route(w)
    first = waypoint_vector(w, route, cum)
    w.position = route[len(route) // 2].copy()
    second = waypoint_vector(w, route, cum)
    assert np.linalg.norm(first - second) > 1e-3


def test_expanded_policy_computes_the_same_actions_as_the_source():
    class Dummy:
        pass
    old_space = spaces.Box(-np.inf, np.inf, (256,), dtype=np.float32)
    new_space = spaces.Box(-np.inf, np.inf, (256 + EXTRA,), dtype=np.float32)
    act = spaces.Box(-1, 1, (4,), dtype=np.float32)

    import gymnasium as gym
    class E(gym.Env):
        def __init__(self, space):
            self.observation_space, self.action_space = space, act
        def reset(self, seed=None, options=None):
            return np.zeros(self.observation_space.shape, np.float32), {}
        def step(self, a):
            return np.zeros(self.observation_space.shape, np.float32), 0., False, False, {}
    kw = {'net_arch': {'pi': [128, 128], 'vf': [128, 128]}}
    source = PPO('MlpPolicy', E(old_space), device='cpu', seed=1, policy_kwargs=kw)
    new = expand_policy(source, E(new_space), 1)
    x = torch.randn(7, 256)
    extra = torch.randn(7, EXTRA)
    with torch.no_grad():
        a = source.policy.get_distribution(x).distribution.loc
        b = new.policy.get_distribution(torch.cat([x, extra], dim=1)).distribution.loc
        va, vb = source.policy.predict_values(x), new.policy.predict_values(torch.cat([x, extra], dim=1))
    assert torch.allclose(a, b, atol=1e-6) and torch.allclose(va, vb, atol=1e-6)
