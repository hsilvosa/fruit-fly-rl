"""SB3 integration: the frozen brain advances only during environment transitions."""
from pathlib import Path
import json
import numpy as np
import torch
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecEnv
from stable_baselines3.common.callbacks import BaseCallback
from fly_rl.connectome.brain import Brain,FEATURES
from fly_rl.simulation.world import FlightWorld,REWARD_VERSION

class BrainEnv(VecEnv):
    def __init__(self,data='data',batch=1,device='cuda',seed=0,brain=None,mode='obstacles',layout_seeds=None,dynamics='legacy',sensor_version=None,map_profile=None):
        from fly_rl.simulation.map_profiles import resolve_profile
        self.map_profile=resolve_profile(map_profile)
        self.worlds=[FlightWorld(seed+i,mode,layout_seeds,dynamics,sensor_version,self.map_profile) for i in range(batch)]
        self.brain=brain or Brain(data,batch,device,sensor_version=sensor_version)
        if any(w.sensor_version!=self.brain.sensor_version for w in self.worlds): raise ValueError('World/brain sensor contract mismatch')
        self.returns=np.zeros(batch);self.lengths=np.zeros(batch,dtype=int)
        super().__init__(batch,spaces.Box(-np.inf,np.inf,(FEATURES,),dtype=np.float32),self.worlds[0].action_space)

    def reset(self):
        self.brain.reset()
        sensors=[]
        for i,w in enumerate(self.worlds):
            obs,info=w.reset(seed=self._seeds[i],options=self._options[i]); sensors.append(obs)
            self.reset_infos[i]=info
        self._reset_seeds();self._reset_options()
        self.returns.fill(0);self.lengths.fill(0)
        return self.brain.step(np.asarray(sensors))

    def step_async(self,actions): self.actions=actions

    def step_wait(self):
        sensors=[]; rewards=[];dones=[]; infos=[]
        for i,(w,a) in enumerate(zip(self.worlds,self.actions)):
            obs,r,terminated,truncated,info=w.step(a)
            sensors.append(obs);rewards.append(r);dones.append(terminated or truncated)
            info['TimeLimit.truncated']=bool(truncated and not terminated)
            self.returns[i]+=r;self.lengths[i]+=1
            if terminated or truncated: info['episode']={'r':self.returns[i],'l':self.lengths[i]}
            infos.append(info)
        features=self.brain.step(np.asarray(sensors))
        for i,info in enumerate(infos):
            info['next_sensors']=sensors[i].copy()
            info['next_brain_features']=features[i].copy()
        ended=np.flatnonzero(dones)
        if len(ended):
            for i in ended: infos[i]['terminal_observation']=features[i].copy()
            self.brain.reset(ended)
            # Recompute fresh observations without advancing nonterminal brain states.
            saved=self.brain.state.clone()
            resets=np.asarray(sensors)
            for i in ended:
                resets[i],self.reset_infos[i]=self.worlds[i].reset()
                self.returns[i]=0;self.lengths[i]=0
            reset_features=self.brain.step(resets)
            continuing=np.flatnonzero(~np.asarray(dones))
            self.brain.state[:,continuing]=saved[:,continuing]
            features[ended]=reset_features[ended]
        return features,np.asarray(rewards,dtype=np.float32),np.asarray(dones,dtype=bool),infos

    def close(self): pass
    def get_attr(self,name,indices=None):
        return [getattr(self.worlds[i],name) for i in self._get_indices(indices)]
    def set_attr(self,name,value,indices=None):
        for i in self._get_indices(indices): setattr(self.worlds[i],name,value)
    def env_method(self,name,*args,indices=None,**kwargs):
        return [getattr(self.worlds[i],name)(*args,**kwargs) for i in self._get_indices(indices)]
    def env_is_wrapped(self,wrapper_class,indices=None): return [False for i in self._get_indices(indices)]

