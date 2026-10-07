"""Architectural simulation environment using full-connectome neural observations."""
from fly_rl.training.learning import BrainEnv
from fly_rl.simulation.sensors import SENSOR_V6
from fly_rl.connectome.segmented_readout import SEGMENTED_DUAL_READOUT
from fly_rl.simulation.architectural_world import ArchitecturalWorld

class ArchitecturalBrainEnv(BrainEnv):
    def __init__(self, scene, situation=0, data='data', batch=1, device='cuda', seed=0):
        worlds = [ArchitecturalWorld(scene,situation,seed+i) for i in range(batch)]
        super().__init__(data=data,batch=batch,device=device,seed=seed,mode='empty',
                         dynamics='coordinated',sensor_version=SENSOR_V6,history_frames=8,
                         history_stride=8,readout_version=SEGMENTED_DUAL_READOUT,
                         sensor_backend='torch-cuda' if device=='cuda' else 'numpy')
        self.worlds = worlds
        self.architectural_scene = scene
        self.architectural_situation = situation

    def select_situation(self, scene, situation=0, seed=0):
        """Change geometry, then clear neural state and observation history."""
        worlds = [ArchitecturalWorld(scene,situation,seed+i) for i in range(self.num_envs)]
        self.worlds = worlds
        self.architectural_scene = scene
        self.architectural_situation = situation
        self.seed(seed)
        return self.reset()
