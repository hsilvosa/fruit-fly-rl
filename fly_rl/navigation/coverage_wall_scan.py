"""Choose wall exploration direction from visited coverage, not beacon bearing alone."""
import numpy as np
from fly_rl.navigation.revisit_wall_scan import RevisitWallScanController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-coverage-wall-scan-exp1'

class CoverageWallScanController(RevisitWallScanController):
    def choose_scan_target(self, scan):
        normal, tangent = scan['normal'], scan['tangent']
        projected = self.position - normal * ((self.position - scan['center']) @ normal + 1.7)
        options = []
        seen = (np.asarray(list(self.seen_positions), dtype=float) + .5) * 2. if self.seen_positions else np.empty((0, 3))
        scan['coverage_direction_scores'] = []
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
            relative = seen - projected
            longitudinal = relative @ normal
            along = (relative @ tangent) * direction
            coverage = int(((np.abs(longitudinal) < 3.) & (along > 2.) & (along < 18.)).sum())
            penalty = self.scan_visits.get(key, 0) * 20 + coverage
            scan['coverage_direction_scores'].append(dict(direction=int(direction), covered_cells=coverage, penalty=penalty))
            options.append((penalty, int(direction != scan['direction']), direction, point))
        if not options:
            return None
        _, _, direction, point = min(options, key=lambda item: item[:2])
        scan['direction'] = direction
        return point


    def plan(self, goal):
        super().plan(goal)
        self.debug.update(scan_coverage_scores=self.scan.get('coverage_direction_scores', []) if self.scan else [],
                          scan_direction=int(self.scan['direction']) if self.scan else None)
