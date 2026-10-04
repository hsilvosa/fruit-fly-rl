import numpy as np
import torch
from scipy import sparse
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.sensors import SENSOR_V3
from fly_rl.training.learning import BrainEnv,make_policy
from fly_rl.training.temporal_policy import transfer_history_policy


def env(history=0,stride=2,batch=2):
    brain=Brain(batch=batch,device='cpu',matrix=sparse.eye(128,format='csr')*.1,sensor_version=SENSOR_V3)
    return BrainEnv(batch=batch,brain=brain,device='cpu',mode='dense',map_profile='large',sensor_version=SENSOR_V3,history_frames=history,history_stride=stride)


def test_history_samples_previous_brain_features_and_resets_independently():
    e=env(4);obs=e.reset();assert obs.shape==(2,5,256)
    assert not obs[:,:-1].any()
    e.step(np.zeros((2,4)));previous=e.latest_features.copy()
    obs,_,_,_=e.step(np.zeros((2,4)))
    np.testing.assert_array_equal(obs[:,-2],previous)
    e.worlds[0].ticks=e.worlds[0].episode_limit-1
    obs,_,done,infos=e.step(np.zeros((2,4)))
    assert done.tolist()==[True,False]
    assert not obs[0,:-1].any() and obs[1,:-1].any()
    assert infos[0]['terminal_observation'].shape==(5,256)
    assert infos[0]['terminal_observation'][:-1].any()
    assert infos[0]['next_brain_features'].shape==(256,)
    assert e.history_ticks.tolist()==[0,3]
    e.reset();assert not e.feature_history.any() and not e.history_ticks.any()


def test_warm_upgrade_preserves_actions_values_and_optimizer_states():
    oldenv=env();source=make_policy(oldenv,smoke=True)
    source.learn(128)
    newenv=env(8);new=transfer_history_policy(source,newenv)
    obs=newenv.reset();flat=obs[:,-1,:]
    np.testing.assert_allclose(source.predict(flat,deterministic=True)[0],new.predict(obs,deterministic=True)[0],atol=1e-7)
    with torch.no_grad():
        torch.testing.assert_close(source.policy.predict_values(torch.as_tensor(flat)),new.policy.predict_values(torch.as_tensor(obs)))
    assert new.num_timesteps==source.num_timesteps
    assert new.history_transfer['optimizer_state_preserved_for_copied_parameters']
    old_params=dict(source.policy.named_parameters());new_params=dict(new.policy.named_parameters())
    for name in new.history_transfer['copied_parameters']:
        for key,value in source.policy.optimizer.state[old_params[name]].items():
            other=new.policy.optimizer.state[new_params[name]][key]
            if torch.is_tensor(value):torch.testing.assert_close(value,other)
    # The branch can distinguish different past activity without changing current activity.
    extractor=new.policy.features_extractor
    a=torch.zeros((1,9,256));b=a.clone();b[:,0]=1
    torch.testing.assert_close(extractor(a),extractor(b))
    with torch.no_grad():extractor.residual.weight.fill_(.01)
    assert not torch.allclose(extractor(a),extractor(b))
