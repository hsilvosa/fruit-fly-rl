"""Training-only obstacle-aware progress; no route or geometry in observations."""
import time
import numpy as np
from fly_rl.simulation.world import FlightWorld, RADIUS

VERSION = 'certified-route-progress-v1'
PROTOCOL = {'version': VERSION, 'source': 'privileged training geometry and certified polyline',
            'policy_inputs': 'unchanged connectome features only', 'sample_spacing': 1.0,
            'clearance': .02, 'progress_scale': 2., 'time_cost': .02,
            'terminal_rewards': 'unchanged success/collision/timeout bonuses',
            'potential_based': False, 'evaluation_reward': 'unchanged navigation-v2'}


class RouteDistance:
    """Length of a visible connection to a fixed feasible route and its suffix.

    This is an upper bound from sampled connections, not the shortest geodesic.
    The field is fixed per episode, with no waypoint index or progress ratchet.
    """
    def __init__(self, route, obstacles, spacing=1., margin=RADIUS+.02):
        route = np.asarray(route, dtype=float)
        if route.ndim != 2 or route.shape[1] != 3 or len(route)<2 or not np.isfinite(route).all():
            raise ValueError('Finite certified polyline required')
        if not np.isfinite(spacing) or spacing<=0: raise ValueError('Positive sample spacing required')
        self.points=np.vstack([a+(b-a)*t for a,b in zip(route,route[1:])
                               for t in np.linspace(0,1,max(2,int(np.ceil(np.linalg.norm(b-a)/spacing))+1))[:-1]]+[route[-1]])
        edges=np.linalg.norm(np.diff(self.points,axis=0),axis=1)
        self.remaining=np.r_[np.cumsum(edges[::-1])[::-1],0.]
        self.boxes=np.asarray(obstacles,dtype=float).reshape(-1,2,3).copy()
        self.margin=margin

    def __call__(self, position):
        position=np.asarray(position,dtype=float)
        if position.shape!=(3,) or not np.isfinite(position).all():raise ValueError('Finite position required')
        delta=self.points-position
        visible=np.ones(len(delta),dtype=bool)
        if len(self.boxes):
            low=self.boxes[None,:,0,:]-self.margin-position
            high=self.boxes[None,:,1,:]+self.margin-position
            d=delta[:,None,:];parallel=np.abs(d)<1e-12
            a=np.divide(low,d,out=np.zeros((len(delta),len(self.boxes),3)),where=~parallel)
            b=np.divide(high,d,out=np.zeros_like(a),where=~parallel)
            near=np.where(parallel,-np.inf,np.minimum(a,b)).max(axis=2)
            far=np.where(parallel,np.inf,np.maximum(a,b)).min(axis=2)
            outside=(parallel & ((low>0)|(high<0))).any(axis=2)
            hit=(np.maximum(near,0)<=np.minimum(far,1)) & ~outside
            visible=~hit.any(axis=1)
        costs=np.linalg.norm(delta,axis=1)+self.remaining
        return float(np.min(costs[visible])) if visible.any() else None


class RouteStats:
    def __init__(self):
        self.transitions=0;self.fallback_transitions=0;self.progress_sum=0.;self.base_reward_sum=0.;self.reward_sum=0.;self.preprocessing_seconds=0.
        self.outcomes={'success':0,'collision':0,'timeout':0}
    def snapshot(self):
        return {'protocol':dict(PROTOCOL),'version':VERSION,'transitions':self.transitions,
                'fallback_transitions':self.fallback_transitions,'route_progress_sum':self.progress_sum,
                'base_reward_sum':self.base_reward_sum,'training_reward_sum':self.reward_sum,
                'preprocessing_seconds':self.preprocessing_seconds,'episode_outcomes':dict(self.outcomes)}


class RouteProgressWorld(FlightWorld):
    def __init__(self,*args,stats,**kwargs):
        self.stats=stats
        if kwargs.get('mode')!='dense' or not kwargs.get('layout_seeds') or kwargs.get('map_profile') is None:
            raise ValueError('Route progress requires explicit profiled training layouts')
        super().__init__(*args,**kwargs)

    def reset(self,seed=None,options=None):
        observation,info=super().reset(seed,options)
        self.route_distance=RouteDistance(self.reference_route,self.obstacles)
        self.previous_route_distance=self.route_distance(self.position)
        if self.previous_route_distance is None:raise RuntimeError('Initial certified route is not visible')
        return observation,info

    def step(self,action):
        old_direct=self.distance
        observation,base,terminated,truncated,info=super().step(action)
        started=time.perf_counter()
        distance=self.route_distance(self.position) if not info['collision'] else None
        # Never invent a jump to Euclidean distance at an occluded or colliding state.
        # A temporarily invisible route retains its previous field value and is counted.
        progress=0. if distance is None else self.previous_route_distance-distance
        self.stats.fallback_transitions+=distance is None
        if distance is not None:self.previous_route_distance=distance
        self.stats.preprocessing_seconds+=time.perf_counter()-started
        euclidean_progress=2.*(old_direct-self.distance)
        reward=float(base-euclidean_progress+PROTOCOL['progress_scale']*progress)
        self.stats.transitions+=1;self.stats.progress_sum+=progress;self.stats.base_reward_sum+=base;self.stats.reward_sum+=reward
        for key in self.stats.outcomes:self.stats.outcomes[key]+=bool(info.get('truncated' if key=='timeout' else key,False))
        info.update(base_reward=float(base),training_shaping_reward=reward-base,
                    direct_progress_reward=float(euclidean_progress),route_progress_reward=2.*progress,
                    training_route_distance=distance,route_distance_fallback=distance is None)
        return observation,reward,terminated,truncated,info


def configure_route_progress(env,seed):
    if hasattr(env,'curriculum') or hasattr(env,'reward_shaping'):
        raise ValueError('Do not combine route progress with another intervention')
    stats=RouteStats()
    env.worlds=[RouteProgressWorld(seed=seed+i,mode=w.mode,layout_seeds=w.layout_seeds,
                  dynamics=w.dynamics,sensor_version=w.sensor_version,map_profile=w.map_profile,stats=stats)
                for i,w in enumerate(env.worlds)]
    env.reward_shaping=stats
    return stats
