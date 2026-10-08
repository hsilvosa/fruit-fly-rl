"""Openings are inferred from ray observations, not supplied from the generator."""
import numpy as np
from fly_rl.navigation.portal_reference import PortalReferenceController
from fly_rl.simulation.world import FlightWorld
from fly_rl.simulation.sensors import SENSOR_V6


def observed_wall(opening=True):
    w=FlightWorld(0,mode='dense',dynamics='coordinated',sensor_version=SENSOR_V6,map_profile='large')
    w.position=np.array([6.,24.,8.]);w.target=np.array([46.,24.,8.]);w.yaw=0.
    if opening:
        w.obstacles=[(np.array(a),np.array(b)) for a,b in [
            ([8.,0.,0.],[8.7,22.4,16.]),([8.,25.6,0.],[8.7,48.,16.]),
            ([8.,22.4,0.],[8.7,25.6,6.4]),([8.,22.4,9.6],[8.7,25.6,16.])]]
    else:w.obstacles=[(np.array([8.,0.,0.]),np.array([8.7,48.,16.]))]
    return w.observe()


def controller():
    c=PortalReferenceController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    return c


def test_visible_gap_inferred_from_ranges_only():
    portal=controller().detect_portal(observed_wall())
    assert portal is not None
    assert np.allclose(portal['normal'],[1,0,0],atol=.1)
    assert np.allclose(portal['center'],[2,0,8],atol=.5)
    assert portal['ray_support']>=3


def test_solid_wall_does_not_fabricate_an_opening():
    assert controller().detect_portal(observed_wall(False)) is None


def test_maximum_range_without_a_surface_has_no_portal():
    v=np.zeros(3869);v[269:2069]=1
    assert controller().detect_portal(v) is None
