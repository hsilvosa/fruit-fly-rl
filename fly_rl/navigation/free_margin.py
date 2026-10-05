"""Experimental v58: costly traversal of observed-free safety margins."""
import numpy as np
from fly_rl.navigation.goal_margin import GoalMarginController

CONTROLLER_VERSION = 'observed-neuronal-map-v58-free-margin'


class FreeMarginController(GoalMarginController):
    """Keep surfaces solid while admitting observed-free inflated cells at cost 8."""

    def grid(self):
        costs = super().grid()
        allowance = (self.evidence < 0) & ~np.isfinite(costs)
        allowance[:, :, 0] = False
        allowance[:, :, -1] = False
        costs[allowance] = 8.
        return costs
