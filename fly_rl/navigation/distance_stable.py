"""Experimental v61 keeps v60 controls and changes only the distance readout."""
from fly_rl.navigation.adaptive_margin import AdaptiveMarginController
from fly_rl.connectome.distance_readout import DISTANCE_STABLE_READOUT, DistanceStableActivityBrain

CONTROLLER_VERSION = 'observed-neuronal-map-v61-distance-stable'
READOUT_VERSION = DISTANCE_STABLE_READOUT
READOUT_MODULE = 'fly_rl.connectome.distance_readout'
READOUT_CLASS = DistanceStableActivityBrain


class DistanceStableController(AdaptiveMarginController):
    """Use unchanged adaptive planning with distance-stable neural coordinates."""
