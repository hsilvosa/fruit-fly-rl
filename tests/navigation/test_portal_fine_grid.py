"""Finer representation retains declared room bounds and independent evidence."""
import numpy as np
from fly_rl.navigation.portal_fine_grid import FineGridPortalController


def test_maze_grid_covers_height_and_rotated_room_extent():
    c=FineGridPortalController((64,64,20))
    assert c.res==.4 and c.shape[2]==51
    assert c.valid(c.cells(np.array([[0,0,.2],[64,0,19.8],[-64,0,19.8],[0,64,10]]))).all()
    assert c.evidence.dtype==np.int8


def test_fine_map_resets_independently():
    a=FineGridPortalController();b=FineGridPortalController()
    a.evidence[1,1,1]=12
    assert b.evidence[1,1,1]==0
    assert not b.reference_vetoes and not b.completed_planes
