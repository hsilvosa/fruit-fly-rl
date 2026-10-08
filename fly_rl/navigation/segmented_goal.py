"""Visible-goal controller using repeatable segmented full-connectome activity."""
from fly_rl.navigation.portal_visible_goal import VisibleGoalController, FEATURE_COUNT, SUPPORTED_PROFILES
from fly_rl.connectome.segmented_readout import SegmentedDualActivityBrain, SEGMENTED_DUAL_READOUT

CONTROLLER_VERSION = 'observed-neuronal-map-segmented-goal-exp1'
READOUT_VERSION = SEGMENTED_DUAL_READOUT
READOUT_MODULE = 'fly_rl.connectome.segmented_readout'
READOUT_CLASS = SegmentedDualActivityBrain

class SegmentedGoalController(VisibleGoalController):
    pass
