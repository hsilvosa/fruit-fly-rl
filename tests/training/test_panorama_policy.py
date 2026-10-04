import copy
import numpy as np
import pytest
import torch
from gymnasium.spaces import Box
from fly_rl.training.panorama_policy import PanoramicBrainHistory,CircularConv
from fly_rl.training.panorama_navigation import validate_plan

def test_horizontal_wrap_and_neural_policy_backward():
    torch.set_num_threads(2)
    conv=CircularConv(2,8);x=torch.randn(2,2,25,72)
    assert torch.allclose(conv(torch.roll(x,5,-1)),torch.roll(conv(x),5,-1),atol=1e-6)
    model=PanoramicBrainHistory(Box(-np.inf,np.inf,(9,3869),dtype=np.float32))
    y,wp=model.forward_with_waypoint(torch.randn(2,9,3869)*.08)
    assert y.shape==(2,192) and wp.shape==(2,4)
    loss=y.square().mean()+wp.square().mean();loss.backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
    with pytest.raises(ValueError):PanoramicBrainHistory(Box(-np.inf,np.inf,(9,1447),dtype=np.float32))

def test_plan_rejects_changed_budget_and_episode_resets():
    p={'status':'approved','kind':'panoramic-neural-navigation-v1','steps':98304,'teacher_steps':65536,'student_steps':32768,
       'prior_substantive_transitions':868352,'cumulative_cap':966656,'reuse_rows':0,'actor_updates':8192,'student_updates':4096,
       'teacher_initialization':'original_position_and_heading','student_continuity':'preserve_until_physical_terminal',
       'validation_seeds':list(range(430000,430008)),'optimization_layouts':list(range(370000,370112))}
    validate_plan(p)
    for key,value in [('steps',100000),('actor_updates',9000),('reuse_rows',98304),('student_continuity','reset_each_round')]:
        bad=copy.deepcopy(p);bad[key]=value
        with pytest.raises(ValueError):validate_plan(bad)


def test_trace_records_reset_and_terminal_action_phases():
    from scipy import sparse
    from fly_rl.connectome.readout import InputGroupedBrain,GROUP_READOUT
    from fly_rl.simulation.sensors import SENSOR_V6
    from fly_rl.simulation.world import RADIUS
    from fly_rl.training.learning import BrainEnv
    from fly_rl.training.guided_learning import collect_guided
    brain=InputGroupedBrain(matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2,batch=1,device='cpu',sensor_version=SENSOR_V6)
    env=BrainEnv(brain=brain,batch=1,device='cpu',seed=370000,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V6,map_profile='large',history_frames=8,readout_version=GROUP_READOUT)
    features=env.reset();w=env.worlds[0];w.position=np.array([w.room[0]-RADIUS-.001,24.,8.]);w.yaw=0.
    brain.reset();features=env._pack_features(brain.step(np.array([w.observe()])))
    class ForwardPolicy:
        num_timesteps=0
        def predict(self,features,deterministic=True):return np.array([[1.,0.,0.,0.]],dtype=np.float32),None
    trace={'executed_actions':np.zeros((2,4),np.float32),'position':np.zeros((2,3),np.float32),'velocity':np.zeros((2,3),np.float32),
        'yaw':np.zeros(2,np.float32),'layout_seed':np.zeros(2,np.int64),'teacher_used':np.zeros(2,bool),
        'episode_tick':np.zeros(2,np.int64),'yaw_rate':np.zeros(2,np.float32),'previous_actions':np.zeros((2,4),np.float32),'outcome_flags':np.zeros((2,3),bool)}
    collect_guided(env,ForwardPolicy(),np.zeros((2,9,3869),np.float32),np.zeros((2,4),np.float32),0,2,np.random.default_rng(1),0.,features=features,trace=trace,recover=True)
    np.testing.assert_array_equal(trace['outcome_flags'][0],[False,True,False])
    np.testing.assert_array_equal(trace['episode_tick'],[0,0])
    assert trace['position'][0,0]>47.8 and trace['position'][1,0]<47.8
    np.testing.assert_array_equal(trace['previous_actions'],np.zeros((2,4)))
