"""Temporary route vetoes recover conservative range-braking deadlocks."""
import numpy as np
from fly_rl.navigation.portal_fast import FastPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp8'


class RecoveryPortalController(FastPortalController):
    """Keep observed occupancy separate from temporary execution constraints."""

    def __init__(self, room_size=(48.,48.,16.)):
        super().__init__(room_size)
        self.reference_vetoes={}
        self.stall_ticks=0
        self.stall_recoveries=0

    def grid(self):
        costs=super().grid()
        current=tuple(self.cells(self.position))
        self.reference_vetoes={cell:expiry for cell,expiry in self.reference_vetoes.items() if expiry>self.tick}
        for cell in self.reference_vetoes:
            if cell!=current:costs[cell]=np.inf
        return costs

    def veto_stalled_reference(self, delta, speed, actual_speed):
        stalled=(delta is not None and speed<.02 and actual_speed<.05)
        self.stall_ticks=self.stall_ticks+1 if stalled else 0
        if self.stall_ticks<25:return False
        cell=self.cells(self.position+np.asarray(delta))
        if not self.valid(cell) or tuple(cell)==tuple(self.cells(self.position)):return False
        self.reference_vetoes[tuple(cell)]=self.tick+200
        self.reference=None
        self.route=[]
        self.stall_ticks=0
        self.stall_recoveries+=1
        return True

    def action(self, features):
        result=super().action(features)
        recovered=self.veto_stalled_reference(self.debug.get('target_delta_global'),
            self.debug.get('requested_speed',1.),self.debug.get('actual_speed',1.))
        self.debug.update(stall_recovery=recovered,stall_ticks=self.stall_ticks,
            stall_recoveries=self.stall_recoveries,temporary_reference_vetoes=len(self.reference_vetoes))
        return result
