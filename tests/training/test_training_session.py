import json
from types import SimpleNamespace
import numpy as np
import torch
from fly_rl.training import learning as m
from fly_rl.simulation.sensors import SENSOR_V3


class TinyBrain:
    """Cheap test double; flight physics and episode handling remain real."""
    def __init__(self,data,batch,device,sensor_version=None):
        self.sensor_version=sensor_version;self.state=torch.zeros((1,batch))
    def reset(self,indices=None):
        if indices is None:self.state.zero_()
        else:self.state[:,indices]=0
    def step(self,sensors):
        self.state+=.001
        return np.repeat(self.state.numpy().T,256,axis=1).astype(np.float32)


class SteppingModel:
    """No optimization; drive actual environments across training boundaries."""
    def __init__(self,env):
        self.env=env;self.num_timesteps=0;self._n_updates=0;self.last=None
        self.policy=torch.nn.Linear(1,1)
        self.logger=SimpleNamespace(name_to_value={'train/loss':1.})
        self.seed_calls=0;self.terminal=[]
    def set_random_seed(self,seed):self.seed_calls+=1;self.env.seed(seed)
    def learn(self,total_timesteps,reset_num_timesteps,callback):
        if self.last is None:self.last=self.env.reset()
        for _ in range(total_timesteps):
            self.last,rewards,dones,infos=self.env.step(np.zeros((1,4)))
            self.num_timesteps+=1
            if dones[0]:self.terminal.append((infos[0],float(rewards[0])))


def test_timeout_crosses_chunk_boundary_without_reseeding_or_reset(tmp_path,monkeypatch):
    monkeypatch.setattr(m,'Brain',TinyBrain)
    monkeypatch.setattr(m,'make_policy',lambda env,*args:SteppingModel(env))
    monkeypatch.setattr(m,'save_model',lambda model,path,brain:None)
    session=m.TrainingSession()
    common=dict(data='unused',device='cpu',batch=1,mode='dense',dynamics='coordinated',
                sensor_version=SENSOR_V3,map_profile='gate-near',session=session)
    first=tmp_path/'one.zip';second=tmp_path/'two.zip'
    m.train(steps=1024,output=first,**common)
    env=session.env;model=session.model;activity=env.brain.state.clone()
    assert env.worlds[0].ticks==1024 and not model.terminal
    result=m.train(steps=512,output=second,resume=first,**common)
    assert session.env is env and session.model is model and model.seed_calls==1
    assert result['episode_continuity']['continued_live_session']
    assert result['episode_continuity']['ticks_before']==[1024]
    assert env.worlds[0].ticks==336 and model.num_timesteps==1536
    info,reward=model.terminal[0]
    assert info['truncated'] and info['episode']['l']==1200 and reward < -5
    assert env.brain.state[0,0]<activity[0,0]  # reset only on the actual timeout


def test_inference_randomness_does_not_replace_training_random_stream():
    import random
    session=m.TrainingSession()
    random.seed(5);np.random.seed(5);torch.manual_seed(5)
    session.capture_random_state()
    expected=(random.random(),np.random.random(),torch.rand(3))
    random.seed(100);np.random.seed(100);torch.manual_seed(100)
    session.restore_random_state()
    actual=(random.random(),np.random.random(),torch.rand(3))
    assert expected[:2]==actual[:2] and torch.equal(expected[2],actual[2])


def test_mastery_advances_on_natural_reset_not_on_chunk_boundary(tmp_path,monkeypatch):
    from fly_rl.training.mastery_curriculum import VERSION
    from fly_rl.simulation.map_profiles import PROFILES
    monkeypatch.setattr(m,'Brain',TinyBrain)
    monkeypatch.setattr(m,'make_policy',lambda env,*args:SteppingModel(env))
    monkeypatch.setattr(m,'save_model',lambda *args:None)
    session=m.TrainingSession();practice=list(range(1000,1016))
    profiles=[PROFILES[n].to_dict() for n in ['gate-near','gate-long']]
    common=dict(data='unused',device='cpu',batch=1,mode='dense',dynamics='coordinated',
                sensor_version=SENSOR_V3,map_profile='gate-long',session=session,curriculum=VERSION,
                curriculum_total=1536,curriculum_profiles=profiles,practice_seeds=practice,layout_seeds=[20,21])
    first=tmp_path/'one.zip'
    m.train(steps=1024,output=first,curriculum_offset=0,**common)
    gate=session.env.curriculum;world=session.env.worlds[0]
    batches=[{'training_invoked':False,'map_profile':profiles[0],
              'episodes':[{'seed':s,'success':True,'collision':False,'timeout':False,'steps':1}
                          for s in practice[i*8:(i+1)*8]]} for i in range(2)]
    gate.record_practice(batches)
    assert gate.stage==1 and world.map_profile.name=='gate-near' and world.ticks==1024
    m.train(steps=512,output=tmp_path/'two.zip',resume=first,curriculum_offset=1024,
            curriculum_state=gate.snapshot(),**common)
    assert world.map_profile.name=='gate-long' and world.ticks==336
    assert gate.transitions==1536 and gate.outcomes['gate-near']['timeout']==1
