"""Ordered CSR execution retains signed connectivity and empty neuron rows."""
import torch
from fly_rl.connectome.repeatable_readout import RepeatableDualActivityBrain


def test_signed_sparse_product_matches_dense_with_empty_rows():
    matrix=torch.tensor([[0.,-2.,0.],[1.,0.,3.],[0.,0.,0.],[4.,0.,-1.]])
    csr=matrix.to_sparse_csr();values=torch.tensor([[1.,2.],[3.,4.],[5.,6.]])
    brain=object.__new__(RepeatableDualActivityBrain);brain._csr_cache={}
    first=brain.multiply(csr,values);second=brain.multiply(csr,values)
    assert torch.equal(first,matrix@values)
    assert torch.equal(first,second)
    assert len(brain._csr_cache)==1


def test_repeatable_checkpoint_has_its_own_validated_fingerprint(tmp_path):
    import json,pytest
    from fly_rl.training.learning import checkpoint_sensor_version,checkpoint_readout
    from fly_rl.connectome.repeatable_readout import REPEATABLE_DUAL_READOUT
    from fly_rl.simulation.sensors import SENSOR_V6
    path=tmp_path/'policy.zip'
    metadata=dict(sensor_version=SENSOR_V6,readout_version=REPEATABLE_DUAL_READOUT,
        fingerprint=f'test-data:reservoir-v2-{SENSOR_V6}-256-seed42-leak0.5-scale0.9:{REPEATABLE_DUAL_READOUT}')
    path.with_suffix('.json').write_text(json.dumps(metadata))
    assert checkpoint_sensor_version(path)==SENSOR_V6
    assert checkpoint_readout(path)==REPEATABLE_DUAL_READOUT
    metadata['fingerprint']=metadata['fingerprint'].replace(REPEATABLE_DUAL_READOUT,'neural-projection-dual-map005-distance-clean-v1')
    path.with_suffix('.json').write_text(json.dumps(metadata))
    with pytest.raises(ValueError,match='metadata/fingerprint'):checkpoint_readout(path)
