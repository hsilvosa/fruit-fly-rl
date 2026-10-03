import json
import numpy as np
import pytest
from scipy import sparse
from fly_rl.training.collision_diagnostics import ray_risk,motion_ttc,object_visibility
from fly_rl.training.risk_shaping import RiskWorld,RiskStats,configure_risk_shaping
from fly_rl.training.risk_comparison import run_risk_comparison,freeze_risk_winner
from fly_rl.training.validation_trace import validation_cases
from fly_rl.training.learning import BrainEnv
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.sensors import SENSOR_V3


def test_ray_penalty_depends_on_visible_approach_not_distance_alone():
    obs=np.zeros(269);obs[:128]=1
    assert ray_risk(obs)==0
    obs[0]=.3/8;obs[128]=1/3
    assert ray_risk(obs)==pytest.approx(1-.14/.75)
    obs[128]=-1/3;assert ray_risk(obs)==0
    obs[128]=1/3;obs[0]=1;assert ray_risk(obs)==0
    with pytest.raises(ValueError):ray_risk(obs,horizon=0)
    with pytest.raises(ValueError):ray_risk(np.nan)


def test_motion_ttc_and_geometric_visibility():
    room=np.array([6.,6.,6.]);boxes=np.array([[[2.,2.,2.],[3.,3.,3.]]])
    assert motion_ttc([1.,2.5,2.5],[1,0,0],room,boxes)==pytest.approx(.84)
    assert motion_ttc([1,1,1],[0,0,0],room,boxes) is None
    world=FlightWorld(0);world.position=np.array([1.,2.5,2.5]);world.obstacles=[tuple(boxes[0])]
    assert object_visibility(world.position,world.yaw,world.observe(),boxes,[0])>0


def test_shaping_changes_only_training_reward_and_records_components():
    kwargs={'seed':42,'mode':'dense','layout_seeds':[230000],'dynamics':'coordinated','sensor_version':SENSOR_V3}
    shaped=RiskWorld(stats=RiskStats(),**kwargs);base=FlightWorld(**kwargs)
    low,high=base.obstacles[0];p=np.array([low[0]-.3,(low[1]+high[1])/2,(low[2]+high[2])/2])
    for w in [shaped,base]:w.position=p.copy();w.velocity=np.array([1.,0,0]);w.distance=float(np.linalg.norm(w.target-p))
    a=shaped.step([0,0,0,0]);b=base.step([0,0,0,0])
    assert np.array_equal(a[0],b[0]) and a[2:4]==b[2:4]
    assert a[1]<b[1] and a[1]==pytest.approx(b[1]+a[4]['training_shaping_reward'])
    assert a[4]['base_reward']==b[1] and shaped.stats.transitions==1 and shaped.stats.active==1


def test_ordinary_evaluation_env_has_no_shaping_and_forbids_mixed_interventions():
    env=BrainEnv(batch=1,device='cpu',brain=Brain(matrix=sparse.eye(16,format='csr'),device='cpu',sensor_version=SENSOR_V3),mode='dense',layout_seeds=[230000],dynamics='coordinated',sensor_version=SENSOR_V3)
    assert type(env.worlds[0]) is FlightWorld and not hasattr(env,'reward_shaping')
    env.curriculum=object()
    with pytest.raises(ValueError,match='combine'):configure_risk_shaping(env,42)
    env.close()


def test_collision_filter_cannot_select_a_timeout_or_test_seed(tmp_path):
    from test_validation_trace import experiment
    folder,_=experiment(tmp_path)
    _,cases=validation_cases(folder,4,'collision')
    assert [r['seed'] for r in cases]==[140000]
    with pytest.raises(ValueError):validation_cases(folder,2,'test')


def test_draft_refuses_training_and_matched_selection_uses_validation(tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    draft=tmp_path/'draft.json';draft.write_text(json.dumps({'steps_per_seed':None,'batch':8,'rounds':2,'seeds':[42,73],'status':'draft-budget-required'}))
    with pytest.raises(ValueError,match='budget'):run_risk_comparison(draft,tmp_path/'run')
    assert not (tmp_path/'run').exists()
    from test_sensor_comparison import groups
    members=groups(tmp_path)
    for group in members:
        file=group/'selection.json';record=json.loads(file.read_text());record['evaluation_configuration']['sensor_version']=SENSOR_V3;file.write_text(json.dumps(record))
    winner=freeze_risk_winner([('baseline',members[0]),('risk',members[1])],tmp_path/'winner',{42:65536,73:65536})
    assert winner['selected_arm']=='risk' and not winner['final_test_evaluated']
    bad=members[0]/'experiment.json';state=json.loads(bad.read_text());state['seed_experiments'][0]['added_transitions']=1;bad.write_text(json.dumps(state))
    with pytest.raises(ValueError,match='budgets'):freeze_risk_winner([('baseline',members[0]),('risk',members[1])],tmp_path/'bad',{42:65536,73:65536})
