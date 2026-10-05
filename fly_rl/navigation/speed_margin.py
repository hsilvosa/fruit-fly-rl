"""Experimental v59 combines separately checked speed and known-free margins."""
from fly_rl.navigation.cruise import CruiseController
from fly_rl.navigation.free_margin import FreeMarginController

CONTROLLER_VERSION = 'observed-neuronal-map-v59-speed-margin'


class SpeedMarginController(CruiseController, FreeMarginController):
    """Use v57 flight commands with v58 grid construction; references stay frozen."""
