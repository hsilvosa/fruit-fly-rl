"""Unknown-cost experiments preserve solids, known free costs, and input scope."""
import numpy as np
from fly_rl.navigation.frontier_cost import FrontierCostController


def test_unknown_penalty_preserves_free_space_and_solids():
    c=FrontierCostController();c.position[:]=[0,0,5]
    here=c.cells(c.position);free=here+np.array([4,0,0]);solid=here+np.array([8,0,0])
    c.evidence[tuple(here)]=-8;c.evidence[tuple(free)]=-8;c.evidence[tuple(solid)]=6
    costs=c.grid()
    assert costs[tuple(here)]==1 and costs[tuple(free)]==1
    assert costs[tuple(here+np.array([0,4,0]))]==12
    assert np.isinf(costs[tuple(solid)])


def test_maze_contract_retained_without_geometry_input():
    c=FrontierCostController((64,64,20))
    assert c.room_size.tolist()==[64,64,20]
    assert not hasattr(c,'obstacles') and not hasattr(c,'reference_route')
