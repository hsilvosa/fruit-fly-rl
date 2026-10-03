import json
from pathlib import Path
import pytest
from fly_rl.training.experiment_selection import select_experiment
from fly_rl.training.generalization import sha256
from fly_rl.training.suites import prepare_suite


def experiment(root, seed, success):
    root.mkdir(); checkpoint=root/'selected-policy.zip';checkpoint.write_bytes(str(seed).encode())
    checkpoint.with_suffix('.json').write_text('{}');suite=root/'suite.json';prepare_suite(suite,60000,70000,80000,1,1,1)
    validation={'success_rate':success,'collision_rate':0.,'mean_distance_end':2.}
    state={'status':'completed','training_seed':seed,'final_test_evaluated':False,'training':{'added_transitions':65536}}
    frozen={'checkpoint':str(checkpoint),'checkpoint_sha256':sha256(checkpoint),
        'metadata_sha256':sha256(checkpoint.with_suffix('.json')),'suite':str(suite),'suite_sha256':sha256(suite),
        'dynamics':'coordinated','mode':'dense','validation':validation}
    (root/'experiment.json').write_text(json.dumps(state));(root/'selection.json').write_text(json.dumps(frozen))
    return root


def test_repeated_seed_selection_uses_validation_and_preserves_original(tmp_path):
    a=experiment(tmp_path/'a',42,.9);b=experiment(tmp_path/'b',73,.8)
    result=select_experiment([a,b],tmp_path/'selected')
    assert result['selected_experiment']==str(a.resolve())
    assert (tmp_path/'selected/selected-policy.zip').read_bytes()==b'42'
    assert result['training']['added_transitions']==131072
    assert not result['final_test_evaluated'] and (b/'selected-policy.zip').read_bytes()==b'73'
    state=json.loads((a/'experiment.json').read_text());state['final_test_evaluated']=True
    (a/'experiment.json').write_text(json.dumps(state))
    with pytest.raises(ValueError,match='before any final test'):
        select_experiment([a,b],tmp_path/'invalid')


def test_duplicate_training_seeds_are_not_repeated_seed_evidence(tmp_path):
    a=experiment(tmp_path/'a',42,.9);b=experiment(tmp_path/'b',42,.8)
    with pytest.raises(ValueError,match='distinct training seeds'):
        select_experiment([a,b],tmp_path/'selected')
