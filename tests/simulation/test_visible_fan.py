import numpy as np
import pytest
from scipy import sparse
from fly_rl.simulation.sensors import SENSOR_V3,SENSOR_V5,FAN_COUNT,FAN_RANGE,fan_directions,sensor_count,ray_count
from fly_rl.simulation.world import FlightWorld
from fly_rl.connectome.brain import Brain


def flip_first_aperture(w):
    route=np.asarray(w.reference_route);i=min(range(5),key=lambda k:abs(w.obstacles[4*k][0][0]+.35-w.position[0]))*4
    x=w.obstacles[i][0][0]+.35;y=48-route[1][1];z=16-route[1][2];yl,yh=y-1.6,y+1.6;zl,zh=z-1.6,z+1.6
    w.obstacles[i:i+4]=[(np.array([x-.35,0,0]),np.array([x+.35,yl,16])),(np.array([x-.35,yh,0]),np.array([x+.35,48,16])),(np.array([x-.35,yl,0]),np.array([x+.35,yh,zl])),(np.array([x-.35,yl,zh]),np.array([x+.35,yh,16]))]


@pytest.mark.parametrize('seed',range(370000,370016))
def test_long_dense_scan_distinguishes_the_first_aperture_counterfactual(seed):
    old=FlightWorld(seed,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V3,map_profile='large')
    new=FlightWorld(seed,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V5,map_profile='large')
    a=old.observe();b=new.observe();np.testing.assert_array_equal(a,b[:269])
    flip_first_aperture(old);flip_first_aperture(new)
    np.testing.assert_array_equal(a,old.observe())
    assert np.max(np.abs(new.observe()[269:]-b[269:]))>1e-4
    assert new.observe().shape==(1447,) and ray_count(SENSOR_V5)==717


def test_fan_has_unit_directions_and_is_centered_on_observed_goal_bearing():
    target=np.array([0,1.,0]);d=fan_directions(target)
    assert d.shape==(FAN_COUNT,3)
    np.testing.assert_allclose(np.linalg.norm(d,axis=1),1.)
    np.testing.assert_allclose(d.reshape(19,31,3)[9,15],target,atol=1e-7)


def test_fan_reads_nearest_obstacle_instead_of_a_hidden_opening_or_route():
    w=FlightWorld(1,sensor_version=SENSOR_V5,mode='empty');w.position=np.array([2.,6.,3.]);w.target=np.array([11.,6.,3.])
    w.obstacles=[(np.array([4.,5.,2.]),np.array([5.,7.,4.]))]
    d,r=w.fan_rays();assert r.reshape(19,31)[9,15]==pytest.approx(2.)
    w.reference_route=[np.array([99,99,99])]
    np.testing.assert_array_equal(r,w.fan_rays()[1])


def test_new_projection_retains_legacy_assignments_and_requires_versioned_shape():
    matrix=sparse.eye(32,format='csr')
    a=Brain(matrix=matrix,batch=1,device='cpu',sensor_version=SENSOR_V3)
    b=Brain(matrix=matrix,batch=1,device='cpu',sensor_version=SENSOR_V5)
    import torch
    assert torch.equal(a.input_index,b.input_index) and torch.equal(a.bucket,b.bucket)
    legacy=np.random.default_rng(42).uniform(-1,1,(1,269)).astype(np.float32)
    neutral=np.concatenate([legacy,np.full((1,FAN_COUNT),.5,dtype=np.float32),np.zeros((1,FAN_COUNT),dtype=np.float32)],axis=1)
    np.testing.assert_array_equal(a.step(legacy),b.step(neutral))
    assert a.fingerprint!=b.fingerprint
    with pytest.raises(ValueError):b.step(legacy)


def test_fan_does_not_change_physics_goals_or_legacy_sensor_values():
    kwargs=dict(seed=370004,mode='dense',dynamics='coordinated',map_profile='large')
    a=FlightWorld(sensor_version=SENSOR_V3,**kwargs);b=FlightWorld(sensor_version=SENSOR_V5,**kwargs)
    for _ in range(10):
        x=a.step([.1,0,.1,.1]);y=b.step([.1,0,.1,.1])
        np.testing.assert_array_equal(x[0],y[0][:269]);np.testing.assert_array_equal(a.position,b.position)
        assert x[1:4]==y[1:4]


def test_explicit_fan_transfer_copies_weights_without_modifying_source(tmp_path):
    import json
    from fly_rl.training.sensor_migration import migrate_sensors
    source=tmp_path/'source.zip';source.write_bytes(b'unchanged movement weights')
    source.with_suffix('.json').write_text(json.dumps({'sensor_version':SENSOR_V3,'fingerprint':'graph:reservoir-v2-'+SENSOR_V3+'-256-seed42-leak0.5-scale0.9'}))
    original=source.with_suffix('.json').read_bytes();target=tmp_path/'v5.zip'
    migrate_sensors(source,target,SENSOR_V5)
    assert source.read_bytes()==target.read_bytes() and source.with_suffix('.json').read_bytes()==original
    assert json.loads(target.with_suffix('.json').read_text())['sensor_version']==SENSOR_V5
