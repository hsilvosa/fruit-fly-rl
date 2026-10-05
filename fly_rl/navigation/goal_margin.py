"""Experimental v56: locally admit observed-free goal-margin cells at high cost.

The frozen v55 module is unchanged. This candidate does not remove observed
solids, enlarge the search budget, change deadlines, or learn movement weights.
"""
import numpy as np
from fly_rl.navigation.observed_map import ObservedMapController

CONTROLLER_VERSION = 'observed-neuronal-map-v56-goal-margin'


class GoalMarginController(ObservedMapController):
    """Goal-side counterpart of local start-margin escape, restricted to known free cells."""

    def grid(self):
        costs = super().grid()
        if self.initial_goal is None:
            return costs
        cell = self.cells(self.initial_goal)
        if not self.valid(cell) or self.evidence[tuple(cell)] >= 0 or np.isfinite(costs[tuple(cell)]):
            return costs
        lower, upper = np.maximum(cell-1, 0), np.minimum(cell+2, self.shape)
        region = tuple(slice(int(a), int(b)) for a, b in zip(lower, upper))
        values = costs[region]
        evidence = self.evidence[region]
        known_free = evidence < 0
        # Preserve blocked top/bottom boundaries even if ray evidence says free.
        z = np.arange(lower[2], upper[2])
        known_free &= ((z > 0) & (z < self.shape[2]-1))[None, None, :]
        values[known_free & ~np.isfinite(values)] = 8.0
        return costs
