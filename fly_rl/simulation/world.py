"""Lightweight 3D flight with exact segment-versus-box collision checks."""
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from fly_rl.simulation.sensors import DIRECTIONS,RAY_RANGE,SENSORS
ROOM=np.array([12.,12.,6.])
RADIUS=.16
DT=.05
REWARD_VERSION='navigation-v2-progress-timeout'
WORLD_VERSION='rooms-v3-dense-random-goals'

def segment_box(start,end,low,high):
    """Return whether a closed segment intersects a closed axis-aligned box."""
    delta=np.asarray(end)-start
    t0=0.; t1=1.
    for axis in range(3):
        if abs(delta[axis])<1e-12:
            if start[axis]<low[axis] or start[axis]>high[axis]: return False
        else:
            a=(low[axis]-start[axis])/delta[axis]; b=(high[axis]-start[axis])/delta[axis]
            t0=max(t0,min(a,b)); t1=min(t1,max(a,b))
            if t0>t1: return False
    return True

def ray_box(start,direction,low,high):
    near=0.; far=float('inf')
    for k in range(3):
        if abs(direction[k])<1e-12:
            if not low[k]<=start[k]<=high[k]: return float('inf')
        else:
            a=(low[k]-start[k])/direction[k]; b=(high[k]-start[k])/direction[k]
            near=max(near,min(a,b)); far=min(far,max(a,b))
    return near if far>=near else float('inf')

