"""Refine a sparsely observed opening while approaching its fitted surface."""
import numpy as np
from fly_rl.navigation.portal_recovery import RecoveryPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp9'


class RefiningPortalController(RecoveryPortalController):
    """Accept stronger support for the same opening; keep crossing references fixed."""

    def __init__(self, room_size=(48.,48.,16.)):
        super().__init__(room_size)
        self.portal_refinements=0

    def refine_portal(self, observed):
        old=self.portal
        if old is None or observed is None or self.portal_phase!='approach':return False
        offset=observed['center']-old['center']
        normal=old['normal']
        support=observed['ray_support']
        if (support<=old['ray_support'] or support<3 or observed['normal']@normal<.98
                or abs(offset@normal)>.4 or np.linalg.norm(offset-normal*(offset@normal))>3.):return False
        weight=support/(support+old['ray_support'])
        change=offset*weight
        old['center']=old['center']+change
        old['ray_support']=support
        if np.linalg.norm(change)>.15:self.reference=None;self.route=[]
        self.portal_refinements+=1
        return True

    def plan(self, goal):
        refined=False
        if self.portal is not None and self.portal_phase=='approach':
            refined=self.refine_portal(self.detect_portal(self.current_values))
        super().plan(goal)
        self.debug.update(portal_refined=refined,portal_refinements=self.portal_refinements)
