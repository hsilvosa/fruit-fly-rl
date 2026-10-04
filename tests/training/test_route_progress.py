import numpy as np
import pytest
from fly_rl.training.route_progress import RouteDistance,RouteProgressWorld,RouteStats
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.sensors import SENSOR_V3


def field():
    route=[[2,2,2],[4,9,2],[6,9,2],[8,2,2]]
    boxes=[([4.8,0,0],[5.2,8,4])]
    return RouteDistance(route,boxes)


def test_required_detour_is_rewarded_although_direct_distance_increases():
    distance=field();a=np.array([4.,5.,2.]);b=np.array([4.,6.,2.]);goal=np.array([8.,2.,2.])
    assert np.linalg.norm(goal-b)>np.linalg.norm(goal-a)
    assert distance(b)<distance(a)
    # Connecting straight through a wall cannot obtain direct-distance credit.
    assert distance(a)>np.linalg.norm(goal-a)+3


def test_fixed_distance_field_has_no_waypoint_ratchet_or_loop_reward():
    distance=field();points=[[2,2,2],[4,5,2],[4,6,2],[4,5,2],[2,2,2]]
    values=[distance(p) for p in points]
    assert sum(a-b for a,b in zip(values,values[1:]))==pytest.approx(0.)
    assert distance([8,2,2])==pytest.approx(0.)


def test_shaping_keeps_physics_sensing_goal_and_terminal_state_identical():
    kwargs=dict(seed=370004,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V3,map_profile='large',layout_seeds=[370004])
    base=FlightWorld(**kwargs);stats=RouteStats();shaped=RouteProgressWorld(stats=stats,**kwargs)
    np.testing.assert_array_equal(base.observe(),shaped.observe())
    for _ in range(10):
        x=base.step([.1,0,.1,.1]);y=shaped.step([.1,0,.1,.1])
        np.testing.assert_array_equal(x[0],y[0]);np.testing.assert_array_equal(base.position,shaped.position)
        assert x[2:4]==y[2:4] and y[4]['base_reward']==x[1]
        assert y[1]==pytest.approx(x[1]-y[4]['direct_progress_reward']+y[4]['route_progress_reward'])
    assert stats.transitions==10 and base.observe().shape==(269,)


def test_collision_does_not_receive_a_false_route_distance_jump():
    stats=RouteStats();w=RouteProgressWorld(stats=stats,seed=1,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V3,map_profile='large',layout_seeds=[1])
    w.position=np.array([.17,1.,1.]);w.velocity=np.array([-2.,0,0]);w.distance=float(np.linalg.norm(w.target-w.position))
    _,r,t,tr,info=w.step([0,0,0,0])
    assert t and info['collision'] and not tr and r==pytest.approx(-5.02)
    assert info['route_distance_fallback'] and stats.outcomes['collision']==1


def test_route_progress_requires_declared_optimizer_layouts():
    with pytest.raises(ValueError,match='explicit'):
        RouteProgressWorld(stats=RouteStats(),mode='dense',map_profile='large')
