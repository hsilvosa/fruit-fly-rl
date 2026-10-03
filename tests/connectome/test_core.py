import numpy as np
import pytest
from scipy import sparse
from fly_rl.simulation.world import FlightWorld,segment_box,ray_box,DIRECTIONS,ROOM,RADIUS
from fly_rl.connectome.brain import Brain,SENSORS

def test_swept_collision_and_parallel_rays():
    low=np.array([2.,2.,2.]);high=low+1
    assert segment_box(np.array([0.,2.5,2.5]),np.array([5.,2.5,2.5]),low,high)
    assert not segment_box(np.array([0.,1.,2.5]),np.array([5.,1.,2.5]),low,high)
    assert ray_box(np.array([0.,2.5,2.5]),np.array([1.,0.,0.]),low,high)==2
    assert np.isinf(ray_box(np.array([0.,1.,2.5]),np.array([1.,0.,0.]),low,high))

def test_rays_and_observations():
    w=FlightWorld(10);w.obstacles=[];w.position=np.array([6.,6.,3.]);w.yaw=0
    directions,lengths=w.rays()
    assert len(lengths)==128 and np.allclose(np.linalg.norm(directions,axis=1),1)
    index=np.where((DIRECTIONS==[0,0,1]).all(axis=1))[0][0]
    assert lengths[index]==3
    assert w.observation_space.contains(w.observe())

def test_motion_and_terminal_cases():
    w=FlightWorld(0);before=w.position.copy()
    obs,reward,done,truncated,info=w.step([1,0,0,0])
    assert w.position[0]>before[0] and np.isfinite(reward)
    w.position=np.array([ROOM[0]-RADIUS-.001,6,3.]);w.velocity=np.array([3.,0,0])
    _,_,done,_,info=w.step([1,0,0,0]);assert done and info['collision']
    w.reset();w.target=w.position.copy();_,_,done,_,info=w.step([0,0,0,0]);assert done and info['success']
    w.reset();w.ticks=599;_,_,done,truncated,_=w.step([0,0,0,0]);assert truncated and not done
    with pytest.raises(ValueError): w.step([np.nan,0,0,0])

def test_reproducible_rooms_have_free_corridors():
    w=FlightWorld(4);other=FlightWorld(4)
    assert np.array_equal(w.position,other.position)
    assert np.array_equal(w.target,other.target)
    for seed in range(50):
        w.reset(seed=seed)
        # A route via x=1,y=1,z=5 then x=11,y=1,z=5 is clear.
        route=[w.position,np.array([1.,1.,5.]),np.array([11.,1.,5.]),w.target]
        for start,end in zip(route,route[1:]):
            assert not any(segment_box(start,end,low-RADIUS,high+RADIUS) for low,high in w.obstacles)

def test_brain_orientation_recurrence_and_reset():
    # Test fixture only; application never substitutes this for the real dataset.
    m=sparse.csr_matrix(np.array([[0.,0.],[.9,0.]],dtype=np.float32))
    b=Brain(batch=2,device='cpu',matrix=m)
    b.state[:]=0.;b.state[0,:]=.5
    b.step(np.zeros((2,SENSORS),dtype=np.float32))
    assert np.allclose(b.state[0].numpy(),.25)
    assert np.allclose(b.state[1].numpy(),.5*np.tanh(.45))
    second=b.state[:,1].clone();b.reset([0])
    assert (b.state[:,0]==0).all() and (b.state[:,1]==second).all()
    for _ in range(100): features=b.step(np.ones((2,SENSORS),dtype=np.float32))
    assert np.isfinite(features).all() and (b.state.abs()<=1).all()

def test_checkpoint_configuration_mismatch(tmp_path):
    import json
    from fly_rl.training.learning import load_model
    b=Brain(batch=1,device='cpu',matrix=sparse.eye(2,format='csr',dtype=np.float32))
    p=tmp_path/'policy.zip';p.with_suffix('.json').write_text(json.dumps({'fingerprint':'different'}))
    with pytest.raises(ValueError,match='mismatch'): load_model(p,b)

def test_vec_reset_does_not_advance_continuing_brain():
    from fly_rl.training.learning import BrainEnv
    b=Brain(batch=2,device='cpu',matrix=sparse.eye(8,format='csr',dtype=np.float32)*.9)
    env=BrainEnv(batch=2,brain=b,device='cpu');env.reset()
    env.worlds[0].ticks=599
    sensors=[]
    # Compute expected continuing state in an independent identical reservoir.
    expected=Brain(batch=2,device='cpu',matrix=sparse.eye(8,format='csr',dtype=np.float32)*.9)
    expected.state.copy_(b.state)
    sensor1=env.worlds[1].observe()
    import copy
    other=copy.deepcopy(env.worlds[1])
    sensor1=other.step([0,0,0,0])[0]
    expected.step(np.array([sensor1,sensor1]))
    _,_,done,infos=env.step(np.zeros((2,4)))
    assert done[0] and not done[1]
    assert np.allclose(b.state[:,1],expected.state[:,1])
    assert 'terminal_observation' in infos[0]
