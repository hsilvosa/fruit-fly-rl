"""Explicit training-only short-goal architectural curriculum world."""
import numpy as np
from fly_rl.simulation.architectural_world import ArchitecturalWorld
from fly_rl.simulation.architectural_training_goals import sample_training_goal
from fly_rl.simulation.world import DT

STAGES=(1.,2.,4.,8.,None)


class ArchitecturalCurriculumWorld(ArchitecturalWorld):
    """Keep geometry and starts; label changed training goals and deadlines."""
    def __init__(self, scene, situation=0, seed=0, stage=0):
        self.set_stage(stage)
        super().__init__(scene,situation,seed)

    def set_stage(self, stage):
        if type(stage) is not int or not 0 <= stage < len(STAGES):
            raise ValueError('Invalid architectural curriculum stage')
        self.stage=stage

    def reset(self, seed=None, options=None):
        _,info=super().reset(seed=seed,options=options)
        self.original_target=self.target.copy()
        self.original_episode_limit=self.episode_limit
        distance=STAGES[self.stage]
        if distance is not None:
            self.target=sample_training_goal(self,distance,self.rng)
            self.distance=float(np.linalg.norm(self.target-self.position))
            # Only lesson deadlines change. Original tasks use their full limit.
            self.episode_limit=min(self.original_episode_limit,
                int(np.ceil((10.+2*distance)/DT)))
        info.update(self.curriculum_metadata())
        return self.observe(),info

    def curriculum_metadata(self):
        return dict(training_curriculum=True,curriculum_stage=self.stage,
                    curriculum_distance=STAGES[self.stage],
                    original_target=self.original_target.tolist(),
                    original_episode_limit=self.original_episode_limit,
                    training_episode_limit=self.episode_limit)

    def snapshot(self):
        result=super().snapshot()
        result.update(self.curriculum_metadata())
        return result

    def step(self, action, observe=True):
        observation,reward,terminated,truncated,info=super().step(action,observe=observe)
        info.update(self.curriculum_metadata())
        return observation,reward,terminated,truncated,info
