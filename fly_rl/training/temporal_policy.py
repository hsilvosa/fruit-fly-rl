"""Learned temporal readout of connectome features; no raw sensory access."""
import copy
import torch
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class ResidualBrainHistory(BaseFeaturesExtractor):
    def __init__(self,observation_space,hidden_size=64):
        if len(observation_space.shape)!=2 or any(size <= 0 for size in observation_space.shape):
            raise ValueError('Temporal readout requires a positive history and feature width')
        width=observation_space.shape[1]
        super().__init__(observation_space,features_dim=width)
        self.memory=nn.GRU(width,hidden_size,batch_first=True)
        self.residual=nn.Linear(hidden_size,width)
        nn.init.zeros_(self.residual.weight);nn.init.zeros_(self.residual.bias)

    def forward(self,observations):
        sequence,_=self.memory(observations)
        return observations[:,-1,:]+self.residual(sequence[:,-1,:])


def transfer_history_policy(source,env,seed=42,share_history=True):
    """Explicit new policy interface; preserve existing actor/critic and Adam state."""
    from fly_rl.training.learning import make_policy
    if source.observation_space.shape!=(256,) or not env.history_frames:
        raise ValueError('History transfer requires a legacy feature policy and a temporal environment')
    model=make_policy(env,seed=seed,share_history=share_history)
    before=dict(source.policy.named_parameters());after=dict(model.policy.named_parameters())
    names=[n for n in before if n.startswith(('mlp_extractor.','action_net.','value_net.')) or n=='log_std']
    with torch.no_grad():
        for name in names:
            if name not in after or before[name].shape!=after[name].shape:raise ValueError('Incompatible movement policy')
            after[name].copy_(before[name])
            if before[name] in source.policy.optimizer.state:
                model.policy.optimizer.state[after[name]]=copy.deepcopy(source.policy.optimizer.state[before[name]])
    model.num_timesteps=source.num_timesteps;model._n_updates=source._n_updates
    model.history_transfer={'source_timesteps':source.num_timesteps,'copied_parameters':names,'optimizer_state_preserved_for_copied_parameters':True,'memory_output_initialization':'zero residual; identical current-feature readout'}
    return model


def synchronize_critic_history(policy):
    """Initialize a separate critic memory from the actor before critic fitting.

    This copies parameters once; subsequent value gradients cannot change the
    actor memory. Legacy shared-memory policies require an explicit new policy
    construction rather than an in-place reinterpretation of their checkpoint.
    """
    if policy.share_features_extractor:
        raise ValueError('Critic history isolation requires separate extractors')
    policy.vf_features_extractor.load_state_dict(policy.pi_features_extractor.state_dict())
