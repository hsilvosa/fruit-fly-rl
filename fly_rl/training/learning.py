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
    def __init__(self,data='data',batch=1,device='cuda',seed=0,brain=None,mode='obstacles',layout_seeds=None,dynamics='legacy',sensor_version=None,map_profile=None,timeout_as_terminal=False,history_frames=0,history_stride=8,readout_version="random-pool-256-v1",sensor_backend="numpy"):
        if sensor_backend not in ("numpy","torch-cuda"):raise ValueError("Unknown sensor backend")
        self.sensor_backend=sensor_backend
        self.timeout_as_terminal=bool(timeout_as_terminal)
        if type(history_frames) is not int or not 0<=history_frames<=128 or type(history_stride) is not int or not 1<=history_stride<=64:
            raise ValueError('Invalid brain history dimensions')
        self.history_frames=history_frames;self.history_stride=history_stride
        self.history_ticks=np.zeros(batch,dtype=int)
        from fly_rl.simulation.map_profiles import resolve_profile
        self.map_profile=resolve_profile(map_profile)
        self.worlds=[FlightWorld(seed+i,mode,layout_seeds,dynamics,sensor_version,self.map_profile) for i in range(batch)]
        from fly_rl.connectome.readout import InputGroupedBrain,GROUP_READOUT,LEGACY_READOUT
        from fly_rl.connectome.innovation import WhitenedActivityBrain,WHITENED_READOUT,ContrastActivityBrain,CONTRAST_READOUT
        if readout_version not in (GROUP_READOUT,LEGACY_READOUT,WHITENED_READOUT,CONTRAST_READOUT):raise ValueError('Unknown brain readout')
        brain_type=ContrastActivityBrain if readout_version==CONTRAST_READOUT else WhitenedActivityBrain if readout_version==WHITENED_READOUT else InputGroupedBrain if readout_version==GROUP_READOUT else Brain
        self.brain=brain or brain_type(data,batch,device,sensor_version=sensor_version)
        if sensor_backend=="torch-cuda" and self.brain.device.type!="cuda":raise ValueError("CUDA sensor backend requires a CUDA brain")
        self.feature_count=getattr(self.brain,'feature_count',FEATURES)
        self.feature_history=np.zeros((batch,history_frames,self.feature_count),dtype=np.float32)
        self.latest_features=np.zeros((batch,self.feature_count),dtype=np.float32)
        if any(w.sensor_version!=self.brain.sensor_version for w in self.worlds): raise ValueError('World/brain sensor contract mismatch')
        self.returns=np.zeros(batch);self.lengths=np.zeros(batch,dtype=int)
        shape=(history_frames+1,self.feature_count) if history_frames else (self.feature_count,)
        super().__init__(batch,spaces.Box(-np.inf,np.inf,shape,dtype=np.float32),self.worlds[0].action_space)

    def reset(self):
        self.brain.reset()
        sensors=[]
        for i,w in enumerate(self.worlds):
            obs,info=w.reset(seed=self._seeds[i],options=self._options[i]); sensors.append(obs)
            self.reset_infos[i]=info
        self._reset_seeds();self._reset_options()
        self.returns.fill(0);self.lengths.fill(0)
        self.feature_history.fill(0);self.history_ticks.fill(0)
        self.latest_sensors=np.asarray(sensors).copy()
        return self._pack_features(self.brain.step(np.asarray(sensors)))

    def _pack_features(self,features):
        self.latest_features=features.copy()
        if not self.history_frames:return features
        return np.concatenate([self.feature_history,features[:,None,:]],axis=1)

    def step_async(self,actions): self.actions=actions

    def step_wait(self):
        if self.history_frames:
            self.history_ticks+=1
            for i in np.flatnonzero(self.history_ticks%self.history_stride==0):
                self.feature_history[i,:-1]=self.feature_history[i,1:].copy()
                self.feature_history[i,-1]=self.latest_features[i]
        sensors=[]; rewards=[];dones=[]; infos=[]
        for i,(w,a) in enumerate(zip(self.worlds,self.actions)):
            obs,r,terminated,truncated,info=w.step(a) if self.sensor_backend=="numpy" else w.step(a,observe=False)
            sensors.append(obs);rewards.append(r);dones.append(terminated or truncated)
            info['TimeLimit.truncated']=bool(truncated and not terminated and not self.timeout_as_terminal)
            info['timeout_failure_terminal']=bool(truncated and self.timeout_as_terminal)
            self.returns[i]+=r;self.lengths[i]+=1
            if terminated or truncated: info['episode']={'r':self.returns[i],'l':self.lengths[i]}
            infos.append(info)
        if self.sensor_backend=="torch-cuda":
            from fly_rl.simulation.gpu_sensors import observe_batch
            sensors=observe_batch(self.worlds,self.brain.device)
        features=self.brain.step(np.asarray(sensors))
        for i,info in enumerate(infos):
            info['next_sensors']=sensors[i].copy()
            info['next_brain_features']=features[i].copy()
        ended=np.flatnonzero(dones)
        if len(ended):
            for i in ended:
                infos[i]['terminal_observation']=np.concatenate([self.feature_history[i],features[i][None,:]],axis=0) if self.history_frames else features[i].copy()
                self.feature_history[i].fill(0);self.history_ticks[i]=0
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
            sensors=resets
        self.latest_sensors=np.asarray(sensors).copy()
        return self._pack_features(features),np.asarray(rewards,dtype=np.float32),np.asarray(dones,dtype=bool),infos

    def close(self): pass
    def get_attr(self,name,indices=None):
        return [getattr(self.worlds[i],name) for i in self._get_indices(indices)]
    def set_attr(self,name,value,indices=None):
        for i in self._get_indices(indices): setattr(self.worlds[i],name,value)
    def env_method(self,name,*args,indices=None,**kwargs):
        return [getattr(self.worlds[i],name)(*args,**kwargs) for i in self._get_indices(indices)]
    def env_is_wrapped(self,wrapper_class,indices=None): return [False for i in self._get_indices(indices)]

