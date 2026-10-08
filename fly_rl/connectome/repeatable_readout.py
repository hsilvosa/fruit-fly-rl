"""Repeatable full-graph dual reconstruction using ordered CUDA accumulation."""
import os
import torch
from fly_rl.connectome.dual_readout import DualActivityBrain, DUAL_READOUT
REPEATABLE_DUAL_READOUT = 'neural-projection-dual-repeatable-index-add-v1'

class RepeatableDualActivityBrain(DualActivityBrain):
    def __init__(self,*args,**kwargs):
        os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
        torch.use_deterministic_algorithms(True)
        super().__init__(*args,**kwargs)
        self.readout_version=REPEATABLE_DUAL_READOUT
        self.model_spec=self.model_spec.replace(DUAL_READOUT,REPEATABLE_DUAL_READOUT)
        self._csr_cache={}

    def multiply(self,matrix,dense):
        key=id(matrix)
        if key not in self._csr_cache:
            columns=matrix.col_indices();weights=matrix.values()
            lengths=matrix.crow_indices()[1:]-matrix.crow_indices()[:-1]
            rows=torch.repeat_interleave(torch.arange(matrix.shape[0],device=matrix.device),lengths,output_size=weights.numel())
            self._csr_cache[key]=(rows,columns,weights)
        rows,columns,weights=self._csr_cache[key]
        output=torch.zeros((matrix.shape[0],dense.shape[1]),dtype=dense.dtype,device=dense.device)
        output.index_add_(0,rows,weights[:,None]*dense[columns])
        return output

    @torch.no_grad()
    def step(self,sensors):
        previous=self.state.clone()
        x=torch.as_tensor(sensors,dtype=torch.float32,device=self.device)
        if x.shape!=(self.batch,self.sensor_count):raise ValueError('Incorrect sensor batch dimensions')
        sensory=(x[:,self.input_index]*self.input_sign).sum(-1).T*.5
        if self.clock_weight is not None:sensory+=self.clock_weight[:,None]*x[:,-1][None,:]
        if self.fan_index is not None:sensory+=.25*((x[:,self.fan_index]-self.fan_center)*self.fan_sign).sum(-1).T
        update=torch.tanh(self.multiply(self.matrix,self.state)+sensory)
        self.state.mul_(.5).add_(update,alpha=.5)
        return self.reconstruct_activity(previous,self.state)

    @torch.no_grad()
    def reconstruct_activity(self,previous,current):
        if previous.shape!=self.state.shape or current.shape!=self.state.shape:raise ValueError('Full neuron states required')
        drive=torch.atanh((2*current-previous).clamp(-1+1e-6,1-1e-6))
        drive+=self.centering_drive[:,None]
        recurrent=self.multiply(self.matrix,previous)
        rhs=self.multiply(self.projection_transpose,torch.cat([drive-recurrent,recurrent],dim=1))
        decoded=torch.cholesky_solve(rhs,self.factor)/self.norm[:,None]
        clean,context=decoded.chunk(2,dim=1)
        mapping=clean+self.recurrent_gain*context
        return torch.cat([mapping,clean[269:2069]],dim=0).T.contiguous().cpu().numpy()
