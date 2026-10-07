"""Bounded fresh PPO curriculum; original-goal validation and no planner actions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.architectural_curriculum_env import ArchitecturalCurriculumEnv
from fly_rl.training.architectural_mastery import ArchitecturalMastery
from fly_rl.training.architectural_mixed_schedule import MixedTaskScheduler, restore_mastery
from fly_rl.training.autonomous_architecture import make_autonomous_policy, save_autonomous_policy, load_autonomous_policy


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)



def save_curriculum_checkpoint(model, path, env, mastery, protocol_hash):
    save_autonomous_policy(model,path,env)
    metadata_path=Path(path).with_suffix('.json')
    metadata=json.loads(metadata_path.read_text(encoding='utf-8'))
    metadata['training_curriculum']=dict(protocol_sha256=protocol_hash,
        physical_stage=env.curriculum_stage,mastery=mastery.snapshot(),
        original_tasks_unchanged_for_validation=True)
    save(metadata_path,metadata)


def evaluate(model, env, cases):
    if env.curriculum_stage != 4:
        raise ValueError("Validation requires unchanged original goals")
    results=[]
    for case in cases:
        observation=env.select_situation(case['scene'],case['situation'],case['seed'])
        limit=env.worlds[0].episode_limit
        for step in range(limit):
            action,_=model.predict(observation,deterministic=True)
            observation,reward,done,infos=env.step(action)
            if not np.isfinite(observation).all() or not np.isfinite(reward).all():
                raise ValueError('Non-finite validation transition')
            if done[0]:
                info=infos[0]
                results.append(dict(case,steps=step+1,success=bool(info['success']),
                                    collision=bool(info['collision']),timeout=bool(info['truncated']),
                                    distance_end=float(info['distance'])))
                break
        else:raise RuntimeError('Episode failed to end at its original physical deadline')
    return results


class Telemetry(BaseCallback):
    def __init__(self, output, state, started, mastery):
        super().__init__();self.output=output;self.state=state;self.started=started;self.mastery=mastery

    def _on_step(self):
        for info in self.locals['infos']:
            if 'episode' in info:
                if self.training_env.curriculum_stage==self.mastery.stage:
                    self.mastery.record((self.training_env.architectural_scene,self.training_env.architectural_situation),bool(info['success']))
                self.state['mastery']=self.mastery.snapshot()
                with (self.output/'episodes.jsonl').open('a',encoding='utf-8') as handle:
                    handle.write(json.dumps(dict(transitions=self.num_timesteps-self.state['source_transitions'],total_transitions=self.num_timesteps,
                        curriculum_stage=self.training_env.curriculum_stage,
                        scene=self.training_env.architectural_scene,
                        situation=self.training_env.architectural_situation,
                        reward=float(info['episode']['r']),steps=int(info['episode']['l']),
                        success=bool(info['success']),collision=bool(info['collision']),
                        timeout=bool(info['truncated'])))+'\n')
        if self.num_timesteps%512==0:
            self.state.update(training_transitions=self.num_timesteps-self.state['source_transitions'],total_transitions=self.num_timesteps,
                              training_elapsed_seconds=time.monotonic()-self.started)
            save(self.output/'status.json',self.state)
        return True


def train(output, transitions, source, version='learned-architecture-1.0-exp.2', verification=False):
    if type(verification) is not bool or type(transitions) is not int or (transitions != 128 if verification else transitions not in (65536,131072)):
        raise ValueError('Use 65536 or 131072 additional transitions, or a 128-transition verification')
    chunk_steps=128 if verification else 4096
    rollout_steps=128 if verification else 512
    epochs=1 if verification else 5
    chunks=transitions//chunk_steps
    output=Path(output)
    if output.exists():raise ValueError('Never overwrite or restart a prior experiment')
    source=Path(source)
    source_metadata=json.loads(source.with_suffix('.json').read_text())
    if source_metadata.get('version') != version or 'training_curriculum' not in source_metadata:
        raise ValueError('Source must be a compatible curriculum checkpoint')
    training=[];validation=[]
    for scene,builder in BUILDERS.items():
        count=len(builder().situations)
        training.extend(dict(scene=scene,situation=i) for i in range(count-1))
        validation.append(dict(scene=scene,situation=count-1,seed=200001))
    protected={str(p):digest(p) for p in Path('runs').glob('*policy.*') if p.suffix in ('.json','.zip')}
    protected.update({str(source):digest(source),str(source.with_suffix('.json')):digest(source.with_suffix('.json'))})
    sources={str(p):digest(p) for p in list(Path('fly_rl').rglob('*.py'))+[Path(__file__)]}
    protocol=dict(version='autonomous-architecture-mixed-1',algorithm='PPO',fresh_initialization=False,source_checkpoint=str(source),source_transitions=source_metadata['training_transitions'],scheduler_restart=True,policy_version=version,
        planner_assistance=False,imitation_updates=0,training_transitions=transitions,
        rollout_steps=rollout_steps,epochs=epochs,batch_size=128,seed=42,verification_only=verification,
        curriculum_stage_order=[0,1,2,4],curriculum_distances=[1,2,4,'original'],
        mastery='two disjoint rounds, eight completed episodes per task, at least six goals in every task',
        progression_boundary='between chunks; no old-stage episodes counted in new stage',
        unavailable_goal='fail explicitly; no silent geometry or distance changes',
        training_cases=training,validation_cases=validation,
        schedule='alternate lesson and original task chunks, training cases only',
        lesson_chunk_transitions=128 if verification else 2048,original_chunk_transitions=2048,
        checkpoint_selection='final-budget checkpoint only; no tuning on validation',
        validation='before and after: one withheld situation per inspected scene; shared geometry, not independent generalization',
        reserved_test_access=False,protected_before=protected,sources=sources,
        scene_hashes={name:builder().fingerprint() for name,builder in BUILDERS.items()})
    output.mkdir(parents=True);save(output/'protocol.json',protocol)
    state=dict(status='initializing',started_utc=datetime.now(timezone.utc).isoformat(),
               training_transitions=0,training_budget=transitions,protocol_sha256=digest(output/'protocol.json'))
    save(output/'status.json',state);env=None
    try:
        import torch
        env=ArchitecturalCurriculumEnv(training[0]['scene'],device='cuda',seed=42,stage=4)
        mastery=ArchitecturalMastery([(c['scene'],c['situation']) for c in training])
        mastery=restore_mastery(mastery.cases,source_metadata['training_curriculum']['mastery'])
        scheduler=MixedTaskScheduler(mastery.cases)
        assert env.brain.n==167184 and env.brain.audit['edges']==25583622
        model=load_autonomous_policy(source,env)
        if verification:
            model.n_steps=128;model.n_epochs=1
            model.rollout_buffer.buffer_size=128;model.rollout_buffer.reset()
        elif model.n_steps!=512 or model.n_epochs!=5:
            raise ValueError('Source PPO settings disagree with protocol')
        initial_steps=model.num_timesteps
        initial_updates=model._n_updates
        assert initial_steps==source_metadata['training_transitions']
        state['source_transitions']=initial_steps
        state['restored_mastery']=mastery.snapshot()
        state['source_optimizer_epoch_passes']=initial_updates
        state.update(status='validation-before',neurons=env.brain.n,edges=env.brain.audit['edges'],
                     policy_device=str(model.device),brain_fingerprint=env.brain.fingerprint)
        save(output/'status.json',state)
        state['validation_before']=evaluate(model,env,validation)
        if verification:
            obs=env.select_situation(training[0]['scene'],training[0]['situation'],42)
            action,_=model.predict(obs,deterministic=True)
            probe_obs,probe_reward,_,_=env.step(action)
            assert np.isfinite(probe_obs).all() and np.isfinite(probe_reward).all()
            state['original_goal_probe_transitions']=1
            state['original_goal_probe_stage']=env.curriculum_stage
        env.select_stage(mastery.stage,seed=42)
        started=time.monotonic();torch.cuda.reset_peak_memory_stats()
        state['status']='running';save(output/'status.json',state)
        index=0
        while model.num_timesteps-initial_steps<transitions:
            physical_stage,(scene,situation)=scheduler.select(mastery)
            case=dict(scene=scene,situation=situation)
            chunk_steps=min(transitions-(model.num_timesteps-initial_steps),128 if verification else 2048)
            with (output/'schedule.jsonl').open('a',encoding='utf-8') as handle:
                handle.write(json.dumps(dict(chunk=index+1,transitions=model.num_timesteps-initial_steps,total_transitions=model.num_timesteps,stage=physical_stage,case=case,chunk_steps=chunk_steps))+'\n')
            assert all(digest(name)==sha for name,sha in sources.items()),'Frozen sources changed'
            if env.curriculum_stage!=physical_stage:
                env.select_stage(physical_stage,seed=42+index)
            observation=env.select_situation(case['scene'],case['situation'],42+index)
            model._last_obs=observation
            model._last_episode_starts=np.ones(env.num_envs,dtype=bool)
            state.update(active_chunk=index+1,active_scene=case['scene'],active_situation=case['situation'])
            model.learn(total_timesteps=chunk_steps,reset_num_timesteps=False,callback=Telemetry(output,state,started,mastery))
            losses={k:float(v) for k,v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}
            assert losses and all(np.isfinite(v) for v in losses.values()),'Non-finite PPO losses'
            with (output/'updates.jsonl').open('a',encoding='utf-8') as handle:
                handle.write(json.dumps(dict(chunk=index+1,transitions=model.num_timesteps-initial_steps,total_transitions=model.num_timesteps,losses=losses))+'\n')
            if (model.num_timesteps-initial_steps)%32768==0:
                save_curriculum_checkpoint(model,output/f'step-{model.num_timesteps}.zip',env,mastery,state['protocol_sha256'])
            index+=1
        assert model.num_timesteps-initial_steps==transitions
        save_curriculum_checkpoint(model,output/'final-policy.zip',env,mastery,state['protocol_sha256'])
        state.update(status='validation-after',training_transitions=model.num_timesteps-initial_steps,
                     training_elapsed_seconds=time.monotonic()-started,
                     peak_vram_gib=torch.cuda.max_memory_allocated()/2**30)
        save(output/'status.json',state)
        env.select_stage(4,seed=200001)
        state['validation_after']=evaluate(model,env,validation)
        state['mastery']=mastery.snapshot()
        observation=env.reset();expected=model.predict(observation,deterministic=True)[0]
        reloaded=load_autonomous_policy(output/'final-policy.zip',env)
        assert np.allclose(expected,reloaded.predict(observation,deterministic=True)[0],atol=1e-6)
        state.update(status='completed',checkpoint_roundtrip=True,finite_losses=True,
                     optimizer_epoch_passes=model._n_updates-initial_updates,ppo_rollouts=transitions//rollout_steps,
                     planner_assistance=False,reserved_test_access=False,promoted=False)
    except BaseException as exc:
        state.update(status='failed',error=repr(exc))
        raise
    finally:
        if env is not None:env.close()
        state.update(finished_utc=datetime.now(timezone.utc).isoformat(),
                     sources_unchanged=all(digest(name)==sha for name,sha in sources.items()),
                     protected_after={name:digest(name) for name in protected})
        state['protected_unchanged']=state['protected_after']==protected
        save(output/'status.json',state)
    return state


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--policy-version',choices=['learned-architecture-1.0-exp.1','learned-architecture-1.0-exp.2'],default='learned-architecture-1.0-exp.2')
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--transitions',type=int,required=True)
    parser.add_argument('--verification',action='store_true',help='Exactly 128 learning transitions and one PPO update; no performance claim')
    args=parser.parse_args()
    result=train(args.output,args.transitions,args.source,args.policy_version,args.verification)
    print(json.dumps(result,indent=2))