def make_policy(env,smoke=False,seed=42):
    return PPO('MlpPolicy',env,device='cpu',seed=seed,verbose=0,
        learning_rate=3e-4,n_steps=128 if smoke else 512,batch_size=128,
        n_epochs=1 if smoke else 5,gamma=.995,gae_lambda=.95,clip_range=.2,
        policy_kwargs={'net_arch':{'pi':[128,128],'vf':[128,128]}},
        tensorboard_log=None if smoke else 'runs/tensorboard')

def save_model(model,path,brain):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    model.save(str(path))
    world=model.get_env().worlds[0] if model.get_env() is not None else None
    path.with_suffix('.json').write_text(json.dumps({'training_reward_shaping':model.get_env().reward_shaping.snapshot() if model.get_env() is not None and hasattr(model.get_env(),'reward_shaping') else None,'training_curriculum':model.get_env().curriculum.snapshot() if model.get_env() is not None and hasattr(model.get_env(),'curriculum') else None,'fingerprint':brain.fingerprint,
        'dataset':brain.audit.get('dataset','MaleCNS v1.0'),'timesteps':model.num_timesteps,
        'kind':'smoke-test' if model.n_steps==128 else 'policy','trained_navigation':False,
        'reward_version':REWARD_VERSION,'training_seed':model.seed,'sensor_version':brain.sensor_version,
        'environment':{'mode':world.mode,'dynamics':world.dynamics,'size':world.room.tolist(),'episode_limit':world.episode_limit,
                       'training_layout_seeds':world.layout_seeds,
                       'map_profile':model.get_env().map_profile.to_dict() if model.get_env().map_profile else None,
                       'active_training_map_profile':world.map_profile.to_dict() if world.map_profile else None} if world is not None else None},indent=2),encoding='utf8')

def load_model(path,brain,env=None,allow_transfer=False):
    path=Path(path)
    metadata=json.loads(path.with_suffix('.json').read_text())
    if metadata['fingerprint']!=brain.fingerprint: raise ValueError('Checkpoint graph or model configuration mismatch')
    if env is not None and not allow_transfer:
        old=(metadata.get('environment') or {}).get('dynamics','legacy')
        if old!=env.worlds[0].dynamics: raise ValueError('Checkpoint flight dynamics mismatch; explicit transfer is required')
        profile=env.map_profile.to_dict() if env.map_profile else None
        if (metadata.get('environment') or {}).get('map_profile')!=profile:
            raise ValueError('Checkpoint map profile mismatch; explicit transfer is required')
    return PPO.load(str(path),env=env,device='cpu')

class TimedCheckpoint(BaseCallback):
    def __init__(self,directory,brain):
        super().__init__();self.directory=Path(directory);self.brain=brain;self.last=0.
    def _on_training_start(self):
        self.started_steps=self.model.num_timesteps
    def _on_step(self):
        import time
        now=time.monotonic()
        if self.last==0.: self.last=now
        if now-self.last>=60:
            save_model(self.model,self.directory/f'step-{self.num_timesteps}.zip',self.brain);self.last=now
        return True

    def _on_rollout_end(self):
        status={'transitions':self.num_timesteps,'updates':self.model._n_updates,
                'added_transitions':self.num_timesteps-self.started_steps,
                'room_mode':self.training_env.worlds[0].mode}
        if hasattr(self.training_env,'reward_shaping'):status['reward_shaping']=self.training_env.reward_shaping.snapshot()
        if hasattr(self.training_env,'curriculum'):status['curriculum']=self.training_env.curriculum.snapshot()
        path=self.directory/'progress.json';path.parent.mkdir(parents=True,exist_ok=True)
        tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(status,indent=2));tmp.replace(path)

