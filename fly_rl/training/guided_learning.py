"""Explicit bounded imitation warm-start; the teacher is absent at inference."""
from pathlib import Path
import numpy as np
import torch
from fly_rl.simulation.world import RADIUS

TEACHER_VERSION='certified-3d-coordinated-teacher-v1'


class RouteTeacher:
    """Training-only path follower with coupled horizontal/vertical velocity."""
    def __init__(self,world,recover=False):
        self.recover=bool(recover)
        self.route=np.asarray(world.reference_route[1:],dtype=float).copy()
        if not len(self.route):raise ValueError('Teacher requires a training route')
        self.index=0

    def action(self,world):
        if self.recover:
            direction=np.sign(self.route[-1,0]-self.route[0,0])
            while self.index<len(self.route)-1 and direction*(world.position[0]-self.route[self.index,0])>.06:
                self.index+=1
        delta=self.route[self.index]-world.position
        if np.linalg.norm(delta)<.06 and self.index<len(self.route)-1:
            self.index+=1;delta=self.route[self.index]-world.position
        error=(np.arctan2(delta[1],delta[0])-world.yaw+np.pi)%(2*np.pi)-np.pi
        distance=np.linalg.norm(delta)
        speed=min(1.4,distance*.9)*max(0.,np.cos(error))**4
        desired=delta/max(distance,1e-9)*speed
        speed_xy=np.linalg.norm(desired[:2]);local=world.velocity@world.rotation()
        acceleration=np.clip(3*(speed_xy-local[0])+.6*speed_xy,-1.2,3.)
        vertical=np.clip(3*(desired[2]-world.velocity[2])+.8*desired[2],-2.5,2.5)/2.5
        return np.array([acceleration/(3. if acceleration>=0 else 1.2),0.,vertical,
                         np.clip(error*2/1.8,-1.,1.)],dtype=np.float32)


def actor_mean(policy, observations):
    features=policy.extract_features(observations)
    if isinstance(features,tuple):features=features[0]
    latent=policy.mlp_extractor.forward_actor(features)
    return policy.action_net(latent)


