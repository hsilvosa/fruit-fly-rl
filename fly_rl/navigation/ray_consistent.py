"""Experimental v63: interpolation cannot override current free-ray evidence."""
import numpy as np
from fly_rl.navigation.distance_stable import DistanceStableController
from fly_rl.navigation.distance_stable import READOUT_VERSION, READOUT_MODULE, READOUT_CLASS

CONTROLLER_VERSION = 'observed-neuronal-map-v63-ray-consistent'


class RayConsistentController(DistanceStableController):
    """Keep measured hits; suppress only virtual surface writes over current free rays."""

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
        free_ids = unique.copy()
        endpoints = self.position + dirs * ranges[:, None]
        hit = ranges < 23.4
        surface = [endpoints[hit]]
        direct_cells = self.cells(endpoints[hit])
        direct_cells = direct_cells[self.valid(direct_cells)]
        direct_ids = np.unique(np.ravel_multi_index(tuple(direct_cells.T), self.shape))
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
        unique = np.union1d(np.setdiff1d(unique, free_ids, assume_unique=True), direct_ids)
        flat[unique] = np.minimum(flat[unique] + 3, 12)
        here = self.cells(self.position)
        self.evidence[tuple(here)] = -8

