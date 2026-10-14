"""Render a gallery of randomized training and held-out maps (top-down projection). Preview only, no flights."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl')
sys.path.insert(0, '.')
from fly_rl.simulation.random_profiles import ProfileSampler, DifficultyController, RandomProfileWorld

OUT = sys.argv[1] if len(sys.argv) > 1 else 'docs/images/random-profile-gallery.png'
panels = [('train', d) for d in (0.1, 0.4, 0.7, 1.0) for _ in range(2)] + [('heldout_b', 0.8)] * 4
fig, axes = plt.subplots(3, 4, figsize=(16, 11))
for ax, (index, (mode, d)) in zip(axes.ravel(), enumerate(panels)):
    world = RandomProfileWorld(seed=100 + index, mode='dense', dynamics='coordinated',
                               sampler=ProfileSampler(mode), controller=DifficultyController(initial=d, window=10 ** 9))
    world.reset(seed=100 + index)
    room = world.room
    ax.set_xlim(0, room[0]); ax.set_ylim(0, room[1]); ax.set_aspect('equal')
    for low, high in world.obstacles:
        ax.add_patch(Rectangle((low[0], low[1]), high[0] - low[0], high[1] - low[1], alpha=0.12, color='#335'))
    route = np.asarray(world.reference_route)
    ax.plot(route[:, 0], route[:, 1], color='#c60', lw=1.2)
    ax.plot(*world.position[:2], 'o', color='#17c', ms=8)
    ax.plot(*world.target[:2], '*', color='#e90', ms=13)
    p = world.map_profile
    ax.set_title(f"{'held out (B)' if mode == 'heldout_b' else 'train d=' + str(d)}: {p.room_size[0]:.0f}x{p.room_size[1]:.0f}x{p.room_size[2]:.0f}, "
                 f"{p.wall_count} walls, {p.aperture_width:.1f} m, {p.obstacle_count} boxes", fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
fig.suptitle('Randomized map samples, top-down view. Blue: start. Amber: goal. Orange line: certified reference route. Last four panels: level B held-out region', fontsize=11)
fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=110)
print('saved', OUT)
