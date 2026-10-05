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


def test_projection_history_preserves_current_features_and_can_learn_memory():
    from gymnasium import spaces
    from fly_rl.training.temporal_policy import ResidualBrainHistory
    extractor=ResidualBrainHistory(spaces.Box(-np.inf,np.inf,(9,3869),dtype=np.float32))
    a=torch.zeros((1,9,3869));b=a.clone();b[:,0]=.5;b[:,-1]=a[:,-1]
    torch.testing.assert_close(extractor(a),a[:,-1])
    torch.testing.assert_close(extractor(b),b[:,-1])
    with torch.no_grad():extractor.residual.weight.fill_(.01)
    assert not torch.allclose(extractor(a),extractor(b))
    assert extractor.features_dim==3869 and torch.isfinite(extractor(b)).all()


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


def test_value_optimization_cannot_change_isolated_actor_memory(tmp_path):
    from stable_baselines3 import PPO
    from fly_rl.training.temporal_policy import synchronize_critic_history
    e=env(4);model=make_policy(e,share_history=False)
    policy=model.policy
    with torch.no_grad():policy.pi_features_extractor.residual.weight.fill_(.01)
    synchronize_critic_history(policy)
    obs=torch.randn(8,5,256)
    before=model.predict(obs.numpy(),deterministic=True)[0].copy()
    actor_before={k:v.clone() for k,v in policy.pi_features_extractor.state_dict().items()}
    critic_before={k:v.clone() for k,v in policy.vf_features_extractor.state_dict().items()}
    policy.optimizer.zero_grad()
    loss=(policy.predict_values(obs)-10).square().mean()
    loss.backward()
    assert all(p.grad is None for p in policy.pi_features_extractor.parameters())
    assert any(p.grad is not None and p.grad.abs().max()>0 for p in policy.vf_features_extractor.parameters())
    policy.optimizer.step()
    for k,v in policy.pi_features_extractor.state_dict().items():torch.testing.assert_close(v,actor_before[k],rtol=0,atol=0)
    assert any(not torch.equal(v,critic_before[k]) for k,v in policy.vf_features_extractor.state_dict().items())
    np.testing.assert_array_equal(before,model.predict(obs.numpy(),deterministic=True)[0])
    path=tmp_path/'isolated.zip';model.save(path)
    reloaded=PPO.load(path,device='cpu')
    assert not reloaded.policy.share_features_extractor
    np.testing.assert_array_equal(before,reloaded.predict(obs.numpy(),deterministic=True)[0])


def test_isolated_history_transfer_preserves_warm_actor_and_critic():
    from fly_rl.training.temporal_policy import synchronize_critic_history
    source=make_policy(env(),smoke=True);e=env(4)
    model=transfer_history_policy(source,e,share_history=False)
    obs=e.reset();flat=obs[:,-1,:]
    np.testing.assert_allclose(source.predict(flat,deterministic=True)[0],model.predict(obs,deterministic=True)[0],atol=1e-7)
    with torch.no_grad():torch.testing.assert_close(source.policy.predict_values(torch.as_tensor(flat)),model.policy.predict_values(torch.as_tensor(obs)))
    assert model.policy.pi_features_extractor is not model.policy.vf_features_extractor
    synchronize_critic_history(model.policy)


def test_matched_history_isolation_preserves_actor_initialization_and_imitation():
    from fly_rl.training.guided_learning import fit_actor
    source=make_policy(env(),smoke=True)
    shared=transfer_history_policy(source,env(4),seed=42,share_history=True)
    isolated=transfer_history_policy(source,env(4),seed=42,share_history=False)
    for name,value in shared.policy.pi_features_extractor.state_dict().items():
        torch.testing.assert_close(value,isolated.policy.pi_features_extractor.state_dict()[name],rtol=0,atol=0)
    rng=np.random.default_rng(2026)
    observations=rng.normal(size=(64,5,256)).astype(np.float32)
    targets=rng.uniform(-.5,.5,size=(64,4)).astype(np.float32)
    fit_actor(shared,observations,targets,64,8,np.random.default_rng(43),batch_size=16)
    fit_actor(isolated,observations,targets,64,8,np.random.default_rng(43),batch_size=16)
    np.testing.assert_array_equal(shared.predict(observations,deterministic=True)[0],
                                  isolated.predict(observations,deterministic=True)[0])
