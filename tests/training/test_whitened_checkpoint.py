import json
import pytest
from fly_rl.training.learning import checkpoint_sensor_version, checkpoint_readout
from fly_rl.connectome.innovation import WHITENED_READOUT, CONTRAST_READOUT, MOTION_STABLE_READOUT
from fly_rl.simulation.sensors import SENSOR_V6


@pytest.mark.parametrize('reader', [WHITENED_READOUT, CONTRAST_READOUT, MOTION_STABLE_READOUT])
def test_whitened_reader_contract_is_validated_for_demo_and_resume(tmp_path, reader):
    path = tmp_path / 'policy.zip'
    spec = f'reservoir-v2-{SENSOR_V6}-256-seed42-leak0.5-scale0.9:{reader}'
    metadata = {'sensor_version': SENSOR_V6, 'readout_version': reader,
                'fingerprint': 'test-audited-graph:' + spec}
    path.with_suffix('.json').write_text(json.dumps(metadata))
    assert checkpoint_sensor_version(path) == SENSOR_V6
    assert checkpoint_readout(path) == reader
    metadata['fingerprint'] = 'test-audited-graph:incompatible-reader'
    path.with_suffix('.json').write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match='metadata/fingerprint'):
        checkpoint_readout(path)