def make_policy(env,smoke=False,seed=42,share_history=True):
    policy_options={'net_arch':{'pi':[128,128],'vf':[128,128]}}
    if getattr(env.brain,'readout_version',None)=='input-associated-neural-mean-v1':
        from fly_rl.simulation.sensors import SENSOR_V6
        if env.brain.sensor_version==SENSOR_V6:
            from fly_rl.training.panorama_policy import PanoramicBrainHistory
            extractor=PanoramicBrainHistory
        else:
            from fly_rl.training.spatial_policy import SpatialBrainHistory
            extractor=SpatialBrainHistory
        policy_options.update(features_extractor_class=extractor,ortho_init=False,
                              share_features_extractor=False)
    elif getattr(env,'history_frames',0):
        from fly_rl.training.temporal_policy import ResidualBrainHistory
        policy_options.update(features_extractor_class=ResidualBrainHistory,ortho_init=False,
                              share_features_extractor=share_history)
    return PPO('MlpPolicy',env,device='cpu',seed=seed,verbose=0,
        learning_rate=3e-4,n_steps=128 if smoke else 512,batch_size=128,
        n_epochs=1 if smoke else 5,gamma=.995,gae_lambda=.95,clip_range=.2,
        policy_kwargs=policy_options,
        tensorboard_log=None if smoke else 'runs/tensorboard')

