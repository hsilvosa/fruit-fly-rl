"""Angular wall support changes with range; gap inference remains observable."""
import numpy as np
from fly_rl.navigation.portal_near_wall import NearWallPortalController
from tests.navigation.test_portal_reference import observed_wall


def test_near_wall_candidate_retains_gap_and_solid_checks():
    c=NearWallPortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    found=c.detect_portal(observed_wall())
    assert found is not None
    assert np.allclose(found['center'],[2,0,8],atol=.5)
    assert c.detect_portal(observed_wall(False)) is None


def test_unobserved_surface_has_no_opening():
    c=NearWallPortalController();c.initial_goal=np.array([60.,0.,10.]);c.position[2]=10
    v=np.zeros(3869);v[269:2069]=1
    assert c.detect_portal(v) is None
