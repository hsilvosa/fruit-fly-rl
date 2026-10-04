"""Versioned sparse directional pooling over the same neural panorama."""
import torch
from fly_rl.training.directional_panorama_policy import DirectionalPanoramicBrainHistory
from fly_rl.simulation.sensors import SENSORS,PANORAMA_COUNT,PANORAMA_SHAPE

class SparseDirectionalPanoramicBrainHistory(DirectionalPanoramicBrainHistory):
    def forward_with_attention(self,observations):
        batch,frames,_=observations.shape
        values=observations.reshape(batch*frames,-1)*self.neural_scale
        panorama=values[:,SENSORS:].reshape(batch*frames,2,*PANORAMA_SHAPE)
        image=self.visual_map(panorama)
        goal=values[:,256:259]
        goal=goal/torch.linalg.vector_norm(goal,dim=1,keepdim=True).clamp_min(1e-5)
        logits=self.attention(image).flatten(1)+3.*(goal@self.ray_directions.T)
        selected=logits.topk(9,dim=1).indices
        scores=logits.gather(1,selected).softmax(dim=1)
        weights=torch.zeros_like(logits).scatter(1,selected,scores)
        occupied=values.ne(0).any(dim=1)
        # Empty histories must not acquire an arbitrary direction from tied logits.
        weights=torch.where(occupied[:,None],weights,logits.softmax(1))
        direction=weights@self.ray_directions
        direction=direction/torch.linalg.vector_norm(direction,dim=1,keepdim=True).clamp_min(1e-5)
        direction=torch.where(occupied[:,None],direction,torch.zeros_like(direction))
        pooled=(image.flatten(2)*weights[:,None]).sum(dim=2)
        distance_signal=(panorama[:,0].flatten(1)*weights).sum(1,keepdim=True)
        summary=torch.cat([pooled,direction,distance_signal,goal,torch.linalg.vector_norm(values[:,256:259],dim=1,keepdim=True)],dim=1)
        encoded=torch.cat([self.proprioception(values[:,:SENSORS]),self.visual_projection(summary)],dim=1)
        sequence,_=self.memory(encoded.reshape(batch,frames,192));latent=sequence[:,-1]
        raw=self.waypoint_head(latent)
        waypoint=torch.cat([direction.reshape(batch,frames,3)[:,-1],raw[:,3:]],dim=1)
        return latent+self.waypoint_residual(waypoint),waypoint,logits.reshape(batch,frames,PANORAMA_COUNT)[:,-1]
