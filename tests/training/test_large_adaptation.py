import json
from pathlib import Path
import pytest
from fly_rl.training.mastery_curriculum import PROTOCOL
from fly_rl.simulation.map_profiles import PROFILES
from fly_rl.training.generalization import sha256


def test_large_runner_rejects_budget_changes_before_creating_output(tmp_path):
    from fly_rl.training.large_adaptation import run_large_adaptation
    plan={'kind':'large-warm-mastery-v3','total_added_transitions':1}
    config=tmp_path/'configuration.json';config.write_text(json.dumps(plan))
    with pytest.raises(ValueError,match='bounded'):run_large_adaptation(config,tmp_path/'output','cpu')
    assert not (tmp_path/'output').exists()


@pytest.mark.parametrize('rate,assessed',[(.5,False),(.875,True)])
@pytest.mark.parametrize('continuous',[False,True])
def test_reserved_final_access_requires_declared_large_validation_gate(tmp_path,monkeypatch,rate,assessed,continuous):
    import fly_rl.training.large_adaptation as m
    monkeypatch.chdir(tmp_path)
    initial=tmp_path/'initial.zip';initial.write_bytes(b'warm')
    initial.with_suffix('.json').write_text(json.dumps({'sensor_version':m.SENSOR_V3,'timesteps':114688}))
    suite_file=tmp_path/'suite.json';suite_file.write_text('{}')
    suite={'map_profile':PROFILES['large'].to_dict(),'training_profiles':[PROFILES['gate-near'].to_dict(),PROFILES['large'].to_dict()],
           'splits':{'train':{'seeds':list(range(32))}}}
    plan={'kind':'large-warm-mastery-v3','total_added_transitions':524288,'steps_per_seed':262144,'rounds':32,
          'batch':8,'seeds':[42,73],'validation_interval':4,'validation_minimum':.85,'final_success_target':.8,
          'curriculum':PROTOCOL,'source_hashes':{},'suite':str(suite_file),'suite_sha256':sha256(suite_file),
          'baseline':str(initial),'baseline_sha256':sha256(initial),'baseline_metadata_sha256':sha256(initial.with_suffix('.json')),
          'data':'unused'}
    expected_steps=212992 if continuous else 262144
    if continuous:
        plan.update(kind='large-warm-continuous-v4',total_added_transitions=425984,steps_per_seed=expected_steps,
                    rounds=26,continuous_episodes=True,previous_interrupted_transitions=98304)
    config=tmp_path/'plan.json';config.write_text(json.dumps(plan))
    monkeypatch.setattr(m,'code_hashes',lambda:{})
    monkeypatch.setattr(m,'load_suite',lambda p:suite)
    monkeypatch.setattr(m,'require_unconsumed',lambda s:None)
    train_calls=[]
    def train(*args,**kwargs):
        train_calls.append((args,kwargs))
        assert args[5]==expected_steps and kwargs.get('continuous_episodes',False)==continuous
        return {'training':{'added_transitions':expected_steps},'validation':{'success_rate':rate},
                'results':[{'training':{'curriculum':{'stage':0}}}]}
    monkeypatch.setattr(m,'train_dense',train)
    monkeypatch.setattr(m,'select_experiment',lambda *a,**k:{'validation':{'success_rate':rate}})
    finals=[]
    def final(*args):
        finals.append(args)
        return {'selected_summary':{'success_rate':.8125},'untrained_summary':{'success_rate':0.}}
    monkeypatch.setattr(m,'final_test',final)
    result=m.run_large_adaptation(config,tmp_path/'output','cpu')
    assert len(train_calls)==2 and all(c[1]['allow_transfer'] and c[1]['validation_interval']==4 for c in train_calls)
    assert result['test_evaluated']==assessed and len(finals)==int(assessed)
    assert result['goal_achieved']==assessed and result['warm_start_unchanged']


def test_sparse_validation_still_checks_final_round_and_explicit_transfer(tmp_path,monkeypatch):
    import fly_rl.training.dense_training as m
    from fly_rl.training.suites import prepare_suite
    from fly_rl.simulation.sensors import SENSOR_V3
    monkeypatch.chdir(tmp_path)
    suite=tmp_path/'suite.json';prepare_suite(suite,100,200,300,1,1,1,map_profile='large')
    initial=tmp_path/'initial.zip';initial.write_bytes(b'initial');initial.with_suffix('.json').write_text('{}')
    calls=[]
    def train(*a,**k):
        assert k['allow_transfer']
        p=a[4];p.parent.mkdir(parents=True);p.write_bytes(b'learned');p.with_suffix('.json').write_text('{}')
        return {'added_transitions':4096}
    def evaluate(*a,**k):
        calls.append(a[2]);assert k['allow_transfer']
        return {'success_rate':len(calls)/10,'collision_rate':0.,'mean_distance_end':1.,'sensor_version':SENSOR_V3}
    monkeypatch.setattr(m,'train',train);monkeypatch.setattr(m,'evaluate',evaluate)
    result=m.train_dense('unused','cpu',suite,tmp_path/'output',initial,12288,8,'coordinated',3,42,False,
                         allow_transfer=True,validation_interval=2)
    assert len(calls)==3  # baseline, round two, and the final third round
    assert result['results'][0]['validation'] is None
    assert result['results'][1]['validation'] and result['results'][2]['validation']
