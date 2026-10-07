"""Bounded full-connectome checks on original architectural development objectives."""
import argparse
from datetime import datetime,timezone
import hashlib,json,time
from pathlib import Path
import numpy as np


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,value):
    def convert(value):
        if isinstance(value,np.ndarray):return value.tolist()
        if isinstance(value,np.generic):return value.item()
        raise TypeError(type(value).__name__)
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2,default=convert)+'\n',encoding='utf-8')
    temporary.replace(path)


def check(output,cap=32768,seconds=600):
    if type(cap) is not int or not 1<=cap<=32768 or not np.isfinite(seconds) or not 1<=seconds<=600:
        raise ValueError('Use at most 32768 transitions and 600 seconds after initialization')
    output=Path(output)
    if output.exists():raise ValueError('Never overwrite or restart an existing architectural check')
    from fly_rl.simulation.architectural_scenes import BUILDERS
    from fly_rl.navigation.architectural_diagnostics import recovery_snapshot
    sources={str(p.resolve()):digest(p) for p in list(Path('fly_rl').rglob('*.py'))+[Path(__file__)]}
    protected={str(Path('runs')/name):digest(Path('runs')/name) for name in
        ['dense-flight-policy.json','dense-flight-policy.zip','dense-policy.json','dense-policy.zip','navigation-policy.json','navigation-policy.zip']}
    cases=[dict(scene=name,situation=index,situation_name=situation.name,scene_sha256=builder().fingerprint(),seed=42)
           for name,builder in BUILDERS.items() for index,situation in enumerate(builder().situations)]
    plan=dict(kind='inspected-architectural-development',controller='planner-1.4-exp.1',cases=cases,
              transition_cap=cap,seconds_cap_after_initialization=seconds,sources=sources,
              acceptance='Report every original objective with its existing physical deadline. No scene edits, shortened objectives, training, reserved tests or generalization claim. Incomplete cases are not timeouts.',
              training_transitions=0,optimizer_updates=0,reserved_test_access=False)
    output.mkdir(parents=True)
    save(output/'protocol.json',plan)
    status=dict(status='initializing',protocol_sha256=digest(output/'protocol.json'),
                started_utc=datetime.now(timezone.utc).isoformat(),physical_transitions=0,cases=[],
                training_transitions=0,optimizer_updates=0,reserved_test_evaluated=False)
    save(output/'status.json',status);env=None;trace=[];began=None
    try:
        import torch
        from fly_rl.simulation.architectural_env import ArchitecturalBrainEnv
        from fly_rl.navigation.architectural import ArchitecturalPlannerPolicy
        env=ArchitecturalBrainEnv(cases[0]['scene'],device='cuda',seed=42)
        assert env.brain.n==167184 and env.brain.audit['edges']==25583622
        status.update(status='running',neurons=env.brain.n,edges=env.brain.audit['edges'],
                      brain_fingerprint=env.brain.fingerprint,sensor_backend=env.sensor_backend)
        began=time.monotonic();torch.cuda.reset_peak_memory_stats()
        stop=False
        for case in cases:
            if stop or status['physical_transitions']>=cap or time.monotonic()-began>=seconds:break
            assert all(digest(name)==sha for name,sha in sources.items()), 'Frozen runtime changed'
            features=env.select_situation(case['scene'],case['situation'],case['seed'])
            world=env.worlds[0];policy=ArchitecturalPlannerPolicy(world.room)
            entry=dict(case,episode_limit=world.episode_limit,start=world.position.copy(),goal=world.target.copy(),
                       steps=0,success=False,collision=False,timeout=False,incomplete=True,distance_end=world.distance)
            status['cases'].append(entry)
            for step in range(world.episode_limit):
                if status['physical_transitions']>=cap or time.monotonic()-began>=seconds:
                    stop=True;break
                action,_=policy.predict(features)
                assert np.isfinite(action).all() and np.isfinite(features).all()
                features,rewards,dones,infos=env.step(action)
                assert np.isfinite(features).all() and np.isfinite(rewards).all()
                info=infos[0];entry.update(steps=step+1,distance_end=info['distance'])
                status['physical_transitions']+=1
                if step%20==0 or dones[0]:
                    trace.append(dict(scene=case['scene'],situation=case['situation'],step=step+1,
                                      position=info['transition_state']['position'],distance=info['distance'],
                                      action=action[0],controller=policy.controller.debug.copy(),
                                      recovery=recovery_snapshot(policy.controller)))
                if status['physical_transitions']%100==0:
                    status['elapsed_seconds']=time.monotonic()-began;save(output/'status.json',status)
                if dones[0]:
                    entry.update(success=info['success'],collision=info['collision'],timeout=bool(info['truncated']),incomplete=False)
                    break
            save(output/'status.json',status)
        status.update(status='completed' if len(status['cases'])==len(cases) and not any(c['incomplete'] for c in status['cases']) else 'budget-stopped',
                      elapsed_seconds=time.monotonic()-began,peak_vram_gib=torch.cuda.max_memory_allocated()/2**30)
    except BaseException as exc:
        status.update(status='failed',error=repr(exc))
        raise
    finally:
        status.update(finished_utc=datetime.now(timezone.utc).isoformat(),
                      sources_unchanged=all(digest(name)==sha for name,sha in sources.items()),
                      protected_unchanged=all(digest(name)==sha for name,sha in protected.items()),protected_before=protected,
                      protected_after={name:digest(name) for name in protected})
        if env is not None:env.close()
        save(output/'trace.json',trace);save(output/'status.json',status)
    return status


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--max-transitions',type=int,default=32768)
    parser.add_argument('--max-seconds',type=float,default=600)
    args=parser.parse_args()
    result=check(args.output,args.max_transitions,args.max_seconds)
    print(json.dumps({k:v for k,v in result.items() if k not in ['cases','protected_before','protected_after']},indent=2))
