"""Experimental v57 speed isolation; v55 and v56 remain frozen references."""
import numpy as np
from fly_rl.navigation.goal_margin import GoalMarginController
from fly_rl.simulation.sensors import DIRECTIONS

CONTROLLER_VERSION = "observed-neuronal-map-v57-cruise"


class CruiseController(GoalMarginController):
    """Change only clear-space cruise limit; retain margin speed and ray braking."""

    def action(self, features):
        v = np.asarray(features)[-1]
        goal = self.update(v)
        if self.tick % 10 == 1:
            self.integrate(v)
        if self.tick % 20 == 1 or not self.route:
            self.plan(goal)
        delta = self.local_goal if np.linalg.norm(self.local_goal) < 1.5 else self.target() @ self.rotation()
        velocity = v[260:263] * 3
        D = max(np.linalg.norm(delta), 1e-06)
        error = np.arctan2(delta[1], delta[0]) if np.linalg.norm(delta[:2]) > 0.05 else 0.0
        ranges = np.r_[np.clip(v[:128] * 8, 0, 8), np.clip(v[269:2069] * 24, 0, 24)]
        points = ranges[:, None] * np.vstack([DIRECTIONS, self.directions])
        direction = delta / D
        along = points @ direction
        perp = np.linalg.norm(points - along[:, None] * direction, axis=1)
        ahead = along[(along > 0) & (perp < 0.25)].min(initial=24.0)
        limit = np.sqrt(2.4 * max(ahead - 0.27, 0))
        speed = min(0.8 if self.tight else 2.6, D * 1.5, limit)
        desired = direction * speed
        desired[:2] *= max(0.0, np.cos(error)) ** 4
        horizontal = np.linalg.norm(desired[:2])
        thrust = np.clip(3 * (horizontal - velocity[0]) + 0.6 * horizontal, -1.2, 3)
        vertical = np.clip((3 * (desired[2] - velocity[2]) + 0.8 * desired[2]) / 2.5, -1, 1)
        self.debug.update(ahead=float(ahead), requested_speed=float(speed))
        return np.array([thrust / (3 if thrust >= 0 else 1.2), 0, vertical, np.clip(error * 2 / 1.8, -1, 1)], np.float32)
