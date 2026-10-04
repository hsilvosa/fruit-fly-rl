import copy
import numpy as np
import torch
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.logger import configure
from fly_rl.training.guarded_ppo import configure_kl_guard


class ObservationFixture(gym.Env):
    observation_space = gym.spaces.Box(-1, 1, (3,), dtype=np.float32)
    action_space = gym.spaces.Box(-1, 1, (2,), dtype=np.float32)


def fixture_model(attempts=8):
    model = PPO('MlpPolicy', ObservationFixture(), n_steps=16, batch_size=8,
                learning_rate=.001, seed=42, device='cpu', policy_kwargs={'net_arch':[8]})
    model.set_logger(configure(None, []))
    model.rollout_buffer.full = True
    return configure_kl_guard(model, max_attempts=attempts)


def test_guard_retries_with_smaller_steps_and_checks_whole_rollout(monkeypatch):
    model = fixture_model()
    before = model.policy.action_net.bias.detach().clone()

    def candidate(self):
        with torch.no_grad():
            self.policy.action_net.bias.add_(self.lr_schedule(1) * 1000)
        self._n_updates += 1

    monkeypatch.setattr(PPO, 'train', candidate)
    model.train()
    record = model.kl_guard_history[-1]
    assert record['accepted'] and len(record['attempts']) > 1
    assert record['observations'] == 16
    assert record['retained_mean_kl'] <= .01 and record['retained_max_kl'] <= .05
    assert model._n_updates == 1
    assert not torch.equal(before, model.policy.action_net.bias)


def test_guard_restores_weights_optimizer_counter_and_rng_when_every_step_is_rejected(monkeypatch):
    model = fixture_model(attempts=2)
    before = copy.deepcopy(model.policy.state_dict())
    optimizer_before = copy.deepcopy(model.policy.optimizer.state_dict())
    numpy_before = np.random.get_state()
    torch_before = torch.get_rng_state()

    def excessive(self):
        np.random.random(); torch.rand(1)
        with torch.no_grad():self.policy.action_net.bias.add_(2)
        self.policy.optimizer.state[self.policy.action_net.bias] = {'step':torch.tensor(1.)}
        self._n_updates += 1

    monkeypatch.setattr(PPO, 'train', excessive)
    model.train()
    assert not model.kl_guard_history[-1]['accepted']
    assert model._n_updates == 0
    for name,value in model.policy.state_dict().items():
        torch.testing.assert_close(value,before[name],atol=0,rtol=0)
    assert model.policy.optimizer.state_dict() == optimizer_before
    np.testing.assert_array_equal(np.random.get_state()[1],numpy_before[1])
    torch.testing.assert_close(torch.get_rng_state(),torch_before,atol=0,rtol=0)


def test_guard_restores_checkpoint_on_optimizer_exception(monkeypatch):
    import pytest
    model = fixture_model()
    before = model.policy.action_net.bias.detach().clone()
    def broken(self):
        with torch.no_grad():self.policy.action_net.bias.add_(10)
        raise RuntimeError('optimizer failure')
    monkeypatch.setattr(PPO,'train',broken)
    with pytest.raises(RuntimeError,match='optimizer failure'):model.train()
    torch.testing.assert_close(model.policy.action_net.bias,before,atol=0,rtol=0)


def test_guard_checkpoint_contract_reloads_training_and_predictions(tmp_path):
    from scipy import sparse
    from fly_rl.connectome.brain import Brain
    from fly_rl.training.learning import BrainEnv,make_policy,save_model,load_model
    from fly_rl.training.guarded_ppo import GuardedPPO
    brain=Brain(matrix=sparse.eye(16,format='csr'),batch=1,device='cpu')
    env=BrainEnv(brain=brain,batch=1,device='cpu')
    model=configure_kl_guard(make_policy(env,smoke=True))
    observations=np.zeros((2,256),dtype=np.float32)
    before=model.predict(observations,deterministic=True)[0]
    path=tmp_path/'guarded.zip';save_model(model,path,brain)
    restored=load_model(path,brain,env)
    assert isinstance(restored,GuardedPPO)
    assert restored.kl_guard_mean_limit==.01 and restored.kl_guard_max_limit==.05
    np.testing.assert_array_equal(before,restored.predict(observations,deterministic=True)[0])


def test_guarded_navigation_refuses_unapproved_or_excessive_plan_before_brain_allocation(tmp_path):
    import json,pytest
    from fly_rl.training.guarded_navigation import run_guarded_navigation
    path=tmp_path/'plan.json'
    path.write_text(json.dumps({'status':'draft-budget-required'}))
    with pytest.raises(ValueError,match='approved plan'):run_guarded_navigation(path)
    path.write_text(json.dumps({'status':'approved','kind':'guarded-original-large-v1','steps':65536}))
    with pytest.raises(ValueError,match='budget'):run_guarded_navigation(path)
