"""Opening centers use observed surface support, not hidden aperture bounds."""
import numpy as np
from fly_rl.navigation.portal_clearance_center import ClearancePortalController
from tests.navigation.test_portal_reference import observed_wall


def test_clearance_center_inside_observed_gap():
    c=ClearancePortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    p=c.detect_portal(observed_wall())
    assert p is not None
    assert np.allclose(p['center'],[2,0,8],atol=.7)
    assert c.detect_portal(observed_wall(False)) is None


def test_no_observation_has_no_clearance_center():
    c=ClearancePortalController();c.initial_goal=np.array([60.,0.,10.]);c.position[2]=10
    v=np.zeros(3869);v[269:2069]=1
    assert c.detect_portal(v) is None


def test_actual_maze_width_and_height_observed_fixture():
    from fly_rl.simulation.world import FlightWorld
    from fly_rl.simulation.sensors import SENSOR_V6
    w=FlightWorld(0,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V6,map_profile='maze')
    w.position=np.array([6.,32.,10.]);w.target=np.array([62.,32.,10.]);w.yaw=0.
    w.obstacles=[(np.array(a),np.array(b)) for a,b in [
        ([8.,0.,0.],[8.7,30.8,20.]),([8.,33.2,0.],[8.7,64.,20.]),
        ([8.,30.8,0.],[8.7,33.2,8.6]),([8.,30.8,11.4],[8.7,33.2,20.])]]
    c=ClearancePortalController((64.,64.,20.));c.position[:]=[0,0,10];c.initial_goal=np.array([56.,0.,10.])
    portal=c.detect_portal(w.observe())
    assert portal is not None
    assert abs(portal['center'][0]-2.)<.12
    assert abs(portal['center'][1])<1.04
    assert 8.76<portal['center'][2]<11.24
