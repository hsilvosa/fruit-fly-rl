"""Bounded, decision-aligned history for a user-selected modeled neuron."""
from collections import deque
import numpy as np
from fly_rl.simulation.world import DT

class NeuralTrace:
    def __init__(self,capacity=240):
        self.rows=deque(maxlen=capacity);self.body_id=None;self.index=None

    def select(self,body_id,index):
        if body_id!=self.body_id:
            self.rows.clear();self.body_id=body_id;self.index=index

    def sample(self,neural,episode,world):
        if self.index is None or neural.last is None: return None
        step=neural.last['decision_step']
        if self.rows and self.rows[-1]['decision_step']==step: return None
        row={'body_id':int(self.body_id),'decision_step':step,'seconds':(step-1)*DT,'phase':'before_action',
             'episode_id':episode,'activity':float(neural.snapshot[self.index]),
             'change':float(neural.delta[self.index]),'sensitivity':float(neural.sensitivity[self.index]),
             'sensitivity_basis':neural.last.get('sensitivity_basis','recurrent_neuron_state'),
             'sensitivity_control':neural.last['dominant_control'],'action':neural.last['action'],
             'speed':float(np.linalg.norm(world.velocity)),'target_distance':float(world.distance),
             'bank':float(world.bank),'yaw_rate':float(world.yaw_rate)}
        self.rows.append(row);return row
