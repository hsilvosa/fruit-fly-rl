import json
import numpy as np
import pytest
from scipy import sparse
from fly_rl.connectome.brain import Brain
from fly_rl.simulation.sensors import SENSOR_V4
from fly_rl.training.learning import BrainEnv
from fly_rl.training.mastery_curriculum import configure_mastery,MasterySchedule

PROFILES=['gate-near','gate-long','gate-two','passages-wide','large-wide','large-narrow','large']
PRACTICE=list(range(370112,370128))

def environment():
    brain=Brain(batch=4,device='cpu',matrix=sparse.eye(128,format='csr')*.1,sensor_version=SENSOR_V4)
    return BrainEnv(batch=4,device='cpu',brain=brain,mode='dense',layout_seeds=list(range(370000,370008)),dynamics='coordinated',sensor_version=SENSOR_V4,map_profile='large')


def test_target_lanes_get_exact_transitions_even_with_failed_practice():
    env=environment();gate=configure_mastery(env,132,0,42,PROFILES,PRACTICE,target_envs=2)
    env.reset()
    assert [w.map_profile.name for w in env.worlds]==['large','large','gate-near','gate-near']
    for _ in range(32):env.step(np.zeros((4,4)))
    assert gate.stage==0
    assert gate.steps['large']==64 and gate.steps['gate-near']==64 and gate.transitions==128
    assert all(w.layout_seeds==list(range(370000,370008)) for w in env.worlds)
    # A natural timeout preserves the dedicated lane without advancing the gate.
    env.worlds[0].ticks=env.worlds[0].episode_limit-1
    _,_,done,infos=env.step(np.zeros((4,4)))
    assert done[0] and env.worlds[0].map_profile.name=='large' and env.worlds[0].ticks==0
    assert infos[0]['truncated']
    snapshot=json.loads(json.dumps(gate.snapshot()))
    restored=MasterySchedule(132,PROFILES,PRACTICE,gate.transitions,snapshot,target_envs=2)
    assert restored.steps==gate.steps
    with pytest.raises(ValueError,match='resume'):
        MasterySchedule(132,PROFILES,PRACTICE,gate.transitions,snapshot,target_envs=1)

@pytest.mark.parametrize('count',[-1,4,True])
def test_invalid_target_allocation_rejected(count):
    env=environment()
    with pytest.raises(ValueError):configure_mastery(env,128,0,42,PROFILES,PRACTICE,target_envs=count)
