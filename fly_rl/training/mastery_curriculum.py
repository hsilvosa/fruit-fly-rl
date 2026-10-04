"""Passage progression gated by withheld training-practice inference, not time."""
import copy
import numpy as np
from fly_rl.simulation.map_profiles import resolve_profile
from fly_rl.training.geometry_curriculum import GeometrySchedule, GeometryWorld

VERSION = 'geometry-v2-practice-mastery'
PROTOCOL = {'version': VERSION, 'practice_layouts': 16, 'practice_batches': 2,
            'minimum_goals_per_batch': 7, 'episodes_per_batch': 8,
            'checks': 'after each training round; deterministic inference',
            'progress': 'both distinct practice batches pass at the current stage',
            'change_on': 'next episode reset', 'current_profile_probability': .8,
            'validation_controls_schedule': False, 'reward_shaping': None}


def practice_partition(suite):
    seeds = suite['splits']['train']['seeds']
    if len(seeds) < 32 or seeds != list(range(seeds[0], seeds[0]+len(seeds))):
        raise ValueError('Mastery requires at least 32 contiguous training seeds')
    # These layouts and all profile variants already have frozen suite hashes.
    return seeds[:-16], seeds[-16:]


def validate_mastery_profiles(profiles):
    profiles = [resolve_profile(p) for p in profiles]
    if len(profiles) < 2 or any(p is None for p in profiles) or len({p.name for p in profiles}) != len(profiles):
        raise ValueError('Mastery requires distinct ordered passage profiles')
    if profiles[0] != resolve_profile('gate-near'):
        raise ValueError('Mastery starts with the frozen gate-near profile')
    for a, b in zip(profiles, profiles[1:]):
        if any(x > y for x, y in zip(a.room_size, b.room_size)) or a.wall_count > b.wall_count or a.obstacle_count > b.obstacle_count:
            raise ValueError('Mastery profiles must increase gradually in size and structure')
    return profiles


class MasterySchedule(GeometrySchedule):
    def __init__(self, total, profiles, practice_seeds, offset=0, state=None, target_envs=0):
        self.profiles = validate_mastery_profiles(profiles)
        if type(target_envs) is not int or target_envs < 0:raise ValueError('Nonnegative target environment count required')
        self.target_envs=target_envs
        self.protocol=dict(PROTOCOL)
        if target_envs:self.protocol.update(target_envs=target_envs,target_exposure='dedicated environment lanes; final profile from initialization')
        if type(total) is not int or total <= 0 or type(offset) is not int or not 0 <= offset <= total:
            raise ValueError('Invalid mastery transition budget')
        self.practice_seeds = list(practice_seeds)
        if len(self.practice_seeds) != 16 or len(set(self.practice_seeds)) != 16 or any(type(s) is not int or not 0 <= s < 2**32 for s in self.practice_seeds):
            raise ValueError('Declare 16 distinct valid training-practice seeds')
        self.total, self.transitions, self.initial_offset = total, offset, offset
        self._stage = 0
        self.probes = []
        self.resets = {p.name: 0 for p in self.profiles}
        self.steps = {p.name: 0 for p in self.profiles}
        self.outcomes = {p.name: {'success': 0, 'collision': 0, 'timeout': 0} for p in self.profiles}
        if state is not None:
            if (state['version'] != VERSION or state['protocol'] != self.protocol or state['total'] != total
                    or state['transitions'] != offset or state['profiles'] != [p.to_dict() for p in self.profiles]
                    or state['practice_seeds'] != self.practice_seeds):
                raise ValueError('Mastery resume state does not match the frozen training protocol')
            self._stage = state['stage']
            if type(self._stage) is not int or not 0 <= self._stage < len(self.profiles):
                raise ValueError('Invalid restored mastery stage')
            self.probes = copy.deepcopy(state['practice_checks'])
            self.resets = dict(state['resets_including_initialization'])
            self.steps = dict(state['transitions_by_profile'])
            self.outcomes = copy.deepcopy(state['episode_outcomes_by_profile'])
        elif offset:
            raise ValueError('Resuming mastery requires its saved gate state')

    @property
    def stage(self):
        return self._stage

    def record_practice(self, batches):
        if len(batches) != 2:
            raise ValueError('Two independent practice batches required')
        goals, decisions = [], 0
        for i, result in enumerate(batches):
            rows = result['episodes']
            if (result.get('training_invoked') is not False
                    or result.get('map_profile') != self.profiles[self.stage].to_dict()
                    or sorted(r['seed'] for r in rows) != self.practice_seeds[i*8:(i+1)*8]):
                raise ValueError('Only declared current-stage training-practice inference can open the gate')
            if any(sum(bool(r[k]) for k in ('success', 'collision', 'timeout')) != 1 for r in rows):
                raise ValueError('Practice episodes need exactly one terminal outcome')
            goals.append(sum(bool(r['success']) for r in rows))
            decisions += sum(r['steps'] for r in rows)
        passed = all(n >= 7 for n in goals)
        self.probes.append({'stage': self.stage, 'transitions': self.transitions,
                            'goals_by_batch': goals, 'inference_decisions': decisions,
                            'passed': passed})
        if passed and self.stage < len(self.profiles)-1:
            self._stage += 1
        return passed

    def snapshot(self):
        return {'version': VERSION, 'protocol': dict(self.protocol), 'total': self.total,
                'initial_offset': self.initial_offset, 'transitions': self.transitions,
                'stage': self.stage, 'profiles': [p.to_dict() for p in self.profiles],
                'resets_including_initialization': dict(self.resets),
                'transitions_by_profile': dict(self.steps),
                'episode_outcomes_by_profile': copy.deepcopy(self.outcomes),
                'practice_seeds': self.practice_seeds.copy(),
                'practice_checks': copy.deepcopy(self.probes)}


