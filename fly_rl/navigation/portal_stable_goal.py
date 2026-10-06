"""Require stable distant visibility before abandoning an opening reference."""
import numpy as np
from fly_rl.navigation.portal_visible_goal import VisibleGoalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES
CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp18'

class StableVisibleGoalController(VisibleGoalController):
    def __init__(self,room_size=(48.,48.,16.)):
        super().__init__(room_size)
        self.visible_ticks=0
        self.goal_handover=False

    def update(self,values):
        goal=super().update(values)
        visible=VisibleGoalController.direct_goal_visible(self,values)
        self.visible_ticks=self.visible_ticks+1 if visible else 0
        self.goal_handover=visible and (np.linalg.norm(self.local_goal)<8. or self.visible_ticks>=20)
        return goal

    def direct_goal_visible(self,values):
        return bool(self.goal_handover)
