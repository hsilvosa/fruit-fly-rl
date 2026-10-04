"""Exact panoramic ray observations with bounded CUDA scratch memory."""
import numpy as np
import torch
from fly_rl.simulation.sensors import DIRECTIONS,panorama_directions,SENSOR_V6,RAY_COUNT,RAY_RANGE,FAN_RANGE,PANORAMA_COUNT
from fly_rl.simulation.world import RADIUS

@torch.no_grad()
def _observe_chunk(worlds,device):
    positions=torch.as_tensor(np.stack([w.position for w in worlds]),device=device,dtype=torch.float64)
    velocity=torch.as_tensor(np.stack([w.velocity for w in worlds]),device=device,dtype=torch.float64)
    rooms=torch.as_tensor(np.stack([w.room for w in worlds]),device=device,dtype=torch.float64)
    rotation=torch.as_tensor(np.stack([w.rotation() for w in worlds]),device=device,dtype=torch.float64)
    local=torch.as_tensor(np.vstack([DIRECTIONS,panorama_directions()]),device=device,dtype=torch.float64)
    directions=local[None]@rotation.transpose(1,2)
    delta=torch.as_tensor(np.stack([w.target for w in worlds]),device=device,dtype=torch.float64)-positions
    exits=(torch.where(directions>0,rooms[:,None],torch.zeros_like(directions))-positions[:,None])/torch.where(abs(directions)>1e-9,directions,torch.ones_like(directions))
    exits=torch.where((abs(directions)>1e-9)&(exits>=0),exits,torch.inf)
    distance=exits.min(-1).values
    count=max(len(w.obstacles) for w in worlds)
    if count:
        padded=np.zeros((len(worlds),count,2,3),dtype=np.float64)
        valid=np.zeros((len(worlds),count),dtype=bool)
        for i,w in enumerate(worlds):
            if w.obstacles:padded[i,:len(w.obstacles)]=w.obstacles
            valid[i,:len(w.obstacles)]=True
        boxes=torch.as_tensor(padded,device=device,dtype=torch.float64)
        validity=torch.as_tensor(valid,device=device)
        d=directions[:,:,None,:];parallel=abs(d)<1e-12;safe=torch.where(parallel,torch.ones_like(d),d)
        for offset in range(0,count,128):
            part=boxes[:,offset:offset+128]
            dl=part[:,None,:,0,:]-positions[:,None,None,:];dh=part[:,None,:,1,:]-positions[:,None,None,:]
            a=dl/safe;b=dh/safe
            near=torch.where(parallel,-torch.inf,torch.minimum(a,b)).max(-1).values
            far=torch.where(parallel,torch.inf,torch.maximum(a,b)).min(-1).values
            outside=(parallel&((dl>0)|(dh<0))).any(-1)
            hit=(far>=near.clamp_min(0))&~outside&validity[:,None,offset:offset+128]
            first=torch.where(hit,near.clamp_min(0),torch.inf).min(-1).values
            distance=torch.minimum(distance,first)
    ranges=torch.cat([torch.full((RAY_COUNT,),RAY_RANGE,device=device,dtype=torch.float64),torch.full((PANORAMA_COUNT,),FAN_RANGE,device=device,dtype=torch.float64)])
    distances=torch.minimum(distance,ranges)
    approach=(directions*velocity[:,None]).sum(-1)/3.
    norm=torch.linalg.vector_norm(delta,dim=-1)
    target_local=(delta[:,None]@rotation)[:,0]/norm.clamp_min(1e-6)[:,None]
    local_velocity=(velocity[:,None]@rotation)[:,0]/3.
    previous=torch.as_tensor(np.stack([w.last_action for w in worlds]),device=device,dtype=torch.float64)
    scalars=torch.stack([positions[:,2]/rooms[:,2],torch.tensor([(w.yaw_rate if w.dynamics=='coordinated' else 2.1*w.last_action[3])/2.6 for w in worlds],device=device,dtype=torch.float64)],dim=1)
    base=torch.cat([distances[:,:128]/8.,approach[:,:128],target_local,(norm/torch.linalg.vector_norm(rooms-2*RADIUS,dim=1))[:,None],local_velocity,previous,scalars],dim=1)
    return torch.cat([base,distances[:,128:]/24.,approach[:,128:]],dim=1).clamp(-1,1).float().cpu().numpy()



@torch.no_grad()
def observe_batch(worlds,device='cuda'):
    """Bound scratch memory by world and obstacle chunks; never reduce sensors."""
    if not worlds or any(w.sensor_version!=SENSOR_V6 for w in worlds):
        raise ValueError('Panoramic CUDA observation requires nonempty v6 worlds')
    return np.concatenate([_observe_chunk(worlds[start:start+8],device) for start in range(0,len(worlds),8)],axis=0)
