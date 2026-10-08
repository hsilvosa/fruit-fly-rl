"""Prefer a beacon corridor observed by nearby clean neural range rays."""
import numpy as np
from fly_rl.navigation.portal_center_refinement import RefiningPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES
from fly_rl.navigation.room_aware import RoomAwareController
from fly_rl.simulation.sensors import DIRECTIONS
CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp17'

class VisibleGoalController(RefiningPortalController):
    def direct_goal_visible(self,values):
        delta=np.asarray(self.local_goal)
        distance=float(np.linalg.norm(delta))
        if not .45<distance<23.:return False
        direction=delta/distance
        align=self.directions@direction
        nearest=np.argsort(align)[-4:]
        ranges=np.clip(values[269:2069],0,1)*24
        return bool(np.all(align[nearest]>.98) and np.all(ranges[nearest]*align[nearest]>distance+.3))

    def plan(self,goal):
        visible=self.direct_goal_visible(self.current_values)
        if visible:
            self.portal=None
            self.portal_phase='none'
            self.reference=None
            self.route=[]
            RoomAwareController.plan(self,goal)
        else:
            super().plan(goal)
        self.debug.update(direct_goal_visible=visible)

    def flight_action(self, features):
        v = np.asarray(features)[-1]
        goal = self.update(v)
        if self.tick % 10 == 1:
            self.integrate(v)
        if self.tick % 20 == 1 or not self.route:
            self.plan(goal)
        delta = self.local_goal if np.linalg.norm(self.local_goal) < 1.5 or self.direct_goal_visible(v) else self.target() @ self.rotation()
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
        speed = min(1.0 if self.tight else 3.0, distance*1.5, limit)
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
        self.debug.update(direct_goal_visible=self.direct_goal_visible(v), ahead=float(ahead), requested_speed=float(speed),
            momentum_ahead=float(motion_ahead), actual_speed=actual_speed,
            momentum_guard=bool(guarded), effective_desired_speed=float(np.linalg.norm(desired)))
        return np.array([thrust/(3 if thrust >= 0 else 1.2), 0, vertical,
                         np.clip(error*2/1.8, -1, 1)], np.float32)
