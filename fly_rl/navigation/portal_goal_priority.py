"""Prefer the actual goal over unnecessary terminal portal commitments."""
import numpy as np
from fly_rl.navigation.portal_center_refinement import RefiningPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp10'


class GoalPriorityPortalController(RefiningPortalController):
    """Use global occupancy planning near a goal or along a known-free segment."""

    def prefer_goal_route(self):
        if self.initial_goal is None:return False
        distance=np.linalg.norm(self.initial_goal-self.position)
        if distance<5:return True
        steps=np.linspace(0,1,max(2,int(np.ceil(distance/.3))+1))
        cells=self.cells(self.position+(self.initial_goal-self.position)*steps[:,None])
        if not self.valid(cells).all() or not hasattr(self,'cost'):return False
        return bool((self.evidence[tuple(cells.T)]<0).all() and np.isfinite(self.cost[tuple(cells.T)]).all())

    def portal_leads_toward_goal(self, portal):
        return bool((self.initial_goal-portal['center'])@portal['normal']>=1.3)

    def detect_portal(self, values):
        if self.prefer_goal_route():return None
        portal=super().detect_portal(values)
        return portal if portal is not None and self.portal_leads_toward_goal(portal) else None

    def plan(self, goal):
        priority=self.prefer_goal_route()
        if priority and self.portal is not None:
            self.portal=None;self.portal_phase='none';self.reference=None;self.route=[]
        super().plan(goal)
        self.debug['goal_route_priority']=priority
