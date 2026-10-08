"""Occupancy must use the declared clean neural range channel."""
import numpy as np
from fly_rl.navigation.portal_clean_map import CleanMapPortalController
from tests.navigation.test_portal_reference import observed_wall


def test_clean_observed_wall_is_mapped_despite_context_channel():
    c=CleanMapPortalController();c.position[:]=[0,0,8]
    clean=observed_wall(False)
    c.mapping_values=clean.copy();c.mapping_values[269:2069]=1
    c.integrate(clean)
    occupied=np.argwhere(c.evidence>=2)
    assert len(occupied)>0
    centers=c.origin+(occupied+.5)*c.res
    assert np.any((np.abs(centers[:,0]-2)<.6)&(np.abs(centers[:,2]-8)<1))
