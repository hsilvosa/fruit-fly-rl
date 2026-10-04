"""Fixed whole-connectome reservoir. No gradients or hidden policy bypass."""
from pathlib import Path
import json
import numpy as np
from scipy import sparse
import torch

FEATURES=256
from fly_rl.simulation.sensors import SENSORS,SENSOR_VERSION
MODEL_SPEC=f'reservoir-v2-{SENSOR_VERSION}-256-seed42-leak0.5-scale0.9'

class Brain:
    def __init__(self, data='data', batch=1, device='cuda', matrix=None,sensor_version=None):
        from fly_rl.simulation.sensors import validate_sensor_version,sensor_count,SENSOR_V4,SENSOR_V5,SENSOR_V6
        self.sensor_version=validate_sensor_version(sensor_version or SENSOR_VERSION)
        self.sensor_count=sensor_count(self.sensor_version)
        self.model_spec=f'reservoir-v2-{self.sensor_version}-256-seed42-leak0.5-scale0.9'
        self.device=torch.device(device)
        if self.device.type=='cuda' and not torch.cuda.is_available():
            raise RuntimeError('CUDA unavailable. Use --device cpu explicitly; no automatic graph reduction.')
        if matrix is None:
            path=Path(data)/'processed'
            self.audit=json.loads((path/'audit.json').read_text())
            from fly_rl.connectome.data import sha256
            for filename,digest in self.audit['processed_files'].items():
                if sha256(path/filename)!=digest: raise ValueError('Processed graph checksum mismatch: '+filename)
            matrix=sparse.load_npz(path/'brain.npz').tocsr()
            if matrix.shape[0]!=self.audit['annotated_neurons']: raise ValueError('Graph coverage mismatch')
        else:
            self.audit={'fingerprint':'test-only','annotated_neurons':matrix.shape[0], 'edges':matrix.nnz}
            matrix=matrix.tocsr()
        self.n=matrix.shape[0]
        if matrix.shape!=(self.n,self.n): raise ValueError('Graph must be square')
        self.matrix=torch.sparse_csr_tensor(torch.from_numpy(matrix.indptr.astype(np.int64)),
            torch.from_numpy(matrix.indices.astype(np.int64)),torch.from_numpy(matrix.data.astype(np.float32)),
            size=matrix.shape,device=self.device)
        rng=np.random.default_rng(42)
        self.input_index=torch.as_tensor(rng.integers(0,SENSORS,(self.n,2)),device=self.device)
        self.input_sign=torch.as_tensor(rng.choice([-1.,1.],(self.n,2)).astype(np.float32),device=self.device)
        bucket=rng.integers(0,FEATURES,self.n)
        sign=rng.choice([-1.,1.],self.n).astype(np.float32)
        normalization=np.sqrt(np.maximum(np.bincount(bucket,minlength=FEATURES),1))
        self.bucket=torch.as_tensor(bucket,device=self.device)
        self.output_sign=torch.as_tensor(sign/normalization[bucket],dtype=torch.float32,device=self.device)
        self.state=torch.zeros((self.n,batch),device=self.device)
        self.batch=batch
        # Preserve every existing sensory and pooling assignment for explicit transfer.
        clock_rng=np.random.default_rng(104729)
        self.clock_weight=torch.as_tensor(clock_rng.choice([-0.25,0.,0.25],self.n,p=[.125,.75,.125]).astype(np.float32),device=self.device) if self.sensor_version==SENSOR_V4 else None

        self.fan_index=None
        if self.sensor_version in (SENSOR_V5,SENSOR_V6):
            fan_rng=np.random.default_rng(123457)
            self.fan_index=torch.as_tensor(fan_rng.integers(SENSORS,self.sensor_count,(self.n,2)),device=self.device)
            self.fan_sign=torch.as_tensor(fan_rng.choice([-1.,1.],(self.n,2)).astype(np.float32),device=self.device)
            from fly_rl.simulation.sensors import FAN_COUNT,PANORAMA_COUNT
            visual_count=FAN_COUNT if self.sensor_version==SENSOR_V5 else PANORAMA_COUNT
            self.fan_center=torch.as_tensor((self.fan_index.cpu().numpy()<SENSORS+visual_count)*.5,dtype=torch.float32,device=self.device)

    @torch.no_grad()
    def reset(self, indices=None):
        if indices is None: self.state.zero_()
        else: self.state[:,indices]=0

    @torch.no_grad()
    def step(self, sensors):
        x=torch.as_tensor(sensors,dtype=torch.float32,device=self.device)
        if x.shape!=(self.batch,self.sensor_count): raise ValueError(f'Expected {(self.batch,self.sensor_count)}, got {x.shape}')
        sensory=(x[:,self.input_index]*self.input_sign).sum(-1).T*0.5
        if self.clock_weight is not None:
            sensory=sensory+self.clock_weight[:,None]*x[:,-1][None,:]
        if self.fan_index is not None:
            sensory+=.25*((x[:,self.fan_index]-self.fan_center)*self.fan_sign).sum(-1).T
        update=torch.tanh(torch.sparse.mm(self.matrix,self.state)+sensory)
        self.state.mul_(0.5).add_(update,alpha=0.5)
        pooled=torch.zeros((FEATURES,self.batch),device=self.device)
        pooled.index_add_(0,self.bucket,self.state*self.output_sign[:,None])
        return pooled.T.contiguous().cpu().numpy()

    @property
    def fingerprint(self):
        return self.audit['fingerprint']+':'+self.model_spec