class MasteryWorld(GeometryWorld):
    def __init__(self,*args,target_lane=False,**kwargs):
        self.target_lane=bool(target_lane)
        super().__init__(*args,**kwargs)

    def reset(self, seed=None, options=None):
        from fly_rl.simulation.world import FlightWorld
        if seed is not None:
            self.profile_rng = np.random.default_rng(int(seed)^0x6E04A1)
        stage = self.schedule.stage
        index = stage
        if self.target_lane:
            index=len(self.schedule.profiles)-1
        elif stage and self.profile_rng.random() >= .8:
            index = int(self.profile_rng.integers(stage))
        self.map_profile = self.schedule.profiles[index]
        self.room = np.array(self.map_profile.room_size, dtype=float)
        observation, info = FlightWorld.reset(self, seed, options)
        self.schedule.resets[self.map_profile.name] += 1
        info['curriculum'] = {'version': VERSION, 'stage': stage, 'profile': self.map_profile.name,
                              'transition_offset': self.schedule.transitions,
                              'dedicated_target_lane':self.target_lane}
        return observation, info


def configure_mastery(env, total, offset, seed, profiles, practice_seeds, state=None, target_envs=0):
    from fly_rl.simulation.sensors import SENSOR_V3,SENSOR_V4
    if hasattr(env, 'curriculum') or hasattr(env, 'reward_shaping'):
        raise ValueError('Do not combine mastery with another intervention')
    if any(w.mode != 'dense' or w.dynamics != 'coordinated' or w.sensor_version not in (SENSOR_V3,SENSOR_V4)
           or not w.layout_seeds or set(w.layout_seeds).intersection(practice_seeds) for w in env.worlds):
        raise ValueError('Mastery needs v3 coordinated training layouts disjoint from practice')
    if type(target_envs) is not int or not 0 <= target_envs < env.num_envs:
        raise ValueError('Target environments must leave at least one curriculum environment')
    schedule = MasterySchedule(total, profiles, practice_seeds, offset, state,target_envs)
    if env.map_profile != schedule.profiles[-1]:
        raise ValueError('Last mastery profile must match the evaluation target')
    env.worlds = [MasteryWorld(seed=seed+i, mode=w.mode, layout_seeds=w.layout_seeds,
                  dynamics=w.dynamics, sensor_version=w.sensor_version,
                  map_profile=env.map_profile, schedule=schedule,target_lane=i<target_envs) for i, w in enumerate(env.worlds)]
    env.curriculum = schedule
    return schedule
