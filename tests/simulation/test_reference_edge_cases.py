import numpy as np
from fly_rl.simulation.planner import reference_path, path_clear


def test_clear_fallback_to_wrong_endpoint_cannot_certify_unreachable_goal():
    wall=[(np.array([4,0,0]),np.array([6,10,10]))]
    route=reference_path([10]*3,wall,[1,5,5],[9,5,5],fallback=[[1,5,5],[2,5,5]])
    assert route['length'] is None and route['status']=='no_sampled_route'


def test_single_point_inside_box_is_not_a_clear_path():
    assert not path_clear([[5,5,5]],[10]*3,[([4,4,4],[6,6,6])])
    assert path_clear([[1,1,1]],[10]*3,[([4,4,4],[6,6,6])])
