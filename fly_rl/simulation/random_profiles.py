"""Randomized map distribution for Phase 2 (roadmap action R3).

Draws a fresh partitioned-room profile for every episode from declared parameter ranges. A scalar difficulty in
[0, 1] moves every parameter from easy (few partitions, wide openings) to hard (many partitions, narrow openings),
and an adaptive controller moves that scalar from observed outcomes. A held-out parameter region (level B) is
never drawn by the training sampler and is drawn alone by the held-out sampler. Geometry comes from the existing
generator (`map_profiles.generate_layout`); this module only chooses profile parameters.
"""
from dataclasses import dataclass
import numpy as np

from fly_rl.simulation.map_profiles import MapProfile
from fly_rl.simulation.world import FlightWorld

# Level B region: narrow openings together with many partitions. The existing `large` profile (3.2 m openings,
# five partitions) lies inside it. Training never samples it. Held-out evaluation samples only it.
HELDOUT_B_MAX_APERTURE_WIDTH = 3.8
HELDOUT_B_MIN_WALLS = 4

CLEARANCE = 0.22


def in_heldout_b(profile):
    return profile.aperture_width < HELDOUT_B_MAX_APERTURE_WIDTH and profile.wall_count >= HELDOUT_B_MIN_WALLS


@dataclass(frozen=True)
class Ranges:
    """Parameter ranges at difficulty 0 (first value) and difficulty 1 (second value)."""
    room_x: tuple = (28., 48.)
    room_y: tuple = (28., 44.)
    room_z: tuple = (10., 16.)
    walls: tuple = (0., 5.)
    aperture_width: tuple = (8., 3.2)
    aperture_height: tuple = (5.5, 3.2)
    extra_obstacles: tuple = (8., 70.)
    branch_chance: tuple = (0., 0.5)


def _lerp(pair, t):
    return pair[0] + (pair[1] - pair[0]) * t


class ProfileSampler:
    """Draws MapProfile objects. `mode` is 'train' (excludes the level B region) or 'heldout_b' (only inside it)."""
    def __init__(self, mode='train', ranges=None, jitter=0.15, max_tries=200):
        if mode not in ('train', 'heldout_b'):
            raise ValueError('mode must be train or heldout_b')
        self.mode, self.ranges, self.jitter, self.max_tries = mode, ranges or Ranges(), jitter, max_tries

    def _candidate(self, difficulty, rng):
        r = self.ranges
        t = float(np.clip(difficulty + rng.uniform(-self.jitter, self.jitter), 0., 1.))
        if self.mode == 'heldout_b':
            walls = int(rng.integers(HELDOUT_B_MIN_WALLS, 6))
            width = float(rng.uniform(3.2, HELDOUT_B_MAX_APERTURE_WIDTH - 0.05))
            t = max(t, 0.6)
        else:
            walls = int(round(_lerp(r.walls, t)))
            width = float(_lerp(r.aperture_width, t) + rng.uniform(-0.3, 0.3))
        width = float(np.clip(width, 3.2, 8.))
        height = float(np.clip(_lerp(r.aperture_height, t) + rng.uniform(-0.3, 0.3), 3.2, 5.5))
        room = (float(round(_lerp(r.room_x, rng.uniform(0, 1)), 1)), float(round(_lerp(r.room_y, rng.uniform(0, 1)), 1)),
                float(round(_lerp(r.room_z, rng.uniform(0, 1)), 1)))
        if walls:
            room = (max(room[0], 8. + 2.5 * (walls + 1) + 2.), room[1], room[2])
        branch = 0
        if walls >= 2 and rng.random() < _lerp(r.branch_chance, t):
            branch = int(rng.integers(1, min(2, walls - 1) + 1))
        extra = int(round(_lerp(r.extra_obstacles, t) * rng.uniform(0.7, 1.3)))
        count = int(min(256, 4 * (walls + branch) + max(0, extra)))
        return dict(name='random', room_size=room, obstacle_count=count, wall_count=walls, aperture_width=width,
                    aperture_height=height, route_clearance=CLEARANCE, minimum_separation=min(14., room[0] - 4.),
                    branch_count=branch)

    def sample(self, difficulty, rng):
        for _ in range(self.max_tries):
            try:
                profile = MapProfile(**self._candidate(difficulty, rng))
            except ValueError:
                continue
            if self.mode == 'train' and in_heldout_b(profile):
                continue
            if self.mode == 'heldout_b' and not in_heldout_b(profile):
                continue
            return profile
        raise RuntimeError('Could not draw a valid profile')


class DifficultyController:
    """Moves the difficulty scalar up after a high recent success rate and down after a low one."""
    def __init__(self, initial=0.2, window=64, up=0.7, down=0.3, step=0.05, low=0., high=1.):
        if not 0. <= low <= initial <= high <= 1. or not 0. < down < up < 1.:
            raise ValueError('Invalid controller settings')
        self.difficulty, self.window, self.up, self.down = initial, window, up, down
        self.step, self.low, self.high, self.outcomes, self.history = step, low, high, [], []

    def update(self, success):
        self.outcomes.append(bool(success))
        if len(self.outcomes) >= self.window:
            rate = float(np.mean(self.outcomes))
            if rate >= self.up:
                self.difficulty = min(self.high, self.difficulty + self.step)
            elif rate <= self.down:
                self.difficulty = max(self.low, self.difficulty - self.step)
            self.history.append((self.difficulty, rate))
            self.outcomes = []


class RandomProfileWorld(FlightWorld):
    """FlightWorld that draws a new profile at every reset. Shares one controller across workers if given one."""
    def __init__(self, *args, sampler=None, controller=None, **kwargs):
        self.profile_sampler = sampler or ProfileSampler()
        self.controller = controller or DifficultyController()
        self.current_profile = None
        super().__init__(*args, **kwargs)

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        for attempt in range(8):
            self.map_profile = self.profile_sampler.sample(self.controller.difficulty, self.rng)
            self.room = np.array(self.map_profile.room_size, dtype=float)
            try:
                observation, info = super().reset(seed=None, options=options)
                break
            except RuntimeError:  # the generator could not fill the layout for this draw
                continue
        else:
            raise RuntimeError('Could not generate a layout from the sampled profiles')
        self.current_profile = self.map_profile
        info['profile'] = self.map_profile.to_dict()
        info['difficulty'] = self.controller.difficulty
        return observation, info

    def step(self, action, observe=True):
        result = super().step(action, observe)
        info = result[4]
        if info['terminated'] or info['truncated']:
            self.controller.update(info['success'])
        return result
