import numpy as np
import pytest
from fly_rl.simulation.architectural_world import ArchitecturalWorld
from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.architectural_training_goals import sample_training_goal
from fly_rl.simulation.world import RADIUS, segment_box


@pytest.mark.parametrize('scene',list(BUILDERS))
def test_nearby_goal_is_safe_repeatable_and_does_not_modify_original_task(scene):
    world=ArchitecturalWorld(scene,seed=42);world.reset(seed=42)
    original_target=world.target.copy();original_position=world.position.copy()
    original_deadline=world.episode_limit
    goal=sample_training_goal(world,1.,np.random.default_rng(42))
    assert np.allclose(goal,sample_training_goal(world,1.,np.random.default_rng(42)))
    assert np.isclose(np.linalg.norm(goal-world.position),1.)
    assert (goal >= RADIUS+.1).all() and (goal <= world.room-RADIUS-.1).all()
    assert not any(segment_box(world.position,goal,low-RADIUS-.1,high+RADIUS+.1) for low,high in world.obstacles)
    assert np.array_equal(world.target,original_target)
    assert np.array_equal(world.position,original_position)
    assert world.episode_limit==original_deadline


def test_impossible_or_invalid_curriculum_does_not_silently_change_task():
    world=ArchitecturalWorld('office-floor',seed=42);world.reset(seed=42)
    for distance in (0,.45,np.nan,13):
        with pytest.raises(ValueError):sample_training_goal(world,distance,np.random.default_rng(42))
    original=world.target.copy()
    world.obstacles=[(np.zeros(3),world.room.copy())]
    with pytest.raises(ValueError,match='No clear training goal'):
        sample_training_goal(world,1.,np.random.default_rng(42))
    assert np.array_equal(world.target,original)
