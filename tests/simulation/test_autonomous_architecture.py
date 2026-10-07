from types import SimpleNamespace
import ast
from pathlib import Path
import numpy as np
import pytest
import torch
from gymnasium import spaces
from fly_rl.training.autonomous_architecture import ArchitecturalHistoryEncoder, contract, load_autonomous_policy


def test_encoder_shape_and_trainable_gradient():
    space=spaces.Box(-np.inf,np.inf,(9,5669),dtype=np.float32)
    encoder=ArchitecturalHistoryEncoder(space)
    output=encoder(torch.randn(2,9,5669))
    assert output.shape==(2,128) and torch.isfinite(output).all()
    output.square().mean().backward()
    assert encoder.frame[0].weight.grad is not None
    assert torch.isfinite(encoder.frame[0].weight.grad).all()
    with pytest.raises(ValueError):
        ArchitecturalHistoryEncoder(spaces.Box(-np.inf,np.inf,(9,2069),dtype=np.float32))


def test_module_does_not_import_a_planner():
    tree=ast.parse(Path('fly_rl/training/autonomous_architecture.py').read_text())
    modules=[node.module for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
    assert not any(module and module.startswith('fly_rl.navigation') for module in modules)


def test_planner_checkpoint_is_rejected_before_loading(tmp_path):
    import json
    env=SimpleNamespace(observation_space=SimpleNamespace(shape=(9,5669)),
        brain=SimpleNamespace(fingerprint='contract-fixture',readout_version='segmented',sensor_version='v6'),
        history_frames=8,history_stride=8,worlds=[SimpleNamespace(dynamics='coordinated')],
        architectural_scene='office-floor',architectural_situation=0)
    metadata=contract(env);metadata['planner_assistance']=True
    checkpoint=tmp_path/'invalid.zip'
    checkpoint.with_suffix('.json').write_text(json.dumps(metadata))
    with pytest.raises(ValueError,match='planner_assistance'):
        load_autonomous_policy(checkpoint,env)
