"""A committed goal tolerates brief observation changes with braking intact."""
import numpy as np
from fly_rl.navigation.portal_committed_goal import CommittedVisibleGoalController
from tests.navigation.test_portal_stable_goal import values


def test_commitment_survives_short_loss_then_releases():
    c=CommittedVisibleGoalController((64.,64.,20.));v=values(16.)
    for _ in range(20):c.update(v)
    assert c.goal_handover
    near=np.argsort(c.directions@np.array([1.,0.,0.]))[-4:];v[269+near[0]]=1./24
    for _ in range(19):c.update(v)
    assert c.goal_handover
    c.update(v);assert not c.goal_handover


def test_commitment_resets_between_instances():
    a=CommittedVisibleGoalController((64.,64.,20.));b=CommittedVisibleGoalController((64.,64.,20.))
    a.update(values(2.));assert a.goal_handover
    assert not b.goal_handover and b.blocked_ticks==0
