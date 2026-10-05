"""Describe sampled planner execution from saved traces, without running a flight."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def vector(value, name):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f'{name} must be a finite three-coordinate vector')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in value):
        raise ValueError(f'{name} must be a finite three-coordinate vector')
    return value


def summarize(rows, seed, search_cap=12000):
    """Count sampled indicators; reversals are not a causal route diagnosis."""
    if isinstance(search_cap, bool) or not isinstance(search_cap, int) or search_cap <= 0:
        raise ValueError('Search cap must be a positive integer')
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError('Trace must be a list of records')
    selected = [row for row in rows if row.get('seed') == seed]
    if len(selected) < 2:
        raise ValueError('Requested room needs at least two recorded samples')
    previous = -1
    for row in selected:
        step = row.get('step')
        if isinstance(step, bool) or not isinstance(step, int) or step <= previous:
            raise ValueError('Room steps must be nonnegative and strictly increasing')
        previous = step
        vector(row.get('position'), 'position')
        controller = row.get('controller')
        if not isinstance(controller, dict):
            raise ValueError('Missing controller diagnostics')
        if 'target_delta_global' in controller:
            vector(controller['target_delta_global'], 'target_delta_global')
        for name in ('actual_speed', 'estimated_pose_error', 'expanded'):
            if name in controller:
                value = controller[name]
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                    raise ValueError(f'{name} must be finite and nonnegative')
        for name in ('found', 'momentum_guard'):
            if name in controller and not isinstance(controller[name], bool):
                raise ValueError(f'{name} must be Boolean')

    def phase(samples):
        diagnostics = [row['controller'] for row in samples]
        reversals = eligible = 0
        for first, second in zip(diagnostics, diagnostics[1:]):
            a, b = first.get('target_delta_global'), second.get('target_delta_global')
            if a is None or b is None or sum(v*v for v in a) <= 1e-12 or sum(v*v for v in b) <= 1e-12:
                continue
            eligible += 1
            reversals += sum(x*y for x, y in zip(a, b)) < 0
        speeds = [c['actual_speed'] for c in diagnostics if 'actual_speed' in c]
        errors = [c['estimated_pose_error'] for c in diagnostics if 'estimated_pose_error' in c]
        spans = [max(row['position'][i] for row in samples)-min(row['position'][i] for row in samples) for i in range(3)]
        return dict(samples=len(samples), first_step=samples[0]['step'], last_step=samples[-1]['step'],
            found_samples=sum(c.get('found', False) for c in diagnostics),
            found_observed_samples=sum('found' in c for c in diagnostics),
            momentum_guard_samples=sum(c.get('momentum_guard', False) for c in diagnostics),
            momentum_guard_observed_samples=sum('momentum_guard' in c for c in diagnostics),
            search_cap_samples=sum(c.get('expanded', 0) >= search_cap for c in diagnostics),
            search_observed_samples=sum('expanded' in c for c in diagnostics),
            reference_reversals_over_90_degrees=reversals, eligible_reference_pairs=eligible,
            sampled_speed_range=[min(speeds), max(speeds)] if speeds else None,
            maximum_estimated_pose_error=max(errors) if errors else None, position_span=spans)

    strides = [b['step']-a['step'] for a, b in zip(selected, selected[1:])]
    return dict(seed=seed, search_cap=search_cap, sampled_step_stride_range=[min(strides), max(strides)],
        full=phase(selected), second_half=phase(selected[len(selected)//2:]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--search-cap', type=int, default=12000)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve() == args.trace.resolve():
        parser.error('Output must not overwrite the input trace')
    raw = args.trace.read_bytes()
    report = dict(kind='offline-sampled-execution-diagnostics', trace_sha256=hashlib.sha256(raw).hexdigest(),
        new_physical_transitions=0, optimizer_updates=0, reserved_test_access=False,
        limitations='Sampled indicators do not establish cause, route optimality, or behavior between samples.',
        room=summarize(json.loads(raw), args.seed, args.search_cap))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
