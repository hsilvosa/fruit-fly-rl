"""Bounded neural waypoint supervision with continuous autonomous student flights."""
import hashlib,json,os,traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import torch
from stable_baselines3 import PPO
from fly_rl.training.learning import BrainEnv,load_model,save_model
from fly_rl.training.waypoint_policy import transfer_waypoint_policy
from fly_rl.training.guided_learning import collect_guided,fit_actor,RouteTeacher
from fly_rl.connectome.readout import GROUP_READOUT
from fly_rl.simulation.sensors import SENSOR_V5
from fly_rl.training.evaluation import evaluate

def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def validate_plan(plan):
    if (plan.get('status')!='approved' or plan.get('kind')!='neural-waypoint-navigation-v1'
        or plan['steps']!=81920 or plan['teacher_steps']!=16384 or plan['student_steps']!=65536
        or plan['prior_substantive_transitions']+plan['steps']!=plan['cumulative_cap']
        or plan['reuse_rows']!=98304 or plan['actor_updates']!=2048 or plan['student_updates']!=4096
        or plan['teacher_initialization']!='original_position_and_heading'
        or plan['student_continuity']!='preserve_until_physical_terminal'):
        raise ValueError('Invalid frozen waypoint experiment scope or budget')
    if plan['validation_seeds']!=list(range(430000,430008)):raise ValueError('Development suite mismatch')
    if plan['optimization_layouts']!=list(range(370000,370112)):raise ValueError('Optimization pool mismatch')
    if set(plan['optimization_layouts'])&set(plan['validation_seeds']):raise ValueError('Overlapping layouts')

def reset_training_world(world,layout_seed):
    """Select an exact optimization layout, retaining its generated initial pose."""
    pool=world.layout_seeds
    try:
        world.layout_seeds=None
        sensors,_=world.reset(seed=layout_seed)
    finally:world.layout_seeds=pool
    if world.seed_value!=layout_seed:raise RuntimeError('Explicit optimization layout mismatch')
    return sensors

