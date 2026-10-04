import numpy as np
import pytest
import torch
from scipy import sparse
from stable_baselines3.common.callbacks import BaseCallback
from fly_rl.connectome.brain import Brain
from fly_rl.training.learning import BrainEnv,make_policy,train,TrainingSession

class Continue(BaseCallback):
    def _on_step(self):return True

@pytest.mark.parametrize('terminal,expected',[(False,-5.02+.995*10),(True,-5.02)])
def test_failed_timeout_bootstrap_changes_actual_ppo_rollout(terminal,expected):
    brain=Brain(batch=1,device='cpu',matrix=sparse.eye(8,format='csr')*.1)
    env=BrainEnv(batch=1,device='cpu',brain=brain,mode='dense',map_profile='gate-near',timeout_as_terminal=terminal)
    model=make_policy(env,smoke=True)
    _,callback=model._setup_learn(2,Continue())
    env.worlds[0].ticks=env.worlds[0].episode_limit-1
    # Fix action at zero and terminal value at ten to isolate SB3's bootstrap.
    model.policy.forward=lambda obs,deterministic=False:(torch.zeros((1,4)),torch.zeros((1,1)),torch.zeros(1))
    model.policy.predict_values=lambda obs:torch.full((len(obs),1),10.)
    assert model.collect_rollouts(env,callback,model.rollout_buffer,n_rollout_steps=2)
    assert model.rollout_buffer.rewards[0,0]==pytest.approx(expected,abs=1e-5)

@pytest.mark.parametrize('gamma',[1.,float('nan'),.5])
def test_invalid_horizon_rejected_before_graph_loading(gamma):
    with pytest.raises(ValueError,match='Discount gamma'):
        train('missing','cpu',128,1,'unused.zip',gamma=gamma)
