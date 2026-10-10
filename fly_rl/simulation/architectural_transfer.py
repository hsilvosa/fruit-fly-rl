"""Architectural scenes for any sensor contract (level C of the unseen-map plan).

`ArchitecturalWorld` is fixed to the panorama sensor contract and is a protected historical source. This class
repeats its geometry and reset logic with a configurable sensor version, so that policies with the v2 or v3
contract can be evaluated on the synthetic architectural scenes. Geometry, deadlines and situations are identical.
"""
import numpy as np
from fly_rl.simulation.world import FlightWorld, DT, ROOM
from fly_rl.simulation.architectural_scenes import BUILDERS, validate


class ArchitecturalSceneWorld(FlightWorld):
    def __init__(self, scene, situation=0, seed=0, sensor_version=None):
        if scene not in BUILDERS:
            raise ValueError('Unknown architectural scene')
        self.scene = BUILDERS[scene]()
        validate(self.scene)
        if type(situation) is not int or not 0 <= situation < len(self.scene.situations):
            raise ValueError('Unknown architectural situation')
        self.situation_index = situation
        self.scene_hash = self.scene.fingerprint()
        route = np.asarray(self.scene.situations[situation].route)
        length = float(np.linalg.norm(np.diff(route, axis=0), axis=1).sum())
        self.architectural_deadline = int(np.ceil(max(60., 2 * length / 1.5 + 15.) / DT))
        super().__init__(seed=seed, mode='empty', dynamics='coordinated', sensor_version=sensor_version)

    def reset(self, seed=None, options=None):
        self.room = ROOM.copy()
        self.mode = 'empty'
        super().reset(seed=seed, options=options)
        self.mode = 'architecture'
        self.room = np.asarray(self.scene.size, dtype=float).copy()
        self.obstacles = [(np.asarray(s.low, dtype=float).copy(), np.asarray(s.high, dtype=float).copy())
                          for s in self.scene.solids]
        situation = self.scene.situations[self.situation_index]
        self.position = np.asarray(situation.route[0], dtype=float).copy()
        self.target = np.asarray(situation.route[-1], dtype=float).copy()
        self.reference_route = []
        self.episode_limit = self.architectural_deadline
        self.velocity = np.zeros(3)
        self.yaw = float(self.rng.uniform(-np.pi, np.pi))
        self.distance = float(np.linalg.norm(self.target - self.position))
        info = {'room_seed': self.seed_value, 'scene': self.scene.name, 'scene_sha256': self.scene_hash,
                'situation': situation.name}
        return self.observe(), info


def all_situations():
    """Every (scene, situation index, situation name) of the six synthetic scenes."""
    return [(name, i, s.name) for name, build in BUILDERS.items() for i, s in enumerate(build().situations)]
