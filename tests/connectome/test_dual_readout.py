"""Dual features preserve the old decoder while adding clean neural ranges."""
import numpy as np
import torch
from scipy import sparse
from fly_rl.connectome.dual_readout import DualActivityBrain, DUAL_READOUT
from fly_rl.connectome.innovation import MotionStableActivityBrain
from fly_rl.simulation.sensors import SENSOR_V6


def test_dual_prefix_matches_old_decoder_and_extra_ranges_are_clean():
    torch.set_num_threads(2)
    brain=DualActivityBrain(matrix=sparse.eye(30000,format='csr',dtype=np.float32)*.2,
                           device='cpu',batch=2,sensor_version=SENSOR_V6)
    sensors=np.random.default_rng(92).uniform(-.6,.6,(2,3869)).astype(np.float32)
    sensors[:,269:2069]=np.random.default_rng(93).uniform(0,1,(2,1800))
    brain.step(sensors);previous=brain.state.clone();features=brain.step(sensors)
    old=MotionStableActivityBrain.reconstruct_activity(brain,previous,brain.state)
    clean=brain.project_activity(previous,brain.state,True)
    assert features.shape==(2,5669) and brain.feature_count==5669
    np.testing.assert_equal(features[:,:3869],old)
    np.testing.assert_allclose(features[:,3869:],clean[:,269:2069],atol=3e-6)
    np.testing.assert_allclose(features[:,3869:],sensors[:,269:2069],atol=2e-5)
    assert brain.fingerprint.endswith(DUAL_READOUT)
    state=brain.state.clone();brain.reconstruct_activity(previous,brain.state)
    torch.testing.assert_close(brain.state,state)
    brain.reset([0]);assert not torch.count_nonzero(brain.state[:,0])
    torch.testing.assert_close(brain.state[:,1],state[:,1])


def test_dual_sensitivity_matches_a_drive_perturbation_without_mutating_gradient():
    from fly_rl.visualization.neural_view import NeuralInspector
    torch.set_num_threads(2)
    brain=DualActivityBrain(matrix=sparse.eye(30000,format='csr',dtype=np.float32)*.2,
                           device='cpu',sensor_version=SENSOR_V6)
    sensors=np.full((1,3869),.3,np.float32);brain.step(sensors)
    previous=brain.state.clone();brain.step(sensors);current=brain.state.clone()
    inspector=NeuralInspector.__new__(NeuralInspector);inspector.brain=brain
    gradient=torch.zeros(5669);gradient[270]=.7;gradient[3869]=.9;before=gradient.clone()
    sensitivity,basis=inspector.current_sensitivity(gradient)
    assert basis=='reconstructed_neuronal_drive'
    torch.testing.assert_close(gradient,before)
    index=int(np.argmax(np.abs(sensitivity)));drive=torch.atanh(2*current-previous)
    delta=torch.zeros_like(drive);delta[index,0]=.01
    plus=(previous+torch.tanh(drive+delta))*.5
    minus=(previous+torch.tanh(drive-delta))*.5
    derivative=float(((brain.reconstruct_activity(previous,plus)[0]-brain.reconstruct_activity(previous,minus)[0])*gradient.numpy()).sum()/.02)
    np.testing.assert_allclose(derivative,sensitivity[index],rtol=2e-3,atol=2e-5)
