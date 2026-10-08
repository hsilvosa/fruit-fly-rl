"""Visible-goal planner with explicit repeatable full-connectome reconstruction."""
from fly_rl.navigation.portal_visible_goal import VisibleGoalController, FEATURE_COUNT, SUPPORTED_PROFILES
from fly_rl.connectome.repeatable_readout import RepeatableDualActivityBrain, REPEATABLE_DUAL_READOUT
CONTROLLER_VERSION = 'observed-neuronal-map-repeatable-goal-exp1'
READOUT_VERSION = REPEATABLE_DUAL_READOUT
READOUT_MODULE = 'fly_rl.connectome.repeatable_readout'
READOUT_CLASS = RepeatableDualActivityBrain
class RepeatableGoalController(VisibleGoalController):
    pass
