import numpy as np
import pytest

from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.architectural_transfer import ArchitecturalSceneWorld, all_situations
from fly_rl.simulation.architectural_world import ArchitecturalWorld
from fly_rl.simulation.sensors import SENSOR_V3, SENSOR_VERSION


def test_there_are_twenty_one_situations_in_six_scenes():
    assert len(all_situations()) == 21
    assert {s for s, _, _ in all_situations()} == set(BUILDERS)


@pytest.mark.parametrize('sensor_version', [SENSOR_VERSION, SENSOR_V3])
def test_every_situation_resets_with_the_older_sensor_contracts(sensor_version):
    for scene, index, _ in all_situations():
        world = ArchitecturalSceneWorld(scene, index, 3, sensor_version)
        observation, info = world.reset(seed=3)
        assert observation.shape == world.observation_space.shape and np.isfinite(observation).all()
        assert info['scene'] == scene and len(world.obstacles) == len(world.scene.solids)
        assert world.episode_limit == world.architectural_deadline


def test_geometry_start_goal_and_deadline_match_the_protected_world():
    for scene, index, _ in all_situations():
        protected = ArchitecturalWorld(scene, index, 5)
        protected.reset(seed=5)
        copy = ArchitecturalSceneWorld(scene, index, 5, sensor_version=SENSOR_VERSION)
        copy.reset(seed=5)
        assert np.allclose(protected.position, copy.position) and np.allclose(protected.target, copy.target)
        assert np.allclose(protected.room, copy.room) and protected.episode_limit == copy.episode_limit
        assert len(protected.obstacles) == len(copy.obstacles)
        assert protected.scene_hash == copy.scene_hash


def test_unknown_scene_and_situation_are_rejected():
    with pytest.raises(ValueError):
        ArchitecturalSceneWorld('castle', 0, 1)
    with pytest.raises(ValueError):
        ArchitecturalSceneWorld('apartment', 99, 1)
