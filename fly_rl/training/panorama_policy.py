"""Prototype visual controller that consumes full-connectome activity only."""
import torch
from torch import nn
from torch.nn import functional as F
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from fly_rl.simulation.sensors import SENSORS,PANORAMA_COUNT,PANORAMA_SHAPE

class CircularConv(nn.Module):
    def __init__(self,inputs,outputs,stride=1):
        super().__init__();self.conv=nn.Conv2d(inputs,outputs,3,stride=stride)
    def forward(self,x):
        x=F.pad(x,(1,1,0,0),mode='circular')
        return self.conv(F.pad(x,(0,0,1,1),mode='replicate'))

class PanoramicBrainHistory(BaseFeaturesExtractor):
    def __init__(self,observation_space):
        if len(observation_space.shape)!=2 or observation_space.shape[1]!=SENSORS+2*PANORAMA_COUNT:
            raise ValueError('Panoramic controller requires the explicit v6 neural readout')
        super().__init__(observation_space,features_dim=192)
        self.register_buffer('neural_scale',torch.tensor(10.))
        self.proprioception=nn.Sequential(nn.Linear(SENSORS,64),nn.Tanh())
        self.visual=nn.Sequential(CircularConv(2,8),nn.ReLU(),CircularConv(8,16,2),nn.ReLU(),
            nn.Flatten(),nn.Linear(16*13*36,128),nn.Tanh())
        self.memory=nn.GRU(192,192,batch_first=True)
        self.waypoint_head=nn.Sequential(nn.Linear(192,96),nn.Tanh(),nn.Linear(96,4),nn.Tanh())
        self.waypoint_residual=nn.Linear(4,192)
        nn.init.zeros_(self.waypoint_residual.weight);nn.init.zeros_(self.waypoint_residual.bias)
    def forward_with_waypoint(self,observations):
        batch,frames,_=observations.shape
        values=observations.reshape(batch*frames,-1)*self.neural_scale
        panorama=values[:,SENSORS:].reshape(batch*frames,2,*PANORAMA_SHAPE)
        encoded=torch.cat([self.proprioception(values[:,:SENSORS]),self.visual(panorama)],dim=-1)
        sequence,_=self.memory(encoded.reshape(batch,frames,192));latent=sequence[:,-1,:]
        waypoint=self.waypoint_head(latent)
        return latent+self.waypoint_residual(waypoint),waypoint
    def forward(self,observations):return self.forward_with_waypoint(observations)[0]
