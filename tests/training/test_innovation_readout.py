import numpy as np
import pytest
import torch
from scipy import sparse
from fly_rl.connectome.innovation import InnovationBrain
from fly_rl.simulation.sensors import SENSOR_V6


def test_diagnostic_recovers_activity_and_cancels_declared_recurrence():
    # Unit matrix is for algebra verification only; the actual diagnostic uses
    # the complete graph. Enough neurons are needed to cover all 3869 inputs.
    torch.set_num_threads(2)
    brain = InnovationBrain(matrix=sparse.eye(30000, format='csr', dtype=np.float32) * .2,
                            device='cpu', batch=2, sensor_version=SENSOR_V6)
    rng = np.random.default_rng(48)
    for _ in range(3):
        sensors = rng.uniform(-.8, .8, (2, 3869)).astype(np.float32)
        sensors[:, 269:2069] = rng.uniform(0, 1, (2, 1800))
        features = brain.step(sensors)
        np.testing.assert_allclose(features, sensors, atol=2e-5, rtol=2e-5)
    previous = brain.state.clone()
    canceled = brain.reconstruct_activity(previous, previous)
    retained = brain.project_activity(previous, previous, subtract_recurrence=False)
    assert np.max(np.abs(retained - canceled)) > .01
    brain.reset([0])
    assert torch.count_nonzero(brain.state[:, 0]) == 0
    torch.testing.assert_close(brain.state[:, 1], previous[:, 1])
    with pytest.raises(ValueError, match='Full previous'):
        brain.reconstruct_activity(previous[:2], brain.state)


def test_contrast_preserves_declared_recurrent_contribution():
    from fly_rl.connectome.innovation import ContrastActivityBrain, CONTRAST_READOUT
    torch.set_num_threads(2)
    brain = ContrastActivityBrain(matrix=sparse.eye(30000, format='csr', dtype=np.float32) * .2,
                                  device='cpu', batch=2, sensor_version=SENSOR_V6)
    sensors = np.full((2, 3869), .3, dtype=np.float32)
    brain.step(sensors)
    previous = brain.state.clone()
    features = brain.step(sensors)
    clean = brain.project_activity(previous, brain.state, True)
    retained = brain.project_activity(previous, brain.state, False)
    np.testing.assert_allclose(features, clean + .05 * (retained - clean), atol=3e-6)
    assert np.max(np.abs(features - clean)) > 1e-4
    assert brain.readout_version == CONTRAST_READOUT
    assert brain.fingerprint.endswith(CONTRAST_READOUT)
    saved = brain.state.clone()
    brain.reset([0])
    assert torch.count_nonzero(brain.state[:, 0]) == 0
    torch.testing.assert_close(brain.state[:, 1], saved[:, 1])
