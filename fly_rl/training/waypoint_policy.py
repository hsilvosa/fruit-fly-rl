"""Learn a local waypoint estimate from neural histories, never runtime routes."""
import torch
from torch import nn
from stable_baselines3 import PPO
from fly_rl.training.spatial_policy import SpatialBrainHistory

class WaypointBrainHistory(SpatialBrainHistory):
    def __init__(self,observation_space):
        super().__init__(observation_space)
        self.waypoint_head=nn.Sequential(nn.Linear(128,64),nn.Tanh(),nn.Linear(64,4),nn.Tanh())
        self.waypoint_residual=nn.Linear(4,128)
        nn.init.zeros_(self.waypoint_residual.weight);nn.init.zeros_(self.waypoint_residual.bias)

    def forward_with_waypoint(self,observations):
        encoded=super().forward(observations)
        waypoint=self.waypoint_head(encoded)
        return encoded+self.waypoint_residual(waypoint),waypoint

    def forward(self,observations):
        return self.forward_with_waypoint(observations)[0]


def transfer_waypoint_policy(source,env,seed=42,device='cpu'):
    """Add a supervised perception head with an initially identical motor output."""
    if source.observation_space.shape!=env.observation_space.shape:
        raise ValueError('Waypoint transfer requires identical neural histories')
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cuda.matmul.allow_tf32=False
    model=PPO('MlpPolicy',env,device=device,seed=seed,n_steps=512,batch_size=128,n_epochs=5,
        policy_kwargs={'features_extractor_class':WaypointBrainHistory,'share_features_extractor':False,
            'ortho_init':False,'net_arch':{'pi':[128,128],'vf':[128,128]}})
    before=dict(source.policy.named_parameters());after=dict(model.policy.named_parameters())
    with torch.no_grad():
        for name,value in before.items():
            if name not in after or after[name].shape!=value.shape:raise ValueError('Incompatible spatial motor source')
            after[name].copy_(value)
    model.num_timesteps=source.num_timesteps;model._n_updates=source._n_updates
    model.policy_numeric_precision={'cudnn_allow_tf32':False,'matmul_allow_tf32':False}
    model.waypoint_training={'version':'neural-local-waypoint-auxiliary-v1','runtime_route_access':False,
        'initialization':'zero residual; existing spatial actor output preserved','label_components':['local_unit_x','local_unit_y','local_unit_z','distance_over24_clipped1']}
    return model
