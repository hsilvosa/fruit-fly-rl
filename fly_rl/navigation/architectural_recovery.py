"""Experimental architectural escape references from observed neural ranges."""
import numpy as np
from fly_rl.navigation.architectural import ArchitecturalController, ArchitecturalPlannerPolicy
from fly_rl.simulation.sensors import DIRECTIONS


class EscapeArchitecturalController(ArchitecturalController):
    def __init__(self, room_size):
        super().__init__(room_size)
        self.escape_reference = None
        self.escape_started = 0
        self.escape_count = 0
        self.blocked_ticks = 0

    def choose_escape(self):
        values = self.current_values
        ranges = np.r_[np.clip(values[:128], 0, 1)*8,
                       np.clip(values[269:2069], 0, 1)*24]
        rays = np.vstack([DIRECTIONS, self.directions])
        points = rays*ranges[:, None]
        options = []
        for direction in self.neighbors/self.lengths[:, None]:
            # A candidate needs measured free support along its direction.
            support = rays@direction > .98
            length = .8
            if not support.any() or np.min(ranges[support]) < length+.3:
                continue
            along = points@direction
            perpendicular = np.linalg.norm(points-along[:, None]*direction, axis=1)
            ahead = along[(along > 0) & (perpendicular < .25)].min(initial=24.)
            if ahead < length+.3:
                continue
            delta = direction*length @ self.rotation().T
            point = self.position+delta
            if point[2] < .3 or point[2] > self.room_size[2]-.3:
                continue
            if not self.reference_clear(point):
                continue
            toward = self.initial_goal-self.position
            score = delta@toward/max(np.linalg.norm(toward), 1e-8)
            options.append((score, point))
        return max(options, key=lambda item:item[0])[1].copy() if options else None

    def target(self):
        if self.escape_reference is not None:
            distance = np.linalg.norm(self.escape_reference-self.position)
            if distance < .2 or self.tick-self.escape_started >= 80 or not self.reference_clear(self.escape_reference):
                self.escape_reference = None
            else:
                delta = self.escape_reference-self.position
                self.debug.update(target_delta_global=delta.tolist(), architectural_escape=True)
                return delta
        self.debug['architectural_escape'] = False
        return super().target()

    def action(self, features):
        result = super().action(features)
        blocked = self.debug.get('requested_speed', 1.) < .02 and self.debug.get('actual_speed', 1.) < .05
        self.blocked_ticks = self.blocked_ticks+1 if blocked else 0
        if self.blocked_ticks >= 25 and self.escape_reference is None:
            point = self.choose_escape()
            if point is not None:
                self.escape_reference = point
                self.escape_started = self.tick
                self.escape_count += 1
                self.blocked_ticks = 0
        self.debug.update(architectural_escape_count=self.escape_count,
                          architectural_blocked_ticks=self.blocked_ticks)
        return result


class EscapeArchitecturalPolicy(ArchitecturalPlannerPolicy):
    def reset(self):
        self.controller = EscapeArchitecturalController(self.room_size)

    @property
    def specification(self):
        result = dict(super().specification)
        result.update(controller_version='planner-1.4-exp.2',
                      version='observed-neuronal-map-architecture-escape-exp1')
        return result

    def source_files(self):
        from pathlib import Path
        return sorted(set(super().source_files()) | {Path(__file__)})