def run(plan_path,device='cuda'):
    plan=json.loads(Path(plan_path).read_text(encoding='utf-8-sig'));validate_plan(plan)
    for path,digest in {**plan['source_hashes'],**plan['source_artifacts'],**plan['aliases_before']}.items():
        if sha(path)!=digest:raise ValueError('Frozen file changed: '+path)
    folder=Path(plan['output']);folder.mkdir(parents=True,exist_ok=True);status_path=folder/'status.json'
    if status_path.exists():raise ValueError('Refusing to overwrite or restart existing experiment')
    status={'status':'running','stage':'initializing','pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),
        'plan_sha256':sha(plan_path),'added_transitions':0,'test_evaluated':False,'guided_results':[],'fit_results':[],
        'reused_optimization_rows':plan['reuse_rows'],'source_checkpoint':plan['source']}
    def save():
        temporary=status_path.with_suffix('.tmp');temporary.write_text(json.dumps(status,indent=2));temporary.replace(status_path)
        record={key:status.get(key) for key in ('status','stage','added_transitions','fragment','student_round','stage_updates','stage_loss')}
        record['observed_utc']=datetime.now(timezone.utc).isoformat()
        with (folder/'progress.jsonl').open('a',encoding='utf8') as stream:stream.write(json.dumps(record)+'\n')
    save();env=None;model=None;initial=None
    torch.set_num_threads(4);torch.backends.cudnn.allow_tf32=False;torch.backends.cuda.matmul.allow_tf32=False
    rng=np.random.default_rng(plan['training_seed'])
    try:
        env=BrainEnv(plan.get('data','data'),8,device,seed=plan['training_seed'],mode='dense',dynamics='coordinated',
            sensor_version=SENSOR_V5,map_profile='large',layout_seeds=plan['optimization_layouts'],history_frames=8,
            history_stride=8,readout_version=GROUP_READOUT)
        source=load_model(plan['source'],env.brain,env)
        model=transfer_waypoint_policy(source,env,plan['training_seed'],device=device);initial=model.num_timesteps
        sample=env.reset();old=source.predict(sample,deterministic=True)[0];new=model.predict(sample,deterministic=True)[0]
        status['transfer_motor_max_error']=float(np.max(np.abs(old-new)))
        if not np.allclose(old,new,atol=1e-5,rtol=1e-5):raise RuntimeError('Motor transfer mismatch')
        del source
        model.imitation_training={'runtime_teacher':False,'privileged_training_geometry':True,'ppo_added_transitions':0,
            'guided_transitions':0,'reused_optimization_rows':plan['reuse_rows'],'supervised_updates':0,
            'teacher_start_strategy':plan['teacher_initialization'],'student_continuity':plan['student_continuity']}
        status.update(graph_neurons=env.brain.n,graph_edges=env.brain.audit['edges'],source_lifetime_steps=initial,
            policy_device=str(model.device));save()
        total=plan['reuse_rows']+plan['steps'];shape=(total,9,env.feature_count)
        data=folder/'training-data';data.mkdir()
        x=np.memmap(data/'brain-features.f32',mode='w+',dtype=np.float32,shape=shape)
        y=np.memmap(data/'teacher-actions.f32',mode='w+',dtype=np.float32,shape=(total,4))
        waypoints=np.memmap(data/'waypoint-labels.f32',mode='w+',dtype=np.float32,shape=(total,4))
        waypoints[:plan['reuse_rows']]=np.nan
        old_x=np.memmap(plan['reuse_features'],mode='r',dtype=np.float32,shape=(plan['reuse_rows'],9,env.feature_count))
        old_y=np.memmap(plan['reuse_actions'],mode='r',dtype=np.float32,shape=(plan['reuse_rows'],4))
        for start in range(0,plan['reuse_rows'],4096):
            end=min(start+4096,plan['reuse_rows']);x[start:end]=old_x[start:end];y[start:end]=old_y[start:end]
        del old_x,old_y
        trace_shapes={'executed_actions':(total,4),'position':(total,3),'velocity':(total,3),
            'yaw':(total,),'layout_seed':(total,),'teacher_used':(total,)}
        trace_types={'layout_seed':np.int64,'teacher_used':np.bool_}
        trace={key:np.memmap(data/(key+'.bin'),mode='w+',dtype=trace_types.get(key,np.float32),shape=dimensions)
            for key,dimensions in trace_shapes.items()}
        (data/'schema.json').write_text(json.dumps({'brain_features_shape':list(shape),'trace_valid_start':plan['reuse_rows'],
            'old_waypoint_labels':'NaN; masked from auxiliary loss','trace':{k:{'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in trace.items()}},indent=2))
        count=plan['reuse_rows'];status['dataset_shape']=list(shape);save()
        def progress(n):status['added_transitions']=model.num_timesteps-initial;save()
        def fitted(n,loss):status.update(stage_updates=n,stage_loss=loss);save()
        def flush():
            x.flush();y.flush();waypoints.flush()
            for value in trace.values():value.flush()
            status['data_valid_rows']=count
        def fit(stage,updates):
            status.update(stage=stage,stage_updates=None,stage_loss=None);save()
            result=fit_actor(model,x,y,count,updates,rng,batch_size=128,progress=fitted,
                sampling_strategy='maneuver-start-balanced-v2',waypoint_targets=waypoints,waypoint_loss_weight=2.)
            status['fit_results'].append(result);model.imitation_training['supervised_updates']+=updates;save()
        for fragment in range(8):
            status.update(stage='teacher-starts',fragment=fragment);save()
            sensors=[];seeds=[];headings=[]
            for i,w in enumerate(env.worlds):
                seed=plan['optimization_layouts'][fragment*8+i]
                sensors.append(reset_training_world(w,seed));seeds.append(w.seed_value);headings.append(w.yaw)
            env.brain.reset();env.feature_history.fill(0);env.history_ticks.fill(0);env.returns.fill(0);env.lengths.fill(0)
            features=env._pack_features(env.brain.step(np.asarray(sensors)))
            teachers=[RouteTeacher(w,recover=True) for w in env.worlds]
            features,teachers,result=collect_guided(env,model,x,y,count,2048,rng,1.,features,teachers,progress=progress,
                recover=True,trace=trace,waypoint_targets=waypoints)
            count+=2048;result.update(actual_initial_layouts=seeds,actual_initial_headings=headings)
            status['guided_results'].append(result);flush();save()
        fit('actor-and-waypoint-imitation',2048)
        save_model(model,folder/'imitation-policy.zip',env.brain)
        features=env.reset();teachers=[RouteTeacher(w,recover=True) for w in env.worlds]
        for student_round in range(4):
            # Physical episodes, full brain state and feature histories survive fits.
            status.update(stage='student-rollouts',student_round=student_round,stage_updates=None,stage_loss=None);save()
            features,teachers,result=collect_guided(env,model,x,y,count,16384,rng,0.,features,teachers,progress=progress,
                recover=True,trace=trace,waypoint_targets=waypoints)
            count+=16384;status['guided_results'].append(result);flush();save()
            fit('student-and-waypoint-imitation',1024)
            save_model(model,folder/f'student-round-{student_round}.zip',env.brain)
        status['added_transitions']=model.num_timesteps-initial
        if status['added_transitions']!=plan['steps']:raise RuntimeError('Transition budget mismatch')
        model.imitation_training['guided_transitions']=plan['steps']
        final=folder/'policy.zip';save_model(model,final,env.brain)
        cpu=load_model(final,env.brain,env);gpu=PPO.load(final,device=device)
        status['reload_tensors_equal']=all(torch.equal(v.cpu(),cpu.policy.state_dict()[k].cpu()) for k,v in model.policy.state_dict().items())
        a=model.predict(features,deterministic=True)[0];b=cpu.predict(features,deterministic=True)[0];c=gpu.predict(features,deterministic=True)[0]
        status['cpu_reload_max_error']=float(np.max(np.abs(a-b)));status['same_device_reload_max_error']=float(np.max(np.abs(a-c)))
        status['checkpoint_reload_matches']=bool(status['reload_tensors_equal'] and np.array_equal(a,c) and np.allclose(a,b,atol=1e-5,rtol=1e-5))
        if not status['checkpoint_reload_matches']:raise RuntimeError('Waypoint checkpoint prediction mismatch')
        status.update(stage='validation',checkpoint=str(final));save()
        status['validation']=evaluate(plan.get('data','data'),device,final,8,mode='dense',seed=430000,dynamics='coordinated',map_profile='large')
        status.update(status='completed',stage='done',cumulative_added_transitions=plan['cumulative_cap'])
    except Exception as error:
        status.update(status='failed',error=str(error),traceback=traceback.format_exc());raise
    finally:
        if model is not None and initial is not None:status['added_transitions']=model.num_timesteps-initial
        if env is not None:env.close()
        status['aliases_verified']={p:sha(p)==h for p,h in plan['aliases_before'].items()}
        status['source_checkpoint_unchanged']=sha(plan['source'])==plan['source_artifacts'][plan['source']]
        status['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    return status
