"""Experimental v64: check retained momentum as well as requested direction."""
import numpy as np
from fly_rl.navigation.distance_stable import DistanceStableController
from fly_rl.navigation.distance_stable import READOUT_VERSION, READOUT_MODULE, READOUT_CLASS
from fly_rl.simulation.sensors import DIRECTIONS

CONTROLLER_VERSION = 'observed-neuronal-map-v64-momentum-guard'


class MomentumGuardController(DistanceStableController):
    """Preserve v61 planning; request braking when current motion lacks clearance."""

    def action(self, features):
        v = np.asarray(features)[-1]
        goal = self.update(v)
        if self.tick % 10 == 1:
            self.integrate(v)
        if self.tick % 20 == 1 or not self.route:
            self.plan(goal)
        delta = self.local_goal if np.linalg.norm(self.local_goal) < 1.5 else self.target() @ self.rotation()
        velocity = v[260:263] * 3
        distance = max(np.linalg.norm(delta), 1e-6)
        error = np.arctan2(delta[1], delta[0]) if np.linalg.norm(delta[:2]) > .05 else 0.
        ranges = np.r_[np.clip(v[:128]*8, 0, 8), np.clip(v[269:2069]*24, 0, 24)]
        points = ranges[:, None]*np.vstack([DIRECTIONS, self.directions])
        direction = delta/distance
        along = points@direction
        perpendicular = np.linalg.norm(points-along[:, None]*direction, axis=1)
        ahead = along[(along > 0) & (perpendicular < .25)].min(initial=24.)
        limit = np.sqrt(2.4*max(ahead-.27, 0))
        speed = min(.8 if self.tight else 2.6, distance*1.5, limit)
        desired = direction*speed
        desired[:2] *= max(0., np.cos(error))**4
        actual_speed = float(np.linalg.norm(velocity))
        motion = velocity/max(actual_speed, 1e-8)
        motion_along = points@motion
        motion_perp = np.linalg.norm(points-motion_along[:, None]*motion, axis=1)
        motion_ahead = motion_along[(motion_along > 0) & (motion_perp < .25)].min(initial=24.)
        momentum_limit = np.sqrt(2.4*max(motion_ahead-.27, 0))
        guarded = actual_speed > .1 and actual_speed > momentum_limit
        if guarded:
            desired.fill(0)
        horizontal = np.linalg.norm(desired[:2])
        thrust = np.clip(3*(horizontal-velocity[0])+.6*horizontal, -1.2, 3)
        vertical = np.clip((3*(desired[2]-velocity[2])+.8*desired[2])/2.5, -1, 1)
        self.debug.update(ahead=float(ahead), requested_speed=float(speed),
            momentum_ahead=float(motion_ahead), actual_speed=actual_speed,
            momentum_guard=bool(guarded), effective_desired_speed=float(np.linalg.norm(desired)))
        return np.array([thrust/(3 if thrust >= 0 else 1.2), 0, vertical,
                         np.clip(error*2/1.8, -1, 1)], np.float32)
