"""Visibility handover distinguishes a near beacon from flickering distant evidence."""
import numpy as np
from fly_rl.navigation.portal_stable_goal import StableVisibleGoalController


def values(distance):
    v=np.zeros(3869);v[256]=1.;v[259]=distance/np.linalg.norm(np.array([64.,64.,20.])-.32)
    v[267]=.5;v[269:2069]=1.
    return v


def test_distant_visibility_requires_continuity_and_resets_on_hit():
    c=StableVisibleGoalController((64.,64.,20.));v=values(16.)
    for _ in range(19):c.update(v)
    assert not c.goal_handover
    c.update(v);assert c.goal_handover
    nearest=np.argsort(c.directions@np.array([1.,0.,0.]))[-4:]
    v[269+nearest[0]]=1./24;c.update(v)
    assert not c.goal_handover and c.visible_ticks==0


def test_close_visible_goal_handover_and_reset_isolation():
    a=StableVisibleGoalController((64.,64.,20.));b=StableVisibleGoalController((64.,64.,20.))
    a.update(values(2.))
    assert a.goal_handover
    assert not b.goal_handover and b.visible_ticks==0
