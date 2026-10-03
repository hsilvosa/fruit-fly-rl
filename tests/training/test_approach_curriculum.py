import copy,json
import numpy as np
import pytest
from scipy import sparse
from fly_rl.training.approach_curriculum import ApproachSchedule,ApproachWorld,configure_curriculum,VERSION
from fly_rl.training.approach_comparison import run_approach_comparison,freeze_approach_winner
from fly_rl.training.learning import BrainEnv
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.world import FlightWorld,RADIUS,segment_box
from fly_rl.simulation.sensors import SENSOR_V3


def world(seed=42,total=1000,offset=0):
    return ApproachWorld(seed=seed,mode='dense',layout_seeds=[200000,200001],dynamics='coordinated',sensor_version=SENSOR_V3,schedule=ApproachSchedule(total,offset))


def test_schedule_is_global_and_finishes_at_half_budget():
    schedule=ApproachSchedule(1000)
    assert schedule.probability==.5
    schedule.transitions=250;assert schedule.probability==.25
    schedule.transitions=500;assert schedule.probability==0
    schedule.transitions=1000;assert schedule.probability==0
    assert ApproachSchedule(1000,250).probability==.25
    with pytest.raises(ValueError):ApproachSchedule(0)


def test_near_resets_preserve_training_geometry_and_clear_direct_path():
    found=0
    for seed in range(16):
        w=world(seed);assert w.seed_value in [200000,200001]
        original=FlightWorld(w.seed_value,'dense',dynamics='coordinated',sensor_version=SENSOR_V3)
        assert np.array_equal(w.target,original.target) and np.array_equal(w.obstacles,original.obstacles)
        if w.schedule.resets['near']:
            found+=1;assert .7<=w.distance<=3.
            assert not any(segment_box(w.position,w.target,low-RADIUS-.02,high+RADIUS+.02) for low,high in w.obstacles)
            assert (w.position>=RADIUS+.02).all() and (w.position<=w.room-RADIUS-.02).all()
    assert found>=2


def test_ordinary_resets_and_rewards_remain_identical():
    w=world(offset=500);ordinary=FlightWorld(42,'dense',[200000,200001],'coordinated',SENSOR_V3)
    assert np.array_equal(w.position,ordinary.position) and np.array_equal(w.observe(),ordinary.observe())
    for action in [[.3,.2,.1,-.2],[.4,0,0,0]]:
        a=w.step(action);b=ordinary.step(action)
        assert a[1:4]==b[1:4] and np.array_equal(a[0],b[0])
    w.target=w.position.copy()+np.array([.46,0,0]);w.velocity[:]=0
    _,_,done,_,info=w.step([0,0,0,0]);assert not info['success']
    w.target=w.position.copy()+np.array([.44,0,0]);w.velocity[:]=0
    _,_,done,_,info=w.step([0,0,0,0]);assert info['success']


def test_episode_resets_use_shared_schedule_and_reset_brain_independently():
    brain=Brain(matrix=sparse.eye(16,format='csr'),batch=2,device='cpu',sensor_version=SENSOR_V3)
    env=BrainEnv(batch=2,brain=brain,device='cpu',mode='dense',dynamics='coordinated',sensor_version=SENSOR_V3,layout_seeds=[200000])
    schedule=configure_curriculum(env,128,0,42);env.seed(42);before=env.reset()
    env.worlds[0].episode_limit=1
    after,_,done,info=env.step(np.zeros((2,4)))
    assert done.tolist()==[True,False] and schedule.transitions==2
    assert env.worlds[0].ticks==0 and env.worlds[1].ticks==1
    assert np.isfinite(after).all() and 'terminal_observation' in info[0]
    assert env.reset_infos[0]['curriculum']['transition_offset']==2
    env.close()


def test_draft_cannot_start_and_curriculum_rejects_validation_worlds(tmp_path):
    path=tmp_path/'draft.json';path.write_text(json.dumps({'steps_per_seed':None,'batch':8,'rounds':2,'seeds':[42,73],'status':'draft-budget-required'}))
    with pytest.raises(ValueError,match='budget'):run_approach_comparison(path,tmp_path/'run')
    assert not (tmp_path/'run').exists()
    with pytest.raises(ValueError,match='training layouts'):ApproachWorld(mode='dense',schedule=ApproachSchedule(1000))


def test_matched_arm_selection_uses_validation_and_declared_budgets(tmp_path,monkeypatch):
    from test_sensor_comparison import groups
    monkeypatch.chdir(tmp_path);members=groups(tmp_path)
    for group in members:
        file=group/'selection.json';frozen=json.loads(file.read_text());frozen['evaluation_configuration']['sensor_version']=SENSOR_V3;file.write_text(json.dumps(frozen))
    winner=freeze_approach_winner([('curriculum',members[1]),('baseline',members[0])],tmp_path/'winner',{42:65536,73:65536})
    assert winner['selected_arm']=='curriculum' and winner['training']['added_transitions']==262144
    assert not winner['final_test_evaluated']
