import numpy as np
import pytest

from fly_rl.simulation.map_profiles import MapProfile
from fly_rl.simulation.random_profiles import (CLEARANCE, DifficultyController, ProfileSampler, RandomProfileWorld,
                                               in_heldout_b)


def draws(sampler, difficulty, count, seed=0):
    rng = np.random.default_rng(seed)
    return [sampler.sample(difficulty, rng) for _ in range(count)]


@pytest.mark.parametrize('difficulty', [0., 0.25, 0.5, 0.75, 1.])
def test_training_draws_are_valid_profiles_outside_the_heldout_region(difficulty):
    for profile in draws(ProfileSampler('train'), difficulty, 150):
        assert isinstance(profile, MapProfile)
        assert profile.route_clearance == CLEARANCE
        assert not in_heldout_b(profile)


@pytest.mark.parametrize('difficulty', [0., 0.5, 1.])
def test_heldout_draws_are_valid_and_always_inside_the_region(difficulty):
    for profile in draws(ProfileSampler('heldout_b'), difficulty, 100, seed=1):
        assert in_heldout_b(profile)
        assert profile.wall_count >= 4 and profile.aperture_width < 3.8


def test_existing_large_profile_lies_in_the_heldout_region():
    from fly_rl.simulation.map_profiles import PROFILES
    assert in_heldout_b(PROFILES['large'])
    assert not in_heldout_b(PROFILES['passages'])
    assert not in_heldout_b(PROFILES['passages-wide'])


def test_same_seed_gives_the_same_profile_sequence():
    first = [p.to_dict() for p in draws(ProfileSampler('train'), 0.6, 20, seed=7)]
    second = [p.to_dict() for p in draws(ProfileSampler('train'), 0.6, 20, seed=7)]
    assert first == second


def test_difficulty_makes_maps_harder_on_average():
    sampler = ProfileSampler('train')
    easy, hard = draws(sampler, 0.1, 200, seed=3), draws(sampler, 0.9, 200, seed=3)
    assert np.mean([p.wall_count for p in hard]) > np.mean([p.wall_count for p in easy]) + 1
    assert np.mean([p.aperture_width for p in hard]) < np.mean([p.aperture_width for p in easy]) - 1.5
    assert np.mean([p.obstacle_count for p in hard]) > np.mean([p.obstacle_count for p in easy])


def test_controller_raises_lowers_and_clamps():
    controller = DifficultyController(initial=0.5, window=10, step=0.1)
    for _ in range(10):
        controller.update(True)
    assert controller.difficulty == pytest.approx(0.6)
    for _ in range(10):
        controller.update(False)
    assert controller.difficulty == pytest.approx(0.5)
    low = DifficultyController(initial=0.05, window=5, step=0.1)
    for _ in range(5):
        low.update(False)
    assert low.difficulty == 0.0
    with pytest.raises(ValueError):
        DifficultyController(initial=1.5)


def test_world_draws_a_new_valid_layout_for_every_episode_without_training():
    world = RandomProfileWorld(seed=11, mode='dense', dynamics='coordinated')
    seen = set()
    for episode in range(12):
        observation, info = world.reset()
        assert observation.shape == world.observation_space.shape and np.isfinite(observation).all()
        assert len(world.obstacles) == world.map_profile.obstacle_count
        assert all(np.all(world.room - 0.0 >= high - 1e-9) for _, high in world.obstacles)
        assert info['profile']['name'] == 'random'
        seen.add((world.map_profile.room_size, world.map_profile.wall_count, world.map_profile.aperture_width))
    assert len(seen) > 4


def test_world_feeds_episode_outcomes_to_the_shared_controller():
    controller = DifficultyController(initial=0.3, window=2)
    world = RandomProfileWorld(seed=5, mode='dense', dynamics='coordinated', controller=controller)
    world.reset()
    zero = np.zeros(4, dtype=np.float32)
    for _ in range(world.episode_limit + 1):
        _, _, terminated, truncated, info = world.step(zero)
        if terminated or truncated:
            break
    assert len(controller.outcomes) == 1 and controller.outcomes[0] is False
