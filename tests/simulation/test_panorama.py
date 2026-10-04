import numpy as np
from scipy import sparse
from fly_rl.simulation.sensors import SENSOR_V3,SENSOR_V6,PANORAMA_COUNT,panorama_directions,sensor_count
from fly_rl.simulation.world import FlightWorld
from fly_rl.connectome.brain import Brain

def test_panorama_has_unit_rays_and_independent_target_bearing():
    rays=panorama_directions();assert rays.shape==(1800,3)
    np.testing.assert_allclose(np.linalg.norm(rays,axis=1),1.)
    w=FlightWorld(1,mode='empty',sensor_version=SENSOR_V6)
    w.position=np.array([2.,6.,3.]);w.yaw=0.;w.obstacles=[(np.array([4.,5.7,2.7]),np.array([4.4,6.3,3.3]))]
    d,r=w.fan_rays();assert abs(r[12*72+36]-2.)<1e-6
    w.target=np.array([1.,1.,1.]);np.testing.assert_array_equal(r,w.fan_rays()[1])
    w.yaw=np.pi/2;np.testing.assert_allclose(w.fan_rays()[0][12*72+36],[0.,1.,0.],atol=1e-6)

def test_version_does_not_change_rooms_flight_or_existing_channels():
    options={'seed':370000,'mode':'dense','dynamics':'coordinated','map_profile':'large'}
    old=FlightWorld(sensor_version=SENSOR_V3,**options);new=FlightWorld(sensor_version=SENSOR_V6,**options)
    assert new.observe().shape==(3869,) and sensor_count(SENSOR_V6)==3869
    np.testing.assert_array_equal(old.observe(),new.observe()[:269])
    np.testing.assert_array_equal(np.asarray(old.obstacles),np.asarray(new.obstacles))
    for action in [np.array([.3,0.,.2,-.4]),np.array([-.2,0.,-.1,.2])]:
        old.step(action);new.step(action)
        np.testing.assert_array_equal(old.position,new.position)
        np.testing.assert_array_equal(old.observe(),new.observe()[:269])

def test_neutral_panorama_preserves_original_sparse_recurrence():
    matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2
    old=Brain(matrix=matrix,batch=2,device='cpu',sensor_version=SENSOR_V3)
    new=Brain(matrix=matrix,batch=2,device='cpu',sensor_version=SENSOR_V6)
    base=np.random.default_rng(3).uniform(-1,1,(2,269)).astype(np.float32)
    extended=np.concatenate([base,np.full((2,PANORAMA_COUNT),.5,dtype=np.float32),np.zeros((2,PANORAMA_COUNT),dtype=np.float32)],axis=1)
    for _ in range(3):
        old.step(base);new.step(extended)
        np.testing.assert_array_equal(old.state.numpy(),new.state.numpy())
