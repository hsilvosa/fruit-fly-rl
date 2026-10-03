from types import SimpleNamespace
import numpy as np
from fly_rl.visualization.neural_trace import NeuralTrace

def test_trace_is_pre_action_bounded_and_keeps_episode_boundaries():
    trace=NeuralTrace(2);trace.select(90,1)
    neural=SimpleNamespace(snapshot=np.array([.1,.8]),delta=np.array([0.,.2]),sensitivity=np.array([0.,.4]),
        last={'decision_step':1,'dominant_control':'yaw','action':[.2,0.,0.,-.3]})
    world=SimpleNamespace(velocity=np.array([3.,0.,0.]),distance=7.,bank=.2,yaw_rate=.4)
    row=trace.sample(neural,5,world)
    assert row['phase']=='before_action' and row['seconds']==0 and row['activity']==.8
    assert row['body_id']==90 and row['speed']==3. and row['action'][3]==-.3
    assert trace.sample(neural,5,world) is None
    neural.last['decision_step']=6;trace.sample(neural,5,world)
    neural.last['decision_step']=11;trace.sample(neural,6,world)
    assert len(trace.rows)==2 and [r['episode_id'] for r in trace.rows]==[5,6]
    assert trace.rows[-1]['seconds']==.5
    trace.select(12,0);assert not trace.rows
    trace.select(None,None);assert trace.sample(neural,6,world) is None
