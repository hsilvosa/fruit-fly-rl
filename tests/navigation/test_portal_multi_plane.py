"""Multiple observed surfaces do not introduce generator inputs."""
import pytest
import numpy as np
from fly_rl.navigation.portal_multi_plane import MultiPlanePortalController
from tests.navigation.test_portal_reference import observed_wall


@pytest.mark.xfail(strict=True, reason="Recorded exp.5 regression: accepts a diagonal false wall fit")
def test_visible_opening_and_solid_surface():
    c=MultiPlanePortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    found=c.detect_portal(observed_wall())
    assert found is not None
    assert np.allclose(found['center'],[2,0,8],atol=.5)
    assert c.detect_portal(observed_wall(False)) is None


def test_completed_surface_and_independent_memory():
    a=MultiPlanePortalController();b=MultiPlanePortalController()
    a.completed_planes.append((np.array([1.,0.,8.]),np.array([1.,0.,0.])))
    assert not b.completed_planes
    assert not b.portal_crossings
