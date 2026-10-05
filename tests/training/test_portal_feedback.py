import numpy as np
import torch
from gymnasium.spaces import Box
from fly_rl.training.portal_feedback_policy import feedback_actions, PortalNeuralFeatures, PortalFeedbackPolicy
from fly_rl.training.portal_feedback_policy import EquivariantPortalNeuralFeatures
from fly_rl.training.portal_feedback_policy import LocalPeakPortalNeuralFeatures
from fly_rl.training.portal_feedback_policy import CenteredPortalNeuralFeatures
from fly_rl.training.portal_feedback_policy import guarded_feedback_actions, GuardedPortalFeedbackPolicy
from fly_rl.training.portal_feedback_policy import FreeSpacePortalNeuralFeatures


def test_feedback_brakes_turns_and_controls_altitude():
    delta = torch.tensor([[5., 0., 0.], [-5., 0., 0.], [5., 0., 2.]])
    velocity = torch.tensor([[0., 0., 0.], [1., 0., 0.], [0., 0., 0.]])
    actions = feedback_actions(delta, velocity)
    assert actions[0, 0] > 0 and actions[1, 0] == -1
    assert actions[1, 3] == 1 and actions[2, 2] > 0
    assert torch.isfinite(actions).all() and actions.abs().max() <= 1


def test_perception_shapes_gradients_and_approach_plane_exclusion():
    torch.set_num_threads(2)
    net = PortalNeuralFeatures(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32))
    obs = torch.randn(2, 9, 3869) * .03
    changed = obs.clone(); changed[:, :, 2069:] += 10
    features, logits = net.perception(obs)
    torch.testing.assert_close(features, net(changed))
    assert features.shape == (2, 6) and logits.shape == (2, 1800)
    features.square().mean().backward()
    assert all(torch.isfinite(p.grad).all() for p in net.parameters() if p.grad is not None)


def test_distribution_and_training_use_the_same_feedback_mean():
    torch.set_num_threads(2)
    policy = PortalFeedbackPolicy(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32),
                                  Box(-1, 1, (4,), dtype=np.float32), lambda _: 3e-4)
    obs = torch.randn(2, 9, 3869) * .03
    actions, values, log_prob = policy(obs, deterministic=True)
    torch.testing.assert_close(actions, policy.get_distribution(obs).get_actions(deterministic=True))
    evaluated_values, evaluated_log_prob, entropy = policy.evaluate_actions(obs, actions.detach())
    torch.testing.assert_close(values, evaluated_values)
    torch.testing.assert_close(log_prob, evaluated_log_prob)
    assert torch.isfinite(entropy).all()
    (-evaluated_log_prob.mean() + evaluated_values.square().mean()).backward()
    assert any(p.grad is not None for p in policy.features_extractor.parameters())
    assert all(torch.isfinite(p.grad).all() for p in policy.parameters() if p.grad is not None)


def test_free_space_permits_sideways_opening_and_finite_blocked_fallback():
    net = FreeSpacePortalNeuralFeatures(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32))
    obs = torch.zeros(1, 9, 3869)
    obs[:, -1, 256] = 1
    obs[:, -1, 269 + 12 * 72 + 54] = 1
    features, _ = net.perception(obs)
    assert features[0, 1] > 0 and abs(features[0, 0]) < 1e-5
    assert torch.isfinite(net(torch.zeros_like(obs))).all()


def test_guard_stops_before_a_physical_wall_with_ideal_neural_estimates():
    from fly_rl.simulation.world import FlightWorld
    from fly_rl.simulation.sensors import SENSOR_V6
    world = FlightWorld(2, 'empty', dynamics='coordinated', sensor_version=SENSOR_V6)
    world.position = np.array([5., 6., 3.]); world.velocity = np.array([1.2, 0., 0.]); world.yaw = 0.
    world.obstacles = [(np.array([6., 4., 1.]), np.array([6.3, 8., 5.]))]
    net = FreeSpacePortalNeuralFeatures(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32))
    net.perception = lambda obs: (torch.cat([torch.tensor([[5., 0., 0.]]), obs[:, -1, 260:263] * 3], 1), None)
    for _ in range(60):
        # Isolates physical stopping semantics; full neural accuracy is checked
        # separately and this does not assert a safety guarantee under noise.
        obs = torch.zeros(1, 9, 3869); obs[0, -1] = torch.tensor(world.observe()); obs[0, -1, 259] = 1
        action = guarded_feedback_actions(net(obs))[0].detach().numpy()
        _, _, terminated, _, info = world.step(action, observe=False)
        assert not info['collision']
    assert world.position[0] < 5.84 and abs(world.velocity[0]) < .01


