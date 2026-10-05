"""Experimental v62: retain safe local route prefixes between map updates."""
import time
import numpy as np
from fly_rl.navigation.distance_stable import DistanceStableController
from fly_rl.navigation.distance_stable import READOUT_VERSION, READOUT_MODULE, READOUT_CLASS

CONTROLLER_VERSION = 'observed-neuronal-map-v62-persistent-route'


class PersistentRouteController(DistanceStableController):
    """Keep an eight-unit prefix if currently traversable; search on blockage/stall."""

    def __init__(self):
        super().__init__()
        self.last_route_check_position = None
        self.stagnant_checks = 0

    def prefix_points(self):
        remaining = 8.
        points = [self.position.copy()]
        previous = self.position
        for waypoint in self.route:
            delta = waypoint-previous
            length = float(np.linalg.norm(delta))
            travel = min(length, remaining)
            if length > 1e-8:
                fractions = np.linspace(0, travel/length, max(2, int(np.ceil(travel/.1))+1))[1:]
                points.extend(previous+fractions[:, None]*delta)
            remaining -= travel
            if remaining <= 1e-8:
                break
            previous = waypoint
        return np.asarray(points)

    def plan(self, goal):
        began = time.perf_counter()
        if self.last_route_check_position is not None:
            moved = np.linalg.norm(self.position-self.last_route_check_position)
            self.stagnant_checks = self.stagnant_checks+1 if moved < .03 else 0
        self.last_route_check_position = self.position.copy()
        if self.route and np.linalg.norm(self.route[-1]-goal) < .02 and self.stagnant_checks < 3:
            costs = self.grid()
            cells = self.cells(self.prefix_points())
            if self.valid(cells).all() and np.isfinite(costs[tuple(cells.T)]).all():
                self.cost = costs
                self.debug.update(plan_reused=True, prefix_validation_units=8., expanded=0,
                    plan_seconds=time.perf_counter()-began, position=self.position.tolist(), yaw=self.yaw)
                return
        super().plan(goal)
        self.stagnant_checks = 0
        self.debug.update(plan_reused=False, prefix_validation_units=8.)
