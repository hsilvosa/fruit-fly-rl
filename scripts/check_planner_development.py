"""Prepare and run a frozen planner development comparison; never a final test."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

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


def prepare(output, seed_start, deadline):
    output = Path(output)
    if output.exists():
        raise FileExistsError('Use a new protocol filename')
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
    sources.update(Path(path) for path in ['fly_rl/training/learning.py',
        'scripts/check_planner_failures.py', 'scripts/check_planner_development.py'])
    protocol = dict(schema=1, kind='frozen-prospective-development',
        created_utc=datetime.now(timezone.utc).isoformat(), deadline_utc=stop.isoformat(),
        arms=['v55', 'v60'], seeds=seeds, physical_cap_per_arm=81920,
        training_transitions=0, reserved_test_access=False,
        selection_rule='Report both frozen arms; do not retune either from this suite.',
        task='large', sources={p.as_posix(): digest(p) for p in sorted(sources)},
        aliases={p.as_posix(): digest(p) for p in sorted(Path('runs').glob('*policy.*'))},
        prior_inventory=checked)
    output.parent.mkdir(parents=True, exist_ok=True)
    save(output, protocol)
    return protocol


def validate(protocol):
    if protocol.get('schema') != 1 or protocol.get('kind') != 'frozen-prospective-development':
        raise ValueError('Unsupported protocol')
    if protocol.get('arms') != ['v55', 'v60'] or protocol.get('task') != 'large':
        raise ValueError('Unsupported frozen arms or task')
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
    execute = commands.add_parser('run')
    execute.add_argument('protocol', type=Path)
    execute.add_argument('--arm', choices=['v55', 'v60'], required=True)
    execute.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args.output, args.seed_start, args.deadline)
        print(json.dumps(dict(kind=result['kind'], seeds=result['seeds'], arms=result['arms'],
                             physical_cap_per_arm=result['physical_cap_per_arm']), indent=2))
    else:
        result = run(args.protocol, args.arm, args.output)
        if result['status'] != 'completed' or result['incomplete_episodes']:
            raise SystemExit('Development check did not complete all declared episodes')


if __name__ == '__main__':
    main()
