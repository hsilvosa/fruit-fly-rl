"""Beacon alignment filters surfaces without consuming hidden geometry."""
import numpy as np
from fly_rl.navigation.portal_clean_axis import CleanAxisPortalController
from tests.navigation.test_portal_reference import observed_wall


def test_clean_axis_observed_gap_and_solid_surface():
    c=CleanAxisPortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    p=c.detect_portal(observed_wall())
    assert p is not None and p['normal'][0]>.99
    assert c.detect_portal(observed_wall(False)) is None


def test_unseen_surface_has_no_portal():
    c=CleanAxisPortalController();c.initial_goal=np.array([60.,0.,10.]);c.position[2]=10
    v=np.zeros(3869);v[269:2069]=1
    assert c.detect_portal(v) is None
