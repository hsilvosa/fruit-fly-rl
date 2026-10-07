"""Use repeated completed surface observations to reject discordant opening fits."""
import numpy as np
from fly_rl.navigation.coverage_wall_scan import CoverageWallScanController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-consistent-opening-exp1'

class ConsistentOpeningController(CoverageWallScanController):
    def __init__(self, room_size=(64., 64., 20.)):
        super().__init__(room_size)
        self.discordant_opening_fits = 0

    def crossing_consensus(self):
        if len(self.completed_planes) < 3:
            return None
        normals = np.asarray([normal for _, normal in self.completed_planes])
        counts = (np.abs(normals @ normals.T) > .98).sum(axis=1)
        index = int(np.argmax(counts))
        if counts[index] < 3 or counts[index] < .75 * len(normals):
            return None
        normal = normals[index]
        toward = self.initial_goal - self.position
        toward[2] = 0.
        toward /= max(np.linalg.norm(toward), 1e-8)
        if abs(normal @ toward) < .8:
            return None
        return normal

    def detect_portal(self, values):
        observed = super().detect_portal(values)
        normal = self.crossing_consensus() if self.initial_goal is not None else None
        if observed is not None and normal is not None and abs(observed['normal'] @ normal) < .98:
            self.discordant_opening_fits += 1
            return None
        return observed

    def plan(self, goal):
        super().plan(goal)
        self.debug.update(discordant_opening_fits=self.discordant_opening_fits,
                          crossing_normal_consensus=self.crossing_consensus() is not None)
