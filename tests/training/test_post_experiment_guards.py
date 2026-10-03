import json
from pathlib import Path
import pytest
from fly_rl.training.experiment_selection import select_experiment
from test_seed_selection import experiment


def test_different_evaluation_settings_cannot_be_compared_as_repeated_seeds(tmp_path):
    a=experiment(tmp_path/'a',42,.9);b=experiment(tmp_path/'b',73,.8)
    path=b/'selection.json';frozen=json.loads(path.read_text());frozen['evaluation_configuration']={'clearance':.1}
    path.write_text(json.dumps(frozen))
    with pytest.raises(ValueError,match='evaluation configuration'):
        select_experiment([a,b],tmp_path/'selected')


def test_no_promote_reports_improvement_without_claiming_alias_copy(tmp_path,monkeypatch):
    import fly_rl.training.dense_training as dense
    monkeypatch.chdir(tmp_path)
    suite={'mode':'dense','splits':{'train':{'seeds':[0]},'validation':{'seeds':[10000]},'test':{'seeds':[20000]}}}
    source=tmp_path/'suite.json';source.write_text('{}')
    baseline=tmp_path/'baseline.zip';baseline.write_bytes(b'baseline');baseline.with_suffix('.json').write_text('{}')
    monkeypatch.setattr(dense,'load_suite',lambda path:suite)
    def measured(*args,**kwargs):
        return {'success_rate':.1 if Path(args[2]).name=='baseline.zip' else .9,
                'collision_rate':0.,'mean_distance_end':1.}
    def trained(*args,**kwargs):
        path=Path(args[4]);path.parent.mkdir(parents=True);path.write_bytes(b'trained');path.with_suffix('.json').write_text('{}')
        return {'added_transitions':args[2]}
    monkeypatch.setattr(dense,'evaluate',measured);monkeypatch.setattr(dense,'train',trained)
    result=dense.train_dense('data','cpu',source,tmp_path/'run',baseline,4096,8,'coordinated',1,promote=False)
    assert result['validation_improved'] and result['promoted'] is False
    assert 'promoted_checkpoint' not in result and not (tmp_path/'runs/dense-flight-policy.zip').exists()
