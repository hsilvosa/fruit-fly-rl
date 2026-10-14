"""Generate the report figures used by README.md and the docs from the recorded result files and from the geometry code.
Output: docs/images/figures/*.png. Evaluation figures read the JSON summaries under runs/ (local, not versioned); map figures use only
the geometry code; the brain figure flies one episode of the retained policy with the real connectome (about two minutes on the GPU).
Usage: make_report_figures.py [maps] [results] [reservoir] [brain]   (default: all)"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

os.chdir('C:/Users/Usuario/Desktop/PORTFOLIO/fly-rl'); sys.path.insert(0, '.')
OUT = 'docs/images/figures'
os.makedirs(OUT, exist_ok=True)
what = set(sys.argv[1:]) or {'maps', 'results', 'reservoir', 'brain'}
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
RUNS = 'runs/training'


def load(path):
    return json.load(open(path))


def top_down(ax, world, title):
    room = world.room
    ax.set_xlim(0, room[0]); ax.set_ylim(0, room[1]); ax.set_aspect('equal')
    for low, high in world.obstacles:
        ax.add_patch(Rectangle((low[0], low[1]), high[0] - low[0], high[1] - low[1], alpha=0.16, color='#335'))
    route = world.reference_route
    if route is not None and len(route):
        route = np.asarray(route)
        ax.plot(route[:, 0], route[:, 1], color='#c60', lw=1.1)
    ax.plot(*world.position[:2], 'o', color='#17c', ms=7)
    ax.plot(*world.target[:2], '*', color='#e90', ms=12)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=9)


# ---------------------------------------------------------------- maps
if 'maps' in what:
    from fly_rl.simulation.world import FlightWorld
    from fly_rl.simulation.random_profiles import ProfileSampler, DifficultyController, RandomProfileWorld
    from fly_rl.simulation.architectural_transfer import ArchitecturalSceneWorld, all_situations
    from fly_rl.simulation.sensors import SENSOR_V6

    profiles = [('gate-two', 'gate-two'), ('passages-wide', 'passages-wide'), ('passages-mid', 'scripts/profiles/passages-mid.json'), ('passages', 'passages')]
    fig, axes = plt.subplots(2, 4, figsize=(16, 8.4))
    for col, (label, profile) in enumerate(profiles):
        for row, seed in enumerate((10, 11)):
            world = FlightWorld(seed=seed, mode='dense', map_profile=profile, dynamics='coordinated')
            top_down(axes[row, col], world, f'{label}, seed {seed}: {" x ".join(f"{v:g}" for v in world.room)}, {len(world.obstacles)} boxes')
    fig.suptitle('Partitioned-room profiles (top-down). Blue: start. Amber: goal. Orange: certified reference route. Same geometry code as training and evaluation', fontsize=11)
    fig.tight_layout(); fig.savefig(f'{OUT}/map-profiles-partitioned.png', dpi=110); plt.close(fig)

    fig, axes = plt.subplots(2, 4, figsize=(16, 8.4))
    for index, ax in enumerate(axes.ravel()):
        world = RandomProfileWorld(seed=950000 + index, mode='dense', dynamics='coordinated', sampler=ProfileSampler('heldout_b'),
                                   controller=DifficultyController(initial=0.8, window=10 ** 9))
        world.reset(seed=950000 + index)
        p = world.map_profile
        top_down(ax, world, f'seed {950000 + index}: {p.room_size[0]:.0f}x{p.room_size[1]:.0f}x{p.room_size[2]:.0f}, {p.wall_count} walls, opening {p.aperture_width:.1f} m')
    fig.suptitle('Level B held-out region (opening below 3.8 m with at least four partitions), development seeds 950000 to 950007', fontsize=11)
    fig.tight_layout(); fig.savefig(f'{OUT}/level-b-region-gallery.png', dpi=110); plt.close(fig)

    scenes = {}
    for scene, index, name in all_situations():
        scenes.setdefault(scene, []).append((index, name))
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    for ax, (scene, situations) in zip(axes.ravel(), scenes.items()):
        first = ArchitecturalSceneWorld(scene, situations[0][0], 900000, SENSOR_V6)
        first.reset(seed=900000)
        room = first.room
        ax.set_xlim(0, room[0]); ax.set_ylim(0, room[1]); ax.set_aspect('equal')
        for low, high in first.obstacles:
            ax.add_patch(Rectangle((low[0], low[1]), high[0] - low[0], high[1] - low[1], alpha=0.16, color='#335'))
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
        for k, (index, name) in enumerate(situations):
            route = np.asarray(first.scene.situations[index].route)
            ax.plot(route[:, 0], route[:, 1], color=colors[k], lw=1.4, label=name)
            ax.plot(*route[0][:2], 'o', color=colors[k], ms=5); ax.plot(*route[-1][:2], '*', color=colors[k], ms=10)
        ax.set_title(f'{scene} ({len(situations)} situations)', fontsize=10)
        ax.legend(fontsize=7, loc='upper right', frameon=False); ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle('Level C: the six synthetic architectural scenes and their 21 situations (top-down, one route per situation)', fontsize=11)
    fig.tight_layout(); fig.savefig(f'{OUT}/architectural-scenes-gallery.png', dpi=110); plt.close(fig)
    print('maps done', flush=True)

# ---------------------------------------------------------------- results
if 'results' in what:
    # budget curve: passages, deterministic, successes out of 64 (three experiments, three different fresh pools)
    b1 = load(f'{RUNS}/large-budget/seed801/summary.json')
    b2 = load(f'{RUNS}/large-budget-2m/seed801/summary.json')
    b3 = load(f'{RUNS}/large-budget-2m/b3-eval/summary.json')
    fig, ax = plt.subplots(figsize=(8.4, 5))
    ax.plot([98304, 294912, 589824, 1015808], [b1[f'stage{s}']['passages']['det']['successes'] for s in (3, 9, 18, 31)], 'o-', color='#888', label='B1: 1M run (pool 884000)')
    ax.plot([491520, 1015808, 1507328, 1998848], [b2[f'stage{s}']['passages']['det']['successes'] for s in (15, 31, 46, 61)], 's-', color='#17c', label='B2: 2M run (pool 885000)')
    ax.plot([1015808], [b2['b1_final_on_this_pool']['passages']['det']['successes']], 'D', color='#888', label='B1 final checkpoint on the B2 pool')
    for seed, marker in ((801, '^'), (851, 'v'), (901, 'P')):
        ax.plot([1507328, 1998848], [b3[f'seed{seed}-s46']['passages']['det']['successes'], b3[f'seed{seed}-s61']['passages']['det']['successes']], marker + '--', color='#d60', label=f'B3: seed {seed} (pool 886000)')
    ax.axhline(5, color='#555', ls=':', lw=1); ax.text(60000, 6.5, 'start checkpoint, 5/64', fontsize=8, color='#555')
    ax.axhline(52, color='#a00', ls=':', lw=1); ax.text(60000, 53.5, 'release gate, 52/64 (and at most 3 collisions)', fontsize=8, color='#a00')
    ax.set_xlabel('added training transitions'); ax.set_ylabel('passages successes out of 64 (deterministic)')
    ax.set_ylim(0, 60); ax.set_title('Training budget and the partitioned-room cell `passages`'); ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(0.0, 0.93))
    fig.tight_layout(); fig.savefig(f'{OUT}/budget-curve.png', dpi=120); plt.close(fig)

    # retained lineage against the fresh chain (real and edge-shuffled), passages, deterministic
    c11 = load(f'{RUNS}/connectome-control/c11-eval/summary.json')
    c12 = load(f'{RUNS}/connectome-control/c12-eval/summary.json')
    groups = [('retained\n2.88M', [b3[f'seed{s}-s61']['passages']['det']['successes'] for s in (801, 851, 901)], '#17c'),
              ('real, fresh\n2.88M', [c11[f'real{s}']['passages']['det']['successes'] for s in (1001, 1051)], '#d60'),
              ('shuffled, fresh\n2.88M', [c11[f'shuffled{s}']['passages']['det']['successes'] for s in (1001, 1051)], '#777'),
              ('real, fresh\n4.88M', [c12[f'real{s}']['passages']['det']['successes'] for s in (1001, 1051)], '#d60'),
              ('shuffled, fresh\n4.88M', [c12[f'shuffled{s}']['passages']['det']['successes'] for s in (1001, 1051)], '#777')]
    fig, ax = plt.subplots(figsize=(8.8, 5))
    for i, (label, values, color) in enumerate(groups):
        ax.bar(i, np.mean(values), color=color, alpha=0.45, width=0.6)
        ax.plot([i] * len(values), values, 'o', color='k', ms=5)
    ax.set_xticks(range(len(groups))); ax.set_xticklabels([g[0] for g in groups], fontsize=8)
    ax.set_ylabel('passages successes out of 64 (deterministic)'); ax.set_ylim(0, 50)
    ax.set_title('Real connectome against the edge-shuffled control (bars: mean, dots: seeds)\nretained and 2.88M rows: pool 886000; 4.88M rows: pool 888000', fontsize=10)
    fig.tight_layout(); fig.savefig(f'{OUT}/connectome-control.png', dpi=120); plt.close(fig)

    # four families against the gate
    lc = load(f'{RUNS}/large-budget-2m/b4-eval/summary.json')
    pr = load(f'{RUNS}/planner-reference/summary.json')
    fam = {
        'medium rooms\n(64 episodes)': [b3[f'seed{s}-s61']['medium']['det']['successes'] / 64 for s in (801, 851, 901)],
        'large rooms\n(32)': [pr['retained'][f'seed{s}']['large']['det']['successes'] / 32 for s in (801, 851, 901)],
        'mazes\n(32)': [pr['retained'][f'seed{s}']['maze']['det']['successes'] / 32 for s in (801, 851, 901)],
        'architectural,\nlevel C (168)': [lc[f'seed{s}']['levelC']['det']['successes'] / 168 for s in (801, 851, 901)],
    }
    fig, ax = plt.subplots(figsize=(8.4, 5))
    for i, (name, values) in enumerate(fam.items()):
        ax.bar(i, np.mean(values) * 100, color='#17c', alpha=0.5, width=0.55)
        ax.plot([i] * 3, [v * 100 for v in values], 'o', color='k', ms=5)
    ax.plot([3.32], [pr['planner_levelC']['success'] / 168 * 100], '*', color='#d60', ms=14, label='explicit planner reference (level C)')
    ax.axhline(81.25, color='#a00', ls='--', lw=1.2); ax.text(0.6, 83, 'release gate: 52/64 = 81.25% success and at most 3 collisions per 64', color='#a00', fontsize=8)
    ax.text(0, 66, 'collisions 5 to 11 of 64\n(gate: at most 3)', ha='center', fontsize=7.5, color='#222')
    ax.set_xticks(range(len(fam))); ax.set_xticklabels(list(fam), fontsize=9); ax.set_ylim(0, 100)
    ax.set_ylabel('success rate, deterministic (%)'); ax.legend(fontsize=8, loc='upper right')
    ax.set_title('Retained candidate (three seeds, stage 61) against the four-family release gate\nDevelopment pools; no family meets the gate (medium misses on collisions)', fontsize=10)
    fig.tight_layout(); fig.savefig(f'{OUT}/four-family-gate.png', dpi=120); plt.close(fig)
    print('results done', flush=True)

# ---------------------------------------------------------------- reservoir
if 'reservoir' in what:
    from scipy import sparse
    from fly_rl.connectome.shuffled import shuffle_targets
    real = sparse.load_npz('data/processed/brain.npz').tocsr()
    shuffled = shuffle_targets(real, 1)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    rin, sin = np.diff(real.indptr), np.diff(shuffled.indptr)
    rout = np.bincount(real.indices, minlength=real.shape[0]); sout = np.bincount(shuffled.indices, minlength=real.shape[0])
    bins = np.logspace(0, 4.1, 60)
    axes[0].hist(rin[rin > 0], bins=bins, alpha=0.55, label='real'); axes[0].hist(sin[sin > 0], bins=bins, alpha=0.55, label='edge-shuffled')
    axes[0].set_xscale('log'); axes[0].set_yscale('log'); axes[0].set_title('in-degree per neuron'); axes[0].legend(fontsize=8)
    axes[1].hist(rout[rout > 0], bins=bins, alpha=0.55, label='real'); axes[1].hist(sout[sout > 0], bins=bins, alpha=0.55, label='edge-shuffled')
    axes[1].set_xscale('log'); axes[1].set_yscale('log'); axes[1].set_title('out-degree per neuron')
    wb = np.logspace(-5.2, 0, 60)
    axes[2].hist(np.abs(real.data), bins=wb, alpha=0.55); axes[2].hist(np.abs(shuffled.data), bins=wb, alpha=0.55)
    axes[2].set_xscale('log'); axes[2].set_yscale('log'); axes[2].set_title('absolute edge weight')
    overlap = real.multiply(shuffled != 0).nnz if False else (real.astype(bool).multiply(shuffled.astype(bool))).nnz
    fig.suptitle(f'Real connectome against the edge-shuffled control: same degrees and weights, different wiring. '
                 f'{overlap / real.nnz * 100:.3f}% of the real edges also exist after the shuffle', fontsize=10)
    fig.tight_layout(); fig.savefig(f'{OUT}/shuffled-vs-real-reservoir.png', dpi=115); plt.close(fig)
    print('reservoir done; edges kept', overlap, 'of', real.nnz, flush=True)

# ---------------------------------------------------------------- brain
if 'brain' in what:
    import torch
    from fly_rl.training.learning import BrainEnv, load_model, checkpoint_sensor_version, checkpoint_readout, checkpoint_history
    from fly_rl.connectome.anatomy import load_anatomy, display_positions
    ck = f'{RUNS}/large-budget-2m/seed801/stage-61.zip'
    sv = checkpoint_sensor_version(ck)
    env = BrainEnv('data', 1, 'cuda', seed=886003, mode='dense', dynamics='coordinated', sensor_version=sv, map_profile=None,
                   readout_version=checkpoint_readout(ck), **checkpoint_history(ck))
    model = load_model(ck, env.brain, env, True)
    env.seed(886003); features = env.reset()
    world = env.worlds[0]
    anatomy = load_anatomy('data')
    pos = display_positions(anatomy['raw_positions']); idx = torch.as_tensor(anatomy['indices'], device=env.brain.device)
    trace, feats, snaps, activity = [world.position.copy()], [features[0].copy()], {}, []
    steps = 0
    while steps < world.episode_limit:
        action = model.predict(features, deterministic=True)[0]
        features, rewards, dones, infos = env.step(action)
        steps += 1
        trace.append(infos[0]['transition_state']['position'].copy())  # the world is already reset when the episode ends
        feats.append(features[0].copy())
        state = env.brain.state[:, 0]
        activity.append((float(state.abs().mean()), float((state.abs() > 0.5).float().mean())))
        if steps in (20, 90, 170):
            snaps[steps] = state[idx].abs().cpu().numpy()
        if dones[0]:
            break
    outcome = 'reached the goal' if infos[0].get('success') else 'collision' if infos[0].get('collision') else 'timeout'
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(2, 4, 1)
    room = world.room
    ax.set_xlim(0, room[0]); ax.set_ylim(0, room[1]); ax.set_aspect('equal')
    for low, high in world.obstacles:
        ax.add_patch(Rectangle((low[0], low[1]), high[0] - low[0], high[1] - low[1], alpha=0.16, color='#335'))
    tr = np.asarray(trace); ax.plot(tr[:, 0], tr[:, 1], color='#17c', lw=1.2)
    ax.plot(*tr[0][:2], 'o', color='#17c'); ax.plot(*world.target[:2], '*', color='#e90', ms=13)
    ax.set_title(f'medium room, retained policy, {steps} steps: {outcome}', fontsize=9); ax.set_xticks([]); ax.set_yticks([])
    for k, (step, values) in enumerate(snaps.items()):
        a = fig.add_subplot(2, 4, 2 + k)
        order = np.argsort(values)
        a.scatter(pos[order, 0], pos[order, 1], c=values[order], s=0.6, cmap='magma', vmin=0, vmax=max(0.5, float(np.percentile(values, 99.5))), rasterized=True)
        a.set_aspect('equal'); a.set_xticks([]); a.set_yticks([]); a.set_title(f'|activity| of 167k neurons at step {step} (soma positions, front projection)', fontsize=8)
    a = fig.add_subplot(2, 2, 3)
    a.imshow(np.asarray(feats).T, aspect='auto', cmap='coolwarm', vmin=-1, vmax=1); a.set_xlabel('step'); a.set_ylabel('pooled feature (256)')
    a.set_title('the 256 pooled reservoir features that the PPO policy reads', fontsize=9)
    a = fig.add_subplot(2, 2, 4)
    act = np.asarray(activity); a.plot(act[:, 0], label='mean |state|'); a.plot(act[:, 1], label='fraction of neurons with |state| > 0.5')
    a.set_xlabel('step'); a.legend(fontsize=8); a.set_title('population activity during the flight', fontsize=9)
    fig.suptitle('The fixed full connectome in the loop: one flight of the retained policy (stage 61, seed 801) in a medium room', fontsize=11)
    fig.tight_layout(); fig.savefig(f'{OUT}/brain-activity-example.png', dpi=110); plt.close(fig)
    print('brain done', steps, outcome, flush=True)
