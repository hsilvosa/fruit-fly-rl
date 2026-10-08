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
        import hashlib
        from pathlib import Path
        return dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    sources=[dict(archive_file='controller-'+path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in self.source_files()],
                    controller_version='planner-1.4-exp.1',version=CONTROLLER_VERSION,
                    controller_label='architectural observed-map planner',
                    kind='explicit_geometry_planner',learned=False,training_invoked=False,
                    readout=READOUT_VERSION,input='reconstructed_full_connectome_activity',
                    room_size=self.room_size.tolist(),grid_resolution=self.controller.res,
                    experimental=True,hidden_geometry_input=False,reference_route_input=False)

    def source_files(self):
        import inspect
        from pathlib import Path
        paths={Path(__file__)}
        for kind in ArchitecturalController.__mro__ + READOUT_CLASS.__mro__:
            if kind is not object:paths.add(Path(inspect.getfile(kind)))
        return sorted(paths)

    def archive_sources(self, directory):
        import hashlib,json
        from pathlib import Path
        directory=Path(directory)
        spec=dict(self.specification)
        for path in self.source_files():
            name='controller-'+path.name
            (directory/name).write_bytes(path.read_bytes())
        (directory/'controller.py').write_bytes(Path(__file__).read_bytes())
        (directory/'controller.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
