"""Regression checks for physical route following; synthetic inputs, no flight claim."""
import numpy as np
import pytest
from fly_rl.navigation.observed_map import ObservedMapController, ObservedMapPolicy
from fly_rl.simulation.sensors import DIRECTIONS

def test_route_advances_after_reaching_current_cell():
    c=ObservedMapController();c.position=np.array([.3,.3,4.5]);c.tight=False
    c.route=[c.position.copy(),c.position+np.array([.6,0,0])]
    c.cost=np.full(c.shape,np.inf,dtype=np.float32)
    assert c.target()[0]>.5

def test_margin_escape_preserves_observed_solids():
    c=ObservedMapController();c.position=np.array([.3,.3,4.5]);cell=c.cells(c.position)
    solid=tuple(cell+np.array([1,0,0]));c.evidence[solid]=3
    cost=c.grid()
    assert c.tight and np.isfinite(cost[tuple(cell)]) and not np.isfinite(cost[solid])
    assert np.isfinite(cost[tuple(cell+np.array([0,1,0]))])

def action_without_mapping(monkeypatch,delta,velocity=0.):
    c=ObservedMapController();c.tick=1;c.tight=False;c.route=[np.ones(3)]
    monkeypatch.setattr(c,'update',lambda v:np.ones(3));c.local_goal=np.array([10.,0,0])
    monkeypatch.setattr(c,'target',lambda:np.array(delta,dtype=float))
    v=np.zeros((9,3869),np.float32);v[-1,:128]=1;v[-1,269:2069]=1;v[-1,260]=velocity/3
    forward=np.argmax(DIRECTIONS[:,0]);v[-1,forward]=.22/8
    return c,c.action(v)

def test_forward_wall_does_not_prevent_clear_altitude_change(monkeypatch):
    c,a=action_without_mapping(monkeypatch,[0,0,2])
    assert a[2]>.5 and c.debug['requested_speed']>0

def test_brakes_before_obstacle_in_requested_direction(monkeypatch):
    c,a=action_without_mapping(monkeypatch,[3,0,0],1.)
    assert c.debug['requested_speed']==0 and a[0]<0

def test_reset_drops_previous_map_and_odometry():
    p=ObservedMapPolicy();old=p.controller;old.evidence.fill(3);old.position[:]=7;old.tick=99
    p.reset();assert p.controller is not old
    assert not p.controller.evidence.any() and not p.controller.position.any() and p.controller.tick==0

def test_rejects_incompatible_or_nonfinite_neural_history():
    p=ObservedMapPolicy()
    with pytest.raises(ValueError):p.predict(np.zeros((1,256)))
    a=np.zeros((1,9,3869));a[0,0,0]=np.nan
    with pytest.raises(ValueError):p.predict(a)
