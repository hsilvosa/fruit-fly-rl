"""Room contracts and local reference commitment without true-map inputs."""
import numpy as np
import pytest
from fly_rl.navigation.room_aware import RoomAwareController
from fly_rl.navigation.registry import VersionedPlannerPolicy


def test_maze_neural_goal_and_altitude_decode_declared_dimensions():
    c=RoomAwareController((64,64,20))
    v=np.zeros(3869);v[256]=1;v[259]=.5;v[267]=.7
    goal=c.update(v)
    assert goal[0]==pytest.approx(.5*np.linalg.norm(np.array([64,64,20])-.32))
    assert goal[2]==pytest.approx(14)
    assert c.valid(c.cells(np.array([80.,0.,19.5])))
    assert c.valid(c.cells(goal))


def test_legacy_controller_cannot_silently_decode_maze():
    with pytest.raises(ValueError,match='support'):
        VersionedPlannerPolicy('1.2','maze')
    policy=VersionedPlannerPolicy('1.3-exp.1','maze')
    assert policy.specification['room_size']==[64.,64.,20.]


def test_reference_retains_direction_until_reached_or_blocked():
    c=RoomAwareController();c.position[:]=[0,0,5];c.initial_goal=np.array([10.,0.,5.])
    c.tight=False;c.cost=np.ones(c.shape)
    c.route=[np.array([3.,0.,5.])]
    assert np.array_equal(c.target(),[3.,0.,0.])
    c.route=[np.array([0.,3.,5.])];c.tick=20
    assert np.array_equal(c.target(),[3.,0.,0.])
    assert c.debug['reference_retained']
    c.cost[tuple(c.cells(np.array([1.5,0,5])))]=np.inf
    assert np.array_equal(c.target(),[0.,3.,0.])
    assert not c.debug['reference_retained']


def test_maze_reset_clears_reference_and_independent_map():
    p=VersionedPlannerPolicy('1.3-exp.1','maze');old=p.controller
    old.reference=np.array([1.,2.,3.]);old.evidence.fill(3)
    p.reset()
    assert p.controller.reference is None and not p.controller.evidence.any()
    assert p.controller.shape==old.shape