class FlightWorld(gym.Env):
    metadata={'render_modes':[]}
    def __init__(self, seed=0, mode='obstacles',layout_seeds=None,dynamics='legacy',sensor_version=None,map_profile=None):
        from fly_rl.simulation.sensors import SENSOR_VERSION,validate_sensor_version
        self.sensor_version=validate_sensor_version(sensor_version or SENSOR_VERSION)
        if dynamics not in ['legacy','coordinated']: raise ValueError('Unknown dynamics')
        self.dynamics=dynamics
        if mode not in ['near','empty','obstacles','dense']: raise ValueError('Unknown room mode')
        self.mode=mode
        from fly_rl.simulation.map_profiles import resolve_profile
        self.map_profile=resolve_profile(map_profile)
        if self.map_profile is not None and mode!='dense': raise ValueError('Map profiles require dense room mode')
        self.room=np.array([32.,32.,12.]) if mode=='dense' else ROOM.copy()
        if self.map_profile is not None: self.room=np.array(self.map_profile.room_size,dtype=float)
        self.episode_limit=1200 if mode=='dense' else 600
        self.layout_seeds=list(layout_seeds) if layout_seeds is not None else None
        self.sampler=np.random.default_rng(seed)
        self.rng=np.random.default_rng(seed)
        self.action_space=spaces.Box(-1,1,(4,),dtype=np.float32)
        self.observation_space=spaces.Box(-1,1,(SENSORS,),dtype=np.float32)
        self.seed_value=seed
        self.reset(seed=seed)

    def reset(self,seed=None,options=None):
        super().reset(seed=seed)
        if self.layout_seeds is not None:
            if seed is not None: self.sampler=np.random.default_rng(seed)
            seed=int(self.sampler.choice(self.layout_seeds))
        if seed is not None: self.rng=np.random.default_rng(seed); self.seed_value=seed
        self.obstacles=[]
        # Center-lane blocks leave a guaranteed free corridor at each side and above.
        for x in [4.,7.,9.5]:
            center=np.array([x,self.rng.uniform(4.5,7.5),self.rng.uniform(1.5,2.5)])
            half=np.array([.35,self.rng.uniform(.6,1.1),self.rng.uniform(.5,1.)])
            self.obstacles.append((center-half,center+half))
        self.position=np.array([1.,self.rng.uniform(3.,9.),self.rng.uniform(2.,4.)])
        self.target=np.array([11.,self.rng.uniform(3.,9.),self.rng.uniform(2.,4.)])
        if self.mode!='obstacles': self.obstacles=[]
        if self.mode=='near':
            self.position=np.array([5.,self.rng.uniform(4.,8.),self.rng.uniform(2.,4.)])
            delta=np.array([self.rng.uniform(1.5,3.),self.rng.uniform(-1.,1.),self.rng.uniform(-.6,.6)])
            self.target=self.position+delta
        self.reference_route=[]
        if self.mode=='dense':
            if self.map_profile is None: self._dense_layout()
            else:
                from fly_rl.simulation.map_profiles import generate_layout
                generate_layout(self,self.map_profile)
        self.velocity=np.zeros(3); self.yaw=0.; self.ticks=0
        self.yaw_rate=0.;self.bank=0.;self.pitch=0.
        if self.mode=='dense': self.yaw=float(self.rng.uniform(-np.pi,np.pi))
        self.last_action=np.zeros(4,dtype=np.float32)
        self.distance=float(np.linalg.norm(self.target-self.position))
        return self.observe(),{'room_seed':self.seed_value}

    def _dense_layout(self):
        self.position=self.rng.uniform([2.,2.,1.5],self.room-[2.,2.,1.5])
        for _ in range(1000):
            self.target=self.rng.uniform([2.,2.,1.5],self.room-[2.,2.,1.5])
            if np.linalg.norm(self.target-self.position)>=14.: break
        else: raise RuntimeError('Could not place separated endpoints')
        lane_y=self.rng.uniform(2.,30.);height=self.rng.uniform(1.5,10.5)
        self.reference_route=[self.position.copy(),np.array([self.position[0],lane_y,height]),
            np.array([self.target[0],lane_y,height]),self.target.copy()]
        self.obstacles=[]
        for _ in range(5000):
            half=self.rng.uniform([.35,.35,.5],[2.2,2.2,4.5])
            center=self.rng.uniform(half+.3,self.room-half-.3)
            low,high=center-half,center+half
            # Retain a varying certified route, never supplied to the controller.
            if any(segment_box(a,b,low-RADIUS-.35,high+RADIUS+.35)
                   for a,b in zip(self.reference_route,self.reference_route[1:])): continue
            self.obstacles.append((low,high))
            if len(self.obstacles)==48: return
        raise RuntimeError('Could not build the dense room with a clear route')

    def rotation(self):
        c=np.cos(self.yaw);s=np.sin(self.yaw)
        return np.array([[c,-s,0],[s,c,0],[0,0,1.]])

    def rays(self):
        directions=DIRECTIONS@self.rotation().T
        distances=[]
        for d in directions:
            exits=[((self.room[k] if d[k]>0 else 0)-self.position[k])/d[k] for k in range(3) if abs(d[k])>1e-9]
            distance=min(v for v in exits if v>=0)
            distances.append(min(distance,RAY_RANGE))
        distances=np.array(distances)
        if self.obstacles:
            boxes=np.asarray(self.obstacles)
            delta_low=boxes[None,:,0,:]-self.position
            delta_high=boxes[None,:,1,:]-self.position
            d=directions[:,None,:];parallel=np.abs(d)<1e-12
            a=np.divide(delta_low,d,out=np.zeros((len(directions),len(boxes),3)),where=~parallel)
            b=np.divide(delta_high,d,out=np.zeros_like(a),where=~parallel)
            near=np.where(parallel,-np.inf,np.minimum(a,b)).max(axis=2)
            far=np.where(parallel,np.inf,np.maximum(a,b)).min(axis=2)
            outside=(parallel & ((delta_low>0)|(delta_high<0))).any(axis=2)
            hit=(far>=np.maximum(near,0)) & ~outside
            hits=np.where(hit,np.maximum(near,0),np.inf).min(axis=1)
            distances=np.minimum(distances,hits)
        return directions,distances

    def observe(self):
        directions,rays=self.rays()
        delta=self.target-self.position
        distance=np.linalg.norm(delta)
        local=delta@self.rotation()/max(distance,1e-6)
        velocity=self.velocity@self.rotation()/3.
        approach=directions@self.velocity/3.
        from fly_rl.simulation.sensors import SENSOR_V3
        v3=self.sensor_version==SENSOR_V3
        distance_scale=float(np.linalg.norm(self.room-2*RADIUS)) if v3 else 18.
        altitude=self.position[2]/self.room[2] if v3 else self.position[2]/ROOM[2]
        yaw_rate=(self.yaw_rate if self.dynamics=='coordinated' else 2.1*self.last_action[3])/2.6 if v3 else self.last_action[3]
        return np.concatenate([rays/RAY_RANGE,approach,local,[distance/distance_scale],velocity,self.last_action,
            [altitude,yaw_rate]]).astype(np.float32).clip(-1,1)

    def snapshot(self):
        return {'position':self.position.copy(),'velocity':self.velocity.copy(),'yaw':float(self.yaw),
                'target':self.target.copy(),'obstacles':np.asarray(self.obstacles).copy(),'ticks':self.ticks,
                'room_size':self.room.copy(),'mode':self.mode,'layout_seed':self.seed_value,
                'dynamics':self.dynamics,'bank':self.bank,'pitch':self.pitch,'yaw_rate':self.yaw_rate,
                'map_profile':self.map_profile.to_dict() if self.map_profile else None,
                'episode_limit':self.episode_limit}

    def step(self,action):
        action=np.clip(np.asarray(action,dtype=float),-1,1)
        if action.shape!=(4,) or not np.isfinite(action).all(): raise ValueError('Invalid action')
        old=self.position.copy(); old_distance=self.distance
        if self.dynamics=='coordinated':
            from fly_rl.simulation.flight import advance
            advance(self,action,DT)
        else:
            self.yaw=(self.yaw+action[3]*2.1*DT+np.pi)%(2*np.pi)-np.pi
            acceleration=self.rotation()@(action[:3]*3.)
            self.velocity+=(acceleration-.6*self.velocity)*DT
        speed=np.linalg.norm(self.velocity)
        if speed>3.: self.velocity*=3./speed
        new=old+self.velocity*DT
        collision=bool((new<RADIUS).any() or (new>self.room-RADIUS).any())
        collision |= any(segment_box(old,new,low-RADIUS,high+RADIUS) for low,high in self.obstacles)
        self.position=np.clip(new,RADIUS,self.room-RADIUS)
        self.last_action=action.astype(np.float32); self.ticks+=1
        self.distance=float(np.linalg.norm(self.target-self.position))
        reached=self.distance<.45 and not collision
        terminated=collision or reached; truncated=self.ticks>=self.episode_limit and not terminated
        # Dense physical progress is useful now, rather than only at discounted arrival.
        # Standing still always costs time; a timeout is a failed attempt.
        reward=2.*(old_distance-self.distance)-.02
        if terminated: reward+=20. if reached else -5.
        if truncated: reward-=5.
        return self.observe(),reward,terminated,truncated,{'collision':collision,'success':reached,'distance':self.distance,
            'terminated':bool(terminated),'truncated':bool(truncated),'transition_state':self.snapshot()}