def fit_actor(model,observations,targets,count,updates,rng,batch_size=256,progress=None):
    """Fit only the feature extractor and actor; never feed teacher state to it."""
    if count<=0 or updates<=0:raise ValueError('Positive bounded imitation data and updates required')
    policy=model.policy
    params=list(policy.features_extractor.parameters())+list(policy.mlp_extractor.policy_net.parameters())+list(policy.action_net.parameters())
    optimizer=torch.optim.Adam(params,lr=3e-4)
    turns=np.flatnonzero(np.abs(targets[:count,3])>.25)
    weights=torch.tensor([1.,1.,2.,2.],device=model.device)
    losses=[]
    policy.set_training_mode(True)
    for _ in range(updates):
        indices=rng.integers(count,size=batch_size)
        if len(turns):indices[:batch_size//2]=rng.choice(turns,batch_size//2)
        obs=torch.as_tensor(np.array(observations[indices]),device=model.device)
        actions=torch.as_tensor(np.array(targets[indices]),device=model.device)
        predicted=actor_mean(policy,obs)
        loss=((predicted-actions).square()*weights).mean()
        if not torch.isfinite(loss):raise RuntimeError('Nonfinite imitation loss')
        optimizer.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(params,1.);optimizer.step()
        losses.append(float(loss.detach()))
        if progress is not None and len(losses)%100==0:progress(len(losses),losses[-1])
    policy.set_training_mode(False)
    return {'updates':updates,'examples':count,'first_loss':losses[0],
            'last_loss':losses[-1],'mean_last_100_loss':float(np.mean(losses[-100:])),
            'finite_losses':bool(np.isfinite(losses).all()),'maneuver_examples':int(len(turns))}


def collect_guided(env,model,observations,targets,offset,steps,rng,beta,features=None,teachers=None,rewards=None,terminals=None,progress=None,recover=False,trace=None):
    """Continuous full-brain rollouts; beta controls teacher action probability.

    All labels come from optimization worlds. Teacher route/state remain in this
    collector and never enter brain sensors, policy tensors or saved weights.
    """
    if steps<=0 or steps%env.num_envs or not 0<=beta<=1:raise ValueError('Invalid bounded guided rollout')
    if features is None:features=env.reset()
    if teachers is None:teachers=[RouteTeacher(w,recover=recover) for w in env.worlds]
    outcomes={'success':0,'collision':0,'timeout':0};teacher_actions=0;dones=np.zeros(env.num_envs,dtype=bool)
    for tick in range(steps//env.num_envs):
        labels=np.stack([teacher.action(w) for teacher,w in zip(teachers,env.worlds)])
        start=offset+tick*env.num_envs
        observations[start:start+env.num_envs]=features
        targets[start:start+env.num_envs]=labels
        chosen=rng.random(env.num_envs)<beta
        actions=labels.copy()
        if not chosen.all():
            predicted=model.predict(features,deterministic=True)[0]
            actions[~chosen]=predicted[~chosen]
        teacher_actions+=int(chosen.sum())
        if trace is not None:
            selection=slice(start,start+env.num_envs)
            trace['executed_actions'][selection]=actions
            trace['position'][selection]=np.stack([w.position for w in env.worlds])
            trace['velocity'][selection]=np.stack([w.velocity for w in env.worlds])
            trace['yaw'][selection]=[w.yaw for w in env.worlds]
            trace['layout_seed'][selection]=[w.seed_value for w in env.worlds]
            trace['teacher_used'][selection]=chosen
        features,reward,dones,infos=env.step(actions)
        if rewards is not None:rewards[start:start+env.num_envs]=reward
        if terminals is not None:terminals[start:start+env.num_envs]=dones
        model.num_timesteps+=env.num_envs
        for i in np.flatnonzero(dones):
            info=infos[i]
            outcomes['success']+=bool(info['success']);outcomes['collision']+=bool(info['collision']);outcomes['timeout']+=bool(info['truncated'])
            teachers[i]=RouteTeacher(env.worlds[i],recover=recover)
        if progress is not None and (tick+1)%128==0:progress((tick+1)*env.num_envs)
    model._last_obs=features.copy();model._last_episode_starts=dones.copy()
    return features,teachers,{'transitions':steps,'teacher_actions':teacher_actions,'student_actions':steps-teacher_actions,
                             'episode_outcomes':outcomes,'beta':beta}


def fit_critic(model,observations,rewards,terminals,count,envs,updates,rng,batch_size=256,data_boundaries=None):
    """Fit critic to bounded discounted guided returns; actor stays fixed."""
    values=np.zeros(count,dtype=np.float32);running=np.zeros(envs)
    stops=np.asarray(terminals[:count],dtype=bool).copy()
    if data_boundaries is not None:
        if np.asarray(data_boundaries).shape!=(count,):raise ValueError("Critic data boundaries must match recorded transitions")
        stops|=np.asarray(data_boundaries,dtype=bool)
    for start in range(count-envs,-1,-envs):
        running=rewards[start:start+envs]+model.gamma*running*(~stops[start:start+envs])
        values[start:start+envs]=running
    policy=model.policy;params=list(policy.mlp_extractor.value_net.parameters())+list(policy.value_net.parameters())
    optimizer=torch.optim.Adam(params,lr=1e-3);losses=[]
    for _ in range(updates):
        indices=rng.integers(count,size=batch_size)
        obs=torch.as_tensor(np.array(observations[indices]),device=model.device)
        target=torch.as_tensor(values[indices],device=model.device)
        with torch.no_grad():features=policy.extract_features(obs)
        if isinstance(features,tuple):features=features[1]
        predicted=policy.value_net(policy.mlp_extractor.forward_critic(features)).flatten()
        loss=(predicted-target).square().mean()
        if not torch.isfinite(loss):raise RuntimeError('Nonfinite guided critic loss')
        optimizer.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(params,10.);optimizer.step();losses.append(float(loss.detach()))
    return {'updates':updates,'first_loss':losses[0],'last_loss':losses[-1],
            'mean_last_100_loss':float(np.mean(losses[-100:])),
            'finite_losses':bool(np.isfinite(losses).all()),'unfinished_suffix_bootstrap':0.,
            'target_mean':float(values.mean()),
            'data_boundary_rows':int(np.count_nonzero(data_boundaries)) if data_boundaries is not None else 0}


def run_guided(plan_path,device='cuda'):
    """Run only an explicitly supplied frozen local plan with a hard budget."""
    import json,hashlib,os,traceback
    from datetime import datetime,timezone
    from fly_rl.training.learning import BrainEnv,load_model,save_model,TimedCheckpoint
    from fly_rl.training.temporal_policy import transfer_history_policy
    from fly_rl.training.route_progress import configure_route_progress
    from fly_rl.training.evaluation import evaluate
    def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    plan_path=Path(plan_path);plan=json.loads(plan_path.read_text(encoding='utf-8-sig'))
    if plan.get('status')=='draft-budget-required':raise ValueError('This draft requires explicit budget approval before execution')
    if (plan['kind'] not in ('guided-brain-navigation-v1','guided-brain-navigation-v2') or plan['steps']<=0 or plan['steps']%4096
            or plan['teacher_steps']+plan['dagger_steps']+plan['ppo_steps']!=plan['steps']
            or plan['prior_substantive_transitions']+plan['steps']>plan['cumulative_cap']):
        raise ValueError('Invalid or excessive guided navigation budget')
    if set(plan['optimization_layouts']).intersection(plan['validation_seeds']+plan['excluded_practice_seeds']):
        raise ValueError('Optimizer layouts overlap withheld layouts')
    for path,digest in plan['source_hashes'].items():
        if sha(path)!=digest:raise ValueError('Frozen source changed: '+path)
    if sha(plan['source'])!=plan['source_sha256']:raise ValueError('Warm source changed')
    for path,digest in plan['aliases_before'].items():
        if sha(path)!=digest:raise ValueError('Original alias changed')
    folder=Path(plan['output']);folder.mkdir(parents=True,exist_ok=True);status_path=folder/'status.json'
    if status_path.exists():raise ValueError('Refusing to overwrite or restart an existing guided run')
    status={'status':'running','stage':'initializing','pid':os.getpid(),
            'started_utc':datetime.now(timezone.utc).isoformat(),'plan_sha256':sha(plan_path),
            'test_evaluated':False,'added_transitions':0,'guided_results':[],'fit_results':[]}
    def save():
        temp=status_path.with_suffix('.tmp');temp.write_text(json.dumps(status,indent=2));temp.replace(status_path)
    save();env=None;model=None;initial=0
    torch.set_num_threads(4);rng=np.random.default_rng(plan['training_seed'])
    try:
        env=BrainEnv(plan.get('data','data'),plan['batch'],device,seed=plan['training_seed'],mode='dense',
                     dynamics='coordinated',sensor_version=plan['sensor_version'],map_profile='large',
                     layout_seeds=plan['optimization_layouts'],history_frames=32,history_stride=8)
        configure_route_progress(env,plan['training_seed'])
        source=load_model(plan['source'],env.brain)
        model=transfer_history_policy(source,env,plan['training_seed']);initial=model.num_timesteps
        model.gamma=.9995;model.rollout_buffer.gamma=model.gamma
        model.imitation_training={'teacher_version':TEACHER_VERSION,'privileged_training_geometry':True,
                                  'runtime_teacher':False,'guided_transitions':0,'supervised_updates':0,
                                  'ppo_added_transitions':0,'history_frames':32,'history_stride':8}
        total_guided=plan['teacher_steps']+plan['dagger_steps'];shape=(total_guided,33,256)
        data_folder=folder/'training-data';data_folder.mkdir()
        x=np.memmap(data_folder/'brain-features.f32',mode='w+',dtype=np.float32,shape=shape)
        y=np.memmap(data_folder/'teacher-actions.f32',mode='w+',dtype=np.float32,shape=(total_guided,4))
        rewards=np.zeros(total_guided,dtype=np.float32);terminals=np.zeros(total_guided,dtype=bool)
        data_boundaries=np.zeros(total_guided,dtype=bool)
        trace_shapes={'executed_actions':(total_guided,4),'position':(total_guided,3),
                      'velocity':(total_guided,3),'yaw':(total_guided,),
                      'layout_seed':(total_guided,),'teacher_used':(total_guided,)}
        trace_types={'layout_seed':np.int64,'teacher_used':np.bool_}
        trace={key:np.memmap(data_folder/(key+'.bin'),mode='w+',
                  dtype=trace_types.get(key,np.float32),shape=shape) for key,shape in trace_shapes.items()}
        (data_folder/'trace-schema.json').write_text(json.dumps({key:{'shape':list(value.shape),'dtype':str(value.dtype)}
                 for key,value in trace.items()},indent=2))
        status.update(graph_neurons=env.brain.n,graph_edges=env.brain.audit['edges'],dataset_shape=list(shape));save()
        def collected(n):
            status['added_transitions']=model.num_timesteps-initial;save()
        def flush_data(valid_rows):
            x.flush();y.flush()
            np.save(data_folder/'rewards.npy',rewards[:valid_rows])
            np.save(data_folder/'terminals.npy',terminals[:valid_rows])
            np.save(data_folder/'data-boundaries.npy',data_boundaries[:valid_rows])
            for value in trace.values():value.flush()
            status['guided_data_valid_rows']=valid_rows
        features=None;teachers=None;count=0
        for _ in range(plan['teacher_steps']//8192):
            status['stage']='teacher-rollouts';save()
            features,teachers,result=collect_guided(env,model,x,y,count,8192,rng,1.,features,teachers,rewards,terminals,collected,trace=trace)
            count+=8192;status['guided_results'].append(result);status['added_transitions']=model.num_timesteps-initial
            model.imitation_training['guided_transitions']=count;flush_data(count)
            save_model(model,folder/'guided-before-fit.zip',env.brain);save()
        def fitted(n,loss):status.update(stage_updates=n,stage_loss=loss);save()
        status['stage']='actor-imitation';save()
        result=fit_actor(model,x,y,count,plan['actor_updates'],rng,progress=fitted)
        status['fit_results'].append(dict(stage='actor-imitation',**result))
        model.imitation_training['supervised_updates']+=result['updates']
        save_model(model,folder/'imitation-policy.zip',env.brain);save()
        dagger_rounds=plan.get('dagger_rounds',1)
        for _ in range(dagger_rounds):
            status['stage']='dagger-rollouts';save()
            if plan.get('dagger_restart_from_original_start',False):
                if count:
                    data_boundaries[count-env.num_envs:count]=True
                    status.setdefault('critic_data_cuts_at_transition_count',[]).append(count)
                    flush_data(count)
                features=env.reset();teachers=[RouteTeacher(w,recover=True) for w in env.worlds]
            features,teachers,result=collect_guided(env,model,x,y,count,plan['dagger_steps']//dagger_rounds,
                  rng,plan.get('dagger_beta',.8),features,teachers,rewards,terminals,collected,
                  recover=plan.get('dagger_restart_from_original_start',False),trace=trace)
            count+=plan['dagger_steps']//dagger_rounds;status['guided_results'].append(result)
            model.imitation_training['guided_transitions']=count
            status['added_transitions']=model.num_timesteps-initial;flush_data(count);save()
            status['stage']='dagger-imitation';save()
            result=fit_actor(model,x,y,count,plan['dagger_updates']//dagger_rounds,rng,progress=fitted)
            status['fit_results'].append(dict(stage='dagger-imitation',**result))
            model.imitation_training['supervised_updates']+=result['updates']
        status['stage']='critic-initialization';save()
        flush_data(count)
        result=fit_critic(model,x,rewards,terminals,count,plan['batch'],plan['critic_updates'],rng,
                          data_boundaries=data_boundaries[:count])
        status['fit_results'].append(dict(stage='critic-initialization',**result));model.imitation_training['supervised_updates']+=result['updates']
        with torch.no_grad():model.policy.log_std.fill_(-2.)
        # The imitation optimizer is separate. Reset PPO Adam after supervision,
        # and use a small bounded refinement rather than the old high noise.
        model.learning_rate=1e-4;model.lr_schedule=lambda _:1e-4;model.target_kl=.01
        model.policy.optimizer=model.policy.optimizer_class(model.policy.parameters(),lr=1e-4,**model.policy.optimizer_kwargs)
        model.tensorboard_log=str(folder/'tensorboard')
        save_model(model,folder/'guided-policy.zip',env.brain)
        status.update(stage='ppo-refinement',guided_checkpoint=str(folder/'guided-policy.zip'));save()
        before=model.num_timesteps
        model.learn(total_timesteps=plan['ppo_steps'],reset_num_timesteps=False,
                    callback=TimedCheckpoint(folder/'ppo-checkpoints',env.brain))
        model.imitation_training['ppo_added_transitions']=model.num_timesteps-before
        status['added_transitions']=model.num_timesteps-initial
        status['ppo_losses']={k:float(v) for k,v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}
        if not all(np.isfinite(v) for v in status['ppo_losses'].values()):raise RuntimeError('Nonfinite PPO refinement loss')
        if status['added_transitions']!=plan['steps']:raise RuntimeError('Guided transition budget mismatch')
        final=folder/'policy.zip';save_model(model,final,env.brain)
        status.update(stage='validation',checkpoint=str(final),training_summary=env.reward_shaping.snapshot());save()
        status['validation']=evaluate(plan.get('data','data'),device,final,len(plan['validation_seeds']),mode='dense',
                                      seed=plan['validation_seeds'][0],dynamics='coordinated',map_profile='large')
        status.update(status='completed',stage='done',cumulative_added_transitions=plan['prior_substantive_transitions']+status['added_transitions'])
        # Reload compatibility uses real brain observations, without a teacher.
        reloaded=load_model(final,env.brain,env)
        status['checkpoint_reload_matches']=bool(np.allclose(model.predict(model._last_obs,deterministic=True)[0],
                                                              reloaded.predict(model._last_obs,deterministic=True)[0]))
    except Exception as error:
        status.update(status='failed',stage='error',error=str(error),traceback=traceback.format_exc())
        if model is not None:
            status['added_transitions']=model.num_timesteps-initial;save_model(model,folder/'interrupted-policy.zip',env.brain)
        raise
    finally:
        if env is not None:env.close()
        status['finished_utc']=datetime.now(timezone.utc).isoformat()
        status['aliases_after']={path:sha(path) for path in plan['aliases_before']}
        status['aliases_unchanged']=status['aliases_after']==plan['aliases_before']
        status['warm_source_unchanged']=sha(plan['source'])==plan['source_sha256'];save()
    return status
