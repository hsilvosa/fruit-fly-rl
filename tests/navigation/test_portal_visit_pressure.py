"""Visit pressure affects route preference without rewriting observations."""
import numpy as np
from fly_rl.navigation.portal_visit_pressure import VisitPressureController


def test_pressure_preserves_occupancy_and_blocked_cells():
    c=VisitPressureController();c.position[:]=[0,0,8]
    cell=tuple(c.cells(np.array([4.,0.,8.])));solid=tuple(c.cells(np.array([8.,0.,8.])))
    c.evidence[cell]=-8;c.evidence[solid]=8
    evidence=c.evidence.copy();before=c.grid()
    c.visits[cell]=20;c.search_pressure=True;after=c.grid()
    assert after[cell]>before[cell]
    assert np.isinf(after[solid]) and np.isinf(before[solid])
    assert np.array_equal(evidence,c.evidence)
    c.portal={'center':np.zeros(3)}
    assert c.grid()[cell]==before[cell]


def test_visits_and_progress_do_not_leak_between_controllers():
    a=VisitPressureController();b=VisitPressureController()
    a.visits.flat[0]=100;a.goal_progress.append(10.);a.search_pressure=True
    assert b.visits.flat[0]==0
    assert b.goal_progress==[] and not b.search_pressure
