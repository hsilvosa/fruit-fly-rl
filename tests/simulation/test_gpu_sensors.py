import numpy as np
import pytest
import torch
from fly_rl.simulation.world import FlightWorld,RADIUS
from fly_rl.simulation.sensors import SENSOR_V6
from fly_rl.simulation.gpu_sensors import observe_batch

def test_chunked_empty_and_mixed_box_counts_match_scalar_geometry():
    torch.set_num_threads(2)
    worlds=[FlightWorld(370000+i,'dense',dynamics='coordinated',sensor_version=SENSOR_V6,map_profile='large') for i in range(9)]
    worlds[0].obstacles=[];worlds[1].obstacles=worlds[1].obstacles[:5]
    worlds[2].position=np.array([12.,24.,8.]);worlds[2].yaw=0.
    expected=np.stack([w.observe() for w in worlds])
    actual=observe_batch(worlds,device='cpu')
    np.testing.assert_allclose(actual,expected,atol=1e-6,rtol=1e-6)
    with pytest.raises(ValueError):observe_batch([],device='cpu')

@pytest.mark.parametrize('backend',['numpy','torch-cuda'])
def test_sensor_cache_is_the_new_episode_after_collision(backend):
    if backend=='torch-cuda' and not torch.cuda.is_available():pytest.skip('CUDA unavailable')
    from scipy import sparse
    from fly_rl.training.learning import BrainEnv
    from fly_rl.connectome.readout import InputGroupedBrain,GROUP_READOUT
    device='cuda' if backend=='torch-cuda' else 'cpu'
    brain=InputGroupedBrain(matrix=sparse.eye(500,format='csr',dtype=np.float32)*.2,batch=1,device=device,sensor_version=SENSOR_V6)
    env=BrainEnv(brain=brain,batch=1,device=device,seed=370000,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V6,
        map_profile='large',readout_version=GROUP_READOUT,sensor_backend=backend)
    env.reset();w=env.worlds[0];w.position=np.array([w.room[0]-RADIUS-.001,24.,8.]);w.yaw=0.
    _,_,done,infos=env.step(np.array([[1.,0.,0.,0.]],dtype=np.float32))
    assert done[0] and infos[0]['collision'] and w.ticks==0
    np.testing.assert_array_equal(env.latest_sensors[0],w.observe())
    assert not np.array_equal(env.latest_sensors[0],infos[0]['next_sensors'])
