"""Summarize saved planner traces without recomputing sensors, brain, or actions."""
import argparse
import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def summarize(source, output, seeds=None):
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    trace_file = source/'trace.json'
    if not trace_file.exists():
        trace_file = source/'development-trace.json'
    rows = json.loads(trace_file.read_text(encoding='utf-8'))
    if seeds is None:
        seeds = sorted({row['seed'] for row in rows})
    if not seeds or len(seeds) > 16 or len(set(seeds)) != len(seeds):
        raise ValueError('Select one to sixteen distinct recorded seeds')
    for seed in seeds:
        samples = [row for row in rows if row['seed'] == seed]
        if not samples:
            raise ValueError(f'Missing diagnostic seed {seed}')
        positions = np.asarray([row['position'] for row in samples])
        ticks = np.asarray([row['step'] for row in samples])
        if positions.shape != (len(samples), 3) or not np.isfinite(positions).all():
            raise ValueError('Recorded positions must be finite three-dimensional vectors')
        if (ticks < 0).any() or (np.diff(ticks) <= 0).any():
            raise ValueError('Recorded steps must be nonnegative and strictly increasing')
    summaries = []
    fig, axes = plt.subplots(len(seeds), 3, figsize=(15, max(4, 3.7*len(seeds))), constrained_layout=True, squeeze=False)
    for index, seed in enumerate(seeds):
        samples = [row for row in rows if row['seed'] == seed]
        if not samples:
            raise ValueError(f'Missing diagnostic seed {seed}')
        positions = np.array([row['position'] for row in samples])
        ticks = np.array([row['step'] for row in samples])
        if positions.shape != (len(samples), 3) or not np.isfinite(positions).all():
            raise ValueError('Recorded positions must be finite three-dimensional vectors')
        if (ticks < 0).any() or (np.diff(ticks) <= 0).any():
            raise ValueError('Recorded steps must be nonnegative and strictly increasing')
        debug = [row['controller'] for row in samples]
        expanded = np.array([row['expanded'] for row in debug])
        speed = np.array([row.get('requested_speed', np.nan) for row in debug])
        delta = np.array([row.get('target_delta_global', [np.nan]*3) for row in debug])
        lengths = np.linalg.norm(delta, axis=1)
        unit = delta/np.maximum(lengths[:, None], 1e-8)
        turn = np.degrees(np.arccos(np.clip((unit[:-1]*unit[1:]).sum(1), -1, 1)))
        summary = dict(seed=seed, samples=len(samples),
            missing_route_reference_samples=int((~np.isfinite(delta).all(axis=1)).sum()),
            sampled_path_length=float(np.linalg.norm(np.diff(positions, axis=0), axis=1).sum()),
            capped_search_samples=int((expanded >= 12000).sum()),
            found_route_samples=sum(row['found'] for row in debug),
            reused_route_samples=sum(row.get('plan_reused', False) for row in debug),
            found_search_samples=sum(row['found'] and not row.get('plan_reused', False) for row in debug),
            momentum_guard_samples=sum(row.get('momentum_guard', False) for row in debug),
            sampled_stride_min=int(np.diff(ticks).min()) if len(ticks) > 1 else None,
            sampled_stride_max=int(np.diff(ticks).max()) if len(ticks) > 1 else None,
            tight_samples=sum(row.get('tight', False) for row in debug),
            low_requested_speed_samples=int((speed < .05).sum()),
            reference_reversals_over_90_degrees=int((turn > 90).sum()))
        if 'goal_cost' in debug[0]:
            summary.update(blocked_goal_samples=sum(row['goal_cost'] is None for row in debug),
                solid_goal_samples=sum(row['goal_evidence'] >= 2 for row in debug),
                max_estimated_pose_error=max(row['estimated_pose_error'] for row in debug),
                max_estimated_yaw_error=max(abs(row['estimated_yaw_error']) for row in debug))
        summaries.append(summary)
        axes[index, 0].plot(positions[:, 0], positions[:, 1], color='#2563eb')
        axes[index, 0].scatter(*positions[0, :2], label='Start', color='#2563eb')
        axes[index, 0].scatter(*positions[-1, :2], label='End', marker='x', color='#d97706')
        axes[index, 0].set(title=f'{seed}: sampled flight (XY)', xlabel='X', ylabel='Y', aspect='equal')
        axes[index, 0].legend(fontsize=8)
        axes[index, 1].plot(ticks*.05, expanded, color='#64748b', label='Search expansions')
        axes[index, 1].axhline(12000, color='#dc2626', linestyle='--', linewidth=1)
        axes[index, 1].set(title='Search effort', xlabel='Simulated seconds', ylabel='Expanded cells')
        axes[index, 2].plot(ticks*.05, speed, color='#059669', label='Requested speed')
        if any('effective_desired_speed' in row for row in debug):
            effective = np.array([row.get('effective_desired_speed', np.nan) for row in debug])
            axes[index, 2].plot(ticks*.05, effective, color='#2563eb', linewidth=1, label='Effective desired speed')
        axes[index, 2].plot(ticks*.05, lengths, color='#d97706', alpha=.6, label='Reference distance')
        axes[index, 2].set(title='Following and braking', xlabel='Simulated seconds', ylabel='Units / units per second')
        axes[index, 2].legend(fontsize=8)
    fig.suptitle('Recorded planner diagnostics | saved observations only; no independent generalization claim', fontsize=13)
    fig.savefig(output/'planner-diagnostics.png', dpi=120)
    plt.close(fig)
    snapshots = [source/f'map-{seed}.npz' for seed in seeds]
    if all(path.is_file() for path in snapshots):
        from matplotlib.colors import ListedColormap
        columns = min(4, len(seeds))
        rows_count = int(np.ceil(len(seeds)/columns))
        fig, axes = plt.subplots(rows_count, columns, figsize=(5*columns, 5*rows_count), constrained_layout=True, squeeze=False)
        for ax in axes.ravel()[len(seeds):]:
            ax.set_visible(False)
        for ax, path in zip(axes.ravel(), snapshots):
            with np.load(path) as snapshot:
                evidence = snapshot['evidence']
                origin, resolution = snapshot['origin'], float(snapshot['resolution'])
                goal, position = snapshot['goal'], snapshot['position']
                layer = int(np.floor((goal[2]-origin[2])/resolution))
                image = evidence[:, :, layer]
                classes = np.where(image >= 2, 2, np.where(image < 0, 0, 1))
                extent = [origin[0], origin[0]+evidence.shape[0]*resolution,
                          origin[1], origin[1]+evidence.shape[1]*resolution]
                ax.imshow(classes.T, origin='lower', extent=extent,
                          cmap=ListedColormap(['#dbeafe', '#f8fafc', '#475569']), vmin=0, vmax=2)
                route = snapshot['route']
                if len(route):
                    ax.plot(route[:, 0], route[:, 1], color='#059669', linewidth=1, label='Route projection')
                ax.scatter(*position[:2], color='#2563eb', label='Estimated position')
                ax.scatter(*goal[:2], marker='*', color='#d97706', label='Goal')
                ax.set(xlim=(min(position[0], goal[0])-12, max(position[0], goal[0])+12),
                       ylim=(min(position[1], goal[1])-12, max(position[1], goal[1])+12),
                       xlabel='Relative X', ylabel='Relative Y', title=path.stem)
                ax.legend(fontsize=7)
        title = ('Final observed-map slice at goal altitude. Blue: free; white: unknown; dark: solid. '
                 'Route is an XY projection across altitudes. Visited/frontier arrays were not recorded.')
        fig.suptitle(textwrap.fill(title, width=52*columns), fontsize=10)
        fig.savefig(output/'observed-map-slices.png', dpi=120)
        plt.close(fig)
    result = dict(kind='offline-planner-diagnosis', training_invoked=False,
                  evaluation_invoked=False, rooms=summaries,
                  limitations='Sampled path lengths underestimate full paths; reversals are reference changes, not proof of a cause.')
    (output/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seeds', type=int, nargs='+', help='Optional subset of recorded room seeds')
    args = parser.parse_args()
    summarize(args.source, args.output, args.seeds)
