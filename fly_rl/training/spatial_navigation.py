"""Bounded full-connectome spatial imitation experiment on original large rooms."""
import json
import hashlib
import os
import traceback
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import torch
from stable_baselines3 import PPO
from fly_rl.connectome.readout import GROUP_READOUT
from fly_rl.simulation.sensors import SENSOR_V5
from fly_rl.training.learning import BrainEnv,save_model,load_model
from fly_rl.training.spatial_policy import SpatialBrainHistory
from fly_rl.training.guided_learning import collect_guided,fit_actor,RouteTeacher
from fly_rl.training.evaluation import evaluate

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(plan_path,device='cuda'):
    plan=json.loads(Path(plan_path).read_text(encoding='utf-8-sig'))
    if (plan.get('status')!='approved' or plan.get('kind')!='spatial-neural-navigation-v1'
        or plan['teacher_steps']!=65536 or plan['student_steps']!=32768
        or plan['steps']!=98304 or plan['prior_substantive_transitions']+plan['steps']!=plan['cumulative_cap']):
        raise ValueError('Invalid frozen spatial experiment budget')
    if set(plan['optimization_layouts'])&set(plan['validation_seeds']):raise ValueError('Overlapping layouts')
    if plan['validation_seeds']!=list(range(430000,430008)):raise ValueError('Development suite mismatch')
    for path,digest in {**plan['source_hashes'],**plan['aliases_before']}.items():
        if sha(path)!=digest:raise ValueError('Frozen file changed: '+path)
    folder=Path(plan['output']);folder.mkdir(parents=True,exist_ok=True)
    path=folder/'status.json'
    if path.exists():raise ValueError('Refusing to overwrite or restart existing experiment')
    status={'status':'running','stage':'initializing','pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),
        'plan_sha256':sha(plan_path),'added_transitions':0,'test_evaluated':False,'guided_results':[],'fit_results':[]}
    def save():
        temp=path.with_suffix('.tmp');temp.write_text(json.dumps(status,indent=2));temp.replace(path)
    save();env=None;model=None
    torch.set_num_threads(4)
    # Batch-eight convolutions can select TF32 kernels. Keep the declared
    # CPU/CUDA reload tolerance meaningful rather than relaxing its assertion.
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cuda.matmul.allow_tf32=False
    rng=np.random.default_rng(plan['training_seed'])
    try:
        env=BrainEnv(plan.get('data','data'),8,device,seed=plan['training_seed'],mode='dense',
            dynamics='coordinated',sensor_version=SENSOR_V5,map_profile='large',layout_seeds=plan['optimization_layouts'],
            history_frames=8,history_stride=8,readout_version=GROUP_READOUT)
        model=PPO('MlpPolicy',env,device=device,seed=plan['training_seed'],n_steps=512,batch_size=128,n_epochs=5,
            policy_kwargs={'features_extractor_class':SpatialBrainHistory,'ortho_init':False,
                'share_features_extractor':False,'net_arch':{'pi':[128,128],'vf':[128,128]}},verbose=0)
        model.policy_numeric_precision={'cudnn_allow_tf32':False,'matmul_allow_tf32':False}
        model.imitation_training={'runtime_teacher':False,'privileged_training_geometry':True,
            'teacher_version':'certified-3d-coordinated-teacher-v1','ppo_added_transitions':0,
            'guided_transitions':0,'supervised_updates':0,'teacher_start_strategy':'original large route fragment starts; student original starts'}
        status.update(graph_neurons=env.brain.n,graph_edges=env.brain.audit['edges'],policy_device=str(model.device));save()
        shape=(plan['steps'],9,env.feature_count)
        data_folder=folder/'training-data';data_folder.mkdir()
        x=np.memmap(data_folder/'brain-features.f32',mode='w+',dtype=np.float32,shape=shape)
        y=np.memmap(data_folder/'teacher-actions.f32',mode='w+',dtype=np.float32,shape=(plan['steps'],4))
        status['dataset_shape']=list(shape);save()
        def progress(n):status['added_transitions']=model.num_timesteps;save()
        def fitted(n,loss):status.update(stage_updates=n,stage_loss=loss);save()
        count=0
        # Spread supervised fragments over the full optimization pool. Each fragment
        # still flies the unmodified large room; only its training start is changed.
        for fragment in range(16):
            status.update(stage='teacher-fragments',fragment=fragment);save()
            sensors=[];fragment_seeds=[];route_vertices=[]
            for i,w in enumerate(env.worlds):
                seed=plan['optimization_layouts'][(fragment*8+i)%len(plan['optimization_layouts'])]
                w.reset(seed=seed)
                route=np.asarray(w.reference_route)
                vertex=int(rng.integers(max(1,len(route)-1))) if fragment>=4 else 0
                w.position=route[vertex].copy();w.velocity[:]=0
                delta=route[min(vertex+1,len(route)-1)]-w.position
                w.yaw=float(np.arctan2(delta[1],delta[0]));w.distance=float(np.linalg.norm(w.target-w.position))
                sensors.append(w.observe());fragment_seeds.append(seed);route_vertices.append(vertex)
            env.brain.reset();env.feature_history.fill(0);env.history_ticks.fill(0)
            env.returns.fill(0);env.lengths.fill(0)
            features=env._pack_features(env.brain.step(np.asarray(sensors)))
            teachers=[RouteTeacher(w,recover=True) for w in env.worlds]
            features,teachers,result=collect_guided(env,model,x,y,count,4096,rng,1.,features,teachers,
                progress=progress,recover=True)
            result.update(fragment_seeds=fragment_seeds,route_vertices=route_vertices)
            status['guided_results'].append(result);count+=4096;x.flush();y.flush();save()
        status['stage']='actor-imitation';save()
        result=fit_actor(model,x,y,count,plan['actor_updates'],rng,batch_size=128,progress=fitted)
        status['fit_results'].append(result);save_model(model,folder/'imitation-policy.zip',env.brain);save()
        # Student-only actions from original starts; train-only teacher supplies labels.
        for round_index in range(2):
            status.update(stage='student-rollouts',student_round=round_index);save()
            features=env.reset();teachers=[RouteTeacher(w,recover=True) for w in env.worlds]
            features,teachers,result=collect_guided(env,model,x,y,count,16384,rng,0.,features,teachers,
                progress=progress,recover=True)
            count+=16384;status['guided_results'].append(result);x.flush();y.flush();save()
            status['stage']='student-imitation';save()
            status['fit_results'].append(fit_actor(model,x,y,count,plan['student_updates']//2,rng,batch_size=128,progress=fitted))
            save_model(model,folder/f'student-round-{round_index}.zip',env.brain);save()
        if model.num_timesteps!=plan['steps']:raise RuntimeError('Transition budget mismatch')
        model.imitation_training.update(guided_transitions=count,supervised_updates=sum(r['updates'] for r in status['fit_results']))
        final=folder/'policy.zip';save_model(model,final,env.brain)
        reloaded=load_model(final,env.brain,env)
        before=model.predict(features,deterministic=True)[0];after=reloaded.predict(features,deterministic=True)[0]
        status['checkpoint_reload_max_error']=float(np.max(np.abs(before-after)))
        status['checkpoint_reload_matches']=bool(np.allclose(before,after,atol=1e-5,rtol=1e-5))
        if not status['checkpoint_reload_matches']:raise RuntimeError('Checkpoint prediction mismatch')
        status.update(stage='validation',checkpoint=str(final));save()
        status['validation']=evaluate(plan.get('data','data'),device,final,8,mode='dense',seed=430000,
            dynamics='coordinated',map_profile='large')
        status.update(status='completed',stage='done',cumulative_added_transitions=plan['cumulative_cap'])
    except Exception as error:
        status.update(status='failed',error=str(error),traceback=traceback.format_exc());raise
    finally:
        if model is not None:status['added_transitions']=model.num_timesteps
        if env is not None:env.close()
        status['aliases_after']={p:sha(p) for p in plan['aliases_before']}
        status['aliases_unchanged']=status['aliases_after']==plan['aliases_before']
        status['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    return status

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--plan',required=True)
    parser.add_argument('--device',default='cuda');args=parser.parse_args();run(args.plan,args.device)
