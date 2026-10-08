import numpy as np
from fly_rl.navigation.terminal_consensus import TerminalConsensusController


def prepared():
    c=TerminalConsensusController()
    c.initial_goal=np.array([60.,0.,10.]);c.position=np.array([46.,0.,10.])
    c.initial_distance=60.;c.local_goal=np.array([14.,0.,0.])
    c.completed_planes=[(np.array([float(i),0.,10.]),np.array([1.,0.,0.])) for i in range(3)]
    return c


def test_consensus_only_in_terminal_fraction():
    c=prepared()
    assert c.crossing_consensus() is not None
    c.local_goal=np.array([16.,0.,0.])
    assert c.crossing_consensus() is None
    c.local_goal=np.array([15.,0.,0.])
    assert c.crossing_consensus() is not None


def test_gate_scales_with_initial_distance_and_keeps_parent_conditions():
    c=prepared();c.initial_distance=40.
    assert c.crossing_consensus() is None
    c.local_goal=np.array([9.,0.,0.]);c.completed_planes=[]
    assert c.crossing_consensus() is None


def test_initial_distance_is_decoded_once_and_reset_independently():
    c=TerminalConsensusController();v=np.zeros(3869);v[256]=1;v[259]=.5;v[267]=.5
    c.update(v);initial=c.initial_distance
    assert np.isclose(initial,.5*np.linalg.norm(c.room_size-.32))
    v[259]=.1;c.update(v)
    assert c.initial_distance==initial
    assert TerminalConsensusController().initial_distance is None
