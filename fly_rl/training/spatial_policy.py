"""Spatial and temporal readout of neural activity, without raw sensor access."""
import torch
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from fly_rl.simulation.sensors import SENSORS,FAN_COUNT

class SpatialBrainHistory(BaseFeaturesExtractor):
    def __init__(self,observation_space):
        if len(observation_space.shape)!=2 or observation_space.shape[1]!=SENSORS+2*FAN_COUNT:
            raise ValueError('Spatial history requires input-associated v5 neural activity')
        super().__init__(observation_space,features_dim=128)
        self.proprioception=nn.Sequential(nn.Linear(SENSORS,64),nn.Tanh())
        self.visual=nn.Sequential(nn.Conv2d(2,8,3,padding=1),nn.ReLU(),
            nn.Conv2d(8,16,3,stride=2,padding=1),nn.ReLU(),nn.Flatten(),
            nn.Linear(16*10*16,64),nn.Tanh())
        self.memory=nn.GRU(128,128,batch_first=True)

    def forward(self,observations):
        batch,frames,_=observations.shape
        values=observations.reshape(batch*frames,-1)
        # The ordering mirrors the seeded input channels; values are neuron means.
        fan=values[:,SENSORS:].reshape(batch*frames,2,19,31)
        features=torch.cat([self.proprioception(values[:,:SENSORS]),self.visual(fan)],dim=-1)
        sequence,_=self.memory(features.reshape(batch,frames,128))
        return sequence[:,-1,:]
