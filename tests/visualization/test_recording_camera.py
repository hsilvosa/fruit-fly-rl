import json
import numpy as np
from scipy import sparse
from fly_rl.visualization.camera import CameraRig
from fly_rl.simulation.sensors import SENSORS,SENSOR_NAMES,RAY_COUNT
from fly_rl.simulation.world import FlightWorld
from fly_rl.recordings.recording import FlightRecorder
from fly_rl.connectome.brain import Brain
from fly_rl.training.learning import BrainEnv

def test_more_sensors_and_approach():
    w=FlightWorld();w.velocity=np.array([3.,0,0]);w.yaw=0
    values=w.observe();assert values.shape==(269,) and len(SENSOR_NAMES)==SENSORS
    from fly_rl.simulation.sensors import DIRECTIONS
    forward=np.where((DIRECTIONS==[1,0,0]).all(axis=1))[0][0]
    assert values[RAY_COUNT+forward]==1
    assert w.observation_space.contains(values)

def test_camera_rotate_pan_zoom_and_free_move():
    rig=CameraRig();before=rig.pose()[0]
    rig.rotate(.2,.2);assert not np.allclose(before,rig.pose()[0])
    target=rig.target.copy();rig.pan(.2,.1);assert not np.allclose(target,rig.target)
    distance=rig.distance;rig.zoom(1);assert rig.distance<distance
    rig.rotate(0,100);assert rig.pitch<=1.5
    fly=np.array([3.,4.,2.]);rotation=np.eye(3)
    rig.cycle(fly,rotation);assert rig.mode=='chase'
    rig.cycle(fly,rotation);assert rig.mode=='free'
    before=rig.position.copy();rig.move(1,1,1,.1);assert not np.allclose(before,rig.position)
    rig.focus(fly);assert rig.mode=='orbit' and np.array_equal(rig.target,fly)

def test_shift_camera_boost_in_free_motion_and_zoom():
    normal=CameraRig();fast=CameraRig();normal.mode=fast.mode='free'
    start=normal.position.copy()
    normal.move(1,0,0,.1);fast.move(1,0,0,.1,fast=True)
    np.testing.assert_allclose(fast.position-start,(normal.position-start)*10)
    normal.position=start.copy();fast.position=start.copy()
    normal.zoom(1);fast.zoom(1,fast=True)
    np.testing.assert_allclose(fast.position-start,(normal.position-start)*10)
    normal.mode=fast.mode='orbit'
    normal.zoom(1);fast.zoom(1,fast=True)
    assert fast.distance<normal.distance

def test_recording_preserves_terminal_state_and_unique_runs(tmp_path):
    brain=Brain(batch=1,device='cpu',matrix=sparse.eye(8,format='csr',dtype=np.float32)*.9)
    env=BrainEnv(batch=1,brain=brain,device='cpu');features=env.reset()
    w=env.worlds[0];w.ticks=599
    before=w.snapshot();sensors=w.observe()
    next_features,rewards,dones,infos=env.step(np.zeros((1,4),dtype=np.float32))
    assert dones[0] and infos[0]['truncated']
    assert infos[0]['transition_state']['ticks']==600 and w.ticks==0
    recorder=FlightRecorder(tmp_path,{'test':True},chunk_size=1)
    recorder.event('room',0,{'snapshot':before})
    recorder.transition(1,0,sensors,features[0],np.zeros(4),before,infos[0],rewards[0])
    recorder.brain_snapshot(1,np.zeros(8));recorder.close()
    manifest=json.loads((recorder.path/'manifest.json').read_text())
    assert manifest['transition_count']==1 and manifest['status']=='closed'
    assert manifest['event_count']==1 and len(manifest['brain_snapshots'])==1
    with np.load(recorder.path/manifest['chunks'][0]['file'],allow_pickle=False) as chunk:
        assert chunk['sensors'].shape==(1,269) and chunk['brain_features'].shape==(1,256)
        assert np.array_equal(chunk['next_position'][0],infos[0]['transition_state']['position'])
        assert chunk['truncated'][0]
    other=FlightRecorder(tmp_path,{});assert other.path!=recorder.path;other.close()
