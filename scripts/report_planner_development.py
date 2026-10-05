"""Report an already completed, frozen paired development check without evaluation."""
import argparse
import json
import math
from pathlib import Path
from fly_rl.navigation.versions import legacy_version, public_version


def wilson(successes, total):
    if not 0 <= successes <= total or total <= 0:
        raise ValueError('Invalid outcome counts')
    z = 1.959963984540054
    p = successes / total
    denominator = 1+z*z/total
    center = (p+z*z/(2*total))/denominator
    radius = z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/denominator
    return [max(0., center-radius), min(1., center+radius)]


def compare(baseline, candidate, expected_pair=('v55', 'v60')):
    expected_pair = tuple(legacy_version(arm) for arm in expected_pair)
    allowed = [('v55', 'v60'), ('v60', 'v61'), ('v60', 'v63'), ('v60', 'v64'), ('v61', 'v64'), ('v60', 'v65')]
    if tuple(expected_pair) not in allowed:
        raise ValueError('Unsupported declared comparison')
    readouts = dict(v55='neural-projection-motion-stable-visual005-v1',
        v60='neural-projection-motion-stable-visual005-v1',
        v61='neural-projection-distance-stable-speed005-v1',
        v63='neural-projection-distance-stable-speed005-v1',
        v64='neural-projection-distance-stable-speed005-v1',
        v65='neural-projection-dual-map005-distance-clean-v1')
    widths = {arm: (5669 if arm == 'v65' else 3869) for arm in readouts}
    for arm, state in zip(expected_pair, [baseline, candidate]):
        if state['controller'] != arm or state['kind'] != 'frozen-prospective-development':
            raise ValueError('Wrong arm or evidence type')
        if state['status'] != 'completed' or state['incomplete_episodes']:
            raise ValueError('Both arms must complete all declared episodes')
        if state['added_training_transitions'] or state['optimizer_updates'] or state['reserved_test_evaluated']:
            raise ValueError('Unexpected optimization or final-test access')
        if not state.get('protected_unchanged') or not state.get('sources_unchanged'):
            raise ValueError('Preservation checks did not pass')
        if state['graph_neurons'] != 167184 or state['graph_edges'] != 25583622:
            raise ValueError('Full graph contract mismatch')
        if state.get('readout_version', readouts[arm]) != readouts[arm]:
            raise ValueError('Undeclared readout contract')
        if state.get('feature_count', 3869) != widths[arm] or state.get('sensor_count', 3869) != 3869:
            raise ValueError('Declared feature width or sensor count mismatch')
        if len(state['episodes']) != 16 or {e['seed'] for e in state['episodes']} != set(state['seeds']):
            raise ValueError('Missing, duplicate, or undeclared outcomes')
        if state['physical_transitions'] > state['physical_cap']:
            raise ValueError('Physical budget exceeded')
        for e in state['episodes']:
            if sum(bool(e[key]) for key in ['success', 'collision', 'timeout']) != 1:
                raise ValueError('Ambiguous terminal outcome')
            if type(e['steps']) is not int or e['steps'] <= 0 or not math.isfinite(e['flown_distance']) or e['flown_distance'] < 0:
                raise ValueError('Invalid physical episode measurements')
    for name in ['seeds', 'protocol_sha256', 'layout_hashes',
                 'frozen_sources_before', 'protected_before']:
        if baseline[name] != candidate[name]:
            raise ValueError(f'Paired contract mismatch: {name}')
    graphs = [s.get('graph_data_fingerprint', s['brain_fingerprint'].split(':')[0]) for s in [baseline, candidate]]
    if graphs[0] != graphs[1]:
        raise ValueError('Graph data fingerprints differ')
    models = [s['brain_fingerprint'].rsplit(':', 1)[0] for s in [baseline, candidate]]
    if models[0] != models[1]:
        raise ValueError('Undeclared base brain model difference')
    if not baseline['protocol_sha256']:
        raise ValueError('Missing frozen protocol fingerprint')
    arms = {}
    for state in [baseline, candidate]:
        episodes = state['episodes']
        goals = sum(e['success'] for e in episodes)
        arms[state['controller']] = dict(goals=goals, total=16,
            collisions=sum(e['collision'] for e in episodes),
            timeouts=sum(e['timeout'] for e in episodes), wilson_95=wilson(goals, 16),
            physical_transitions=state['physical_transitions'],
            elapsed_seconds=state['elapsed_seconds'], peak_vram_gb=state['peak_vram_gb'])
    b = {e['seed']: e for e in baseline['episodes']}
    c = {e['seed']: e for e in candidate['episodes']}
    paired = dict(both_success=0, baseline_only=0, candidate_only=0, neither_success=0)
    rooms = []
    for seed in baseline['seeds']:
        left, right = b[seed]['success'], c[seed]['success']
        key = 'both_success' if left and right else 'baseline_only' if left else 'candidate_only' if right else 'neither_success'
        paired[key] += 1
        rooms.append(dict(seed=seed, **{expected_pair[0]: b[seed], expected_pair[1]: c[seed]}))
    return dict(kind='frozen-prospective-development', protocol_sha256=baseline['protocol_sha256'],
        arms=arms, paired=paired, rooms=rooms, controllers=list(expected_pair),
        controller_versions={arm: public_version(arm) for arm in expected_pair},
        readouts={arm: readouts[arm] for arm in expected_pair},
        feature_widths={arm: widths[arm] for arm in expected_pair},
        training_invoked=False, evaluation_invoked=False,
        reserved_test_access=False, aliases_unchanged=True, sources_unchanged=True,
        limitations='Sixteen development rooms from one generator; not a final test or biological evidence.')


