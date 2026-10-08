"""Require near-body corridor clearance before direct-goal handover."""
import numpy as np
from fly_rl.navigation.segmented_goal import SegmentedGoalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-clearance-goal-exp1'
from fly_rl.navigation.portal_visible_goal import VisibleGoalController
from fly_rl.simulation.sensors import DIRECTIONS

class ClearanceGoalController(SegmentedGoalController):
    def direct_goal_visible(self, values):
        if self.portal is not None:
            return False
        if not VisibleGoalController.direct_goal_visible(self, values):
            return False
        distance = float(np.linalg.norm(self.local_goal))
        direction = self.local_goal / distance
        ranges = np.r_[np.clip(values[:128], 0, 1) * 8,
                       np.clip(values[269:2069], 0, 1) * 24]
        directions = np.vstack([DIRECTIONS, self.directions])
        points = ranges[:, None] * directions
        along = points @ direction
        perpendicular = np.linalg.norm(points - along[:, None] * direction, axis=1)
        limits = np.r_[np.full(128, 8.), np.full(1800, 24.)]
        obstructed = ((ranges < limits - .05) & (along > 0)
                      & (along < distance + .3) & (perpendicular < .25))
        return not bool(obstructed.any())
