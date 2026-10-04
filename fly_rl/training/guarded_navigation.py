"""Frozen, bounded original-large PPO correction with an explicit KL gate."""
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import torch


def run_guarded_navigation(plan_path, device='cuda'):
    from fly_rl.training.learning import BrainEnv,load_model,save_model,TimedCheckpoint
    from fly_rl.training.guarded_ppo import configure_kl_guard
    from fly_rl.training.route_progress import configure_route_progress
    from fly_rl.training.evaluation import evaluate
    sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    plan_path=Path(plan_path)
    plan=json.loads(plan_path.read_text(encoding='utf-8-sig'))
    if plan.get('status')!='approved':raise ValueError('Explicit approved plan required')
    if (plan['kind']!='guarded-original-large-v1' or not 0<plan['steps']<=32768
            or plan['steps']%4096 or plan['prior_substantive_transitions']+plan['steps']>plan['cumulative_cap']):
        raise ValueError('Invalid guarded navigation budget')
    if plan['validation_seeds']!=list(range(plan['validation_seeds'][0],plan['validation_seeds'][0]+8)):
        raise ValueError('Exactly eight contiguous development layouts required')
    if set(plan['optimization_layouts']) & set(plan['validation_seeds']):raise ValueError('Layout overlap')
    for path,digest in plan['source_hashes'].items():
        if sha(path)!=digest:raise ValueError('Frozen implementation changed: '+path)
    if sha(plan['source'])!=plan['source_sha256'] or sha(Path(plan['source']).with_suffix('.json'))!=plan['source_metadata_sha256']:
        raise ValueError('Frozen source checkpoint changed')
    for path,digest in plan['aliases_before'].items():
        if sha(path)!=digest:raise ValueError('Original alias changed')
    folder=Path(plan['output']);folder.mkdir(parents=True,exist_ok=True)
    status_path=folder/'status.json'
    if status_path.exists():raise ValueError('Refusing to overwrite an existing experiment')
    status={'status':'running','stage':'baseline-validation','pid':os.getpid(),
            'started_utc':datetime.now(timezone.utc).isoformat(),'plan_sha256':sha(plan_path),
            'added_transitions':0,'test_evaluated':False}
    def save():
        temp=status_path.with_suffix('.tmp');temp.write_text(json.dumps(status,indent=2));temp.replace(status_path)
    save();env=None;model=None;initial=0
    torch.set_num_threads(4)
    try:
        # This source is declared before outcomes are measured; no selection occurs here.
        status['baseline_validation']=evaluate(plan['data'],device,plan['source'],8,mode='dense',
            seed=plan['validation_seeds'][0],dynamics='coordinated',map_profile='large');save()
        env=BrainEnv(plan['data'],8,device,seed=42,mode='dense',dynamics='coordinated',
                     sensor_version=plan['sensor_version'],map_profile='large',
                     layout_seeds=plan['optimization_layouts'],history_frames=32,history_stride=8)
        configure_route_progress(env,42)
        model=load_model(plan['source'],env.brain,env)
        if model.policy.share_features_extractor:raise ValueError('Separated history checkpoint required')
        configure_kl_guard(model,plan['mean_kl_limit'],plan['max_kl_limit'],plan['guard_attempts'])
        initial=model.num_timesteps
        model.tensorboard_log=str(folder/'tensorboard')
        status.update(stage='ppo-training',graph_neurons=env.brain.n,graph_edges=env.brain.audit['edges']);save()
        model.learn(total_timesteps=plan['steps'],reset_num_timesteps=False,
                    callback=TimedCheckpoint(folder/'checkpoints',env.brain))
        status['added_transitions']=model.num_timesteps-initial
        if getattr(model,'imitation_training',None):
            model.imitation_training['ppo_added_transitions']+=status['added_transitions']
        if status['added_transitions']!=plan['steps']:raise RuntimeError('Transition budget mismatch')
        status['guard_updates']=model.kl_guard_history
        status['losses']={k:float(v) for k,v in model.logger.name_to_value.items()
                          if k.startswith('train/') and np.isscalar(v)}
        if not all(np.isfinite(v) for v in status['losses'].values()):raise RuntimeError('Nonfinite losses')
        if not all(r['retained_mean_kl']<=plan['mean_kl_limit'] and r['retained_max_kl']<=plan['max_kl_limit']
                   for r in status['guard_updates']):raise RuntimeError('Retained KL exceeds contract')
        final=folder/'policy.zip';save_model(model,final,env.brain)
        status.update(stage='validation',checkpoint=str(final),training_summary=env.reward_shaping.snapshot());save()
        status['validation']=evaluate(plan['data'],device,final,8,mode='dense',
             seed=plan['validation_seeds'][0],dynamics='coordinated',map_profile='large')
        reloaded=load_model(final,env.brain,env)
        status['checkpoint_reload_matches']=bool(np.array_equal(model.predict(model._last_obs,deterministic=True)[0],
                                                                  reloaded.predict(model._last_obs,deterministic=True)[0]))
        status.update(status='completed',stage='done',cumulative_added_transitions=plan['prior_substantive_transitions']+status['added_transitions'])
    except Exception as error:
        import traceback
        status.update(status='failed',stage='error',error=str(error),traceback=traceback.format_exc())
        if model is not None:
            status['added_transitions']=model.num_timesteps-initial
            save_model(model,folder/'interrupted-policy.zip',env.brain)
        raise
    finally:
        if env is not None:env.close()
        status['aliases_after']={path:sha(path) for path in plan['aliases_before']}
        status['aliases_unchanged']=status['aliases_after']==plan['aliases_before']
        status['source_unchanged']=sha(plan['source'])==plan['source_sha256']
        status['finished_utc']=datetime.now(timezone.utc).isoformat();save()
    return status
