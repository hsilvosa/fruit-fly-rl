import numpy as np
from fly_rl.navigation.architectural_recovery import EscapeArchitecturalController, EscapeArchitecturalPolicy


def fixture():
    c=EscapeArchitecturalController((16.,12.,2.8))
    c.position=np.array([0.,0.,1.4])
    c.initial_goal=np.array([3.,0.,1.4])
    c.current_values=np.ones(5669)
    c.cost=np.ones(c.shape)
    return c


def test_escape_requires_observed_range_support_and_clear_grid():
    c=fixture()
    point=c.choose_escape()
    assert point is not None and np.linalg.norm(point-c.position) > .7
    c.current_values[:128]=0
    c.current_values[269:2069]=0
    assert c.choose_escape() is None
    c.current_values[:]=1
    c.cost[:]=np.inf
    assert c.choose_escape() is None


def test_escape_respects_ceiling_and_candidate_is_separate():
    c=fixture();c.position[2]=2.4;c.initial_goal[2]=10
    point=c.choose_escape()
    assert point is not None and point[2] <= 2.5
    policy=EscapeArchitecturalPolicy((16.,12.,2.8))
    assert policy.specification['controller_version']=='planner-1.4-exp.2'
    policy.controller.escape_count=2
    policy.reset()
    assert policy.controller.escape_count==0
