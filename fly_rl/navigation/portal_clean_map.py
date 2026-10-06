"""Experimental opening references with clean neural ranges for occupancy."""
from fly_rl.navigation.portal_near_wall import NearWallPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES
from fly_rl.navigation.observed_map import ObservedMapController

CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp6'


class CleanMapPortalController(NearWallPortalController):
    """Keep dual readout and safety; build occupancy from clean range coordinates."""

    def integrate(self, values):
        ObservedMapController.integrate(self, values)

    def action(self, features):
        result=super().action(features)
        self.debug['mapping_ranges']='clean-neural'
        return result
