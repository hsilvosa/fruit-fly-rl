"""Goal priority uses occupancy evidence and never promises a clear near route."""
import numpy as np
from fly_rl.navigation.portal_goal_priority import GoalPriorityPortalController


def test_near_goal_priority_and_no_crossing_past_goal():
    c=GoalPriorityPortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([4.,0.,8.])
    assert c.prefer_goal_route()
    p=dict(center=np.array([3.,0.,8.]),normal=np.array([1.,0.,0.]))
    assert not c.portal_leads_toward_goal(p)
    p['center']=np.array([2.,0.,8.])
    assert c.portal_leads_toward_goal(p)


def test_unknown_segment_is_not_known_free():
    c=GoalPriorityPortalController();c.position[:]=[0,0,8];c.initial_goal=np.array([8.,0.,8.]);c.cost=c.grid()
    assert not c.prefer_goal_route()
    cells=c.cells(c.position+(c.initial_goal-c.position)*np.linspace(0,1,40)[:,None]);c.evidence[tuple(cells.T)]=-8;c.cost=c.grid()
    assert c.prefer_goal_route()
    c.evidence[tuple(cells[20])]=3;c.cost=c.grid()
    assert not c.prefer_goal_route()