def render(result):
    names = result.get('controllers', ['v55', 'v60'])
    labels = {name: f'{public_version(name)} ({name})' for name in names}
    lines = [f"# Frozen {' / '.join(labels[name] for name in names)} paired development results", '',
        'These are fresh development measurements of frozen controllers, not a reserved final test.', '',
        '| Arm | Goals / 16 | Collisions | Timeouts | Wilson 95% interval |',
        '| --- | ---: | ---: | ---: | --- |']
    for name, arm in result['arms'].items():
        low, high = arm['wilson_95']
        lines.append(f"| {labels[name]} | {arm['goals']} | {arm['collisions']} | {arm['timeouts']} | {100*low:.1f}–{100*high:.1f}% |")
    p = result['paired']
    lines += ['', f"Paired outcomes: {p['both_success']} both succeed, {p['baseline_only']} baseline only, "
        f"{p['candidate_only']} candidate only, {p['neither_success']} neither succeeds.", '',
        f'| Room | {labels[names[0]]} outcome / steps / flown distance | {labels[names[1]]} outcome / steps / flown distance |',
        '| --- | --- | --- |']
    for row in result['rooms']:
        cells = []
        for arm in names:
            e = row[arm]
            outcome = 'goal' if e['success'] else 'collision' if e['collision'] else 'timeout'
            cells.append(f"{outcome} / {e['steps']} / {e['flown_distance']:.2f}")
        lines.append(f"| {row['seed']} | {cells[0]} | {cells[1]} |")
    total = sum(a['physical_transitions'] for a in result['arms'].values())
    lines += ['', f'Physical transitions across both arms: {total:,}. Zero training transitions or optimizer updates.',
        'Original aliases and frozen sources match before/after. Initial layout and graph-data fingerprints match across arms.',
        'Flown distance includes every scored physical step; it is not an optimal-route measurement.', '',
        f"Protocol SHA-256: `{result['protocol_sha256']}`.", '', result['limitations'], '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline-version', type=public_version, choices=['planner-1.0', 'planner-1.1', 'planner-1.2-exp.1'], default='planner-1.0', help='Controller revision number or historical alias')
    parser.add_argument('--candidate-version', type=public_version, choices=['planner-1.1', 'planner-1.2-exp.1', 'planner-1.2-exp.3', 'planner-1.2-exp.4', 'planner-1.2'], default='planner-1.1', help='Controller revision number or historical alias')
    args = parser.parse_args()
    result = compare(json.loads(args.baseline.read_text()), json.loads(args.candidate.read_text()),
                     (args.baseline_version, args.candidate_version))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    (args.output/'results.md').write_text(render(result), encoding='utf-8')
    print(json.dumps(dict(arms=result['arms'], paired=result['paired']), indent=2))
