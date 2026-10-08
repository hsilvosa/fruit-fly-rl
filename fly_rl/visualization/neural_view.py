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
        device=next(policy.policy.parameters()).device
        x=torch.as_tensor(features,dtype=torch.float32,device=device).clone().requires_grad_(True)
        mean=policy.policy.get_distribution(x).distribution.mean.clamp(-1,1)
        axis=int(np.argmax(np.abs(action)))
        gradient=torch.autograd.grad(mean[0,axis],x)[0][0].detach()
        if gradient.ndim==2: gradient=gradient[-1]
        sensitivity,basis=self.current_sensitivity(gradient)
        self.snapshot=state;self.delta=change;self.sensitivity=sensitivity
        influential=np.argsort(-np.abs(sensitivity))[:6]
        def values(indices,array): return [{'neuron_id':int(self.ids[i]),'value':float(array[i])} for i in indices]
        self.last={'decision_step':step,'phase':'before_action','activity':values(active,state),
            'activity_change':values(changing,change),'dominant_control':['forward','bank/lateral','vertical','yaw'][axis],
            'local_sensitivity':values(influential,sensitivity),'sensitivity_basis':basis,
            'sensitivity_conditioning':'current readout; older history and previous neuron state held fixed','action':np.asarray(action).tolist(),
            'mean_abs_activity':float(np.abs(state).mean()),'causal_claim':False}
        self.previous=state
        return self.last

    def sample_activity(self,action,step):
        """Record actual activity without inventing gradients for a planner."""
        state=self.brain.state[:,0].detach().cpu().numpy().copy()
        change=np.zeros_like(state) if self.previous is None else state-self.previous
        self.snapshot=state;self.delta=change;self.sensitivity=np.zeros_like(state)
        def values(array):
            indices=np.argsort(-np.abs(array))[:6]
            return [{'neuron_id':int(self.ids[i]),'value':float(array[i])} for i in indices]
        axis=int(np.argmax(np.abs(action)))
        self.last={'decision_step':step,'phase':'before_action','activity':values(state),
            'activity_change':values(change),'dominant_control':['forward','bank/lateral','vertical','yaw'][axis],
            'local_sensitivity':[],'sensitivity_basis':'unavailable_for_explicit_planner',
            'sensitivity_available':False,'action':np.asarray(action).tolist(),
            'mean_abs_activity':float(np.abs(state).mean()),'causal_claim':False}
        self.previous=state
        return self.last

    @torch.no_grad()
    def current_sensitivity(self, gradient):
        """Pull a current-feature gradient back through its actual readout."""
        brain=self.brain
        gradient=gradient.to(brain.device)
        if hasattr(brain,'projection_transpose'):
            from fly_rl.connectome.dual_readout import DUAL_READOUT, DUAL_FEATURES
            from fly_rl.connectome.repeatable_readout import REPEATABLE_DUAL_READOUT
            from fly_rl.connectome.segmented_readout import SEGMENTED_DUAL_READOUT
            if getattr(brain,'readout_version',None) in (DUAL_READOUT, REPEATABLE_DUAL_READOUT, SEGMENTED_DUAL_READOUT):
                if gradient.shape!=(DUAL_FEATURES,):
                    raise ValueError('Dual readout sensitivity requires its declared feature width')
                # Both outputs depend on the same reconstructed current drive.
                # Sum their contributions; previous-state context remains fixed.
                combined=gradient[:brain.sensor_count].clone()
                combined[269:2069]+=gradient[brain.sensor_count:]
                gradient=combined
            # y = N^-1 G^-1 B^T drive. Previous-state recurrence and centering
            # are fixed here. This derivative is with respect to reconstructed
            # preactivation drive, not the plotted leaky neuron state.
            rhs=(gradient/brain.norm)[:,None]
            coefficients=torch.cholesky_solve(rhs,brain.factor)
            projection=brain.projection_transpose.transpose(0,1)
            sensitivity=torch.sparse.mm(projection,coefficients).flatten()
            basis='reconstructed_neuronal_drive'
        elif hasattr(brain,'group_count'):
            weighted=gradient/brain.group_count
            sensitivity=(weighted[brain.input_index]*brain.input_sign).sum(1)
            sensitivity+=(weighted[brain.fan_index]*brain.fan_sign).sum(1)
            basis='recurrent_neuron_state'
        else:
            sensitivity=gradient[brain.bucket]*brain.output_sign
            basis='recurrent_neuron_state'
        return sensitivity.detach().cpu().numpy(),basis

    def reset(self): self.previous=None;self.last=None

    def text(self):
        if self.last is None: return 'NEURON ACTIVITY\nWaiting for a decision'
        result=self.last
        def lines(key):
            return '\n'.join(f'{r["neuron_id"]}: '+(f'{r["value"]:+.2e}' if key=='local_sensitivity' else f'{r["value"]:+.4f}') for r in result[key])
        return ('MODELED NEURON ACTIVITY\nReal MaleCNS body IDs / schematic values\n'
            f'Decision {result["decision_step"]} / before action\n\nMost active | signed activity\n'+lines('activity')+
            '\n\nLargest change since last sample\n'+lines('activity_change')+
            '\n\nLocal sensitivity: '+result['dominant_control']+'\nBasis: '+result['sensitivity_basis']+'\n'+lines('local_sensitivity')+
            '\n\nSensitivity is a local derivative.\nActivity alone does not prove causation.\nB: toggle / SPACE: pause')
