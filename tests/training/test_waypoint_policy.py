import numpy as np
import torch
from scipy import sparse
from fly_rl.connectome.readout import InputGroupedBrain,GROUP_READOUT
from fly_rl.simulation.sensors import SENSOR_V5
from fly_rl.training.learning import BrainEnv,make_policy,save_model,load_model
from fly_rl.training.waypoint_policy import transfer_waypoint_policy
from fly_rl.training.guided_learning import fit_actor

def test_waypoint_transfer_auxiliary_and_reload(tmp_path):
    torch.set_num_threads(2)
    brain=InputGroupedBrain(batch=1,device='cpu',matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2,sensor_version=SENSOR_V5)
    env=BrainEnv(batch=1,device='cpu',brain=brain,sensor_version=SENSOR_V5,history_frames=8,readout_version=GROUP_READOUT)
    source=make_policy(env,smoke=True);obs=env.reset()
    before={key:value.clone() for key,value in source.policy.state_dict().items()}
    state=brain.state.clone()
    model=transfer_waypoint_policy(source,env)
    assert np.array_equal(source.predict(obs,deterministic=True)[0],model.predict(obs,deterministic=True)[0])
    values=np.repeat(obs,32,axis=0)
    labels=np.tile([0.,0.,.3,1.],(32,1)).astype(np.float32)
    waypoints=np.tile([0.,1.,0.,.5],(32,1)).astype(np.float32)
    waypoints[::2]=np.nan  # Reused data can have no retained auxiliary labels.
    head_before=model.policy.pi_features_extractor.waypoint_head[-2].weight.detach().clone()
    result=fit_actor(model,values,labels,32,3,np.random.default_rng(42),batch_size=32,
        sampling_strategy='maneuver-start-balanced-v2',waypoint_targets=waypoints)
    assert result['finite_losses'] and np.isfinite(result['mean_last_100_waypoint_loss'])
    assert not torch.equal(head_before,model.policy.pi_features_extractor.waypoint_head[-2].weight)
    assert torch.equal(state,brain.state)
    assert all(torch.equal(before[key],value) for key,value in source.policy.state_dict().items())
    path=tmp_path/'waypoint.zip';save_model(model,path,brain)
    reloaded=load_model(path,brain,env)
    assert np.array_equal(model.predict(obs,deterministic=True)[0],reloaded.predict(obs,deterministic=True)[0])
    assert reloaded.waypoint_training['runtime_route_access'] is False
