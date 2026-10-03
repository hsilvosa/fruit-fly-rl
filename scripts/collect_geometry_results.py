"""Read a completed geometry run; never import the simulator or execute a policy."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validation_summary(value):
    episodes = value['episodes']
    require(len(episodes) == 32, 'Expected exactly 32 validation episodes')
    counts = {name: sum(bool(row[name]) for row in episodes) for name in ('success', 'collision', 'timeout')}
    require(sum(counts.values()) == 32, 'Validation outcomes must partition the episodes')
    return dict(episodes=32, successes=counts['success'], collisions=counts['collision'],
                timeouts=counts['timeout'], mean_distance_end=value['mean_distance_end'])


def curriculum_summary(counters):
    """Keep measured counts, without repeating full profiles or machine records."""
    summaries = []
    for index, counter in enumerate(counters, 1):
        if counter is None:
            continue
        fields = ('initial_offset', 'transitions', 'stage', 'mixture', 'resets_including_initialization',
                  'transitions_by_profile', 'episode_outcomes_by_profile')
        summaries.append(dict(round=index, protocol_version=counter['protocol']['version'],
                              **{key: counter[key] for key in fields if key in counter}))
    return summaries


def collect(root):
    root = Path(root).resolve()
    folder = root/'runs/training/geometry-v1'
    state = read(folder/'status.json')
    require(state['status'] == 'completed', 'Comparison not completed; no publication result generated')
    require(state['test_evaluated'] is True, 'Final assessment has not completed')
    plan = read(folder/'configuration.json')
    require(plan['total_training_transitions'] == state['budget_added_transitions'] == 524288,
            'Unexpected comparison budget')
    require(digest(folder/'configuration.json') == state['configuration_sha256'], 'Configuration hash changed')
    suite = read(plan['suite'])
    require(digest(plan['suite']) == plan['suite_sha256'], 'Frozen suite hash changed')
    for name, expected in plan['source_hashes'].items():
        require(digest(folder/'source'/name) == expected, f'Source snapshot mismatch: {name}')
    require(len(state['initializations']) == 2, 'Two initializations required')
    for initial in state['initializations']:
        require(initial['full_neurons'] == 167184, 'Incomplete brain initialization')
        require(initial['initial_timesteps'] == initial['optimizer_updates'] == initial['optimizer_state_entries'] == 0,
                'Initialization was not fresh')
        require(initial['data_fingerprint'] == plan['data_fingerprint'], 'Initialization data mismatch')
        require(digest(initial['v2']) == digest(initial['v3']) == initial['paired_weights_sha256'],
                'Paired initialization archives changed')
    require(len(state['results']) == 4, 'Four completed training runs required')
    expected_runs = {(method, seed) for method in ('baseline', 'curriculum') for seed in (42, 73)}
    require({(row['arm'], row['seed']) for row in state['results']} == expected_runs, 'Method/seed mismatch')
    public_runs = []
    total = 0
    for row in state['results']:
        experiment = read(folder/f"{row['arm']}-seed-{row['seed']}"/'experiment.json')
        require(experiment['status'] == 'completed' and experiment['promoted'] is False,
                'Training incomplete or original alias was promoted')
        require(len(experiment['results']) == 2, 'Two rounds required')
        added = sum(round_row['training']['added_transitions'] for round_row in experiment['results'])
        require(added == row['added_transitions'] == 131072, 'Per-run budget mismatch')
        for round_row in experiment['results']:
            losses = round_row['training']['losses']
            require(bool(losses) and all(math.isfinite(number) for number in losses.values()), 'Missing or nonfinite losses')
            require(round_row['training']['added_transitions'] == 65536, 'Round budget mismatch')
        require(experiment['validation'] == row['validation'], 'Selected validation record mismatch')
        total += added
        public_runs.append(dict(method=row['arm'], seed=row['seed'], added_transitions=added,
                                selected_lifetime_transitions=read(folder/f"{row['arm']}-seed-{row['seed']}"/'selected-policy.json')['timesteps'],
                                validation_improved=experiment['validation_improved'],
                                initial_validation=validation_summary(experiment['baseline_validation']),
                                selected_validation=validation_summary(row['validation']),
                                curriculum_counters=curriculum_summary(row['curriculum_rounds'])))
    require(total == 524288, 'Total budget mismatch')
    before, after = state['alias_hashes_before'], state['alias_hashes_after']
    require(len(before) == 6 and before == after and state['aliases_unchanged'] is True, 'Alias evidence mismatch')
    for path, expected in before.items():
        require(digest(path) == expected, 'Current original alias changed')
    claim = read(root/'runs/suites/consumed'/f"{suite['test_fingerprint']}.json")
    require(claim['test_fingerprint'] == suite['test_fingerprint'], 'Final pool claim mismatch')
    require(set(claim['test_geometries']) == set(suite['splits']['test']['geometry_sha256']),
            'Final claim geometry mismatch')
    metadata = read(folder/'selected/selected-policy.json')
    initial = next(row for row in state['initializations'] if row['seed'] == metadata['training_seed'])
    selected_digest = digest(folder/'selected/selected-policy.zip')
    matches_initial = selected_digest == initial['paired_weights_sha256']
    if metadata['timesteps'] == 0:
        require(matches_initial, 'Zero-transition selection must match its frozen initialization')
    ranking_metrics = {}
    for method in ('baseline', 'curriculum'):
        selection = read(folder/f'{method}-selected'/'selection.json')['validation']
        ranking_metrics[method] = {key: selection[key] for key in ('success_rate', 'collision_rate', 'mean_distance_end')}
    require(state['final_summary']['episodes'] == state['untrained_summary']['episodes'] == 64,
            'Final assessment episode count mismatch')
    return dict(status='completed', protocol='geometry-v1', source_revision=read(root/'runs/training/geometry-v1-launch.json')['source_commit'],
                total_added_transitions=total, runs=public_runs, selected_method=state['selected_arm'],
                selected_training_seed=metadata['training_seed'], selected_lifetime_transitions=metadata['timesteps'],
                final_summary=state['final_summary'],
                untrained_summary=state['untrained_summary'], elapsed_seconds=state['elapsed_seconds'],
                configuration_sha256=state['configuration_sha256'], suite_sha256=plan['suite_sha256'],
                data_fingerprint=plan['data_fingerprint'], selected_checkpoint_sha256=selected_digest,
                selected_checkpoint_matches_initialization=matches_initial, method_ranking_metrics=ranking_metrics,
                aliases_preserved={Path(path).name: expected for path, expected in before.items()},
                all_round_losses_finite=True, full_annotated_neurons=167184, full_directed_edges=25583622,
                source_snapshot_verified=True,
                final_pool_consumed=True, collection_training_invoked=False, collection_evaluation_invoked=False,
                limitations=['Only the validation winner and untrained control were final-tested.',
                             'This is not a paired final comparison of both methods.',
                             'Earlier experiments used different final rooms.',
                             'Navigation does not demonstrate a biological advantage.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    summary = collect(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: summary[key] for key in ('status', 'total_added_transitions', 'selected_method', 'final_summary')}, indent=2))
