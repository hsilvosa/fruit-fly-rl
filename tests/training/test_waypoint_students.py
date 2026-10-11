import numpy as np
import pytest
import torch
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO

from fly_rl.training.waypoint_diagnostic import EXTRA
from fly_rl.training.waypoint_students import AuxPPO, BlindWaypointPolicy, build_student

WIDTH = 256
ACT = spaces.Box(-1, 1, (4,), dtype=np.float32)


class Fake(gym.Env):
    """Observation = 256 noise values + a unit 'waypoint' that is partly predictable from the first values."""
    def __init__(self, width=WIDTH + EXTRA):
        self.observation_space = spaces.Box(-np.inf, np.inf, (width,), dtype=np.float32)
        self.action_space = ACT
        self.rng = np.random.default_rng(0)
        self.t = 0

    def _obs(self):
        x = self.rng.normal(size=WIDTH).astype(np.float32)
        w = x[:3] + 0.1 * self.rng.normal(size=3)
        w = (w / np.linalg.norm(w)).astype(np.float32)
        return np.concatenate([x, w])

    def reset(self, seed=None, options=None):
        self.t = 0
        return self._obs(), {}

    def step(self, a):
        self.t += 1
        return self._obs(), float(self.rng.normal()), False, self.t >= 64, {}


def source_policy():
    class Src(Fake):
        def __init__(self):
            super().__init__(WIDTH)
            self.observation_space = spaces.Box(-np.inf, np.inf, (WIDTH,), dtype=np.float32)
        def _obs(self):
            return self.rng.normal(size=WIDTH).astype(np.float32)
    return PPO('MlpPolicy', Src(), device='cpu', seed=1, policy_kwargs={'net_arch': {'pi': [128, 128], 'vf': [128, 128]}})


@pytest.mark.parametrize('arm', ['aux', 'critic'])
def test_student_starts_identical_to_source_and_actor_ignores_waypoint(arm):
    source = source_policy()
    student = build_student(source, Fake(), 3, arm)
    x = torch.randn(9, WIDTH)
    w1, w2 = torch.randn(9, EXTRA), torch.randn(9, EXTRA)
    with torch.no_grad():
        a = source.policy.get_distribution(x).distribution.loc
        b1 = student.policy.get_distribution(torch.cat([x, w1], 1)).distribution.loc
        b2 = student.policy.get_distribution(torch.cat([x, w2], 1)).distribution.loc
        assert torch.allclose(a, b1, atol=1e-6) and torch.allclose(b1, b2, atol=1e-6)
        assert torch.allclose(source.policy.predict_values(x), student.policy.predict_values(torch.cat([x, w1], 1)), atol=1e-6)


@pytest.mark.parametrize('arm', ['aux', 'critic'])
def test_actor_stays_blind_after_training_and_after_a_save_and_load(arm, tmp_path):
    student = build_student(source_policy(), Fake(), 4, arm)
    student.learn(512)
    def actor_cols(model):
        return model.policy.mlp_extractor.policy_net[0].weight[:, WIDTH:].abs().max().item()
    assert actor_cols(student) == 0.0
    critic_cols = student.policy.mlp_extractor.value_net[0].weight[:, WIDTH:].abs().max().item()
    assert (critic_cols == 0.0) if arm == 'aux' else (critic_cols > 0.0)
    path = str(tmp_path / 'student.zip')
    student.save(path)
    loaded = AuxPPO.load(path, env=Fake(), device='cpu')
    assert isinstance(loaded.policy, BlindWaypointPolicy) and loaded.policy.aux_head_enabled == (arm == 'aux')
    x = torch.randn(5, WIDTH)
    with torch.no_grad():
        m1 = student.policy.get_distribution(torch.cat([x, torch.randn(5, EXTRA)], 1)).distribution.loc
        m2 = loaded.policy.get_distribution(torch.cat([x, torch.randn(5, EXTRA)], 1)).distribution.loc
    assert torch.allclose(m1, m2, atol=1e-6)
    loaded.learn(256)
    assert actor_cols(loaded) == 0.0


def test_auxiliary_head_learns_the_route_direction():
    student = build_student(source_policy(), Fake(), 5, 'aux')
    obs = torch.tensor(np.stack([Fake()._obs() for _ in range(256)]))
    before = student.policy.aux_loss(obs).item()
    student.learn(2048)
    after = student.policy.aux_loss(obs).item()
    assert after < before - 0.05


def test_pretrained_trunk_loads_into_a_blind_actor_and_reproduces_the_source(tmp_path):
    source = source_policy()
    net = source.policy.mlp_extractor.policy_net
    head = torch.nn.Sequential(torch.nn.Linear(128, 64), torch.nn.Tanh(), torch.nn.Linear(64, EXTRA))
    trunk = torch.nn.Sequential(torch.nn.Linear(WIDTH, 128), torch.nn.Tanh(), torch.nn.Linear(128, 128), torch.nn.Tanh())
    with torch.no_grad():
        for i in (0, 2):
            trunk[i].weight.copy_(net[i].weight); trunk[i].bias.copy_(net[i].bias)
    path = str(tmp_path / 'trunk.pt')
    torch.save({'trunk': trunk.state_dict(), 'act': source.policy.action_net.state_dict(), 'head': head.state_dict()}, path)
    student = build_student(source, Fake(), 6, 'pre', pretrained=path)
    x = torch.randn(7, WIDTH)
    with torch.no_grad():
        a = source.policy.get_distribution(x).distribution.loc
        b = student.policy.get_distribution(torch.cat([x, torch.randn(7, EXTRA)], 1)).distribution.loc
    assert torch.allclose(a, b, atol=1e-6)
    student.learn(512)
    assert student.policy.mlp_extractor.policy_net[0].weight[:, WIDTH:].abs().max().item() == 0.0
    with pytest.raises(ValueError):
        build_student(source, Fake(), 6, 'pre')
    with pytest.raises(ValueError):
        build_student(source, Fake(), 6, 'aux', pretrained=path)
