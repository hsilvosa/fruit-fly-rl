"""Bounded observable wall scan after stalled longitudinal navigation."""
import numpy as np
from fly_rl.navigation.distant_opening import DistantOpeningController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES
from fly_rl.navigation.room_aware import RoomAwareController

CONTROLLER_VERSION = 'observed-neuronal-map-progress-wall-scan-exp1'

class ProgressWallScanController(DistantOpeningController):
    def __init__(self, room_size=(64.,64.,20.)):
        super().__init__(room_size)
        self.longitudinal_best = -np.inf
        self.longitudinal_tick = 0
        self.scan = None
        self.scan_visits = {}
        self.scans_started = 0

    def update(self, values):
        goal = super().update(values)
        axis = self.initial_goal[:2] / max(np.linalg.norm(self.initial_goal[:2]), 1e-8)
        progress = float(self.position[:2] @ axis)
        if progress > self.longitudinal_best + 1.:
            self.longitudinal_best = progress
            self.longitudinal_tick = self.tick
        return goal

    def blocking_surface(self, values):
        ranges = np.clip(values[269:2069] * 24, .05, 24)
        directions = self.directions @ self.rotation().T
        points = directions * ranges[:, None]
        z = points[:, 2] + self.position[2]
        keep = (ranges < 23.4) & (z > .5) & (z < self.room_size[2] - .5)
        points = points[keep]
        xy = points[:, :2]
        if len(xy) < 80:
            return None
        toward = self.initial_goal[:2].copy()
        toward /= max(np.linalg.norm(toward), 1e-8)
        best = None
        for i, j in np.random.default_rng(42).integers(len(xy), size=(48, 2)):
            delta = xy[j] - xy[i]
            length = np.linalg.norm(delta)
            if length < 1:
                continue
            normal = np.array([delta[1], -delta[0]]) / length
            if normal @ toward < 0:
                normal = -normal
            distance = float(xy[i] @ normal)
            if normal @ toward < .8 or not .5 < distance < 4:
                continue
            inliers = np.abs(xy @ normal - distance) < .12
            if inliers.sum() < 80:
                continue
            _, vectors = np.linalg.eigh(np.cov(xy[inliers].T))
            normal = vectors[:, 0]
            if normal @ toward < 0:
                normal = -normal
            distance = float(np.median(xy[inliers] @ normal))
            tangent = np.array([-normal[1], normal[0]])
            if (not .5 < distance < 4 or normal @ toward < .8
                    or np.ptp(xy[inliers] @ tangent) < 8
                    or np.ptp(points[inliers, 2]) < min(.65 * self.room_size[2], 3 * distance)):
                continue
            score = float(inliers.sum()) * float(normal @ toward) ** 2
            if best is None or score > best[0]:
                best = (score, np.r_[normal, 0.], distance)
        if best is None:
            return None
        _, normal, distance = best
        return dict(normal=normal, center=self.position + normal * distance)


    def scan_key(self, point):
        return tuple(np.floor(np.asarray(point) / 2.).astype(int))

    def choose_scan_target(self, scan):
        normal, tangent = scan['normal'], scan['tangent']
        projected = self.position - normal * ((self.position - scan['center']) @ normal + 1.7)
        options = []
        for direction in (scan['direction'], -scan['direction']):
            point = projected + tangent * direction * 3.
            point[2] = self.room_size[2] / 2
            if not self.reference_clear(point):
                continue
            delta = (point - self.position) @ self.rotation()
            distance = np.linalg.norm(delta)
            alignment = self.directions @ (delta / max(distance, 1e-8))
            nearest = np.argsort(alignment)[-4:]
            ranges = np.clip(self.current_values[269:2069], 0, 1) * 24
            if not np.all(ranges[nearest] * alignment[nearest] > distance + .3):
                continue
            key = self.scan_key(point)
            penalty = self.scan_visits.get(key, 0)
            options.append((penalty, int(direction != scan['direction']), direction, point))
        if not options:
            return None
        _, _, direction, point = min(options, key=lambda item: item[:2])
        scan['direction'] = direction
        return point

    def plan(self, goal):
        super().plan(goal)
        visible = self.direct_goal_visible(self.current_values)
        if self.portal is not None or visible:
            self.scan = None
        elif self.tick - self.longitudinal_tick >= 320:
            if self.scan is None:
                surface = self.blocking_surface(self.current_values)
                if surface is not None:
                    normal = surface['normal']
                    tangent = np.array([-normal[1], normal[0], 0.])
                    direction = 1 if (self.initial_goal-self.position) @ tangent >= 0 else -1
                    self.scan = dict(**surface, tangent=tangent, direction=direction, target=None,
                                     started=self.tick, best=np.inf, progress_tick=self.tick)
                    self.scans_started += 1
            scan = self.scan
            if scan is not None:
                if (self.tick-scan['started'] > 400
                    or (self.position-scan['center']) @ scan['normal'] > .9):
                    self.scan = None
                    self.longitudinal_tick = self.tick
                else:
                    target = scan['target']
                    if target is not None:
                        distance = np.linalg.norm(target-self.position)
                        if distance < scan['best']-.2:
                            scan['best'] = distance
                            scan['progress_tick'] = self.tick
                        if distance < .8 or self.tick-scan['progress_tick'] >= 100:
                            key = self.scan_key(target)
                            self.scan_visits[key] = self.scan_visits.get(key, 0)+1
                            scan['target'] = None
                            self.reference = None
                    if scan['target'] is None:
                        scan['target'] = self.choose_scan_target(scan)
                        scan['best'] = np.inf
                        scan['progress_tick'] = self.tick
                        self.reference = None
                    if scan['target'] is not None:
                        RoomAwareController.plan(self, scan['target'])
                        if not self.debug['found']:
                            key = self.scan_key(scan['target'])
                            self.scan_visits[key] = self.scan_visits.get(key, 0)+1
                            scan['target'] = None
                            self.reference = None
        self.debug.update(progress_wall_scan=self.scan is not None, scans_started=self.scans_started,
            scan_target=self.scan['target'].tolist() if self.scan and self.scan['target'] is not None else None,
            longitudinal_no_progress_ticks=self.tick-self.longitudinal_tick)
