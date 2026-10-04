import numpy as np
import pytest
from scipy import sparse
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.sensors import SENSOR_V3,SENSOR_V4,sensor_names
from fly_rl.connectome.brain import Brain
from fly_rl.training.learning import BrainEnv


def test_deadline_reset_and_terminal_preserve_previous_sensor_values():
    a=FlightWorld(7,mode='dense',map_profile='large',sensor_version=SENSOR_V3)
    b=FlightWorld(7,mode='dense',map_profile='large',sensor_version=SENSOR_V4)
    assert b.observe().shape==(270,)
    np.testing.assert_array_equal(a.observe(),b.observe()[:-1])
    assert b.observe()[-1]==1.
    b.ticks=b.episode_limit//2
    assert b.observe()[-1]==pytest.approx(1-b.ticks/b.episode_limit)
    b.ticks=b.episode_limit-1
    observation,_,_,truncated,_=b.step(np.zeros(4))
    assert truncated and observation[-1]==0.
    b.reset(seed=7)
    assert b.observe()[-1]==1. and b.observation_space.contains(b.observe())
    assert sensor_names(SENSOR_V4)[-1]=='remaining_time_fraction'


def test_deadline_enters_brain_without_remapping_original_projection():
    matrix=sparse.eye(1024,format='csr')*.1
    a=Brain(device='cpu',matrix=matrix,sensor_version=SENSOR_V3)
    b=Brain(device='cpu',matrix=matrix,sensor_version=SENSOR_V4)
    x=np.random.default_rng(2).uniform(-1,1,(1,269)).astype(np.float32)
    np.testing.assert_array_equal(a.step(x),b.step(np.column_stack([x,[0.]])))
    b.reset();empty=b.step(np.zeros((1,270),dtype=np.float32))
    b.reset();clock=np.zeros((1,270),dtype=np.float32);clock[:,-1]=1.
    assert not np.allclose(empty,b.step(clock))
    assert a.fingerprint!=b.fingerprint
    with pytest.raises(ValueError):b.step(x)


def test_terminal_clock_is_recorded_before_independent_episode_reset():
    brain=Brain(batch=2,device='cpu',matrix=sparse.eye(1024,format='csr')*.1,sensor_version=SENSOR_V4)
    env=BrainEnv(batch=2,device='cpu',brain=brain,sensor_version=SENSOR_V4,mode='dense',map_profile='large',timeout_as_terminal=True)
    env.reset();env.worlds[0].ticks=env.worlds[0].episode_limit-1
    env.worlds[1].ticks=50
    _,_,dones,infos=env.step(np.zeros((2,4)))
    assert dones.tolist()==[True,False]
    assert infos[0]['next_sensors'][-1]==0.
    assert env.worlds[0].observe()[-1]==1.
    assert infos[0]['timeout_failure_terminal'] and not infos[0]['TimeLimit.truncated']
    assert env.worlds[1].ticks==51


def test_explicit_deadline_transfer_keeps_archive_bytes(tmp_path):
    import json
    from fly_rl.training.sensor_migration import migrate_sensors
    from fly_rl.training.learning import checkpoint_sensor_version
    source=tmp_path/'old.zip';source.write_bytes(b'unchanged-policy-and-optimizer')
    source.with_suffix('.json').write_text(json.dumps({'sensor_version':SENSOR_V3,'fingerprint':'graph:reservoir-v2-'+SENSOR_V3+'-256-seed42-leak0.5-scale0.9'}))
    original=source.with_suffix('.json').read_bytes()
    dest=tmp_path/'deadline.zip'
    migrate_sensors(source,dest,SENSOR_V4)
    assert source.read_bytes()==dest.read_bytes()
    assert source.with_suffix('.json').read_bytes()==original
    assert checkpoint_sensor_version(dest)==SENSOR_V4
