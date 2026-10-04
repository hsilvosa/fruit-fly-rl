import numpy as np
import pytest
import torch
from scipy import sparse
from fly_rl.connectome.brain import Brain
from fly_rl.connectome.readout import InputGroupedBrain,GROUP_READOUT
from fly_rl.simulation.sensors import SENSOR_V5
from fly_rl.training.learning import BrainEnv,make_policy,save_model,load_model,checkpoint_sensor_version

def test_grouping_preserves_recurrence_and_uses_activity():
    matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2
    legacy=Brain(batch=2,device='cpu',matrix=matrix,sensor_version=SENSOR_V5)
    grouped=InputGroupedBrain(batch=2,device='cpu',matrix=matrix,sensor_version=SENSOR_V5)
    sensors=np.random.default_rng(3).uniform(-1,1,(2,1447)).astype(np.float32)
    legacy.step(sensors);values=grouped.step(sensors)
    assert torch.equal(legacy.state,grouped.state)
    expected=np.zeros((2,1447));counts=np.zeros(1447)
    for indices,signs in ((grouped.input_index,grouped.input_sign),(grouped.fan_index,grouped.fan_sign)):
        for row in range(grouped.n):
            for col in range(2):
                index=int(indices[row,col]);counts[index]+=1
                expected[:,index]+=grouped.state[row].numpy()*float(signs[row,col])
    assert np.allclose(values,expected/np.maximum(counts,1),atol=1e-7)
    grouped.state.zero_();assert not grouped.read_activity().any()
    grouped.step(sensors);saved=grouped.state[:,1].clone();grouped.reset([0])
    assert not grouped.state[:,0].any();assert torch.equal(saved,grouped.state[:,1])

def test_spatial_checkpoint_and_contract(tmp_path):
    brain=InputGroupedBrain(batch=1,device='cpu',matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2,sensor_version=SENSOR_V5)
    env=BrainEnv(batch=1,device='cpu',brain=brain,sensor_version=SENSOR_V5,history_frames=8,readout_version=GROUP_READOUT)
    model=make_policy(env,smoke=True);obs=env.reset()
    assert obs.shape==(1,9,1447)
    model.learn(128);path=tmp_path/'policy.zip';save_model(model,path,brain)
    loaded=load_model(path,brain,env)
    assert np.array_equal(model.predict(obs,deterministic=True)[0],loaded.predict(obs,deterministic=True)[0])
    assert checkpoint_sensor_version(path)==SENSOR_V5
    legacy=Brain(batch=1,device='cpu',matrix=sparse.eye(500,format='csr'),sensor_version=SENSOR_V5)
    with pytest.raises(ValueError,match='configuration mismatch'):load_model(path,legacy)

def test_numeric_precision_is_saved_and_restored(tmp_path,monkeypatch):
    brain=InputGroupedBrain(batch=1,device='cpu',matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2,sensor_version=SENSOR_V5)
    env=BrainEnv(batch=1,device='cpu',brain=brain,sensor_version=SENSOR_V5,history_frames=8,readout_version=GROUP_READOUT)
    model=make_policy(env,smoke=True)
    model.policy_numeric_precision={'cudnn_allow_tf32':False,'matmul_allow_tf32':False}
    path=tmp_path/'precision.zip';save_model(model,path,brain)
    monkeypatch.setattr(torch.backends.cudnn,'allow_tf32',True)
    monkeypatch.setattr(torch.backends.cuda.matmul,'allow_tf32',True)
    loaded=load_model(path,brain,env)
    assert not torch.backends.cudnn.allow_tf32
    assert not torch.backends.cuda.matmul.allow_tf32
    assert loaded.policy_numeric_precision==model.policy_numeric_precision
