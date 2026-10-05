import numpy as np
import torch
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
import gymnasium as gym
from fly_rl.training.portal_feedback_policy import ContextPortalFeedbackPolicy


class FeatureFixture(gym.Env):
    observation_space = spaces.Box(-np.inf, np.inf, (9, 3869), dtype=np.float32)
    action_space = spaces.Box(-1, 1, (4,), dtype=np.float32)
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        return np.zeros((9, 3869), np.float32), {}


def test_context_policy_gradients_and_checkpoint_reload(tmp_path):
    torch.set_num_threads(2)
    model = PPO(ContextPortalFeedbackPolicy, make_vec_env(FeatureFixture, n_envs=1),
                device='cpu', n_steps=16, batch_size=16, seed=67)
    obs = torch.randn(4, 9, 3869) * .1
    obs[:, -1, 256] = 1
    obs[:, -1, 269:2069] = .5
    predicted, logits = model.policy.features_extractor.perception(obs)
    loss = predicted.square().mean() + logits.square().mean()
    loss.backward()
    gradients = [p.grad for p in model.policy.features_extractor.context.parameters()]
    assert all(g is not None and torch.isfinite(g).all() for g in gradients)
    assert any(torch.count_nonzero(g) for g in gradients)
    wanted = model.predict(obs.numpy(), deterministic=True)[0]
    path = tmp_path / 'context.zip'
    model.save(path)
    loaded = PPO.load(path, device='cpu')
    np.testing.assert_allclose(loaded.predict(obs.numpy(), deterministic=True)[0], wanted, atol=1e-7)


def test_approach_keeps_standoff_until_centered():
    from fly_rl.training.portal_feedback_policy import ApproachContextPortalNeuralFeatures
    features = ApproachContextPortalNeuralFeatures(FeatureFixture.observation_space)
    obs = torch.zeros(3, 9, 3869)
    obs[:, -1, :128] = 1
    obs[:, -1, 256] = 1
    obs[:, -1, 259] = .5
    centers = torch.tensor([[.7, 5., 0.], [.7, .2, 0.], [4., 1., 0.]])
    features.perception = lambda observations: (torch.cat([centers, torch.zeros(3, 3)], 1), None)
    features.normal = lambda observations: torch.tensor([[1., 0., 0.]]).expand(3, -1)
    wanted = torch.tensor([[-.6, 5., 0.], [1.9, .2, 0.], [2.7, 1., 0.]])
    torch.testing.assert_close(features(obs)[:, :3], wanted)
    obs[:, -1, 259] = .01
    target = features(obs)[:, :3]
    torch.testing.assert_close(target[:, 0], features.room_distance_scale.expand(3) * .01)
    torch.testing.assert_close(target[:, 1:], torch.zeros(3, 2))


def test_measured_approach_empty_rays_and_gradients_remain_finite(tmp_path):
    from fly_rl.training.portal_feedback_policy import RangeApproachContextPortalFeedbackPolicy
    model = PPO(RangeApproachContextPortalFeedbackPolicy, make_vec_env(FeatureFixture, n_envs=1),
                device='cpu', n_steps=16, batch_size=16, seed=69)
    obs = torch.zeros(3, 9, 3869)
    obs[:, -1, 256] = 1
    obs[:, -1, 259] = .5
    obs[0, -1, :128] = 1
    obs[1, -1, :128] = .25
    actions, values, log_prob = model.policy(obs)
    assert torch.isfinite(actions).all() and torch.isfinite(values).all() and torch.isfinite(log_prob).all()
    loss = (actions.square().sum() + values.square().sum() + log_prob.sum())
    loss.backward()
    grads = [p.grad for p in model.policy.parameters() if p.grad is not None]
    assert grads and all(torch.isfinite(g).all() for g in grads)
    path = tmp_path / 'measured.zip'
    model.save(path)
    loaded = PPO.load(path, device='cpu')
    np.testing.assert_allclose(loaded.predict(obs.numpy(), deterministic=True)[0],
                               model.predict(obs.numpy(), deterministic=True)[0], atol=1e-7)


def test_previous_panorama_rotation_wrap_and_empty_history_gradients():
    from fly_rl.training.portal_feedback_policy import align_previous_panorama
    obs=torch.zeros(2,9,3869)
    image=torch.arange(72, dtype=torch.float32)[None].expand(25,-1)
    obs[0,-2,269:2069]=image.flatten()
    obs[0,-2,256]=1
    obs[0,-1,256:258]=torch.tensor([2**-.5,-2**-.5])
    aligned=align_previous_panorama(obs)
    wanted=torch.roll(image,-9,dims=1)
    torch.testing.assert_close(aligned[0,-2,269:2069].reshape(25,72),wanted,atol=2e-4,rtol=1e-5)
    assert torch.count_nonzero(aligned[1])==0
    obs.requires_grad_(True)
    align_previous_panorama(obs).square().mean().backward()
    assert torch.isfinite(obs.grad).all()

def test_tube_guard_separates_side_obstacle_from_frontal_body_path():
    from fly_rl.training.portal_feedback_policy import tube_stopping_spaces
    from fly_rl.simulation.sensors import DIRECTIONS, panorama_directions
    short=torch.tensor(DIRECTIONS,dtype=torch.float32)
    panorama=torch.tensor(panorama_directions(),dtype=torch.float32)
    values=torch.ones(2,3869)
    side=int(np.argmax(DIRECTIONS@np.array([1.,1.,0.])/np.sqrt(2)))
    front=int(np.argmax(DIRECTIONS[:,0]))
    values[0,side]=np.sqrt(.4**2+.4**2)/8
    values[1,front]=.6/8
    spaces=tube_stopping_spaces(values,torch.tensor([[1.,0.,0.],[1.,0.,0.]]),short,panorama)
    assert spaces[0,0]>7
    torch.testing.assert_close(spaces[1,0],torch.tensor(.6))
    assert torch.isfinite(spaces).all()
