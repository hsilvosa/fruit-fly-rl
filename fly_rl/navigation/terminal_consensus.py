"""Restrict completed-surface filtering to the final quarter of goal distance."""
import numpy as np
from fly_rl.navigation.consistent_opening import ConsistentOpeningController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-terminal-consensus-exp1'

class TerminalConsensusController(ConsistentOpeningController):
    def __init__(self, room_size=(64.,64.,20.)):
        super().__init__(room_size)
        self.initial_distance = None

    def update(self, values):
        goal = super().update(values)
        if self.initial_distance is None:
            self.initial_distance = float(np.linalg.norm(self.local_goal))
        return goal

    def crossing_consensus(self):
        if self.initial_distance is None or np.linalg.norm(self.local_goal) > .25*self.initial_distance:
            return None
        return super().crossing_consensus()
