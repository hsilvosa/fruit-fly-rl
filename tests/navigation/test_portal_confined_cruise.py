"""Requested confined speed stays bounded by observed stopping distance."""
import inspect
import numpy as np
from fly_rl.navigation.portal_confined_cruise import ConfinedCruiseController
from fly_rl.navigation.portal_fast import FastPortalController


def test_only_speed_request_changes_in_flight_law():
    previous=inspect.getsource(FastPortalController.flight_action)
    current=inspect.getsource(ConfinedCruiseController.flight_action)
    assert current==previous.replace('1.0 if self.tight else 3.0','1.3 if self.tight else 3.0')


def test_blocked_confined_reference_requests_stop(monkeypatch):
    c=ConfinedCruiseController();c.tick=2;c.tight=True;c.route=[np.array([1.,0.,8.])]
    monkeypatch.setattr(c,'update',lambda v:np.array([40.,0.,8.]))
    monkeypatch.setattr(c,'target',lambda:np.array([1.,0.,0.]))
    c.local_goal=np.array([40.,0.,0.])
    v=np.zeros((9,3869));v[:,:128]=.02;v[:,269:2069]=.005
    action=c.flight_action(v)
    assert c.debug['requested_speed']==0
    assert np.isfinite(action).all()