def test_equivariant_portal_bearing_has_no_fixed_forward_bias():
    torch.set_num_threads(2)
    net = EquivariantPortalNeuralFeatures(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32))
    obs = torch.randn(2, 9, 3869) * .03
    rotated = obs.clone()
    rotated[:, :, 269:] = torch.roll(obs[:, :, 269:].reshape(2, 9, 2, 25, 72), 7, -1).reshape(2, 9, 3600)
    angle = np.deg2rad(35); c, s = np.cos(angle), np.sin(angle)
    rotated[:, :, 256] = c * obs[:, :, 256] - s * obs[:, :, 257]
    rotated[:, :, 257] = s * obs[:, :, 256] + c * obs[:, :, 257]
    features, logits = net.perception(obs)
    turned, turned_logits = net.perception(rotated)
    torch.testing.assert_close(turned_logits.reshape(2, 25, 72), torch.roll(logits.reshape(2, 25, 72), 7, -1), atol=3e-5, rtol=3e-5)
    direction = features[:, :3] / features[:, :3].norm(dim=1, keepdim=True)
    expected = direction.clone()
    expected[:, 0] = c * direction[:, 0] - s * direction[:, 1]
    expected[:, 1] = s * direction[:, 0] + c * direction[:, 1]
    torch.testing.assert_close(turned[:, :3] / turned[:, :3].norm(dim=1, keepdim=True), expected, atol=3e-5, rtol=3e-5)


def test_local_peak_keeps_one_hemisphere_and_handles_empty_activity():
    torch.set_num_threads(2)
    net = LocalPeakPortalNeuralFeatures(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32))
    obs = torch.randn(2, 9, 3869) * .03
    obs[:, -1, 256:259] = torch.tensor([1., 0., 0.])
    features, logits = net.perception(obs)
    assert (features[:, 0] > 0).all()
    assert torch.isfinite(features).all() and torch.isfinite(logits).all()
    assert torch.isfinite(net(torch.zeros_like(obs))).all()
    features.square().mean().backward()
    assert all(torch.isfinite(p.grad).all() for p in net.parameters() if p.grad is not None)


def test_center_reference_aims_through_opening_and_uses_observed_near_goal():
    net = CenteredPortalNeuralFeatures(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32))
    net.perception = lambda obs: (torch.tensor([[.3, .4, 0., .1, 0., 0.]]).expand(len(obs), -1), None)
    obs = torch.zeros(2, 9, 3869)
    obs[:, -1, 256] = 1
    obs[0, -1, 259] = .5
    obs[1, -1, 259] = 1 / net.room_distance_scale
    out = net(obs)
    torch.testing.assert_close(out[0, :3], torch.tensor([1.2, .4, 0.]))
    torch.testing.assert_close(out[1, :3], torch.tensor([1., 0., 0.]))


def test_neural_clearance_guard_brakes_and_does_not_reverse_from_rest():
    features = torch.tensor([[5., 0., 2., 1., 0., .5, .2, .2, 5.],
                             [5., 0., 0., 0., 0., 0., .2, 5., 5.],
                             [5., 0., 0., 0., 0., 0., 5., 5., 5.]])
    actions = guarded_feedback_actions(features)
    assert actions[0, 0] < 0 and actions[0, 2] < 0
    assert actions[1, 0] == 0 and actions[2, 0] > 0
    assert torch.isfinite(actions).all()


def test_guard_distribution_matches_evaluation_with_finite_gradients():
    torch.set_num_threads(2)
    policy = GuardedPortalFeedbackPolicy(Box(-np.inf, np.inf, (9, 3869), dtype=np.float32),
                                       Box(-1, 1, (4,), dtype=np.float32), lambda _: 3e-4)
    obs = torch.rand(2, 9, 3869) * .1
    actions, values, log_prob = policy(obs, deterministic=True)
    torch.testing.assert_close(actions, policy.get_distribution(obs).get_actions(deterministic=True))
    v, lp, entropy = policy.evaluate_actions(obs, actions.detach())
    torch.testing.assert_close(lp, log_prob)
    (v.square().mean() - lp.mean()).backward()
    assert torch.isfinite(entropy).all()
    assert all(torch.isfinite(p.grad).all() for p in policy.parameters() if p.grad is not None)
