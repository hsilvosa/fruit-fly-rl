"""Algebra and reset checks use a synthetic graph, not performance evidence."""
import numpy as np
import torch
import pytest
from scipy import sparse
from fly_rl.connectome.distance_readout import DistanceStableActivityBrain, DISTANCE_STABLE_READOUT
from fly_rl.simulation.sensors import SENSOR_V6


def test_distances_decode_cleanly_while_speed_channels_retain_context():
    torch.set_num_threads(2)
    brain = DistanceStableActivityBrain(matrix=sparse.eye(30000, format='csr', dtype=np.float32)*.2,
                                       device='cpu', batch=2, sensor_version=SENSOR_V6)
    rng = np.random.default_rng(49)
    sensors = rng.uniform(-.7, .7, (2, 3869)).astype(np.float32)
    sensors[:, :128] = rng.uniform(0, 1, (2, 128))
    sensors[:, 269:2069] = rng.uniform(0, 1, (2, 1800))
    brain.step(sensors)
    previous = brain.state.clone()
    features = brain.step(sensors)
    clean = brain.project_activity(previous, brain.state, True)
    retained = brain.project_activity(previous, brain.state, False)
    np.testing.assert_allclose(features[:, :2069], clean[:, :2069], atol=3e-6)
    np.testing.assert_allclose(features[:, 269:2069], sensors[:, 269:2069], atol=2e-5)
    np.testing.assert_allclose(features[:, 2069:], (clean+.05*(retained-clean))[:, 2069:], atol=3e-6)
    assert np.max(np.abs(features[:, 2069:]-clean[:, 2069:])) > 1e-4
    assert brain.fingerprint.endswith(DISTANCE_STABLE_READOUT)
    state = brain.state.clone()
    brain.reconstruct_activity(previous, brain.state)
    torch.testing.assert_close(state, brain.state)
    brain.reset([0])
    assert torch.count_nonzero(brain.state[:, 0]) == 0
    torch.testing.assert_close(brain.state[:, 1], state[:, 1])


def test_checkpoint_reload_requires_matching_distance_readout(tmp_path):
    from fly_rl.training.learning import BrainEnv, make_policy, save_model, load_model, checkpoint_readout
    from fly_rl.connectome.innovation import MotionStableActivityBrain
    torch.set_num_threads(2)
    matrix = sparse.eye(30000, format='csr', dtype=np.float32)*.2
    brain = DistanceStableActivityBrain(matrix=matrix, device='cpu', sensor_version=SENSOR_V6)
    env = BrainEnv(brain=brain, device='cpu', sensor_version=SENSOR_V6,
                   readout_version=DISTANCE_STABLE_READOUT, history_frames=8, history_stride=8)
    try:
        model = make_policy(env, smoke=True)
        observation = env.reset()
        path = tmp_path/'untrained-distance-policy.zip'
        save_model(model, path, brain)
        loaded = load_model(path, brain, env)
        np.testing.assert_equal(model.predict(observation, deterministic=True)[0],
                                loaded.predict(observation, deterministic=True)[0])
        assert loaded.num_timesteps == 0
        assert checkpoint_readout(path) == DISTANCE_STABLE_READOUT
        incompatible = MotionStableActivityBrain(matrix=matrix, device='cpu', sensor_version=SENSOR_V6)
        with pytest.raises(ValueError, match='configuration mismatch'):
            load_model(path, incompatible)
    finally:
        env.close()
