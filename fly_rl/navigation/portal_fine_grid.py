"""Experimental finer occupancy representation for narrow maze passages."""
import numpy as np
from fly_rl.navigation.portal_center_refinement import RefiningPortalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT, SUPPORTED_PROFILES

CONTROLLER_VERSION = 'observed-neuronal-map-portal-reference-exp11'


class FineGridPortalController(RefiningPortalController):
    """Change map discretization only; preserve neural decoding and physical guards."""

    def __init__(self, room_size=(48.,48.,16.)):
        super().__init__(room_size)
        self.res=.4
        extent=float(np.ceil(np.linalg.norm(self.room_size[:2])/self.res)*self.res)
        side=int(round(2*extent/self.res))
        self.shape=(side,side,int(np.ceil(self.room_size[2]/self.res))+1)
        self.origin=np.array([-extent,-extent,0.])
        self.evidence=np.zeros(self.shape,np.int8)
        self.reference=None
        self.route=[]
