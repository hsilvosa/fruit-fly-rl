import numpy as np
from fly_rl.navigation.consistent_opening import ConsistentOpeningController
from fly_rl.navigation.coverage_wall_scan import CoverageWallScanController


def prepared():
    c=ConsistentOpeningController()
    c.initial_goal=np.array([40.,0.,10.]);c.position=np.array([0.,0.,10.])
    c.completed_planes=[(np.array([float(i),0.,10.]),np.array([1.,0.,0.])) for i in range(3)]
    return c


def test_repeated_observed_crossings_reject_discordant_fit(monkeypatch):
    c=prepared()
    observed={'center':np.array([5.,3.,10.]),'normal':np.array([.8,.6,0.]),'ray_support':200}
    monkeypatch.setattr(CoverageWallScanController,'detect_portal',lambda self,values:observed)
    assert c.detect_portal(None) is None and c.discordant_opening_fits==1
    observed['normal']=np.array([1.,0.,0.])
    assert c.detect_portal(None) is observed


def test_no_consensus_from_insufficient_or_mixed_crossings():
    c=prepared();c.completed_planes=c.completed_planes[:2]
    assert c.crossing_consensus() is None
    c.completed_planes.extend([(np.zeros(3),np.array([0.,1.,0.]))]*2)
    assert c.crossing_consensus() is None


def test_consensus_releases_when_goal_requires_a_turn():
    c=prepared();c.initial_goal=np.array([0.,40.,10.])
    assert c.crossing_consensus() is None


def test_normal_sign_does_not_change_plane_consensus():
    c=prepared();c.completed_planes[1]=(np.zeros(3),np.array([-1.,0.,0.]))
    assert np.allclose(c.crossing_consensus(),[1.,0.,0.])


def test_independent_reset_history():
    c=prepared();other=ConsistentOpeningController()
    c.discordant_opening_fits=4
    assert other.completed_planes==[] and other.discordant_opening_fits==0
