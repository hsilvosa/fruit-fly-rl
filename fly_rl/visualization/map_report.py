"""Inspect procedural geometry without loading a brain or evaluating a policy."""
import json
from pathlib import Path
import numpy as np
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.map_profiles import PROFILES, difficulty_metrics
from fly_rl.training.suites import layout_hash, geometry_hash


def map_report(output, profiles=('open', 'passages', 'large', 'maze'), seed=10, count=4, figure=None):
    if type(count) is not int or not 1 <= count <= 32 or type(seed) is not int or not 0 <= seed < 2**32-count+1:
        raise ValueError('Use 1 to 32 valid consecutive preview seeds')
    if not profiles or len(profiles) > 4:
        raise ValueError('Inspect one to four profiles')
    rows, examples = [], []
    for profile in profiles:
        for index in range(count):
            world = FlightWorld(seed+index, 'dense', map_profile=profile)
            rows.append({'seed': seed+index, 'configuration': world.map_profile.to_dict() if world.map_profile else None,
                         'layout_sha256': layout_hash(world), 'geometry_sha256': geometry_hash(world),
                         'metrics': difficulty_metrics(world)})
            if index == 0:
                examples.append(world)
    if figure:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        fig = plt.figure(figsize=(14, 10), constrained_layout=True)
        for i, world in enumerate(examples):
            ax = fig.add_subplot(2, 2, i+1, projection='3d')
            for low, high in world.obstacles:
                corners = np.array([[x, y, z] for x in [low[0], high[0]] for y in [low[1], high[1]] for z in [low[2], high[2]]])
                faces = [corners[list(q)] for q in [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]]
                ax.add_collection3d(Poly3DCollection(faces, facecolor='#48708b', edgecolor='#24465c', linewidth=.25, alpha=.20))
            route = np.asarray(world.reference_route)
            ax.plot(*route.T, color='#bd6300', linewidth=2, label='Hidden geometric certificate')
            for branch in getattr(world,'branch_routes',[]):
                ax.plot(*np.asarray(branch).T,color='#944999',linewidth=1.3)
            ax.scatter(*world.position, color='#245db0', s=35, label='Start')
            ax.scatter(*world.target, color='#168254', marker='*', s=90, label='Target')
            ax.set(xlim=(0, world.room[0]), ylim=(0, world.room[1]), zlim=(0, world.room[2]), xlabel='X', ylabel='Y', zlabel='Altitude')
            ax.set_box_aspect(world.room)
            metrics = difficulty_metrics(world)
            ax.set_title(f"{metrics['profile']} | {len(world.obstacles)} boxes\n{metrics['certified_route_length']:.1f} units along certificate; {metrics['episode_seconds']:.1f}s limit", fontsize=10)
            ax.view_init(elev=25, azim=-58)
            if i == 0:
                ax.legend(loc='upper left', fontsize=7)
        fig.suptitle(f'Procedural map profiles | preview seed {seed}\nGeometry only: route hidden from policy; no navigation performance measured', fontsize=13)
        figure = Path(figure)
        figure.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(figure, dpi=150)
        plt.close(fig)
    result = {'kind': 'map-geometry-preview', 'training_invoked': False, 'policy_evaluated': False,
              'rows': rows, 'figure': str(figure) if figure else None,
              'limitations': 'Certificate is feasible geometry, not an optimal or dynamically validated route. Grid occupancy is approximate.'}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result
