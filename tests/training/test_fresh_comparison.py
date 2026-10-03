import json
import pytest
from scipy import sparse
from fly_rl.training import fresh_sensor_comparison as fresh
from fly_rl.training.learning import BrainEnv,checkpoint_sensor_version
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.sensors import SENSOR_V3
from fly_rl.training.suites import prepare_suite,load_suite
from fly_rl.visualization.validation_failures import collect_validation


def fixture(root):
    root.mkdir();prepare_suite(root/'suite.json',60000,70000,80000,1,1,1)
    state={'training_seed':42,'validation':{'episodes':[{'seed':70000,'success':False,'collision':False,'timeout':True,'distance_end':1.,'idle_fraction':.4}]}}
    (root/'experiment.json').write_text(json.dumps(state));return root,state


def test_validation_flags_overlap_without_inventing_causes(tmp_path):
    folder,state=fixture(tmp_path/'run');report=collect_validation([folder]);measured=report['experiments'][0]
    assert measured['timeouts_near_goal']==measured['timeouts_frequent_stopping']==measured['timeouts_near_goal_and_stopping']==1
    assert measured['categories']=={'timeout_with_frequent_stopping':1}
    assert not report['evaluation_invoked'] and report['unique_validation_rooms']==1


@pytest.mark.parametrize('fault',['final','nested-test','seed','duplicate','nan','range'])
def test_validation_rejects_invalid_provenance_and_measurements(tmp_path,fault):
    folder,state=fixture(tmp_path/'run');row=state['validation']['episodes'][0]
    if fault=='final':state['selected_summary']={}
    if fault=='nested-test':state['validation']['split']='test'
    if fault=='seed':row['seed']=80000
    if fault=='duplicate':state['validation']['episodes'].append(row)
    if fault=='nan':row['distance_end']=float('nan')
    if fault=='range':row['idle_fraction']=1.2
    (folder/'experiment.json').write_text(json.dumps(state))
    with pytest.raises(ValueError):collect_validation([folder])


@pytest.mark.parametrize('steps,batch,rounds,seeds',[(1,8,2,[42,73]),(65536,0,2,[42,73]),(65536,8,0,[42,73]),(65536,8,2,[42,42]),(True,8,2,[42,73])])
def test_invalid_budgets(steps,batch,rounds,seeds):
    with pytest.raises(ValueError):fresh.validate_budget(steps,batch,rounds,seeds)


def test_budget_and_draft_cannot_start_training(tmp_path,monkeypatch):
    assert fresh.validate_budget(None,8,2,[42,73]) is None
    assert fresh.validate_budget(131072,8,2,[42,73])==524288
    path=tmp_path/'draft.json';path.write_text(json.dumps({'steps_per_seed':None,'batch':8,'rounds':2,'seeds':[42,73],'status':'draft-budget-required'}))
    monkeypatch.setattr(fresh,'train_dense',lambda *a,**k:pytest.fail('Training must not run'))
    with pytest.raises(ValueError,match='agree'):fresh.run_fresh_comparison(path,tmp_path/'output')
    assert not (tmp_path/'output').exists()


def test_pair_has_identical_weights_and_no_optimizer_history(tmp_path,monkeypatch):
    prepare_suite(tmp_path/'suite.json',60000,70000,80000,1,1,1)
    def tiny_env(data,batch,device,**kwargs):
        return BrainEnv(batch=batch,device='cpu',brain=Brain(matrix=sparse.eye(16,format='csr'),batch=batch,device='cpu'),**kwargs)
    monkeypatch.setattr(fresh,'BrainEnv',tiny_env)
    from stable_baselines3 import PPO
    monkeypatch.setattr(PPO,'learn',lambda *a,**k:pytest.fail('Learning is forbidden during initialization'))
    proof=fresh.initialize_pair('unused','cpu',load_suite(tmp_path/'suite.json'),42,tmp_path/'pair')
    assert proof['initial_timesteps']==proof['optimizer_updates']==proof['optimizer_state_entries']==0
    assert (tmp_path/'pair/v2.zip').read_bytes()==(tmp_path/'pair/v3.zip').read_bytes()
    assert checkpoint_sensor_version(tmp_path/'pair/v3.zip')==SENSOR_V3
    restored=PPO.load(tmp_path/'pair/v3.zip',device='cpu')
    assert restored.num_timesteps==restored._n_updates==0 and not restored.policy.optimizer.state


def test_changed_source_cannot_start_configured_experiment(tmp_path,monkeypatch):
    plan={'steps_per_seed':65536,'batch':8,'rounds':2,'seeds':[42,73],'status':'configured','total_training_transitions':262144,'kind':'fresh-paired-sensor-comparison','version':1,'dynamics':'coordinated','route_metrics':True,'source_hashes':{}}
    path=tmp_path/'plan.json';path.write_text(json.dumps(plan))
    monkeypatch.setattr(fresh,'train_dense',lambda *a,**k:pytest.fail('Training must not run'))
    with pytest.raises(ValueError,match='Source changed'):fresh.run_fresh_comparison(path,tmp_path/'output')
    assert not (tmp_path/'output').exists()
