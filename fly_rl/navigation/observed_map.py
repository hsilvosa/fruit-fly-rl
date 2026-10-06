"""Explicit planning from full-connectome activity; no learned movement weights.

The observation contract is SENSOR_V6 with MOTION_STABLE_READOUT, a 48 x 48 x 16
large room, coordinated dynamics, and a 50 ms decision interval. True world
geometry and pose are never accepted by this controller.
"""
import heapq
import math
import time
import hashlib
from pathlib import Path
import numpy as np
from scipy import ndimage
from fly_rl.simulation.sensors import DIRECTIONS, panorama_directions

CONTROLLER_VERSION = "observed-neuronal-map-v55"

class ObservedMapController:
    """Stateful geometry planner consuming reconstructed neuronal channels only."""

    def __init__(self):
        self.res = 0.6
        self.shape = (216, 216, 28)
        self.origin = np.array([-64.8, -64.8, 0.0])
        self.evidence = np.zeros(self.shape, np.int8)
        self.position = np.zeros(3)
        self.yaw = 0.0
        self.tick = 0
        self.initial_goal = None
        self.route = []
        self.debug = {}
        self.directions = panorama_directions()
        self.neighbors = [(a, b, c) for a in [-1, 0, 1] for b in [-1, 0, 1] for c in [-1, 0, 1] if a or b or c]
        self.lengths = np.array([np.linalg.norm(a) for a in self.neighbors])
        self.neighbors = np.array(self.neighbors, dtype=int)

    def rotation(self):
        c, s = (np.cos(self.yaw), np.sin(self.yaw))
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])

    def cells(self, points):
        return np.floor((points - self.origin) / self.res).astype(int)

    def valid(self, cells):
        return ((cells >= 0) & (cells < self.shape)).all(-1)

    def integrate(self, v):
        ranges = np.clip(v[269:2069] * 24, 0.05, 24)
        dirs = self.directions @ self.rotation().T
        steps = np.arange(0.3, 24, 0.45)
        points = self.position[None, None] + dirs[:, None] * steps[None, :, None]
        free = steps[None] < ranges[:, None] - 0.35
        cells = self.cells(points[free])
        cells = cells[self.valid(cells)]
        indices = tuple(cells.T)
        unique = np.unique(np.ravel_multi_index(indices, self.shape))
        flat = self.evidence.ravel()
        flat[unique] = np.maximum(flat[unique] - 1, -8)
        endpoints = self.position + dirs * ranges[:, None]
        hit = ranges < 23.4
        surface = [endpoints[hit]]
        image = endpoints.reshape(25, 72, 3)
        depth = ranges.reshape(25, 72)
        p00 = image[:-1]
        p01 = np.roll(image[:-1], -1, axis=1)
        p10 = image[1:]
        p11 = np.roll(image[1:], -1, axis=1)
        depths = np.stack([depth[:-1], np.roll(depth[:-1], -1, axis=1), depth[1:], np.roll(depth[1:], -1, axis=1)])
        coherent = (depths.max(0) < 23.4) & (np.ptp(depths, axis=0) < 1.6)
        for a in [0.0, 0.25, 0.5, 0.75, 1.0]:
            for b in [0.0, 0.25, 0.5, 0.75, 1.0]:
                surface.append(((1 - a) * (1 - b) * p00 + (1 - a) * b * p01 + a * (1 - b) * p10 + a * b * p11)[coherent])
        cells = self.cells(np.concatenate(surface))
        cells = cells[self.valid(cells)]
        unique = np.unique(np.ravel_multi_index(tuple(cells.T), self.shape))
        flat[unique] = np.minimum(flat[unique] + 3, 12)
        here = self.cells(self.position)
        self.evidence[tuple(here)] = -8

    def update(self, v):
        if self.tick:
            self.yaw += float(v[268]) * 2.6 * 0.05
            self.position += v[260:263] * 3 @ self.rotation().T * 0.05
        else:
            self.position[2] = float(v[267]) * 16
        local = v[256:259]
        local = local / max(np.linalg.norm(local), 1e-06) * max(v[259], 0) * np.linalg.norm(np.array([48.0, 48.0, 16.0]) - 0.32)
        if self.initial_goal is None:
            self.initial_goal = self.position + local @ self.rotation().T
        expected = self.initial_goal - self.position
        if np.linalg.norm(local[:2]) > 2:
            beacon_yaw = np.arctan2(expected[1], expected[0]) - np.arctan2(local[1], local[0])
            error = (beacon_yaw - self.yaw + np.pi) % (2 * np.pi) - np.pi
            self.yaw += np.clip(error, -0.02, 0.02) * 0.2
        observed = self.position + local @ self.rotation().T
        self.position += np.clip(self.initial_goal - observed, -0.2, 0.2) * 0.15
        self.position[2] = 0.8 * self.position[2] + 0.2 * float(v[267]) * 16
        self.tick += 1
        self.current_values = v.copy()
        self.local_goal = local
        return self.initial_goal

    def grid(self):
        occupied = self.evidence >= 2
        occupied[:, :, 0] = True
        occupied[:, :, -1] = True
        inflated = ndimage.binary_dilation(occupied, structure=ndimage.generate_binary_structure(3, 1))
        current = self.cells(self.position)
        self.tight = bool(inflated[tuple(current)])
        costs = np.where(self.evidence < 0, 1.0, 2.8).astype(np.float32)
        costs[inflated] = np.inf
        if self.tight:
            lower = np.maximum(current - 2, 0)
            upper = np.minimum(current + 3, self.shape)
            region = tuple((slice(int(a), int(b)) for a, b in zip(lower, upper)))
            view = costs[region]
            solid = occupied[region]
            view[~solid & ~np.isfinite(view)] = 8
        costs[tuple(current)] = 1
        return costs

    def plan(self, goal):
        cost = self.grid()
        start = tuple(self.cells(self.position))
        finish = tuple(self.cells(goal))
        sx, sy, sz = self.shape
        n = sx * sy * sz
        flat = cost.ravel()
        start_id = np.ravel_multi_index(start, self.shape)
        end_id = np.ravel_multi_index(finish, self.shape)
        scores = np.full(n, np.inf, np.float32)
        scores[start_id] = 0
        parents = np.full(n, -1, np.int32)
        seen = np.zeros(n, bool)
        shifts = [(int(a), int(b), int(c), int(a) * sy * sz + int(b) * sz + int(c), float(length)) for (a, b, c), length in zip(self.neighbors, self.lengths)]
        q = [(0.0, 0.0, int(start_id))]
        best = int(start_id)
        best_h = np.inf
        expanded = 0
        found = False
        began = time.perf_counter()
        ex, ey, ez = finish
        while q and expanded < 12000:
            _, g, uid = heapq.heappop(q)
            if seen[uid]:
                continue
            seen[uid] = True
            expanded += 1
            x, rem = divmod(uid, sy * sz)
            y, z = divmod(rem, sz)
            h = math.sqrt((x - ex) ** 2 + (y - ey) ** 2 + (z - ez) ** 2)
            if h < best_h:
                best_h = h
                best = uid
            if uid == end_id:
                best = uid
                found = True
                break
            for a, b, c, offset, length in shifts:
                xx, yy, zz = (x + a, y + b, z + c)
                if not (0 <= xx < sx and 0 <= yy < sy and (0 <= zz < sz)):
                    continue
                wid = uid + offset
                if seen[wid] or not math.isfinite(float(flat[wid])):
                    continue
                if a and (not math.isfinite(float(flat[uid + a * sy * sz]))):
                    continue
                if b and (not math.isfinite(float(flat[uid + b * sz]))):
                    continue
                if c and (not math.isfinite(float(flat[uid + c]))):
                    continue
                ng = g + float(flat[wid]) * length
                if ng >= scores[wid]:
                    continue
                scores[wid] = ng
                parents[wid] = uid
                heuristic = math.sqrt((xx - ex) ** 2 + (yy - ey) ** 2 + (zz - ez) ** 2)
                heapq.heappush(q, (ng + 4.5 * heuristic, ng, wid))
        if not found:
            while q and seen[q[0][2]]:
                heapq.heappop(q)
            if q:
                best = q[0][2]
        route = [best]
        while parents[route[-1]] >= 0:
            route.append(int(parents[route[-1]]))
        route.reverse()
        self.route = [self.origin + (np.array(np.unravel_index(i, self.shape)) + 0.5) * self.res for i in route]
        self.cost = cost
        if found:
            self.route.append(np.array(goal, dtype=float))
        self.debug = dict(found=found, expanded=expanded, path_cells=len(route), plan_seconds=time.perf_counter() - began, goal=goal.tolist(), position=self.position.tolist(), yaw=self.yaw)

    def target(self):
        if not self.route:
            return self.initial_goal - self.position
        nearest = int(np.argmin([np.linalg.norm(p - self.position) for p in self.route]))
        self.route = self.route[nearest:]
        while len(self.route) > 1 and np.linalg.norm(self.route[0] - self.position) < 0.35:
            self.route = self.route[1:]
        target = self.route[0]
        for p in self.route[1:]:
            distance = np.linalg.norm(p - self.position)
            if distance > (1.0 if self.tight else 3.0):
                break
            cells = self.cells(self.position[None] + (p - self.position)[None] * np.linspace(0, 1, max(2, int(distance / 0.1)))[:, None])
            if not self.valid(cells).all() or not np.isfinite(self.cost[tuple(cells.T)]).all():
                break
            target = p
        self.debug.update(target_delta_global=(target - self.position).tolist(), tight=self.tight)
        return target - self.position

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
        speed = min(0.8 if self.tight else 1.8, D * 1.5, limit)
        desired = direction * speed
        desired[:2] *= max(0.0, np.cos(error)) ** 4
        horizontal = np.linalg.norm(desired[:2])
        thrust = np.clip(3 * (horizontal - velocity[0]) + 0.6 * horizontal, -1.2, 3)
        vertical = np.clip((3 * (desired[2] - velocity[2]) + 0.8 * desired[2]) / 2.5, -1, 1)
        self.debug.update(ahead=float(ahead), requested_speed=float(speed))
        return np.array([thrust / (3 if thrust >= 0 else 1.2), 0, vertical, np.clip(error * 2 / 1.8, -1, 1)], np.float32)


class ObservedMapPolicy:
    """Viewer adapter with independent map and odometry on every episode reset."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.controller = ObservedMapController()

    def predict(self, features, deterministic=True):
        features = np.asarray(features)
        if features.shape != (1, 9, 3869) or not np.isfinite(features).all():
            raise ValueError("Observed map requires one finite nine-frame v6 observation")
        return self.controller.action(features[0])[None], None

    @property
    def specification(self):
        return {"version": CONTROLLER_VERSION, "kind": "explicit_geometry_planner",
                "learned": False, "training_invoked": False,
                "input": "reconstructed_full_connectome_activity",
                "readout": "neural-projection-motion-stable-visual005-v1",
                "room_size": [48, 48, 16], "dynamics": "coordinated",
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
