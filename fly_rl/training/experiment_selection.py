"""Select among completed adaptation seeds using one shared validation pool."""
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from fly_rl.training.generalization import sha256
from fly_rl.training.suites import load_suite
from fly_rl.training.test_access import require_unconsumed


def select_experiment(experiments, output):
    records = []
    for folder in map(Path, experiments):
        state = json.loads((folder/'experiment.json').read_text())
        frozen = json.loads((folder/'selection.json').read_text())
        if state['status'] != 'completed' or state.get('final_test_evaluated'):
            raise ValueError('Select completed validation-only experiments before any final test')
        for file, expected in [(Path(frozen['checkpoint']), frozen['checkpoint_sha256']),
                               (Path(frozen['checkpoint']).with_suffix('.json'), frozen['metadata_sha256']),
                               (Path(frozen['suite']), frozen['suite_sha256'])]:
            if sha256(file) != expected:
                raise ValueError('Frozen experiment integrity mismatch')
        require_unconsumed(load_suite(frozen['suite']))
        records.append((state, frozen, folder))
    if len(records) < 2 or len({r[0].get('training_seed', 42) for r in records}) != len(records):
        raise ValueError('Use at least two distinct training seeds')
    if len({(r[1]['suite_sha256'], r[1]['dynamics'], json.dumps(r[1].get('evaluation_configuration',{}),sort_keys=True)) for r in records}) != 1:
        raise ValueError('Experiments must share the same frozen suite, dynamics, and evaluation configuration')
    def rank(record):
        metrics = record[1]['validation']
        return metrics['success_rate'], -metrics['collision_rate'], -metrics['mean_distance_end']
    best = max(records, key=rank)
    folder = Path(output); folder.mkdir(parents=True, exist_ok=False)
    checkpoint = folder/'selected-policy.zip'
    shutil.copy2(best[1]['checkpoint'], checkpoint)
    shutil.copy2(Path(best[1]['checkpoint']).with_suffix('.json'), checkpoint.with_suffix('.json'))
    shutil.copy2(best[1]['suite'], folder/'suite.json')
    frozen = dict(best[1], checkpoint=str(checkpoint.resolve()), suite=str((folder/'suite.json').resolve()),
                  frozen_utc=datetime.now(timezone.utc).isoformat())
    members = [{'experiment': str(r[2].resolve()), 'training_seed': r[0]['training_seed'],
                'validation': r[1]['validation'], 'added_transitions': r[0]['training']['added_transitions']}
               for r in records]
    frozen['seed_experiments'] = members
    (folder/'selection.json').write_text(json.dumps(frozen, indent=2), encoding='utf-8')
    state = {'status': 'completed', 'kind': 'validation-selected-adaptation-seeds',
             'validation': frozen['validation'], 'final_test_evaluated': False,
             'selected_experiment': str(best[2].resolve()), 'seed_experiments': members,
             'selection_rule': 'success, then fewer collisions, then lower end distance; stable input order ties',
             'training': {'added_transitions': sum(m['added_transitions'] for m in members)}}
    (folder/'experiment.json').write_text(json.dumps(state, indent=2), encoding='utf-8')
    return state
