"""Static architectural flight using the existing physical and sensor contracts."""
import numpy as np
from fly_rl.simulation.world import FlightWorld, DT, ROOM
from fly_rl.simulation.sensors import SENSOR_V6
from fly_rl.simulation.architectural_scenes import BUILDERS, validate

class ArchitecturalWorld(FlightWorld):
    def __init__(self, scene, situation=0, seed=0):
        if scene not in BUILDERS:
            raise ValueError('Unknown architectural scene')
        self.scene = BUILDERS[scene]()
        validate(self.scene)
        if type(situation) is not int:
            raise ValueError('Situation index must be an integer')
        self.situation_index = situation
        if not 0 <= self.situation_index < len(self.scene.situations):
            raise ValueError('Unknown architectural situation')
        self.scene_hash = self.scene.fingerprint()
        route = np.asarray(self.scene.situations[self.situation_index].route)
        length = float(np.linalg.norm(np.diff(route, axis=0), axis=1).sum())
        self.architectural_deadline = int(np.ceil(max(60., 2*length/1.5+15.)/DT))
        super().__init__(seed=seed, mode='empty', dynamics='coordinated', sensor_version=SENSOR_V6)

    def reset(self, seed=None, options=None):
        self.room = ROOM.copy()
        self.mode = 'empty'
        super().reset(seed=seed, options=options)
        self.mode = 'architecture'
        self.room = np.asarray(self.scene.size, dtype=float).copy()
        self.obstacles = [(np.asarray(s.low,dtype=float).copy(), np.asarray(s.high,dtype=float).copy())
                          for s in self.scene.solids]
        situation = self.scene.situations[self.situation_index]
        self.position = np.asarray(situation.route[0],dtype=float).copy()
        self.target = np.asarray(situation.route[-1],dtype=float).copy()
        self.reference_route = []
        self.episode_limit = self.architectural_deadline
        self.velocity = np.zeros(3)
        self.yaw = float(self.rng.uniform(-np.pi,np.pi))
        self.distance = float(np.linalg.norm(self.target-self.position))
        info = {'room_seed':self.seed_value,'scene':self.scene.name,'scene_sha256':self.scene_hash,
                'situation':situation.name,'architecture_schema':self.scene.to_dict()['schema']}
        return self.observe(),info

    def snapshot(self):
        result=super().snapshot()
        result.update(architecture_schema=self.scene.to_dict()['schema'],
                      architectural_scene=self.scene.name,scene_sha256=self.scene_hash,
                      situation=self.scene.situations[self.situation_index].name,
                      situation_index=self.situation_index)
        return result
