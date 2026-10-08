"""A goal handover requires nearby observed rays beyond the beacon distance."""
import numpy as np
from fly_rl.navigation.portal_visible_goal import VisibleGoalController


def test_visible_goal_accepts_open_corridor_rejects_near_hit():
    c=VisibleGoalController();c.local_goal=np.array([2.,0.,0.])
    v=np.zeros(3869);v[269:2069]=1
    assert c.direct_goal_visible(v)
    nearest=np.argsort(c.directions@np.array([1.,0.,0.]))[-4:]
    v[269+nearest[0]]=1./24
    assert not c.direct_goal_visible(v)


def test_goal_outside_range_is_not_certified_visible():
    c=VisibleGoalController();c.local_goal=np.array([30.,0.,0.])
    v=np.ones(3869)
    assert not c.direct_goal_visible(v)
