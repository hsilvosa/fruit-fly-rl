"""Full-connectome adapter for explicitly selected training curriculum worlds."""
from fly_rl.simulation.architectural_env import ArchitecturalBrainEnv
from fly_rl.simulation.architectural_curriculum_world import ArchitecturalCurriculumWorld


class ArchitecturalCurriculumEnv(ArchitecturalBrainEnv):
    def __init__(self, scene, situation=0, data='data', batch=1, device='cuda', seed=0, stage=0):
        # Validate lesson geometry before loading the full graph.
        worlds=[ArchitecturalCurriculumWorld(scene,situation,seed+i,stage) for i in range(batch)]
        self.curriculum_stage=stage
        super().__init__(scene,situation,data,batch,device,seed)
        self.worlds=worlds

    def select_situation(self, scene, situation=0, seed=0):
        worlds=[ArchitecturalCurriculumWorld(scene,situation,seed+i,self.curriculum_stage)
                for i in range(self.num_envs)]
        self.worlds=worlds
        self.architectural_scene=scene
        self.architectural_situation=situation
        self.seed(seed)
        return self.reset()

    def select_stage(self, stage, seed=0):
        # Every world validates first. Invalid selection cannot partly reset.
        worlds=[ArchitecturalCurriculumWorld(self.architectural_scene,
                  self.architectural_situation,seed+i,stage) for i in range(self.num_envs)]
        self.worlds=worlds
        self.curriculum_stage=stage
        self.seed(seed)
        return self.reset()
