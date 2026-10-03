import json
import numpy as np
import pytest
from scipy import sparse
from fly_rl.training.validation_trace import clearance,contact_geometry,validation_cases,trace_validation
from fly_rl.training.generalization import sha256
from fly_rl.training.suites import prepare_suite
from fly_rl.training.learning import BrainEnv,make_policy,save_model
from fly_rl.connectome.brain import Brain
from fly_rl.visualization.validation_trace import plot_validation_trace


def experiment(tmp_path):
    folder=tmp_path/'experiment';folder.mkdir()
    prepare_suite(folder/'suite.json',130000,140000,150000,1,2,1)
    env=BrainEnv(brain=Brain(matrix=sparse.eye(16,format='csr'),device='cpu'),device='cpu',mode='dense',dynamics='coordinated')
    try:save_model(make_policy(env,seed=42),folder/'selected-policy.zip',env.brain)
    finally:env.close()
    rows=[{'seed':140000+i,'success':False,'collision':i==0,'timeout':i==1,'steps':1200,'distance_end':5.} for i in range(2)]
    frozen={'checkpoint':str(folder/'selected-policy.zip'),'checkpoint_sha256':sha256(folder/'selected-policy.zip'),'metadata_sha256':sha256(folder/'selected-policy.json'),'suite':str(folder/'suite.json'),'suite_sha256':sha256(folder/'suite.json'),'selection_split':'validation','validation':{'episodes':rows},'mode':'dense','dynamics':'coordinated'}
    (folder/'selection.json').write_text(json.dumps(frozen));(folder/'experiment.json').write_text(json.dumps({'status':'completed'}))
    return folder,frozen


def test_swept_contacts_and_clearance_use_actual_collision_geometry():
    obstacles=np.array([[[2,2,2],[3,3,3]]]);room=np.array([6,6,6])
    assert contact_geometry([1.8,2.5,2.5],[2,0,0],room,obstacles)['obstacle_indices']==[0]
    assert contact_geometry([5.83,1,1],[2,0,0],room,obstacles)['kind']=='wall'
    assert contact_geometry([1,1,1],[0,0,0],room,obstacles)['kind']=='none'
    assert clearance([2.5,2.5,2.5],room,obstacles)<0
    assert clearance([1,1,1],room,obstacles)>0
    assert clearance([.1,1,1],room,obstacles)<0


def test_only_validation_cases_and_verified_checkpoint_are_accepted(tmp_path):
    folder,frozen=experiment(tmp_path);_,cases=validation_cases(folder,2)
    assert [r['seed'] for r in cases]==[140000,140001]
    frozen['validation']['episodes'][0]['seed']=150000
    (folder/'selection.json').write_text(json.dumps(frozen))
    with pytest.raises(ValueError,match='provenance'):validation_cases(folder,2)
    (folder/'experiment.json').write_text(json.dumps({'status':'completed','final_summary':{}}))
    with pytest.raises(ValueError,match='individual validation'):validation_cases(folder,2)


def test_trace_keeps_terminal_state_and_never_learns(tmp_path,monkeypatch):
    folder,frozen=experiment(tmp_path)
    import fly_rl.training.learning as learning
    def tiny_env(data,batch,device,**kwargs):
        env=BrainEnv(batch=batch,device='cpu',brain=Brain(matrix=sparse.eye(16,format='csr'),batch=batch,device='cpu',sensor_version=kwargs['sensor_version']),**kwargs)
        for world in env.worlds:world.episode_limit=1
        return env
    monkeypatch.setattr(learning,'BrainEnv',tiny_env)
    from stable_baselines3 import PPO
    monkeypatch.setattr(PPO,'learn',lambda *a,**k:pytest.fail('Diagnostic cannot learn'))
    result=trace_validation('unused','cpu',folder,tmp_path/'traces',2,3)
    assert result['environment_transitions']==result['recorded_transitions']==2
    assert not result['training_invoked'] and not result['test_evaluated'] and result['optimizer_updates_added']==0
    for case in result['cases']:
        with np.load(case['trace']) as arrays:
            assert arrays['action'].shape==(1,4) and arrays['features_before'].shape==(1,256)
            assert arrays['sensors_before'].shape==(1,269) and np.isfinite(arrays['position_after']).all()
            assert arrays['target_distance_after'][0]==pytest.approx(np.linalg.norm(arrays['target']-arrays['position_after'][0]))
        assert case['outcome']['truncated'] and case['decisions']==1
    assert sha256(frozen['checkpoint'])==frozen['checkpoint_sha256']
    with pytest.raises(FileExistsError):trace_validation('unused','cpu',folder,tmp_path/'traces',2,3)


def test_plot_rejects_final_test_trace_without_evaluating(tmp_path):
    source=tmp_path/'test.json';source.write_text(json.dumps({'split':'test'}))
    with pytest.raises(ValueError,match='Validation'):plot_validation_trace(source,tmp_path/'plot.png')
