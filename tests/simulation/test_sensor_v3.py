import numpy as np
import pytest
from scipy import sparse
from fly_rl.simulation.world import FlightWorld,RADIUS
from fly_rl.simulation.sensors import SENSOR_VERSION,SENSOR_V3
from fly_rl.connectome.brain import Brain
from fly_rl.training.learning import BrainEnv


def test_room_scales_remove_dense_saturation_and_report_actual_yaw_rate():
    old=FlightWorld(90000,'dense',dynamics='coordinated')
    new=FlightWorld(90000,'dense',dynamics='coordinated',sensor_version=SENSOR_V3)
    for w in [old,new]:
        w.position=np.array([1.,1.,10.]);w.target=np.array([30.,30.,10.])
        w.yaw_rate=1.3;w.last_action[3]=-.8
    a,b=old.observe(),new.observe()
    assert a[259]==1 and a[-2]==1 and a[-1]==pytest.approx(-.8)
    assert b[259]==pytest.approx(np.linalg.norm(new.target-new.position)/np.linalg.norm(new.room-2*RADIUS))
    assert b[-2]==pytest.approx(10/12) and b[-1]==pytest.approx(.5)
    assert b.shape==(269,) and np.isfinite(b).all() and (np.abs(b)<=1).all()
    np.testing.assert_array_equal(a[:259],b[:259])


def test_versions_preserve_geometry_and_fixed_projection_but_change_fingerprint():
    a,b=FlightWorld(90001,'dense'),FlightWorld(90001,'dense',sensor_version=SENSOR_V3)
    np.testing.assert_array_equal(a.position,b.position);np.testing.assert_array_equal(a.obstacles,b.obstacles)
    brain_a=Brain(matrix=sparse.eye(8),device='cpu')
    brain_b=Brain(matrix=sparse.eye(8),device='cpu',sensor_version=SENSOR_V3)
    assert brain_a.fingerprint!=brain_b.fingerprint
    np.testing.assert_array_equal(brain_a.input_index,brain_b.input_index)
    np.testing.assert_array_equal(brain_a.bucket,brain_b.bucket)
    with pytest.raises(ValueError,match='contract mismatch'):
        BrainEnv(device='cpu',brain=brain_a,sensor_version=SENSOR_V3)


def test_yaw_rate_reset_and_legacy_angular_velocity():
    w=FlightWorld(1,dynamics='coordinated',sensor_version=SENSOR_V3)
    w.step([0,1,0,1]);assert w.observe()[-1]>0
    w.reset(seed=1);assert w.observe()[-1]==0
    legacy=FlightWorld(1,sensor_version=SENSOR_V3);legacy.step([0,0,0,1])
    assert legacy.observe()[-1]==pytest.approx(2.1/2.6)
    with pytest.raises(ValueError,match='Unknown sensor'):FlightWorld(sensor_version='unknown')
