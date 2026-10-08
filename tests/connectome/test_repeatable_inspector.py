"""The inspector must combine both declared dual feature coordinates."""
from types import SimpleNamespace
import pytest,torch
from fly_rl.connectome.dual_readout import DUAL_READOUT,DUAL_FEATURES
from fly_rl.connectome.repeatable_readout import REPEATABLE_DUAL_READOUT
from fly_rl.connectome.segmented_readout import SEGMENTED_DUAL_READOUT
from fly_rl.visualization.neural_view import NeuralInspector

@pytest.mark.parametrize('reader',[DUAL_READOUT,REPEATABLE_DUAL_READOUT,SEGMENTED_DUAL_READOUT])
def test_dual_inspector_combines_repeated_neural_range_coordinate(reader):
    torch.set_num_threads(2)
    projection=torch.sparse_coo_tensor(torch.tensor([[270],[1]]),torch.tensor([2.]),(3869,3)).to_sparse_csr()
    brain=SimpleNamespace(device=torch.device('cpu'),sensor_count=3869,norm=torch.ones(3869),factor=torch.eye(3869),projection_transpose=projection,readout_version=reader)
    inspector=NeuralInspector.__new__(NeuralInspector);inspector.brain=brain
    gradient=torch.zeros(DUAL_FEATURES);gradient[270]=.7;gradient[3870]=.9
    before=gradient.clone();sensitivity,basis=inspector.current_sensitivity(gradient)
    assert basis=='reconstructed_neuronal_drive'
    torch.testing.assert_close(torch.from_numpy(sensitivity),torch.tensor([0.,3.2,0.]))
    assert torch.equal(gradient,before)
