import copy
import numpy as np
import pytest
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.sensors import SENSOR_V5
from fly_rl.training.waypoint_navigation import validate_plan,reset_training_world

def plan():
    return {'status':'approved','kind':'neural-waypoint-navigation-v1','steps':81920,
        'teacher_steps':16384,'student_steps':65536,'prior_substantive_transitions':786432,'cumulative_cap':868352,
        'reuse_rows':98304,'actor_updates':2048,'student_updates':4096,
        'teacher_initialization':'original_position_and_heading','student_continuity':'preserve_until_physical_terminal',
        'validation_seeds':list(range(430000,430008)),'optimization_layouts':list(range(370000,370112))}

def test_declared_scope_and_budget():
    validate_plan(plan())
    for key,value in [('steps',81928),('status','draft'),('teacher_initialization','aligned'),
        ('student_continuity','reset_each_round'),('cumulative_cap',868351)]:
        invalid=copy.deepcopy(plan());invalid[key]=value
        with pytest.raises(ValueError):validate_plan(invalid)

def test_exact_layout_preserves_original_start_and_pool():
    pool=list(range(370000,370112));seed=370016
    world=FlightWorld(42,'dense',pool,dynamics='coordinated',sensor_version=SENSOR_V5,map_profile='large')
    original=FlightWorld(seed,'dense',dynamics='coordinated',sensor_version=SENSOR_V5,map_profile='large')
    sensors=reset_training_world(world,seed)
    assert world.layout_seeds==pool and world.seed_value==seed
    assert np.array_equal(world.position,original.position)
    assert np.array_equal(world.velocity,original.velocity)
    assert world.yaw==original.yaw
    assert np.array_equal(sensors,original.observe())
    assert np.array_equal(np.array(world.obstacles),np.array(original.obstacles))

def test_student_episode_and_neural_history_survive_supervised_fit():
    import torch
    from scipy import sparse
    from fly_rl.connectome.readout import InputGroupedBrain,GROUP_READOUT
    from fly_rl.training.learning import BrainEnv,make_policy
    from fly_rl.training.waypoint_policy import transfer_waypoint_policy
    from fly_rl.training.guided_learning import collect_guided,fit_actor
    torch.set_num_threads(2)
    brain=InputGroupedBrain(batch=1,device='cpu',matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2,sensor_version=SENSOR_V5)
    env=BrainEnv(batch=1,device='cpu',brain=brain,seed=370000,mode='dense',dynamics='coordinated',
        sensor_version=SENSOR_V5,map_profile='large',history_frames=8,readout_version=GROUP_READOUT)
    model=transfer_waypoint_policy(make_policy(env),env)
    x=np.zeros((16,9,1447),np.float32);y=np.zeros((16,4),np.float32);waypoints=np.zeros((16,4),np.float32)
    rng=np.random.default_rng(42)
    features,teachers,result=collect_guided(env,model,x,y,0,8,rng,0.,waypoint_targets=waypoints,recover=True)
    assert result['teacher_actions']==0 and result['student_actions']==8
    before=features.copy();state=brain.state.clone();pose=env.worlds[0].position.copy();history=env.feature_history.copy()
    fit_actor(model,x,y,8,1,rng,batch_size=8,sampling_strategy='maneuver-start-balanced-v2',waypoint_targets=waypoints)
    assert torch.equal(state,brain.state) and np.array_equal(pose,env.worlds[0].position)
    assert np.array_equal(history,env.feature_history) and env.worlds[0].ticks==8
    collect_guided(env,model,x,y,8,8,rng,0.,features,teachers,waypoint_targets=waypoints,recover=True)
    assert env.worlds[0].ticks==16 and env.history_ticks[0]==16
    assert np.array_equal(x[8],before[0]) and model.num_timesteps==16
    assert np.isfinite(waypoints).all()
