"""Explicit bounded fresh PPO pilot; no planner action assistance."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from fly_rl.simulation.architectural_scenes import BUILDERS
from fly_rl.simulation.architectural_env import ArchitecturalBrainEnv
from fly_rl.training.autonomous_architecture import make_autonomous_policy, save_autonomous_policy, load_autonomous_policy


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)


def evaluate(model, env, cases):
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
    def __init__(self, output, state, started):
        super().__init__();self.output=output;self.state=state;self.started=started

    def _on_step(self):
        for info in self.locals['infos']:
            if 'episode' in info:
                with (self.output/'episodes.jsonl').open('a',encoding='utf-8') as handle:
                    handle.write(json.dumps(dict(transitions=self.num_timesteps,
                        scene=self.training_env.architectural_scene,
                        situation=self.training_env.architectural_situation,
                        reward=float(info['episode']['r']),steps=int(info['episode']['l']),
                        success=bool(info['success']),collision=bool(info['collision']),
                        timeout=bool(info['truncated'])))+'\n')
        if self.num_timesteps%512==0:
            self.state.update(training_transitions=self.num_timesteps,
                              training_elapsed_seconds=time.monotonic()-self.started)
            save(self.output/'status.json',self.state)
        return True


def train(output, transitions):
    if type(transitions) is not int or transitions!=131072:
        raise ValueError('This pilot protocol allows exactly 131072 training transitions')
    output=Path(output)
    if output.exists():raise ValueError('Never overwrite or restart a prior experiment')
    training=[];validation=[]
    for scene,builder in BUILDERS.items():
        count=len(builder().situations)
        training.extend(dict(scene=scene,situation=i) for i in range(count-1))
        validation.append(dict(scene=scene,situation=count-1,seed=200001))
    protected={str(p):digest(p) for p in Path('runs').glob('*policy.*') if p.suffix in ('.json','.zip')}
    sources={str(p):digest(p) for p in list(Path('fly_rl').rglob('*.py'))+[Path(__file__)]}
    protocol=dict(version='autonomous-architecture-pilot-1',algorithm='PPO',fresh_initialization=True,
        planner_assistance=False,imitation_updates=0,training_transitions=transitions,
        rollout_steps=512,epochs=5,batch_size=128,seed=42,
        training_cases=training,validation_cases=validation,
        schedule=[training[i%len(training)] for i in range(32)],chunk_transitions=4096,
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
        env=ArchitecturalBrainEnv(training[0]['scene'],device='cuda',seed=42)
        assert env.brain.n==167184 and env.brain.audit['edges']==25583622
        model=make_autonomous_policy(env,seed=42,rollout_steps=512,epochs=5)
        state.update(status='validation-before',neurons=env.brain.n,edges=env.brain.audit['edges'],
                     policy_device=str(model.device),brain_fingerprint=env.brain.fingerprint)
        save(output/'status.json',state)
        state['validation_before']=evaluate(model,env,validation)
        started=time.monotonic();torch.cuda.reset_peak_memory_stats()
        state['status']='running';save(output/'status.json',state)
        for index,case in enumerate(protocol['schedule']):
            assert all(digest(name)==sha for name,sha in sources.items()),'Frozen sources changed'
            observation=env.select_situation(case['scene'],case['situation'],42+index)
            model._last_obs=observation
            model._last_episode_starts=np.ones(env.num_envs,dtype=bool)
            state.update(active_chunk=index+1,active_scene=case['scene'],active_situation=case['situation'])
            model.learn(total_timesteps=4096,reset_num_timesteps=False,callback=Telemetry(output,state,started))
            losses={k:float(v) for k,v in model.logger.name_to_value.items() if k.startswith('train/') and np.isscalar(v)}
            assert losses and all(np.isfinite(v) for v in losses.values()),'Non-finite PPO losses'
            with (output/'updates.jsonl').open('a',encoding='utf-8') as handle:
                handle.write(json.dumps(dict(chunk=index+1,transitions=model.num_timesteps,losses=losses))+'\n')
            if model.num_timesteps%32768==0:
                save_autonomous_policy(model,output/f'step-{model.num_timesteps}.zip',env)
        assert model.num_timesteps==transitions
        save_autonomous_policy(model,output/'final-policy.zip',env)
        state.update(status='validation-after',training_transitions=model.num_timesteps,
                     training_elapsed_seconds=time.monotonic()-started,
                     peak_vram_gib=torch.cuda.max_memory_allocated()/2**30)
        save(output/'status.json',state)
        state['validation_after']=evaluate(model,env,validation)
        observation=env.reset();expected=model.predict(observation,deterministic=True)[0]
        reloaded=load_autonomous_policy(output/'final-policy.zip',env)
        assert np.allclose(expected,reloaded.predict(observation,deterministic=True)[0],atol=1e-6)
        state.update(status='completed',checkpoint_roundtrip=True,finite_losses=True,
                     optimizer_epoch_passes=model._n_updates,ppo_rollouts=transitions//512,
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
    parser.add_argument('--transitions',type=int,required=True)
    args=parser.parse_args()
    result=train(args.output,args.transitions)
    print(json.dumps(result,indent=2))
