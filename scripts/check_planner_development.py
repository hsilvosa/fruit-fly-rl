"""Prepare and run a frozen planner development comparison; never a final test."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from fly_rl.navigation.versions import legacy_version, public_version

try:
    from scripts.check_planner_failures import check, digest, save, validate_request
except ModuleNotFoundError:
    from check_planner_failures import check, digest, save, validate_request


def integers(value):
    if type(value) is int:
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from integers(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from integers(item)


ALLOWED_PAIRS = [('v55', 'v60'), ('v60', 'v61'), ('v60', 'v63'), ('v60', 'v64'), ('v61', 'v64'), ('v60', 'v65')]
READOUTS = dict(v55='neural-projection-motion-stable-visual005-v1',
    v60='neural-projection-motion-stable-visual005-v1',
    v61='neural-projection-distance-stable-speed005-v1',
    v63='neural-projection-distance-stable-speed005-v1',
    v64='neural-projection-distance-stable-speed005-v1',
    v65='neural-projection-dual-map005-distance-clean-v1')
FEATURE_WIDTHS = {arm: (5669 if arm == 'v65' else 3869) for arm in READOUTS}


def prepare(output, seed_start, deadline, baseline='v55', candidate='v60'):
    baseline, candidate = legacy_version(baseline), legacy_version(candidate)
    output = Path(output)
    if output.exists():
        raise FileExistsError('Use a new protocol filename')
    if (baseline, candidate) not in ALLOWED_PAIRS:
        raise ValueError('Unsupported frozen comparison')
    stop = datetime.fromisoformat(deadline)
    if stop.tzinfo is None or stop <= datetime.now(timezone.utc):
        raise ValueError('Deadline must be a future timezone-aware ISO timestamp')
    seeds = list(range(seed_start, seed_start+16))
    validate_request(seeds, 81920, 'frozen-prospective-development')
    inventory = set(Path('runs/suites').rglob('*.json'))
    inventory.update(Path('private').glob('*plan*.json'))
    inventory.update(Path('runs/training').rglob('suite.json'))
    inventory.update(Path('runs/diagnostics').rglob('status.json'))
    checked = {}
    for path in sorted(inventory):
        prior = json.loads(path.read_text(encoding='utf-8'))
        if set(seeds).intersection(integers(prior)):
            raise ValueError(f'Seed overlap with retained protocol or records: {path}')
        checked[path.as_posix()] = digest(path)
    sources = set()
    for folder in ['fly_rl/navigation', 'fly_rl/connectome', 'fly_rl/simulation']:
        sources.update(Path(folder).glob('*.py'))
    sources.update(Path(path) for path in ['fly_rl/atomic_io.py', 'fly_rl/training/temporal_policy.py', 'fly_rl/training/learning.py',
        'scripts/check_planner_failures.py', 'scripts/check_planner_development.py',
        'scripts/report_planner_development.py'])
    protocol = dict(schema=3, kind='frozen-prospective-development',
        created_utc=datetime.now(timezone.utc).isoformat(), deadline_utc=stop.isoformat(),
        arms=[baseline, candidate], readouts={arm: READOUTS[arm] for arm in [baseline, candidate]},
        controller_versions={arm: public_version(arm) for arm in [baseline, candidate]},
        feature_widths={arm: FEATURE_WIDTHS[arm] for arm in [baseline, candidate]}, sensor_count=3869,
        seeds=seeds, physical_cap_per_arm=81920,
        training_transitions=0, reserved_test_access=False,
        selection_rule='Report both frozen arms; do not retune either from this suite.',
        task='large', sources={p.as_posix(): digest(p) for p in sorted(sources)},
        aliases={p.as_posix(): digest(p) for p in sorted(Path('runs').glob('*policy.*'))},
        prior_inventory=checked)
    output.parent.mkdir(parents=True, exist_ok=True)
    save(output, protocol)
    return protocol


def validate(protocol):
    if protocol.get('schema') not in [1, 2, 3] or protocol.get('kind') != 'frozen-prospective-development':
        raise ValueError('Unsupported protocol')
    if tuple(protocol.get('arms', [])) not in ALLOWED_PAIRS or protocol.get('task') != 'large':
        raise ValueError('Unsupported frozen arms or task')
    if 'controller_versions' in protocol and protocol['controller_versions'] != {arm: public_version(arm) for arm in protocol['arms']}:
        raise ValueError('Public controller names do not match the frozen aliases')
    if protocol['schema'] == 1 and protocol['arms'] != ['v55', 'v60']:
        raise ValueError('Readout comparisons require schema two')
    if protocol['schema'] >= 2 and protocol.get('readouts') != {arm: READOUTS[arm] for arm in protocol['arms']}:
        raise ValueError('Readout differences must be explicitly predeclared')
    if protocol['schema'] < 3 and 'v65' in protocol['arms']:
        raise ValueError('Dual features require schema three')
    if protocol['schema'] == 3 and (protocol.get('feature_widths') != {arm: FEATURE_WIDTHS[arm] for arm in protocol['arms']} or protocol.get('sensor_count') != 3869):
        raise ValueError('Feature widths and unchanged sensor count must be predeclared')
    if protocol.get('training_transitions') != 0 or protocol.get('reserved_test_access') is not False:
        raise ValueError('This command cannot train or access final tests')
    validate_request(protocol['seeds'], protocol['physical_cap_per_arm'], protocol['kind'])
    if len(protocol['seeds']) != 16:
        raise ValueError('This comparison requires sixteen paired rooms')
    stop = datetime.fromisoformat(protocol['deadline_utc'])
    if stop.tzinfo is None or stop <= datetime.now(timezone.utc):
        raise ValueError('Protocol deadline has passed or lacks a timezone')
    if not protocol.get('sources'):
        raise ValueError('Missing frozen source hashes')
    for group in ['sources', 'aliases']:
        for name, expected in protocol[group].items():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Protocol paths must stay within the repository')
            if digest(path) != expected:
                raise ValueError(f'Frozen {group} mismatch: {path}')
    return stop


def run(protocol_path, arm, output):
    arm = legacy_version(arm)
    protocol_path = Path(protocol_path)
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    stop = validate(protocol)
    if arm not in protocol['arms']:
        raise ValueError('Arm was not predeclared')
    return check(output, arm, protocol['physical_cap_per_arm'], seeds=protocol['seeds'],
                 kind=protocol['kind'], deadline=stop, frozen_sources=protocol['sources'],
                 protocol_sha256=digest(protocol_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare')
    prep.add_argument('--output', type=Path, required=True)
    prep.add_argument('--seed-start', type=int, default=9500000)
    prep.add_argument('--deadline', required=True)
    prep.add_argument('--baseline-version', type=public_version, choices=['planner-1.0', 'planner-1.1', 'planner-1.2-exp.1'], default='planner-1.0', help='Controller revision number or historical alias')
    prep.add_argument('--candidate-version', type=public_version, choices=['planner-1.1', 'planner-1.2-exp.1', 'planner-1.2-exp.3', 'planner-1.2-exp.4', 'planner-1.2'], default='planner-1.1', help='Controller revision number or historical alias')
    execute = commands.add_parser('run')
    execute.add_argument('protocol', type=Path)
    execute.add_argument('--arm', type=public_version, choices=['planner-1.0', 'planner-1.1', 'planner-1.2-exp.1', 'planner-1.2-exp.3', 'planner-1.2-exp.4', 'planner-1.2'], required=True, help='Controller revision number or historical alias')
    execute.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args.output, args.seed_start, args.deadline, args.baseline_version, args.candidate_version)
        print(json.dumps(dict(kind=result['kind'], seeds=result['seeds'], arms=result['arms'],
                             physical_cap_per_arm=result['physical_cap_per_arm']), indent=2))
    else:
        result = run(args.protocol, args.arm, args.output)
        if result['status'] != 'completed' or result['incomplete_episodes']:
            raise SystemExit('Development check did not complete all declared episodes')


if __name__ == '__main__':
    main()
