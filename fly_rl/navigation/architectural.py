"""Known-dimension architectural planner; layout and reference routes are not inputs."""
import numpy as np
from fly_rl.navigation.clearance_goal import ClearanceGoalController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT

CONTROLLER_VERSION = 'observed-neuronal-map-architecture-exp1'

class ArchitecturalController(ClearanceGoalController):
    def __init__(self, room_size):
        super().__init__((64.,64.,20.))
        size = np.asarray(room_size,dtype=float)
        if size.shape != (3,) or not np.isfinite(size).all() or (size<=.8).any() or np.linalg.norm(size[:2])>128:
            raise ValueError('Unsupported architectural dimensions')
        self.room_size = size.copy()
        self.res = .25
        extent = np.ceil(np.linalg.norm(size[:2])/self.res)*self.res
        side = int(round(2*extent/self.res))
        self.shape = (side,side,int(np.ceil(size[2]/self.res))+1)
        self.origin = np.array([-extent,-extent,0.])
        self.evidence = np.zeros(self.shape,np.int8)


class ArchitecturalPlannerPolicy:
    """Explicit planning adapter with an architecture-specific room contract."""
    def __init__(self, room_size):
        self.room_size = np.asarray(room_size,dtype=float).copy()
        self.reset()

    def reset(self):
        self.controller = ArchitecturalController(self.room_size)

    def predict(self, features, deterministic=True):
        features = np.asarray(features)
        if features.shape != (1,9,FEATURE_COUNT) or not np.isfinite(features).all():
            raise ValueError('Architectural planner requires finite nine-frame full-connectome features')
        return self.controller.action(features[0])[None], None

    @property
    def specification(self):
        return dict(controller_version='planner-1.4-exp.1',version=CONTROLLER_VERSION,
                    kind='explicit_geometry_planner',learned=False,training_invoked=False,
                    readout=READOUT_VERSION,input='reconstructed_full_connectome_activity',
                    room_size=self.room_size.tolist(),grid_resolution=self.controller.res,
                    experimental=True,hidden_geometry_input=False,reference_route_input=False)