def train(data,device,steps,batch,output,resume=None,smoke=False,mode='obstacles',layout_seeds=None,dynamics='legacy',allow_transfer=False,training_seed=42,sensor_version=None,curriculum=None,curriculum_offset=0,curriculum_total=None,reward_shaping=None,map_profile=None,curriculum_profiles=None):
    if not 0<=training_seed<2**32: raise ValueError('Invalid training seed')
    if steps<=0: raise ValueError('Specify a positive number of training steps')
    if smoke and (steps!=128 or batch!=1): raise ValueError('Smoke test is exactly 128 transitions and one PPO update')
    env=BrainEnv(data,batch,device,mode=mode,layout_seeds=layout_seeds,dynamics=dynamics,seed=training_seed,sensor_version=sensor_version or checkpoint_sensor_version(resume),map_profile=map_profile)
    if curriculum is not None:
        from fly_rl.training.approach_curriculum import VERSION,configure_curriculum
        from fly_rl.training.geometry_curriculum import VERSION as GEOMETRY_VERSION,configure_geometry_curriculum
        if curriculum==VERSION:configure_curriculum(env,curriculum_total,curriculum_offset,training_seed)
        elif curriculum==GEOMETRY_VERSION:
            if curriculum_offset+steps>curriculum_total:raise ValueError('Training exceeds geometry schedule budget')
            configure_geometry_curriculum(env,curriculum_total,curriculum_offset,training_seed,curriculum_profiles)
        else:raise ValueError('Unknown training curriculum')
    if reward_shaping is not None:
        from fly_rl.training.risk_shaping import VERSION,configure_risk_shaping
        if reward_shaping!=VERSION:raise ValueError('Unknown training reward shaping')
        configure_risk_shaping(env,training_seed)
    model=load_model(resume,env.brain,env,allow_transfer) if resume else make_policy(env,smoke,training_seed)
    model.set_random_seed(training_seed)
    if resume: model.gamma=.995
    model.tensorboard_log=None if smoke else str(Path(output).parent/'tensorboard')
    before=[p.detach().clone() for p in model.policy.parameters()]
    initial_timesteps=model.num_timesteps
    try:
        model.learn(total_timesteps=steps,reset_num_timesteps=not bool(resume),
                    callback=None if smoke else TimedCheckpoint(Path(output).parent,env.brain))
    finally:
        save_model(model,output,env.brain)
        env.close()
    result={'transitions':model.num_timesteps,'updates':model._n_updates,
        'added_transitions':model.num_timesteps-initial_timesteps,'requested_transitions':steps,
        'room_mode':mode,'training_seed':training_seed,
        'parameters_changed':any(not torch.equal(a,b) for a,b in zip(before,model.policy.parameters())),
        'losses':{k:float(v) for k,v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}}
    if hasattr(env,'reward_shaping'):result['reward_shaping']=env.reward_shaping.snapshot()
    if hasattr(env,'curriculum'):result['curriculum']=env.curriculum.snapshot()
    if not result['losses'] or not all(np.isfinite(v) for v in result['losses'].values()):
        raise RuntimeError('Missing or nonfinite optimizer losses')
    if smoke:
        assert model.num_timesteps==128 and model._n_updates==1
        assert result['parameters_changed'] and all(np.isfinite(v) for v in result['losses'].values())
        observation=env.reset()
        a=model.predict(observation,deterministic=True)[0]
        reloaded=load_model(output,env.brain,env)
        assert np.allclose(a,reloaded.predict(observation,deterministic=True)[0])
        result['checkpoint_roundtrip']=True
    return result


def checkpoint_sensor_version(path):
    from fly_rl.simulation.sensors import SENSOR_VERSION,validate_sensor_version
    if not path: return SENSOR_VERSION
    metadata=json.loads(Path(path).with_suffix('.json').read_text())
    value=validate_sensor_version(metadata.get('sensor_version',SENSOR_VERSION))
    if f':reservoir-v2-{value}-256-seed42-leak0.5-scale0.9' not in metadata.get('fingerprint',''):
        raise ValueError('Checkpoint sensor metadata/fingerprint mismatch')
    return value
