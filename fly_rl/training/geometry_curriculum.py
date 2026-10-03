"""Training-only map mixtures scheduled by transitions, never by test outcomes."""
import numpy as np
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import resolve_profile

VERSION = 'geometry-v1-three-stage-mixture'
PROTOCOL = {'version': VERSION, 'stage_starts': [0., 1/3, 2/3],
            'mixtures': [[.75, .20, .05], [.20, .60, .20], [.10, .20, .70]],
            'change_on': 'episode reset only', 'progress': 'global added training transitions',
            'validation_controls_schedule': False, 'reward_shaping': None}


class GeometrySchedule:
    def __init__(self, total, profiles, offset=0):
        if type(total) is not int or total <= 0 or type(offset) is not int or not 0 <= offset <= total:
            raise ValueError('Invalid geometry curriculum transition budget')
        self.profiles = [resolve_profile(p) for p in profiles]
        if len(self.profiles) != 3 or any(p is None for p in self.profiles) or len({p.name for p in self.profiles}) != 3:
            raise ValueError('Geometry curriculum needs three distinct frozen profiles')
        self.total, self.transitions, self.initial_offset = total, offset, offset
        self.resets = {p.name: 0 for p in self.profiles}
        self.steps = {p.name: 0 for p in self.profiles}
        self.outcomes = {p.name: {'success': 0, 'collision': 0, 'timeout': 0} for p in self.profiles}

    @property
    def stage(self):
        return min(2, (3*self.transitions)//self.total)

    def snapshot(self):
        return {'protocol': PROTOCOL, 'version': VERSION, 'total': self.total,
                'initial_offset': self.initial_offset, 'transitions': self.transitions,
                'stage': self.stage, 'mixture': PROTOCOL['mixtures'][self.stage],
                'profiles': [p.to_dict() for p in self.profiles],
                'resets_including_initialization': dict(self.resets),
                'transitions_by_profile': dict(self.steps),
                'episode_outcomes_by_profile': {k: dict(v) for k, v in self.outcomes.items()}}


class GeometryWorld(FlightWorld):
    def __init__(self, *args, schedule, **kwargs):
        self.schedule = schedule
        self.profile_rng = np.random.default_rng(0)
        if kwargs.get('mode') != 'dense' or not kwargs.get('layout_seeds'):
            raise ValueError('Geometry curriculum requires explicit dense training layouts')
        super().__init__(*args, **kwargs)

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.profile_rng = np.random.default_rng(int(seed)^0x6E04A1)
        stage = self.schedule.stage
        index = int(self.profile_rng.choice(3, p=PROTOCOL['mixtures'][stage]))
        self.map_profile = self.schedule.profiles[index]
        self.room = np.array(self.map_profile.room_size, dtype=float)
        observation, info = super().reset(seed, options)
        self.schedule.resets[self.map_profile.name] += 1
        info['curriculum'] = {'version': VERSION, 'stage': stage, 'profile': self.map_profile.name,
                              'transition_offset': self.schedule.transitions}
        return observation, info

    def step(self, action):
        result = super().step(action)
        self.schedule.transitions += 1
        self.schedule.steps[self.map_profile.name] += 1
        if result[2] or result[3]:
            for key in self.schedule.outcomes[self.map_profile.name]:
                self.schedule.outcomes[self.map_profile.name][key] += bool(result[4].get(key if key != 'timeout' else 'truncated'))
        return result


def configure_geometry_curriculum(env, total, offset, seed, profiles):
    from fly_rl.simulation.sensors import SENSOR_V3
    if hasattr(env, 'curriculum') or hasattr(env, 'reward_shaping'):
        raise ValueError('Do not combine interventions in the geometry comparison')
    if any(w.mode != 'dense' or w.dynamics != 'coordinated' or w.sensor_version != SENSOR_V3 or not w.layout_seeds for w in env.worlds):
        raise ValueError('Geometry curriculum requires v3 coordinated dense training layouts')
    schedule = GeometrySchedule(total, profiles, offset)
    if env.map_profile is None or env.map_profile != schedule.profiles[-1]:
        raise ValueError('Last curriculum profile must be the declared evaluation target')
    env.worlds = [GeometryWorld(seed=seed+i, mode=w.mode, layout_seeds=w.layout_seeds,
                  dynamics=w.dynamics, sensor_version=w.sensor_version, map_profile=env.map_profile,
                  schedule=schedule) for i, w in enumerate(env.worlds)]
    env.curriculum = schedule
    return schedule
