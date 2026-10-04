"""Directional visual attention over recurrent neural groups, without route input."""
import torch
from torch import nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from fly_rl.training.panorama_policy import CircularConv
from fly_rl.simulation.sensors import SENSORS,PANORAMA_COUNT,PANORAMA_SHAPE,panorama_directions

class DirectionalPanoramicBrainHistory(BaseFeaturesExtractor):
    def __init__(self,observation_space):
        if len(observation_space.shape)!=2 or observation_space.shape[1]!=SENSORS+2*PANORAMA_COUNT:
            raise ValueError('Directional attention requires v6 neural histories')
        super().__init__(observation_space,features_dim=192)
        self.register_buffer('neural_scale',torch.tensor(10.))
        self.register_buffer('ray_directions',torch.tensor(panorama_directions(),dtype=torch.float32))
        self.proprioception=nn.Sequential(nn.Linear(SENSORS,64),nn.Tanh())
        self.visual_map=nn.Sequential(CircularConv(2,8),nn.ReLU(),CircularConv(8,16),nn.ReLU())
        self.attention=nn.Conv2d(16,1,1)
        self.visual_projection=nn.Sequential(nn.Linear(24,128),nn.Tanh())
        self.memory=nn.GRU(192,192,batch_first=True)
        self.waypoint_head=nn.Sequential(nn.Linear(192,96),nn.Tanh(),nn.Linear(96,4),nn.Tanh())
        self.waypoint_residual=nn.Linear(4,192)
        nn.init.zeros_(self.waypoint_residual.weight);nn.init.zeros_(self.waypoint_residual.bias)

    def forward_with_attention(self,observations):
        batch,frames,_=observations.shape
        values=observations.reshape(batch*frames,-1)*self.neural_scale
        panorama=values[:,SENSORS:].reshape(batch*frames,2,*PANORAMA_SHAPE)
        image=self.visual_map(panorama)
        goal=values[:,256:259]
        goal=goal/torch.linalg.vector_norm(goal,dim=1,keepdim=True).clamp_min(1e-5)
        # The prior uses the existing synthetic goal-bearing neural groups only.
        logits=self.attention(image).flatten(1)+3.*(goal@self.ray_directions.T)
        weights=logits.softmax(dim=1)
        direction=weights@self.ray_directions
        direction=direction/torch.linalg.vector_norm(direction,dim=1,keepdim=True).clamp_min(1e-5)
        pooled=(image.flatten(2)*weights[:,None]).sum(dim=2)
        distance_signal=(panorama[:,0].flatten(1)*weights).sum(1,keepdim=True)
        summary=torch.cat([pooled,direction,distance_signal,goal,torch.linalg.vector_norm(values[:,256:259],dim=1,keepdim=True)],dim=1)
        visual=self.visual_projection(summary)
        encoded=torch.cat([self.proprioception(values[:,:SENSORS]),visual],dim=1)
        sequence,_=self.memory(encoded.reshape(batch,frames,192));latent=sequence[:,-1]
        raw=self.waypoint_head(latent)
        waypoint=torch.cat([direction.reshape(batch,frames,3)[:,-1],raw[:,3:]],dim=1)
        return latent+self.waypoint_residual(waypoint),waypoint,logits.reshape(batch,frames,PANORAMA_COUNT)[:,-1]

    def forward_with_waypoint(self,observations):
        latent,waypoint,_=self.forward_with_attention(observations)
        return latent,waypoint

    def forward(self,observations):return self.forward_with_waypoint(observations)[0]