def save_model(model,path,brain):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    model.save(str(path))
    world=model.get_env().worlds[0] if model.get_env() is not None else None
    path.with_suffix('.json').write_text(json.dumps({'training_reward_shaping':model.get_env().reward_shaping.snapshot() if model.get_env() is not None and hasattr(model.get_env(),'reward_shaping') else None,'training_curriculum':model.get_env().curriculum.snapshot() if model.get_env() is not None and hasattr(model.get_env(),'curriculum') else None,'fingerprint':brain.fingerprint,
        'readout_version':getattr(brain,'readout_version','random-pool-256-v1'),
        'policy_numeric_precision':getattr(model,'policy_numeric_precision',None),
        'dataset':brain.audit.get('dataset','MaleCNS v1.0'),'timesteps':model.num_timesteps,
        'kind':'smoke-test' if model.n_steps==128 else 'policy','trained_navigation':False,
        'reward_version':REWARD_VERSION,'discount_gamma':model.gamma,
        'brain_history':{'frames':getattr(model.get_env(),'history_frames',0),'stride':getattr(model.get_env(),'history_stride',8)},
        'history_transfer':getattr(model,'history_transfer',None),
        'imitation_training':getattr(model,'imitation_training',None),
        'waypoint_training':getattr(model,'waypoint_training',None),
        'ppo_kl_guard':{'version':'full-rollout-gaussian-kl-v1','mean_limit':model.kl_guard_mean_limit,
                        'max_limit':model.kl_guard_max_limit,'max_attempts':model.kl_guard_max_attempts}
                       if hasattr(model,'kl_guard_mean_limit') else None,
        'training_timeout_as_terminal':getattr(model.get_env(),'timeout_as_terminal',False),'training_seed':model.seed,'sensor_version':brain.sensor_version,
        'environment':{'mode':world.mode,'dynamics':world.dynamics,'size':world.room.tolist(),'episode_limit':world.episode_limit,
                       'training_layout_seeds':world.layout_seeds,
                       'map_profile':model.get_env().map_profile.to_dict() if model.get_env().map_profile else None,
                       'active_training_map_profile':world.map_profile.to_dict() if world.map_profile else None} if world is not None else None},indent=2),encoding='utf8')

def load_model(path,brain,env=None,allow_transfer=False):
    path=Path(path)
    metadata=json.loads(path.with_suffix('.json').read_text())
    if metadata['fingerprint']!=brain.fingerprint: raise ValueError('Checkpoint graph or model configuration mismatch')
    precision=metadata.get('policy_numeric_precision')
    if precision is not None:
        if precision!={'cudnn_allow_tf32':False,'matmul_allow_tf32':False}:
            raise ValueError('Unsupported policy numeric precision contract')
        torch.backends.cudnn.allow_tf32=False
        torch.backends.cuda.matmul.allow_tf32=False
    if env is not None and not allow_transfer:
        old=(metadata.get('environment') or {}).get('dynamics','legacy')
        if old!=env.worlds[0].dynamics: raise ValueError('Checkpoint flight dynamics mismatch; explicit transfer is required')
        profile=env.map_profile.to_dict() if env.map_profile else None
        if (metadata.get('environment') or {}).get('map_profile')!=profile:
            raise ValueError('Checkpoint map profile mismatch; explicit transfer is required')
    algorithm=PPO
    if metadata.get('ppo_kl_guard'):
        from fly_rl.training.guarded_ppo import GuardedPPO
        if metadata['ppo_kl_guard']['version']!='full-rollout-gaussian-kl-v1':
            raise ValueError('Unsupported PPO guard contract')
        algorithm=GuardedPPO
    model=algorithm.load(str(path),env=env,device='cpu')
    if metadata.get('ppo_kl_guard'):
        for field in ('mean_limit','max_limit','max_attempts'):
            if getattr(model,'kl_guard_'+field,None)!=metadata['ppo_kl_guard'][field]:
                raise ValueError('Checkpoint PPO guard metadata mismatch')
    return model

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

class TrainingSession:
    """Keep live episodes and PPO state between chunks; not a disk resume format."""
    def __init__(self):
        self.env=None
        self.model=None
        self.contract=None
        self.last_checkpoint=None
        self.random_state=None

    def capture_random_state(self):
        import random
        self.random_state=(random.getstate(),np.random.get_state(),torch.get_rng_state(),
                           torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None)

    def restore_random_state(self):
        import random
        if self.random_state is None:return
        a,b,c,d=self.random_state
        random.setstate(a);np.random.set_state(b);torch.set_rng_state(c)
        if d is not None:torch.cuda.set_rng_state_all(d)

    def close(self):
        if self.env is not None:self.env.close()


