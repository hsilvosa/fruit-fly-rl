"""Bounded diagnostics on reused v55 failures; no optimization or reserved tests."""
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
    temporary.replace(path)


def check(output, version, cap):
    import torch
    from fly_rl.training.learning import BrainEnv
    from fly_rl.simulation.sensors import SENSOR_V6
    from fly_rl.connectome.innovation import MOTION_STABLE_READOUT
    from fly_rl.navigation.observed_map import ObservedMapController
    if version == 'v60':
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
    for name in ['observed_map', 'goal_margin', 'cruise', 'free_margin', 'speed_margin']:
        path = f'fly_rl/navigation/{name}.py'
        protected[path] = digest(path)
    state = dict(status='running', controller=version, kind='reused-failure-diagnostic',
                 seeds=[8500011, 8500012, 8500013], physical_cap=cap,
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
        env = BrainEnv('data', 3, 'cuda', seed=8500011, mode='dense', dynamics='coordinated',
                       sensor_version=SENSOR_V6, map_profile='large', history_frames=8,
                       history_stride=8, readout_version=MOTION_STABLE_READOUT, sensor_backend='torch-cuda')
        env.seed(8500011)
        features = env.reset()
        controllers = [controller_type() for _ in range(3)]
        active = np.ones(3, bool)
        initial = [(w.position.copy(), w.yaw) for w in env.worlds]
        state.update(graph_neurons=env.brain.n, graph_edges=env.brain.audit['edges'])
        for step in range(cap//3):
            actions = np.zeros((3, 4), np.float32)
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
                    trace.append(dict(seed=8500011+int(i), step=step,
                                      position=env.worlds[i].position.tolist(), controller=debug))
            features, _, done, infos = env.step(actions)
            state['physical_transitions'] += 3
            for i in np.flatnonzero(active & done):
                info = infos[i]
                state['episodes'].append(dict(seed=8500011+int(i), steps=step+1,
                    success=bool(info['success']), collision=bool(info['collision']),
                    timeout=bool(info['truncated']), distance_end=float(info['distance'])))
                c = controllers[i]
                np.savez_compressed(output/f'map-{8500011+int(i)}.npz', evidence=c.evidence,
                                    position=c.position, goal=c.initial_goal, origin=c.origin,
                                    route=np.asarray(c.route), resolution=c.res)
                active[i] = False
            if step % 100 == 0:
                state['last_step'] = step
                save(output/'status.json', state)
            if not active.any():
                break
        state.update(status='completed', incomplete_episodes=int(active.sum()))
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
        save(output/'trace.json', trace)
        save(output/'status.json', state)
    print(json.dumps(state, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--controller', choices=['v55', 'v56', 'v57', 'v58', 'v59', 'v60'], default='v55')
    parser.add_argument('--cap', type=int, default=12000)
    args = parser.parse_args()
    if not 3 <= args.cap <= 12000 or args.cap % 3:
        parser.error('Physical cap must be a multiple of three, at most 12000')
    check(args.output, args.controller, args.cap)
