"""Discourage repeated unproductive cells without changing occupancy evidence."""
import numpy as np
from fly_rl.navigation.portal_center_refinement import RefiningPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES
from fly_rl.navigation.room_aware import RoomAwareController
CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp14'

class VisitPressureController(RefiningPortalController):
    def __init__(self,room_size=(48.,48.,16.)):
        super().__init__(room_size)
        self.visits=np.zeros(self.shape,np.uint16)
        self.goal_progress=[]
        self.search_pressure=False

    def update(self,values):
        goal=super().update(values)
        if self.tick%10==1:
            cell=tuple(self.cells(self.position))
            self.visits[cell]=min(65535,int(self.visits[cell])+1)
            self.goal_progress.append(float(np.linalg.norm(goal-self.position)))
            self.goal_progress=self.goal_progress[-61:]
            self.search_pressure=(len(self.goal_progress)==61 and self.goal_progress[0]-self.goal_progress[-1]<2.)
        return goal

    def grid(self):
        cost=super().grid()
        if self.portal is None and self.search_pressure:
            finite=np.isfinite(cost)
            cost[finite]+=np.minimum(self.visits[finite]*.15,4.)
        return cost

    def plan(self,goal):
        if np.linalg.norm(self.initial_goal-self.position)<3.:
            self.portal=None
            self.portal_phase='none'
            RoomAwareController.plan(self,goal)
        else:
            super().plan(goal)
        self.debug.update(search_pressure=bool(self.search_pressure))