def train(data,device,steps,batch,output,resume=None,smoke=False,mode='obstacles',layout_seeds=None,dynamics='legacy',allow_transfer=False,training_seed=42,sensor_version=None,curriculum=None,curriculum_offset=0,curriculum_total=None,reward_shaping=None,map_profile=None,curriculum_profiles=None,practice_seeds=None,curriculum_state=None,session=None,gamma=.995,timeout_as_terminal=False,target_envs=0,history_frames=0,history_stride=8,transfer_history=False):
    if not 0<=training_seed<2**32: raise ValueError('Invalid training seed')
    if resume and not transfer_history and not history_frames and Path(resume).with_suffix('.json').exists():
        saved_history=checkpoint_history(resume);history_frames=saved_history['history_frames'];history_stride=saved_history['history_stride']
    if steps<=0: raise ValueError('Specify a positive number of training steps')
    if smoke and (steps!=128 or batch!=1): raise ValueError('Smoke test is exactly 128 transitions and one PPO update')
    if target_envs and curriculum!='geometry-v2-practice-mastery':raise ValueError('Dedicated target exposure requires mastery curriculum')
    if not np.isfinite(gamma) or not .9 <= gamma < 1.:raise ValueError('Discount gamma must be finite and in [0.9, 1)')
    live_env=session.env if session is not None and session.env is not None else None
    readout_version=getattr(live_env.brain,'readout_version','random-pool-256-v1') if live_env is not None else checkpoint_readout(resume)
    sensory_version=sensor_version or (live_env.brain.sensor_version if live_env is not None else checkpoint_sensor_version(resume))
    from fly_rl.simulation.sensors import SENSOR_V6
    sensor_backend='torch-cuda' if device=='cuda' and sensory_version==SENSOR_V6 else 'numpy'
    contract=json.dumps({'data':str(Path(data).resolve()),'device':device,'batch':batch,'mode':mode,
        'layouts':layout_seeds,'dynamics':dynamics,'seed':training_seed,'sensor':sensory_version,
        'curriculum':curriculum,'total':curriculum_total,'profiles':curriculum_profiles,'practice':practice_seeds,
        'profile':map_profile,'reward':reward_shaping,'gamma':gamma,'timeout_as_terminal':timeout_as_terminal,'target_envs':target_envs,'history_frames':history_frames,'history_stride':history_stride,'readout':readout_version,'sensor_backend':sensor_backend},sort_keys=True,default=str)
    continuing=session is not None and session.env is not None
    if continuing:
        if session.contract!=contract or str(Path(resume).resolve())!=session.last_checkpoint:
            raise ValueError('Continuous training requires the same configuration and latest checkpoint')
        env=session.env
        if hasattr(env,'curriculum') and (env.curriculum.transitions!=curriculum_offset or env.curriculum.snapshot()!=curriculum_state):
            raise ValueError('Continuous curriculum state mismatch')
        session.restore_random_state()
    else:
        env=BrainEnv(data,batch,device,mode=mode,layout_seeds=layout_seeds,dynamics=dynamics,seed=training_seed,sensor_version=sensory_version,map_profile=map_profile,timeout_as_terminal=timeout_as_terminal,history_frames=history_frames,history_stride=history_stride,readout_version=readout_version,sensor_backend=sensor_backend)
    if curriculum is not None and not continuing:
        from fly_rl.training.approach_curriculum import VERSION,configure_curriculum
        from fly_rl.training.geometry_curriculum import VERSION as GEOMETRY_VERSION,configure_geometry_curriculum
        from fly_rl.training.mastery_curriculum import VERSION as MASTERY_VERSION,configure_mastery
        if curriculum==VERSION:configure_curriculum(env,curriculum_total,curriculum_offset,training_seed)
        elif curriculum==GEOMETRY_VERSION:
            if curriculum_offset+steps>curriculum_total:raise ValueError('Training exceeds geometry schedule budget')
            configure_geometry_curriculum(env,curriculum_total,curriculum_offset,training_seed,curriculum_profiles)
        elif curriculum==MASTERY_VERSION:
            if curriculum_offset+steps>curriculum_total:raise ValueError('Training exceeds mastery budget')
            configure_mastery(env,curriculum_total,curriculum_offset,training_seed,curriculum_profiles,practice_seeds,curriculum_state,target_envs)
        else:raise ValueError('Unknown training curriculum')
    if reward_shaping is not None and not continuing:
        from fly_rl.training.risk_shaping import VERSION,configure_risk_shaping
        from fly_rl.training.route_progress import VERSION as ROUTE_VERSION,configure_route_progress
        if reward_shaping==VERSION:configure_risk_shaping(env,training_seed)
        elif reward_shaping==ROUTE_VERSION:configure_route_progress(env,training_seed)
        else:raise ValueError('Unknown training reward shaping')
    if transfer_history and not continuing:
        if not resume:raise ValueError('History transfer requires an explicit source checkpoint')
        from fly_rl.training.temporal_policy import transfer_history_policy
        source=load_model(resume,env.brain,None,allow_transfer)
        model=transfer_history_policy(source,env,training_seed)
    else:
        model=session.model if continuing else load_model(resume,env.brain,env,allow_transfer) if resume else make_policy(env,smoke,training_seed)
    if not continuing:model.set_random_seed(training_seed)
    if session is not None:
        session.env,session.model,session.contract=env,model,contract
    model.gamma=float(gamma)
    if hasattr(model,'rollout_buffer'):model.rollout_buffer.gamma=float(gamma)
    model.tensorboard_log=None if smoke else str(Path(output).parent/'tensorboard')
    before=[p.detach().clone() for p in model.policy.parameters()]
    initial_timesteps=model.num_timesteps
    initial_ticks=[w.ticks for w in env.worlds]
    try:
        model.learn(total_timesteps=steps,reset_num_timesteps=not bool(resume) and not continuing,
                    callback=None if smoke else TimedCheckpoint(Path(output).parent,env.brain))
    finally:
        save_model(model,output,env.brain)
        if session is None:env.close()
        else:
            session.last_checkpoint=str(Path(output).resolve())
            session.capture_random_state()
    result={'transitions':model.num_timesteps,'updates':model._n_updates,
        'added_transitions':model.num_timesteps-initial_timesteps,'requested_transitions':steps,
        'room_mode':mode,'training_seed':training_seed,'discount_gamma':float(gamma),
        'timeout_as_terminal':bool(timeout_as_terminal),
        'parameters_changed':any(not torch.equal(a,b) for a,b in zip(before,model.policy.parameters())),
        'losses':{k:float(v) for k,v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}}
    if session is not None:
        result['episode_continuity']={'continued_live_session':continuing,'ticks_before':initial_ticks,
                                     'ticks_after':[w.ticks for w in env.worlds]}
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
    expected=f':reservoir-v2-{value}-256-seed42-leak0.5-scale0.9'
    readout=metadata.get('readout_version','random-pool-256-v1')
    from fly_rl.connectome.innovation import WHITENED_READOUT,CONTRAST_READOUT
    if readout in ('input-associated-neural-mean-v1',WHITENED_READOUT,CONTRAST_READOUT):expected+=':'+readout
    elif readout!='random-pool-256-v1':raise ValueError('Unknown checkpoint readout')
    if not metadata.get('fingerprint','').endswith(expected):
        raise ValueError('Checkpoint sensor metadata/fingerprint mismatch')
    return value


def checkpoint_readout(path):
    """Validated reader contract for both demo and explicit checkpoint resume."""
    if not path:return 'random-pool-256-v1'
    checkpoint_sensor_version(path)
    return json.loads(Path(path).with_suffix('.json').read_text()).get('readout_version','random-pool-256-v1')


def checkpoint_history(path):
    if not path:return {'history_frames':0,'history_stride':8}
    metadata=json.loads(Path(path).with_suffix('.json').read_text())
    spec=metadata.get('brain_history') or {'frames':0,'stride':8}
    frames,stride=spec['frames'],spec['stride']
    if type(frames) is not int or not 0<=frames<=128 or type(stride) is not int or not 1<=stride<=64:
        raise ValueError('Invalid checkpoint brain history contract')
    return {'history_frames':frames,'history_stride':stride}
