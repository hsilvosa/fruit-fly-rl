"""Surface fallback preserves solid-wall checks and limits terminal handover."""
import numpy as np
from fly_rl.navigation.portal_surface_fallback import SurfaceFallbackController
from fly_rl.navigation.room_aware import RoomAwareController
from tests.navigation.test_portal_reference import observed_wall


def test_supported_surface_requires_observed_gap():
    c=SurfaceFallbackController();c.position[:]=[0,0,8];c.initial_goal=np.array([40.,0.,8.])
    found=c.detect_portal(observed_wall())
    assert found is not None
    assert np.allclose(found['center'],[2,0,8],atol=.5)
    assert c.detect_portal(observed_wall(False)) is None


def test_close_handover_keeps_occupancy_planner(monkeypatch):
    c=SurfaceFallbackController();c.position[:]=[0,0,8];c.initial_goal=np.array([2.5,0.,8.])
    c.portal=dict(center=np.array([2.,0.,8.]),normal=np.array([1.,0.,0.]))
    calls=[]
    monkeypatch.setattr(RoomAwareController,'plan',lambda self,goal:calls.append(goal.copy()))
    c.plan(c.initial_goal)
    assert c.portal is None
    assert len(calls)==1 and np.array_equal(calls[0],c.initial_goal)
    assert c.debug['portal_phase']=='goal-handover'
