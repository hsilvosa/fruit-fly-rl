import numpy as np
import torch
from gymnasium.spaces import Box
from fly_rl.training.directional_panorama_policy import DirectionalPanoramicBrainHistory

def test_attention_preserves_angular_rotation_and_finite_gradients():
    torch.set_num_threads(2)
    network=DirectionalPanoramicBrainHistory(Box(-np.inf,np.inf,(9,3869),dtype=np.float32))
    observations=torch.randn(2,9,3869)*.03
    rotated=observations.clone();panorama=rotated[:,:,269:].reshape(2,9,2,25,72)
    rotated[:,:,269:]=torch.roll(panorama,5,-1).reshape(2,9,3600)
    theta=np.deg2rad(25);c,s=np.cos(theta),np.sin(theta)
    xy=observations[:,:,256:258]
    rotated[:,:,256]=c*xy[:,:,0]-s*xy[:,:,1]
    rotated[:,:,257]=s*xy[:,:,0]+c*xy[:,:,1]
    features,waypoint,logits=network.forward_with_attention(observations)
    _,turned,turned_logits=network.forward_with_attention(rotated)
    expected=waypoint.clone();expected[:,0]=c*waypoint[:,0]-s*waypoint[:,1];expected[:,1]=s*waypoint[:,0]+c*waypoint[:,1]
    torch.testing.assert_close(turned[:,:3],expected[:,:3],atol=2e-5,rtol=2e-5)
    torch.testing.assert_close(turned_logits.reshape(2,25,72),torch.roll(logits.reshape(2,25,72),5,-1),atol=2e-5,rtol=2e-5)
    assert features.shape==(2,192)
    (features.square().mean()+waypoint.square().mean()).backward()
    assert all(torch.isfinite(p.grad).all() for p in network.parameters() if p.grad is not None)
