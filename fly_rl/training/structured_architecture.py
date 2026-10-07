"""Structured neural panorama encoder for autonomous architectural PPO."""
import torch
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from fly_rl.training.panorama_policy import CircularConv

VERSION='learned-architecture-1.0-exp.2'


class StructuredArchitecturalHistory(BaseFeaturesExtractor):
    """Preserve visual neighborhoods and goal/state channels; learn all actions."""
    def __init__(self, observation_space):
        if observation_space.shape != (9,5669):
            raise ValueError('Expected segmented dual neural history')
        super().__init__(observation_space,features_dim=141)
        self.visual=nn.Sequential(CircularConv(3,8,2),nn.Tanh(),
                                 CircularConv(8,16,2),nn.Tanh(),
                                 nn.AdaptiveAvgPool2d((3,9)),nn.Flatten(),
                                 nn.Linear(16*3*9,96),nn.Tanh())
        self.near=nn.Sequential(nn.Linear(256,32),nn.Tanh())
        self.memory=nn.GRU(141,128,batch_first=True)

    def forward(self, observations):
        batch,frames,_=observations.shape
        values=observations.reshape(batch*frames,5669)
        visual=self.visual(values[:,269:].reshape(batch*frames,3,25,72))
        near=self.near(values[:,:256])
        goal_state=values[:,256:269]
        sequence=torch.cat([visual,near,goal_state],dim=1).reshape(batch,frames,141)
        history,_=self.memory(sequence)
        # Direct neural goal/state features avoid losing small state channels
        # inside the visual compression. No direction-to-action rule is applied.
        return torch.cat([history[:,-1],observations[:,-1,256:269]],dim=1)
