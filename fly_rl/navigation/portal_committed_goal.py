"""Keep a chosen visible-goal reference through brief angular sampling changes."""
from fly_rl.navigation.portal_stable_goal import StableVisibleGoalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES
from fly_rl.navigation.portal_visible_goal import VisibleGoalController
CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp19'

class CommittedVisibleGoalController(StableVisibleGoalController):
    def __init__(self,room_size=(48.,48.,16.)):
        super().__init__(room_size)
        self.blocked_ticks=0

    def update(self,values):
        previous=self.goal_handover
        goal=super().update(values)
        visible=VisibleGoalController.direct_goal_visible(self,values)
        self.blocked_ticks=self.blocked_ticks+1 if previous and not visible else 0
        if previous:
            self.goal_handover=visible or self.blocked_ticks<20
        return goal

    def action(self,features):
        result=super().action(features)
        self.debug.update(goal_handover=self.goal_handover,visible_ticks=self.visible_ticks,blocked_ticks=self.blocked_ticks)
        return result
