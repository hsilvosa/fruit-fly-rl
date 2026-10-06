"""Execution vetoes must not fabricate occupied surfaces or leak across resets."""
import numpy as np
from fly_rl.navigation.portal_recovery import RecoveryPortalController


def test_stall_veto_preserves_evidence_and_expires():
    c=RecoveryPortalController();c.position[:]=[0,0,8];c.tick=100
    original=c.evidence.copy()
    for _ in range(24):assert not c.veto_stalled_reference([0,0,1],0,0)
    assert c.veto_stalled_reference([0,0,1],0,0)
    assert np.array_equal(c.evidence,original)
    cell=tuple(c.cells(c.position+[0,0,1]))
    assert np.isinf(c.grid()[cell])
    c.tick=301
    assert np.isfinite(c.grid()[cell])
    assert not c.reference_vetoes


def test_moving_flight_and_independent_reset_have_no_veto():
    a=RecoveryPortalController();b=RecoveryPortalController()
    a.position[2]=8
    for _ in range(30):assert not a.veto_stalled_reference([0,0,1],1,1)
    for _ in range(25):a.veto_stalled_reference([0,0,1],0,0)
    assert a.reference_vetoes
    assert not b.reference_vetoes and b.stall_ticks==0
