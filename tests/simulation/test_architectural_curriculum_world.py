import numpy as np
import pytest
from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.architectural_world import ArchitecturalWorld
from fly_rl.simulation.architectural_curriculum_world import ArchitecturalCurriculumWorld

TRAINING_CASES=[(scene,i) for scene,builder in BUILDERS.items() for i in range(len(builder().situations)-1)]


@pytest.mark.parametrize('scene,situation',TRAINING_CASES)
def test_short_training_tasks_preserve_original_geometry_and_label_goal_changes(scene,situation):
    original=ArchitecturalWorld(scene,situation,42);original.reset(seed=42)
    lesson=ArchitecturalCurriculumWorld(scene,situation,42,stage=0)
    _,info=lesson.reset(seed=42)
    assert np.array_equal(lesson.position,original.position)
    assert np.array_equal(lesson.original_target,original.target)
    assert lesson.scene_hash==original.scene_hash
    assert len(lesson.obstacles)==len(original.obstacles)
    assert np.isclose(np.linalg.norm(lesson.target-lesson.position),1.)
    assert info['training_curriculum'] and info['curriculum_stage']==0
    assert lesson.episode_limit <= original.episode_limit
    assert lesson.snapshot()['original_target']==original.target.tolist()


def test_final_stage_restores_original_goal_deadline_and_resets_independently():
    lesson=ArchitecturalCurriculumWorld('office-floor',seed=42,stage=0)
    lesson.set_stage(4)
    _,info=lesson.reset(seed=42)
    assert np.array_equal(lesson.target,lesson.original_target)
    assert lesson.episode_limit==lesson.original_episode_limit
    assert info['curriculum_distance'] is None
    target=lesson.target.copy()
    lesson.position+=1
    lesson.reset(seed=42)
    assert np.array_equal(lesson.target,target)
    for stage in (True,-1,5,1.5):
        with pytest.raises(ValueError):lesson.set_stage(stage)
