"""Training-only observed-ray penalty; ordinary inference and evaluation are unchanged."""
import time
from fly_rl.simulation.world import FlightWorld
from fly_rl.training.collision_diagnostics import ray_risk
VERSION='observed-ray-risk-v1'
PROTOCOL={'version':VERSION,'horizon_seconds':.75,'penalty_per_decision':.05,'minimum_closing_speed':.1,'source':'pre-action observed rays and projected approach speeds'}


class RiskStats:
    def __init__(self):self.transitions=0;self.active=0;self.penalty_sum=0.;self.risk_sum=0.;self.preprocessing_seconds=0.
    def snapshot(self):
        return {'version':VERSION,'transitions':self.transitions,'active_transitions':self.active,'penalty_sum':self.penalty_sum,'risk_sum':self.risk_sum,'preprocessing_seconds':self.preprocessing_seconds,'protocol':dict(PROTOCOL)}


class RiskWorld(FlightWorld):
    def __init__(self,*args,stats,**kwargs):
        self.stats=stats
        if kwargs.get('mode')!='dense' or not kwargs.get('layout_seeds'):raise ValueError('Risk shaping requires explicit dense training layouts')
        super().__init__(*args,**kwargs)

    def step(self,action):
        started=time.perf_counter();risk=float(ray_risk(self.observe(),PROTOCOL['horizon_seconds']))
        self.stats.preprocessing_seconds+=time.perf_counter()-started
        observation,reward,terminated,truncated,info=super().step(action)
        penalty=-PROTOCOL['penalty_per_decision']*risk
        self.stats.transitions+=1;self.stats.active+=risk>0;self.stats.penalty_sum+=penalty;self.stats.risk_sum+=risk
        info.update(base_reward=float(reward),training_shaping_reward=penalty,pre_action_ray_risk=risk)
        return observation,reward+penalty,terminated,truncated,info


def configure_risk_shaping(env,seed):
    from fly_rl.simulation.sensors import SENSOR_V3
    if hasattr(env,'curriculum'):raise ValueError('Do not combine interventions in this comparison')
    if any(w.mode!='dense' or w.dynamics!='coordinated' or w.sensor_version!=SENSOR_V3 or not w.layout_seeds for w in env.worlds):raise ValueError('Ray shaping requires v3 coordinated dense training layouts')
    stats=RiskStats()
    env.worlds=[RiskWorld(seed=seed+i,mode=w.mode,layout_seeds=w.layout_seeds,dynamics=w.dynamics,sensor_version=w.sensor_version,map_profile=w.map_profile,stats=stats) for i,w in enumerate(env.worlds)]
    env.reward_shaping=stats
    return stats
