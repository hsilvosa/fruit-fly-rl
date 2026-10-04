import numpy as np
import torch
from gymnasium.spaces import Box
from fly_rl.training.distance_only_panorama_policy import DistanceOnlyPanoramicBrainHistory

def test_visual_approach_plane_does_not_choose_the_direction():
    torch.set_num_threads(2)
    model=DistanceOnlyPanoramicBrainHistory(Box(-np.inf,np.inf,(9,3869),dtype=np.float32))
    observations=torch.randn(2,9,3869)*.03;observations[:,:8]=0
    changed=observations.clone();changed[...,2069:]=torch.randn_like(changed[...,2069:])*100
    a,q,z=model.forward_with_attention(observations)
    b,r,w=model.forward_with_attention(changed)
    torch.testing.assert_close(a,b,atol=0,rtol=0);torch.testing.assert_close(q,r,atol=0,rtol=0)
    torch.testing.assert_close(z,w,atol=0,rtol=0)
    (a.square().mean()+q.square().mean()).backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
