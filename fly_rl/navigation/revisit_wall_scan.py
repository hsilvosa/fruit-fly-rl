"""Restrict wall recovery to repeated visits, preserving exploration of new space."""
import numpy as np
from fly_rl.navigation.progress_wall_scan import ProgressWallScanController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-revisit-wall-scan-exp1'

class RevisitWallScanController(ProgressWallScanController):
    def __init__(self, room_size=(64.,64.,20.)):
        super().__init__(room_size)
        self.seen_positions = set()
        self.recent_novelty = []
        self.low_novelty_streak = 0

    def update(self, values):
        goal = super().update(values)
        if self.tick % 20 == 1:
            self.sample_position()
        return goal

    def sample_position(self):
        cell = tuple(np.floor(self.position / 2.).astype(int))
        self.recent_novelty.append(cell not in self.seen_positions)
        self.seen_positions.add(cell)
        self.recent_novelty = self.recent_novelty[-16:]
        low = self.portal is None and len(self.recent_novelty) == 16 and sum(self.recent_novelty) < 4
        self.low_novelty_streak = self.low_novelty_streak + 1 if low else 0

    def plan(self, goal):
        defer = self.scan is None and self.low_novelty_streak < 3
        last_progress = self.longitudinal_tick
        if defer:
            self.longitudinal_tick = self.tick
        super().plan(goal)
        if defer:
            self.longitudinal_tick = last_progress
        self.debug.update(revisit_scan_eligible=self.low_novelty_streak >= 3,
                          low_novelty_streak=self.low_novelty_streak,
                          novel_position_samples=sum(self.recent_novelty),
                          longitudinal_no_progress_ticks=self.tick-self.longitudinal_tick)
