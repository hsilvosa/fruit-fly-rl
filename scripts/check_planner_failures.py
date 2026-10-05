"""Bounded diagnostics on reused v55 failures; no optimization or reserved tests."""
from fly_rl.atomic_io import replace_file
from fly_rl.navigation.versions import legacy_version, public_version, PUBLIC_VERSIONS
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import numpy as np


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    replace_file(temporary, path)


def validate_request(seeds, cap, kind):
    if not isinstance(seeds, list) or not 1 <= len(seeds) <= 16:
        raise ValueError('Use one to sixteen contiguous integer room seeds')
    if any(type(seed) is not int or seed < 0 for seed in seeds):
        raise ValueError('Room seeds must be nonnegative integers')
    if seeds != list(range(seeds[0], seeds[0]+len(seeds))):
        raise ValueError('Room seeds must be contiguous, ordered, and distinct')
    if kind not in ['reused-failure-diagnostic', 'frozen-prospective-development']:
        raise ValueError('Unsupported verification kind')
    limit = 12000 if kind == 'reused-failure-diagnostic' else 81920
    if type(cap) is not int or not len(seeds) <= cap <= limit or cap % len(seeds):
        raise ValueError('Physical cap exceeds this protocol or is not batch divisible')


def check(output, version, cap, seeds=None, kind='reused-failure-diagnostic',
          deadline=None, frozen_sources=None, protocol_sha256=None):
    version = legacy_version(version)
    seeds = [8500011, 8500012, 8500013] if seeds is None else seeds
    validate_request(seeds, cap, kind)
    batch = len(seeds)
    import torch
    from fly_rl.training.learning import BrainEnv
    from fly_rl.simulation.sensors import SENSOR_V6
    from fly_rl.connectome.innovation import MOTION_STABLE_READOUT
    from fly_rl.navigation.observed_map import ObservedMapController
    readout_version = MOTION_STABLE_READOUT
    if version == 'v65':
        from fly_rl.navigation.dual_safety import DualSafetyController, READOUT_VERSION
        controller_type = DualSafetyController
        readout_version = READOUT_VERSION
    elif version == 'v64':
        from fly_rl.navigation.momentum_guard import MomentumGuardController, READOUT_VERSION
        controller_type = MomentumGuardController
        readout_version = READOUT_VERSION
    elif version == 'v63':
        from fly_rl.navigation.ray_consistent import RayConsistentController, READOUT_VERSION
        controller_type = RayConsistentController
        readout_version = READOUT_VERSION
    elif version == 'v62':
        from fly_rl.navigation.persistent_route import PersistentRouteController, READOUT_VERSION
        controller_type = PersistentRouteController
        readout_version = READOUT_VERSION
    elif version == 'v61':
        from fly_rl.navigation.distance_stable import DistanceStableController, READOUT_VERSION
        controller_type = DistanceStableController
        readout_version = READOUT_VERSION
    elif version == 'v60':
        from fly_rl.navigation.adaptive_margin import AdaptiveMarginController
        controller_type = AdaptiveMarginController
    elif version == 'v59':
        from fly_rl.navigation.speed_margin import SpeedMarginController
        controller_type = SpeedMarginController
    elif version == 'v58':
        from fly_rl.navigation.free_margin import FreeMarginController
        controller_type = FreeMarginController
    elif version == 'v57':
        from fly_rl.navigation.cruise import CruiseController
        controller_type = CruiseController
    elif version == 'v56':
        from fly_rl.navigation.goal_margin import GoalMarginController
        controller_type = GoalMarginController
    else:
        controller_type = ObservedMapController
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    protected = {str(p): digest(p) for p in Path('runs').glob('*policy.*')}
    for name in ['observed_map', 'goal_margin', 'cruise', 'free_margin', 'speed_margin', 'adaptive_margin', 'distance_stable', 'persistent_route', 'ray_consistent', 'momentum_guard']:
        path = f'fly_rl/navigation/{name}.py'
        protected[path] = digest(path)
    state = dict(status='running', controller=version, controller_version=public_version(version), kind=kind,
                 seeds=seeds, physical_cap=cap, protocol_sha256=protocol_sha256, readout_version=readout_version,
                 physical_transitions=0, added_training_transitions=0, optimizer_updates=0,
                 reserved_test_evaluated=False, started_utc=datetime.now(timezone.utc).isoformat(),
                 protected_before=protected, episodes=[])
    import inspect
    source_paths = [Path(__file__)] + [Path(inspect.getfile(kind))
        for kind in controller_type.__mro__ if kind is not object]
    state['source_hashes'] = {str(p): digest(p) for p in source_paths}
    save(output/'status.json', state)
    env = None
    trace = []
    start = time.perf_counter()
    try:
        torch.set_num_threads(4)
        env = BrainEnv('data', batch, 'cuda', seed=seeds[0], mode='dense', dynamics='coordinated',
                       sensor_version=SENSOR_V6, map_profile='large', history_frames=8,
                       history_stride=8, readout_version=readout_version, sensor_backend='torch-cuda')
        for brain_type in type(env.brain).__mro__:
            if brain_type is not object:
                path = Path(inspect.getfile(brain_type))
                state['source_hashes'][str(path)] = digest(path)
        env.seed(seeds[0])
        features = env.reset()
        controllers = [controller_type() for _ in seeds]
        active = np.ones(batch, bool)
        initial = [(w.position.copy(), w.yaw) for w in env.worlds]
        previous = [w.position.copy() for w in env.worlds]
        flown = np.zeros(batch)
        from fly_rl.recordings.recording import serializable
        layouts = [w.snapshot() for w in env.worlds]
        save(output/'initial-layouts.json', json.loads(json.dumps(layouts, default=serializable)))
        layout_hashes = [hashlib.sha256(json.dumps(layout, sort_keys=True, default=serializable).encode()).hexdigest()
                         for layout in layouts]
        torch.cuda.reset_peak_memory_stats()
        state.update(graph_neurons=env.brain.n, graph_edges=env.brain.audit['edges'],
                     feature_count=env.feature_count, sensor_count=env.brain.sensor_count,
                     brain_fingerprint=env.brain.fingerprint, graph_data_fingerprint=env.brain.audit['fingerprint'],
                     layout_hashes=layout_hashes)
        stopped_for_deadline = False
        for step in range(cap//batch):
            if deadline is not None and datetime.now(timezone.utc) >= deadline:
                stopped_for_deadline = True
                break
            actions = np.zeros((batch, 4), np.float32)
            for i in np.flatnonzero(active):
                c = controllers[i]
                actions[i] = c.action(features[i])
                if step % 20 == 0:
                    cell = tuple(c.cells(c.initial_goal))
                    pose, yaw = initial[i]
                    angle = env.worlds[i].yaw-yaw
                    rotation = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                                         [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
                    actual = (env.worlds[i].position-pose) @ rotation
                    actual[2] += pose[2]
                    debug = dict(c.debug)
                    debug.update(goal_cost=float(c.cost[cell]) if np.isfinite(c.cost[cell]) else None,
                                 goal_evidence=int(c.evidence[cell]),
                                 estimated_pose_error=float(np.linalg.norm(c.position-actual)),
                                 estimated_yaw_error=float((c.yaw-angle+np.pi)%(2*np.pi)-np.pi))
                    trace.append(dict(seed=seeds[i], step=step,
                                      position=env.worlds[i].position.tolist(), controller=debug))
            features, _, done, infos = env.step(actions)
            state['physical_transitions'] += batch
            for i in np.flatnonzero(active):
                position = infos[i]['transition_state']['position']
                flown[i] += np.linalg.norm(position-previous[i])
                previous[i] = position.copy()
            for i in np.flatnonzero(active & done):
                info = infos[i]
                state['episodes'].append(dict(seed=seeds[i], steps=step+1, flown_distance=float(flown[i]),
                    success=bool(info['success']), collision=bool(info['collision']),
                    timeout=bool(info['truncated']), distance_end=float(info['distance'])))
                c = controllers[i]
                np.savez_compressed(output/f'map-{seeds[i]}.npz', evidence=c.evidence,
                                    position=c.position, goal=c.initial_goal, origin=c.origin,
                                    route=np.asarray(c.route), resolution=c.res)
                active[i] = False
            if step % 100 == 0:
                state['last_step'] = step
                save(output/'status.json', state)
            if not active.any():
                break
        state.update(status='paused_deadline' if stopped_for_deadline else
                     'budget_exhausted' if active.any() else 'completed',
                     incomplete_episodes=int(active.sum()),
                     peak_vram_gb=torch.cuda.max_memory_allocated()/2**30)
    except Exception as error:
        state.update(status='failed', error=str(error))
        raise
    finally:
        if env is not None:
            env.close()
        state.update(elapsed_seconds=time.perf_counter()-start,
                     finished_utc=datetime.now(timezone.utc).isoformat(),
                     protected_after={p: digest(p) for p in protected})
        state['protected_unchanged'] = state['protected_before'] == state['protected_after']
        if frozen_sources is not None:
            state['frozen_sources_before'] = frozen_sources
            state['frozen_sources_after'] = {path: digest(path) for path in frozen_sources}
            state['sources_unchanged'] = frozen_sources == state['frozen_sources_after']
            if not state['sources_unchanged']:
                state.update(status='failed', error='Frozen sources changed during verification')
        save(output/'trace.json', trace)
        save(output/'status.json', state)
    print(json.dumps(state, indent=2))
    return state


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--controller', type=public_version, choices=PUBLIC_VERSIONS, default='planner-1.0', help='Public controller revision; historical aliases remain accepted')
    parser.add_argument('--cap', type=int, default=12000)
    args = parser.parse_args()
    if not 3 <= args.cap <= 12000 or args.cap % 3:
        parser.error('Physical cap must be a multiple of three, at most 12000')
    check(args.output, args.controller, args.cap)
