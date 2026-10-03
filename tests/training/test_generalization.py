import json
from pathlib import Path
import pytest
from fly_rl.training.generalization import sha256,final_test,summarize

def measurement(success=True):
    return {'episodes':[{'seed':20000,'success':success,'steps':20,'distance_start':10.,'path_length':12.}],
            'success_rate':float(success),'collision_rate':0.,'timeout_rate':float(not success),'mean_distance_end':1.}

def test_dense_selects_best_validation_round_and_never_tests(tmp_path,monkeypatch):
    import fly_rl.training.dense_training as dense
    monkeypatch.chdir(tmp_path)
    suite={'mode':'dense','splits':{'train':{'seeds':[0,1]},'validation':{'seeds':[10000]},'test':{'seeds':[20000]}}}
    source=tmp_path/'suite.json';source.write_text(json.dumps(suite))
    baseline=tmp_path/'baseline.zip';baseline.write_bytes(b'baseline');baseline.with_suffix('.json').write_text('{}')
    monkeypatch.setattr(dense,'load_suite',lambda path:suite)
    calls=[]
    def evaluate(*args,**kwargs):
        calls.append((args[5],kwargs['dynamics']))
        score=[.1,.9,.2][len(calls)-1]
        return dict(measurement(),success_rate=score)
    def train(*args,**kwargs):
        assert kwargs['layout_seeds']==[0,1] and kwargs['dynamics']=='coordinated'
        path=Path(args[4]);path.parent.mkdir(parents=True);path.write_bytes(path.parent.name.encode())
        path.with_suffix('.json').write_text('{}')
        return {'added_transitions':args[2]}
    monkeypatch.setattr(dense,'evaluate',evaluate);monkeypatch.setattr(dense,'train',train)
    result=dense.train_dense('data','cpu',source,tmp_path/'run',baseline,16384,16,'coordinated',2)
    assert calls==[(10000,'coordinated')]*3
    assert result['training']['added_transitions']==16384
    assert Path(result['selected_policy']).read_bytes()==b'round-1'
    assert Path(result['promoted_checkpoint']).read_bytes()==b'round-1'
    assert result['final_test_evaluated'] is False

def test_final_test_checks_freeze_and_refuses_second_test(tmp_path,monkeypatch):
    import fly_rl.training.generalization as module
    checkpoint=tmp_path/'selected.zip';checkpoint.write_bytes(b'weights');checkpoint.with_suffix('.json').write_text('{}')
    suite_path=tmp_path/'suite.json';suite_path.write_text('{}')
    frozen={'checkpoint':str(checkpoint),'checkpoint_sha256':sha256(checkpoint),'metadata_sha256':sha256(checkpoint.with_suffix('.json')),
            'suite':str(suite_path),'suite_sha256':sha256(suite_path),'mode':'dense','dynamics':'coordinated','evaluation_configuration':{'sensor_version':'test-sensor'}}
    (tmp_path/'selection.json').write_text(json.dumps(frozen));(tmp_path/'experiment.json').write_text('{"status":"completed"}')
    monkeypatch.setattr(module,'load_suite',lambda path:{'splits':{'test':{'seeds':[20000]}}})
    calls=[]
    def evaluate(*args,**kwargs):
        calls.append((args[2],args[5],kwargs['dynamics']))
        if args[2] is None: assert kwargs['sensor_version']=='test-sensor'
        return measurement(args[2] is not None)
    monkeypatch.setattr(module,'evaluate',evaluate)
    checkpoint.write_bytes(b'changed')
    with pytest.raises(ValueError,match='integrity'): final_test('data','cpu',tmp_path)
    assert not calls and not (tmp_path/'final-test.json').exists()
    checkpoint.write_bytes(b'weights')
    result=final_test('data','cpu',tmp_path)
    assert result['status']=='completed' and result['success_improvement']==1.
    assert json.loads((tmp_path/'experiment.json').read_text())['final_test_evaluated'] is True
    assert len(calls)==2 and all(c[1:]==(20000,'coordinated') for c in calls)
    with pytest.raises(FileExistsError): final_test('data','cpu',tmp_path)
    assert len(calls)==2

def test_uncertainty_and_success_only_route_metrics():
    result=summarize(measurement(False))
    assert result['mean_success_path_length'] is None
    assert result['success_wilson_95'][1]>0
    result=summarize(measurement())
    assert result['mean_success_arrival_seconds']==1.
    assert result['mean_success_path_over_straight_line']==1.2
    assert result['success_wilson_95'][0]<1
