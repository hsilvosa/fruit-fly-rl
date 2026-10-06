"""Goal-aligned fitting rejects diagonal clutter planes."""
import numpy as np
from fly_rl.navigation.portal_axis import AxisPortalController
from tests.navigation.test_portal_reference import observed_wall


def test_gap_center_and_solid_wall():
    c=AxisPortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    p=c.detect_portal(observed_wall())
    assert p is not None
    assert np.allclose(p['center'],[2,0,8],atol=.5)
    assert np.allclose(p['normal'],[1,0,0],atol=.1)
    assert c.detect_portal(observed_wall(False)) is None
