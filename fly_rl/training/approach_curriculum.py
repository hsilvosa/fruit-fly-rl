"""Training-only start-position curriculum; unchanged goal, collisions and rewards."""
import numpy as np
from fly_rl.simulation.world import FlightWorld,RADIUS,segment_box
VERSION='approach-v1-half-to-zero'


class ApproachSchedule:
    def __init__(self,total,offset=0):
        if type(total) is not int or total<=0 or type(offset) is not int or not 0<=offset<=total:raise ValueError('Invalid curriculum transition schedule')
        self.total=total;self.transitions=offset;self.initial_offset=offset
        self.resets={'near':0,'ordinary':0,'fallback':0}

    @property
    def probability(self):return .5*max(0.,1.-2.*self.transitions/self.total)

    def snapshot(self):
        return {'version':VERSION,'total':self.total,'initial_offset':self.initial_offset,'transitions':self.transitions,
            'near_probability':self.probability,'resets_including_initialization':dict(self.resets),
            'distance_range':[.7,3.],'clearance_extra':.02,'attempt_limit':64}


class ApproachWorld(FlightWorld):
    def __init__(self,*args,schedule,**kwargs):
        self.schedule=schedule;self.approach_rng=np.random.default_rng(0)
        if kwargs.get('mode')!='dense' or not kwargs.get('layout_seeds'):raise ValueError('Curriculum requires explicit dense training layouts')
        super().__init__(*args,**kwargs)

    def reset(self,seed=None,options=None):
        if seed is not None:self.approach_rng=np.random.default_rng(int(seed)^0x5A17A9)
        obs,info=super().reset(seed,options);p=self.schedule.probability;kind='ordinary'
        if self.approach_rng.random()<p:
            kind='fallback'
            for _ in range(64):
                direction=self.approach_rng.normal(size=3);norm=np.linalg.norm(direction)
                if norm<1e-12:continue
                position=self.target+direction/norm*self.approach_rng.uniform(.7,3.)
                margin=RADIUS+.02
                if (position<margin).any() or (position>self.room-margin).any():continue
                if any(segment_box(position,self.target,low-margin,high+margin) for low,high in self.obstacles):continue
                self.position=position;self.distance=float(np.linalg.norm(self.target-position))
                self.reference_route=[position.copy(),self.target.copy()];kind='near';break
        self.schedule.resets[kind]+=1
        info['curriculum']={'version':VERSION,'kind':kind,'near_probability':p,'transition_offset':self.schedule.transitions}
        return self.observe(),info

    def step(self,action):
        result=super().step(action);self.schedule.transitions+=1
        return result


def configure_curriculum(env,total,offset,seed):
    from fly_rl.simulation.sensors import SENSOR_V3
    if any(w.mode!='dense' or w.dynamics!='coordinated' or w.sensor_version!=SENSOR_V3 or not w.layout_seeds for w in env.worlds):raise ValueError('Approach curriculum requires v3 coordinated dense training layouts')
    schedule=ApproachSchedule(total,offset)
    env.worlds=[ApproachWorld(seed=seed+i,mode=w.mode,layout_seeds=w.layout_seeds,dynamics=w.dynamics,sensor_version=w.sensor_version,map_profile=w.map_profile,schedule=schedule) for i,w in enumerate(env.worlds)]
    env.curriculum=schedule
    return schedule
