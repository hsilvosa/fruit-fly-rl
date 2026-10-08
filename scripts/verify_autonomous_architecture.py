"""Explicit 128-transition PPO smoke; not a navigation-performance experiment."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
import torch
from fly_rl.simulation.architectural_env import ArchitecturalBrainEnv
from fly_rl.training.autonomous_architecture import make_autonomous_policy, save_autonomous_policy, load_autonomous_policy


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(output, version='learned-architecture-1.0-exp.1'):
    output=Path(output)
    if output.exists():
        raise ValueError('Never overwrite prior verification')
    aliases=[Path('runs')/name for name in ('dense-flight-policy.json','dense-flight-policy.zip',
            'dense-policy.json','dense-policy.zip','navigation-policy.json','navigation-policy.zip')]
    protected={str(p):digest(p) for p in aliases if p.exists()}
    output.mkdir(parents=True)
    result=dict(status='initializing',verification_only=True,transition_cap=128,policy_version=version,
                planner_assistance=False,reserved_test_access=False,protected_before=protected)
    env=None
    try:
        env=ArchitecturalBrainEnv('office-floor', device='cuda', seed=42)
        assert env.brain.n==167184 and env.brain.audit['edges']==25583622
        model=make_autonomous_policy(env,version=version)
        before={name:p.detach().clone() for name,p in model.policy.named_parameters()}
        started=time.monotonic()
        model.learn(total_timesteps=128)
        assert model.num_timesteps==128 and model._n_updates==1
        losses={key:float(value) for key,value in model.logger.name_to_value.items()
                if key.startswith('train/') and np.isscalar(value)}
        assert losses and all(np.isfinite(value) for value in losses.values())
        changed=any(not torch.equal(before[name],p) for name,p in model.policy.named_parameters())
        assert changed
        observation=env.reset()
        action=model.predict(observation, deterministic=True)[0]
        checkpoint=output/'smoke-policy.zip'
        save_autonomous_policy(model, checkpoint, env)
        reloaded=load_autonomous_policy(checkpoint, env)
        assert np.allclose(action,reloaded.predict(observation,deterministic=True)[0],atol=1e-6)
        result.update(status='completed',transitions=128,optimizer_updates=1,losses=losses,
                      parameters_changed=changed,checkpoint_roundtrip=True,
                      elapsed_seconds=time.monotonic()-started,
                      policy_device=str(model.device),neurons=env.brain.n,edges=env.brain.audit['edges'],
                      navigation_performance_claim=False)
    except BaseException as exc:
        result.update(status='failed',error=repr(exc))
        raise
    finally:
        if env is not None:env.close()
        result['protected_after']={name:digest(Path(name)) for name in protected}
        result['protected_unchanged']=result['protected_after']==protected
        (output/'status.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--policy-version',choices=['learned-architecture-1.0-exp.1','learned-architecture-1.0-exp.2'],default='learned-architecture-1.0-exp.1')
    args=parser.parse_args()
    print(json.dumps(verify(args.output,args.policy_version),indent=2))
