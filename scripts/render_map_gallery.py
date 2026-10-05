"""Render documentation geometry without loading a brain, training, or policy evaluation."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

from fly_rl.simulation.world import FlightWorld


GROUPS = {
    'maps-small': [('Original small', None, 'obstacles'), ('gate-near', 'gate-near', 'dense'),
                   ('gate-long', 'gate-long', 'dense'), ('gate-two', 'gate-two', 'dense')],
    'maps-medium': [('dense-v3', 'dense-v3', 'dense'), ('open', 'open', 'dense'),
                    ('passages-wide', 'passages-wide', 'dense'), ('passages', 'passages', 'dense')],
    'maps-large': [('large-wide', 'large-wide', 'dense'), ('large-narrow', 'large-narrow', 'dense'),
                   ('large', 'large', 'dense'), ('maze', 'maze', 'dense')],
}


def render(output, seed=10):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    records = []
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    for filename, profiles in GROUPS.items():
        fig = plt.figure(figsize=(14, 10), facecolor='#f8fafc')
        for index, (label, profile, mode) in enumerate(profiles):
            world = FlightWorld(seed=seed, mode=mode, map_profile=profile, dynamics='coordinated')
            ax = fig.add_subplot(2, 2, index + 1, projection='3d', facecolor='#f8fafc')
            partitions = 4 * (world.map_profile.wall_count + world.map_profile.branch_count) if world.map_profile else 0
            for box_index, (low, high) in enumerate(world.obstacles):
                corners = np.array([[x, y, z] for x in [low[0], high[0]]
                                    for y in [low[1], high[1]] for z in [low[2], high[2]]])
                faces = [corners[list(q)] for q in [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                                                    (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]]
                color = '#5b748c' if box_index < partitions else '#9bb0c1'
                ax.add_collection3d(Poly3DCollection(faces, facecolor=color, edgecolor='#526a80',
                                                    linewidth=.3, alpha=.22))
            ax.scatter(*world.position, color='#2463eb', s=55, label='Start', depthshade=False)
            ax.scatter(*world.target, color='#d97706', marker='*', s=120, label='Goal', depthshade=False)
            ax.set(xlim=(0, world.room[0]), ylim=(0, world.room[1]), zlim=(0, world.room[2]),
                   xlabel='X', ylabel='Y', zlabel='Altitude')
            # Matplotlib normalizes its argument in place; preserve world geometry.
            ax.set_box_aspect(world.room.copy())
            ax.view_init(elev=28, azim=-58)
            dimensions = ' x '.join(f'{v:g}' for v in world.room)
            ax.set_title(f'{label}\n{dimensions} units | {len(world.obstacles)} collision boxes',
                         fontweight='bold', pad=8)
            ax.tick_params(labelsize=8)
            ax.legend(loc='upper left', fontsize=8, frameon=False)
            boxes = np.asarray(world.obstacles, dtype='<f8')
            records.append({'profile': label, 'seed': seed, 'room': world.room.tolist(),
                            'collision_boxes': len(world.obstacles),
                            'geometry_sha256': hashlib.sha256(boxes.tobytes()).hexdigest(),
                            'image': f'{filename}.png'})
            world.close()
        fig.suptitle(f'Procedural room geometry | preview seed {seed}', fontsize=17, fontweight='bold', y=.975)
        fig.text(.5, .025, 'Transparent obstacles expose openings. No flight trajectory or navigation score is shown.',
                 ha='center', fontsize=11, color='#475569')
        fig.subplots_adjust(left=.035, right=.96, bottom=.07, top=.88, wspace=.05, hspace=.24)
        fig.savefig(output / f'{filename}.png', dpi=125)
        plt.close(fig)
    result = {'kind': 'documentation-map-gallery', 'seed': seed, 'training_invoked': False,
              'policy_evaluated': False, 'brain_loaded': False, 'maps': records}
    (output / 'maps-manifest.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('docs/images'))
    parser.add_argument('--seed', type=int, default=10)
    args = parser.parse_args()
    render(args.output, args.seed)
    print(f'Rendered {sum(map(len, GROUPS.values()))} geometry previews in {args.output}. No training or evaluation.')
