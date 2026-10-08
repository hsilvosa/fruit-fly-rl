"""Room-contract decoding and committed local references for larger maps."""
import numpy as np
from fly_rl.navigation.dual_safety import DualSafetyController, READOUT_VERSION, READOUT_MODULE, READOUT_CLASS, FEATURE_COUNT

CONTROLLER_VERSION = 'observed-neuronal-map-room-aware-exp1'
SUPPORTED_PROFILES = ('large', 'maze')


class RoomAwareController(DualSafetyController):
    """Receives known room dimensions, never hidden layout, pose, or route."""

    def __init__(self, room_size=(48., 48., 16.)):
        super().__init__()
        self.room_size = np.asarray(room_size, dtype=float)
        if self.room_size.shape != (3,) or tuple(self.room_size) not in ((48.,48.,16.), (64.,64.,20.)):
            raise ValueError('Room-aware planning supports declared large and maze contracts only')
        if self.room_size[2] > 16:
            extent = float(np.ceil(np.linalg.norm(self.room_size[:2])/self.res)*self.res)
            side = int(round(2*extent/self.res))
            self.shape = (side, side, int(np.ceil(self.room_size[2]/self.res))+1)
            self.origin = np.array([-extent, -extent, 0.])
            self.evidence = np.zeros(self.shape, np.int8)
        self.reference = None
        self.reference_tick = 0
        self.reference_generation = 0

    def update(self, v):
        if self.tick:
            self.yaw += float(v[268])*2.6*.05
            self.position += v[260:263]*3 @ self.rotation().T*.05
        else:
            self.position[2] = float(v[267])*self.room_size[2]
        local = v[256:259]
        local = local/max(np.linalg.norm(local), 1e-6)*max(v[259], 0)*np.linalg.norm(self.room_size-.32)
        if self.initial_goal is None:
            self.initial_goal = self.position+local @ self.rotation().T
        expected = self.initial_goal-self.position
        if np.linalg.norm(local[:2]) > 2:
            beacon = np.arctan2(expected[1],expected[0])-np.arctan2(local[1],local[0])
            error = (beacon-self.yaw+np.pi)%(2*np.pi)-np.pi
            self.yaw += np.clip(error,-.02,.02)*.2
        observed = self.position+local @ self.rotation().T
        self.position += np.clip(self.initial_goal-observed,-.2,.2)*.15
        self.position[2] = .8*self.position[2]+.2*float(v[267])*self.room_size[2]
        self.tick += 1
        self.current_values = v.copy()
        self.local_goal = local
        return self.initial_goal

    def reference_clear(self, point):
        length = np.linalg.norm(point-self.position)
        fractions = np.linspace(0,1,max(2,int(np.ceil(length/.1))+1))
        cells = self.cells(self.position+(point-self.position)*fractions[:,None])
        return self.valid(cells).all() and np.isfinite(self.cost[tuple(cells.T)]).all()

    def target(self):
        proposed = self.position+super().target()
        reached = self.reference is not None and np.linalg.norm(self.reference-self.position) < .55
        expired = self.tick-self.reference_tick >= 120
        clear = self.reference is not None and self.reference_clear(self.reference)
        retained = self.reference is not None and not reached and not expired and clear
        if not retained:
            self.reference = proposed.copy()
            self.reference_tick = self.tick
            self.reference_generation += 1
        delta = self.reference-self.position
        self.debug.update(target_delta_global=delta.tolist(), reference_retained=bool(retained),
            reference_generation=self.reference_generation, reference_age=self.tick-self.reference_tick,
            reference_reached=bool(reached), reference_expired=bool(expired),
            room_size=self.room_size.tolist())
        return delta
