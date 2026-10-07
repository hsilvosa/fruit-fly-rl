import numpy as np
import torch
from gymnasium import spaces
from fly_rl.training.structured_architecture import StructuredArchitecturalHistory


def test_goal_state_preserved_and_all_encoders_receive_gradients():
    space=spaces.Box(-np.inf,np.inf,(9,5669),dtype=np.float32)
    encoder=StructuredArchitecturalHistory(space)
    observations=torch.randn(2,9,5669,requires_grad=True)
    output=encoder(observations)
    assert output.shape==(2,141)
    assert torch.equal(output[:,-13:],observations[:,-1,256:269])
    output.square().mean().backward()
    assert torch.isfinite(observations.grad).all()
    assert observations.grad[:,:,269:].abs().sum()>0
    assert observations.grad[:,:,:256].abs().sum()>0
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in encoder.parameters())
