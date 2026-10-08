"""Release opening crossings that remain unreachable in the observed map."""
import numpy as np
from fly_rl.navigation.coverage_wall_scan import CoverageWallScanController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-unreachable-crossing-exp1'

class UnreachableCrossingController(CoverageWallScanController):
    def __init__(self, room_size=(64., 64., 20.)):
        super().__init__(room_size)
        self.unreachable_since = None
        self.unreachable_portal = None
        self.rejected_openings = []
        self.crossing_releases = 0

    def detect_portal(self, values):
        observed = super().detect_portal(values)
        self.rejected_openings = [item for item in self.rejected_openings if item[2] > self.tick]
        if observed is not None and any(
                observed['normal'] @ normal > .9 and np.linalg.norm(observed['center'] - center) < 3.
                for center, normal, _ in self.rejected_openings):
            return None
        return observed

    def release_unreachable_crossing(self):
        portal = self.portal
        unreachable = portal is not None and self.portal_phase == 'cross' and not self.debug.get('found', True)
        if not unreachable:
            self.unreachable_since = None
            self.unreachable_portal = None
            return False
        if self.unreachable_portal is not portal:
            self.unreachable_portal = portal
            self.unreachable_since = self.tick
        if self.tick - self.unreachable_since < 100:
            return False
        self.rejected_openings.append((portal['center'].copy(), portal['normal'].copy(), self.tick + 600))
        self.portal = None
        self.portal_phase = 'none'
        self.reference = None
        self.route = []
        self.unreachable_since = None
        self.unreachable_portal = None
        self.crossing_releases += 1
        return True

    def plan(self, goal):
        super().plan(goal)
        released = self.release_unreachable_crossing()
        self.debug.update(crossing_released=released, crossing_releases=self.crossing_releases,
                          rejected_openings=len(self.rejected_openings),
                          unreachable_crossing_ticks=0 if self.unreachable_since is None else self.tick-self.unreachable_since)
