"""Versioned signed neural activity grouped by synthetic input assignments."""
import torch
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.sensors import SENSOR_V5,SENSOR_V6

GROUP_READOUT='input-associated-neural-mean-v1'
LEGACY_READOUT='random-pool-256-v1'

class InputGroupedBrain(Brain):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.sensor_version not in (SENSOR_V5,SENSOR_V6):
            raise ValueError('Input-associated readout requires a declared v5 or v6 sensory contract')
        self.feature_count=self.sensor_count
        self.readout_version=GROUP_READOUT
        self.group_count=torch.bincount(torch.cat([self.input_index.flatten(),self.fan_index.flatten()]),
                                        minlength=self.sensor_count).clamp_min(1).float()
        self.model_spec+=':'+GROUP_READOUT

    @torch.no_grad()
    def read_activity(self):
        grouped=torch.zeros((self.sensor_count,self.batch),device=self.device)
        for indices,signs in ((self.input_index,self.input_sign),(self.fan_index,self.fan_sign)):
            for column in (0,1):
                grouped.index_add_(0,indices[:,column],self.state*signs[:,column,None])
        return (grouped/self.group_count[:,None]).T.contiguous().cpu().numpy()

    @torch.no_grad()
    def step(self,sensors):
        super().step(sensors)
        return self.read_activity()
