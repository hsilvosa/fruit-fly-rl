"""Prefer already observed free corridors over optimistic unknown shortcuts."""
import numpy as np
from fly_rl.navigation.room_aware import RoomAwareController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-frontier-cost-exp1'


class FrontierCostController(RoomAwareController):
    """Unknown cells remain explorable but carry an explicit higher route cost."""

    def grid(self):
        costs=super().grid()
        unknown=(self.evidence>=0)&np.isfinite(costs)
        costs[unknown]=12.
        costs[tuple(self.cells(self.position))]=1.
        return costs

    def plan(self, goal):
        super().plan(goal)
        cells=self.cells(np.asarray(self.route))
        values=self.evidence[tuple(cells.T)] if len(cells) else np.array([])
        self.debug.update(unknown_cell_cost=12.,
            route_unknown_points=int((values>=0).sum()),route_observed_free_points=int((values<0).sum()))
