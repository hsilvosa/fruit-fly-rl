"""An approach may be refined, but not redirected to a different surface."""
import numpy as np
from fly_rl.navigation.portal_center_refinement import RefiningPortalController


def ready():
    c=RefiningPortalController();c.portal_phase='approach'
    c.portal=dict(center=np.array([2.,0.,8.]),normal=np.array([1.,0.,0.]),ray_support=1)
    return c


def test_stronger_same_plane_evidence_refines_center():
    c=ready()
    assert c.refine_portal(dict(center=np.array([2.,.6,8.]),normal=np.array([1.,0.,0.]),ray_support=10))
    assert 0<c.portal['center'][1]<.6
    assert c.portal['ray_support']==10


def test_different_plane_and_crossing_cannot_redirect():
    c=ready();center=c.portal['center'].copy()
    p=dict(center=np.array([4.,0.,8.]),normal=np.array([1.,0.,0.]),ray_support=10)
    assert not c.refine_portal(p)
    p['center']=np.array([2.,.6,8.]);c.portal_phase='cross'
    assert not c.refine_portal(p)
    assert np.array_equal(c.portal['center'],center)
