"""Refined portal candidates preserve solid-wall rejection and episode memory."""
import numpy as np
from fly_rl.navigation.portal_reference_refined import RefinedPortalController
from fly_rl.navigation.registry import VersionedPlannerPolicy


def test_room_contract_and_completed_plane_memory_reset():
    p=VersionedPlannerPolicy('1.3-exp.4','maze')
    p.controller.completed_planes.append((np.ones(3),np.array([1.,0.,0.])))
    p.reset()
    assert not p.controller.completed_planes and p.controller.room_size.tolist()==[64,64,20]


def test_no_observed_surface_means_no_invented_opening():
    c=RefinedPortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    v=np.zeros(3869);v[269:2069]=1
    assert c.detect_portal(v) is None
