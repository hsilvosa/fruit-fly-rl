"""Experimental v60: relax observed-free margins only after search saturation."""
import numpy as np
from fly_rl.navigation.cruise import CruiseController

CONTROLLER_VERSION = 'observed-neuronal-map-v60-adaptive-margin'


class AdaptiveMarginController(CruiseController):
    """Preserve normal routes until a capped search requests clearance recovery."""

    def __init__(self):
        super().__init__()
        self.margin_recovery = False
        self.recovery_tick = None

    def grid(self):
        costs = super().grid()
        if self.margin_recovery:
            allowance = (self.evidence < 0) & ~np.isfinite(costs)
            allowance[:, :, 0] = False
            allowance[:, :, -1] = False
            costs[allowance] = 8.
        return costs

    def plan(self, goal):
        super().plan(goal)
        if not self.debug['found'] and self.debug['expanded'] >= 12000:
            if not self.margin_recovery:
                self.recovery_tick = self.tick
            self.margin_recovery = True
        self.debug.update(margin_recovery=self.margin_recovery,
                          recovery_tick=self.recovery_tick)
