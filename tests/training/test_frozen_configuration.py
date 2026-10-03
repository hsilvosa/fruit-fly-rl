import json
import pytest
from fly_rl.training.generalization import sha256, final_test


def test_changed_evaluator_is_rejected_before_claiming_or_evaluating(tmp_path, monkeypatch):
    import fly_rl.training.generalization as module
    checkpoint=tmp_path/'policy.zip';checkpoint.write_bytes(b'weights')
    checkpoint.with_suffix('.json').write_text('{}');suite=tmp_path/'suite.json';suite.write_text('{}')
    frozen={'checkpoint':str(checkpoint),'checkpoint_sha256':sha256(checkpoint),
        'metadata_sha256':sha256(checkpoint.with_suffix('.json')),'suite':str(suite),'suite_sha256':sha256(suite),
        'evaluation_configuration':{'evaluator_sha256':'0'*64,'planner_sha256':'0'*64}}
    (tmp_path/'selection.json').write_text(json.dumps(frozen));(tmp_path/'experiment.json').write_text('{"status":"completed"}')
    calls=[];monkeypatch.setattr(module,'evaluate',lambda *args,**kwargs:calls.append(1))
    with pytest.raises(ValueError,match='configuration source changed'):
        final_test('data','cpu',tmp_path)
    assert not calls and not (tmp_path/'final-test.json').exists()
