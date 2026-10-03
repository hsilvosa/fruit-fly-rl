"""Actual modeled neuron activity and local actor sensitivity, with real body IDs."""
from pathlib import Path
import numpy as np
import torch

class NeuralInspector:
    def __init__(self,brain,data):
        self.ids=np.load(Path(data)/'processed'/'neuron_ids.npy',allow_pickle=False)
        if len(self.ids)!=brain.n: raise ValueError('Neuron ID ordering mismatch')
        self.brain=brain;self.previous=None
        self.bucket=brain.bucket.cpu().numpy();self.sign=brain.output_sign.cpu().numpy()
        self.last=None

    def sample(self,policy,features,action,step):
        state=self.brain.state[:,0].detach().cpu().numpy().copy()
        change=np.zeros_like(state) if self.previous is None else state-self.previous
        active=np.argsort(-np.abs(state))[:6]
        changing=np.argsort(-np.abs(change))[:6]
        x=torch.as_tensor(features,dtype=torch.float32).clone().requires_grad_(True)
        mean=policy.policy.get_distribution(x).distribution.mean.clamp(-1,1)
        axis=int(np.argmax(np.abs(action)))
        gradient=torch.autograd.grad(mean[0,axis],x)[0][0].detach().numpy()
        sensitivity=gradient[self.bucket]*self.sign
        self.snapshot=state;self.delta=change;self.sensitivity=sensitivity
        influential=np.argsort(-np.abs(sensitivity))[:6]
        def values(indices,array): return [{'neuron_id':int(self.ids[i]),'value':float(array[i])} for i in indices]
        self.last={'decision_step':step,'phase':'before_action','activity':values(active,state),
            'activity_change':values(changing,change),'dominant_control':['forward','bank/lateral','vertical','yaw'][axis],
            'local_sensitivity':values(influential,sensitivity),'action':np.asarray(action).tolist(),
            'mean_abs_activity':float(np.abs(state).mean()),'causal_claim':False}
        self.previous=state
        return self.last

    def reset(self): self.previous=None;self.last=None

    def text(self):
        if self.last is None: return 'NEURON ACTIVITY\nWaiting for a decision'
        result=self.last
        def lines(key):
            return '\n'.join(f'{r["neuron_id"]}: '+(f'{r["value"]:+.2e}' if key=='local_sensitivity' else f'{r["value"]:+.4f}') for r in result[key])
        return ('MODELED NEURON ACTIVITY\nReal MaleCNS body IDs / schematic values\n'
            f'Decision {result["decision_step"]} / before action\n\nMost active | signed activity\n'+lines('activity')+
            '\n\nLargest change since last sample\n'+lines('activity_change')+
            '\n\nLocal sensitivity: '+result['dominant_control']+'\n'+lines('local_sensitivity')+
            '\n\nSensitivity is a local derivative.\nActivity alone does not prove causation.\nB: toggle / SPACE: pause')
